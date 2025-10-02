import os, json, time, uuid, boto3, feedparser
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
    parts, sources = [], []
    for i, it in enumerate(items, start=1):
        title = it.get("title",""); summary = it.get("summary",""); link = it.get("link","")
        parts.append(f"[{i}] Title: {title}\nSummary: {summary}\nLink: {link}")
        if link: sources.append(link)
    joined = "\n\n".join(parts)
    prompt = (
        "You are a concise news writer with a light, witty tone (Morning Brew/Ángel Martín vibe). "
    "Combine the following items into a 120–180 word script intended to be SPOKEN OUT LOUD. "
    "Lead with the most impactful fact, use short sentences, stay neutral, avoid hype. "
    "Do NOT include any 'Sources' line, links, or URLs in the script. "
    "End with a single upbeat closing line. "
    "\n\n" + joined
    )
    return prompt, sources

def _invoke_titan_text(prompt: str) -> str:
    payload = {"inputText": prompt, "textGenerationConfig": {"maxTokenCount": 800, "temperature": 0.3, "topP": 0.9}}
    resp = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(payload))
    body = json.loads(resp["body"].read())
    results = body.get("results", [])
    if not results:
        raise RuntimeError(f"Bedrock returned no results: {body}")
    return results[0].get("outputText","").strip()

# def _synthesize_mp3(text: str) -> bytes:
#     r = polly.synthesize_speech(Text=text, VoiceId=VOICE_ID, OutputFormat="mp3")
#     return r["AudioStream"].read()

def _synthesize_mp3(text: str) -> bytes:
    # Basic SSML: news domain + short pause between sentences
    ssml = f"""
    <speak>
      <amazon:domain name="news">
        {text}
      </amazon:domain>
    </speak>
    """
    r = polly.synthesize_speech(
        Text=ssml,
        TextType="ssml",
        VoiceId= Joanna,   # e.g., Matthew, Joanna, Lupe
        Engine="neural",    # more natural prosody
        OutputFormat="mp3"
    )
    return r["AudioStream"].read()


def _put_s3(key: str, data: bytes, content_type: str):
    s3.put_object(Bucket=BUCKET, Key=key, Body=data, ContentType=content_type)

def lambda_handler(event, context):
    started = datetime.now(timezone.utc).isoformat()
    if not RSS_URLS: raise RuntimeError("No RSS_URLS provided")
    items = _pull_articles(RSS_URLS, MAX_ARTICLES)
    if not items: raise RuntimeError("No articles pulled from feeds")

    prompt, sources = _to_prompt(items)
    script = _invoke_titan_text(prompt)

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
