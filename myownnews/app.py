import os, json, time, uuid, boto3, feedparser, re, html, botocore
from datetime import datetime, timezone

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "amazon.titan-text-lite-v1")
RSS_URLS = [u.strip() for u in os.getenv("RSS_URLS", "").split(",") if u.strip()]
VOICE_ID = os.getenv("VOICE_ID", "Matthew")
BUCKET = os.getenv("BUCKET")
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "3"))

s3 = boto3.client("s3")
polly = boto3.client("polly", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def _pull_articles(urls, limit):
    items = []
    for url in urls:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:limit]:
                items.append({
                    "title": e.get("title",""),
                    "summary": e.get("summary",""),
                    "link": e.get("link",""),
                    "published": e.get("published","")
                })
        except Exception as ex:
            print(f"RSS error for {url}: {ex}")
    return items[:limit]

def _to_prompt(items):
    # collapse items to concise bullets (no labels, no URLs)
    parts = []
    sources = []
    for it in items:
        t = it.get("title", "").strip()
        s = it.get("summary", "").strip()
        if it.get("link"): sources.append(it["link"])
        # keep it compact; no label words
        bullet = f"- {t}. {s}".strip().rstrip(".") + "."
        parts.append(bullet)

    joined = "\n".join(parts)

    prompt = (
    "You are a concise news writer with a light, witty tone (inspired by these sources: Morning Brew/AM Podscast, una produccion de the Voice Village, Informativo de Ángel Martín vibe). "
    "Write a 130–160 word OUT-LOUD script for a daily news brief in a crisp, witty, millennial tone "
    "(think quick cuts, natural contractions, one light, tasteful aside—no snark). "
    "Open with the strongest fact in one sentence. Keep sentences short (6–14 words). "
    "No headings, no lists, no links, no 'Sources'. End with one upbeat closer.\n\n"
    f"Items:\n{joined}"
    )

    return prompt, sources

def _clean_script(text: str) -> str:
    # drop any lines that start with common label words, just in case
    cleaned = re.sub(r'(?im)^\s*(title|summary|link)\s*:.*$', '', text)
    # also remove leading list bullets that sometimes slip in
    cleaned = re.sub(r'(?m)^\s*[-•]\s*', '', cleaned)
    # collapse extra blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def _invoke_titan_text(prompt: str) -> str:
    payload = {"inputText": prompt, "textGenerationConfig": {"maxTokenCount": 800, "temperature": 0.3, "topP": 0.9}}
    resp = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(payload))
    body = json.loads(resp["body"].read())
    results = body.get("results", [])
    if not results:
        raise RuntimeError(f"Bedrock returned no results: {body}")
    return results[0].get("outputText","").strip()

def _to_ssml(text: str) -> str:
    # Normalize and escape
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    safe = html.escape(t, quote=False)
    # Natural pauses (ok for neural)
    safe = safe.replace("\n\n", "<break time='350ms'/>")
    safe = safe.replace("\n", "<break time='180ms'/>")
    # Keep SSML minimal for neural voices: rate tweak only (no pitch)
    return f"<speak><prosody rate='105%'>{safe}</prosody></speak>"

def _synthesize_mp3(text: str) -> bytes:
    ssml = _to_ssml(text)
    print("SSML_PREVIEW:", ssml[:300])

    try:
        r = polly.synthesize_speech(
            Text=ssml,
            TextType="ssml",
            VoiceId=VOICE_ID,
            Engine="neural",
            OutputFormat="mp3"
        )
        return r["AudioStream"].read()
    except botocore.exceptions.ClientError as e:
        # Fallback 1: strip prosody, keep plain <speak>
        if e.response.get("Error", {}).get("Code") in ("InvalidSsmlException", "UnsupportedPlsAlphabet"):
            basic_ssml = f"<speak>{html.escape(text, quote=False)}</speak>"
            print("Retrying Polly with basic SSML…")
            r = polly.synthesize_speech(
                Text=basic_ssml,
                TextType="ssml",
                VoiceId=VOICE_ID,
                Engine="neural",
                OutputFormat="mp3"
            )
            return r["AudioStream"].read()
        raise

def _put_s3(key: str, data: bytes, content_type: str):
    s3.put_object(Bucket=BUCKET, Key=key, Body=data, ContentType=content_type)

def lambda_handler(event, context):
    started = datetime.now(timezone.utc).isoformat()
    if not RSS_URLS: raise RuntimeError("No RSS_URLS provided")
    items = _pull_articles(RSS_URLS, MAX_ARTICLES)
    if not items: raise RuntimeError("No articles pulled from feeds")
    print("DEBUG:", {"rss_count": len(RSS_URLS), "max_articles": MAX_ARTICLES, "voice": VOICE_ID})


    prompt, sources = _to_prompt(items)
    script = _invoke_titan_text(prompt)
    script = _clean_script(script)
    if not script: raise RuntimeError("No script generated")

    ts = int(time.time()); day = datetime.utcnow().strftime("%Y-%m-%d"); uid = uuid.uuid4().hex[:8]
    script_key = f"scripts/{day}/script-{ts}-{uid}.txt"
    audio_key  = f"audio/{day}/voice-{ts}-{uid}.mp3"
    meta_key   = f"runs/{day}/run-{ts}-{uid}.json"

    _put_s3(script_key, script.encode("utf-8"), "text/plain")
    audio_bytes = _synthesize_mp3(script)
    _put_s3(audio_key, audio_bytes, "audio/mpeg")

    meta = {
        "started": started, "model": MODEL_ID, "voice": VOICE_ID, "rss": RSS_URLS,
        "max_articles": MAX_ARTICLES, "script_key": script_key, "audio_key": audio_key, "sources": sources
    }
    _put_s3(meta_key, json.dumps(meta, indent=2).encode("utf-8"), "application/json")

    return {"statusCode": 200, "body": json.dumps({"message": "OK","script_key": script_key,"audio_key": audio_key,"meta_key": meta_key})}
