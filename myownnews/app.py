import os, json, time, uuid, boto3, requests, re, html, botocore
from datetime import datetime, timezone

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "amazon.titan-text-lite-v1")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_CATEGORIES = [c.strip() for c in os.getenv("NEWS_CATEGORIES", "general,technology,business").split(",") if c.strip()]
VOICE_ID = os.getenv("VOICE_ID", "Matthew")
BUCKET = os.getenv("BUCKET")
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "3"))

s3 = boto3.client("s3")
polly = boto3.client("polly", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def _pull_articles(categories, limit):
    items = []
    for category in categories:
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": NEWS_API_KEY,
                "category": category,
                "country": "us",
                "pageSize": limit,
                "sortBy": "publishedAt"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                for article in data.get("articles", [])[:limit]:
                    if article.get("title") and article.get("description"):
                        items.append({
                            "title": article.get("title", ""),
                            "summary": article.get("description", ""),
                            "link": article.get("url", ""),
                            "published": article.get("publishedAt", ""),
                            "source": article.get("source", {}).get("name", ""),
                            "category": category
                        })
            else:
                print(f"News API error for category {category}: {data.get('message', 'Unknown error')}")
                
        except Exception as ex:
            print(f"News API error for category {category}: {ex}")
    
    # Sort by published date and return top articles
    items.sort(key=lambda x: x.get("published", ""), reverse=True)
    return items[:limit]

def _to_prompt(items):
    # collapse items to concise bullets (no labels, no URLs)
    parts = []
    sources = []
    for it in items:
        t = it.get("title", "").strip()
        s = it.get("summary", "").strip()
        source = it.get("source", "").strip()
        category = it.get("category", "").strip()
        
        if it.get("link"): sources.append(it["link"])
        
        # Add source attribution for credibility
        source_text = f" ({source})" if source else ""
        bullet = f"- {t}. {s}{source_text}".strip().rstrip(".") + "."
        parts.append(bullet)

    joined = "\n".join(parts)

    prompt = (
    "You are a concise news writer with a light, witty tone (inspired by these sources: Morning Brew/AM Podscast, una produccion de the Voice Village, Informativo de Ángel Martín vibe). "
    "Write a 130–160 word OUT-LOUD script for a daily news brief in a crisp, witty, millennial tone "
    "(think quick cuts, natural contractions, one light, tasteful aside—no snark). "
    "Open with the strongest fact in one sentence. Keep sentences short (6–14 words). "
    "Mix categories naturally (tech, business, general news). "
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
    print("=== BEDROCK DEBUG START ===")
    print(f"MODEL_ID: {MODEL_ID}")
    print(f"REGION: {REGION}")
    print(f"PROMPT_LENGTH: {len(prompt)} characters")
    print("PROMPT_PREVIEW (first 500 chars):")
    print(prompt[:500])
    print("PROMPT_PREVIEW (last 200 chars):")
    print(prompt[-200:])
    
    payload = {
        "inputText": prompt, 
        "textGenerationConfig": {
            "maxTokenCount": 800, 
            "temperature": 0.3, 
            "topP": 0.9
        }
    }
    
    print(f"BEDROCK_PAYLOAD: {json.dumps(payload, indent=2)}")
    
    try:
        print("Calling Bedrock invoke_model...")
        resp = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(payload))
        print(f"BEDROCK_RESPONSE_STATUS: {resp.get('ResponseMetadata', {}).get('HTTPStatusCode', 'Unknown')}")
        
        body_bytes = resp["body"].read()
        print(f"RESPONSE_BODY_SIZE: {len(body_bytes)} bytes")
        
        body = json.loads(body_bytes)
        print(f"BEDROCK_FULL_RESPONSE: {json.dumps(body, indent=2)}")
        
        results = body.get("results", [])
        print(f"RESULTS_COUNT: {len(results)}")
        
        if not results:
            print("ERROR: No results in Bedrock response")
            raise RuntimeError(f"Bedrock returned no results: {body}")
        
        output_text = results[0].get("outputText", "").strip()
        print(f"OUTPUT_TEXT_LENGTH: {len(output_text)} characters")
        print("OUTPUT_TEXT_PREVIEW (first 300 chars):")
        print(output_text[:300])
        
        print("=== BEDROCK DEBUG END ===")
        return output_text
        
    except botocore.exceptions.ClientError as e:
        print(f"BEDROCK_CLIENT_ERROR: {e}")
        print(f"ERROR_CODE: {e.response.get('Error', {}).get('Code', 'Unknown')}")
        print(f"ERROR_MESSAGE: {e.response.get('Error', {}).get('Message', 'Unknown')}")
        raise
    except Exception as e:
        print(f"BEDROCK_GENERAL_ERROR: {e}")
        print(f"ERROR_TYPE: {type(e).__name__}")
        raise

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
    if not NEWS_API_KEY: raise RuntimeError("No NEWS_API_KEY provided")
    if not NEWS_CATEGORIES: raise RuntimeError("No NEWS_CATEGORIES provided")
    
    print("=== NEWS API DEBUG ===")
    print(f"NEWS_API_KEY_SET: {bool(NEWS_API_KEY)}")
    print(f"NEWS_CATEGORIES: {NEWS_CATEGORIES}")
    print(f"MAX_ARTICLES: {MAX_ARTICLES}")
    
    items = _pull_articles(NEWS_CATEGORIES, MAX_ARTICLES)
    if not items: raise RuntimeError("No articles pulled from News API")
    
    print(f"ARTICLES_FOUND: {len(items)}")
    for i, item in enumerate(items):
        print(f"ARTICLE_{i+1}: {item.get('title', 'No title')[:100]}...")
    
    print("DEBUG:", {"categories": NEWS_CATEGORIES, "max_articles": MAX_ARTICLES, "voice": VOICE_ID, "articles_found": len(items)})


    print("=== SCRIPT GENERATION DEBUG ===")
    prompt, sources = _to_prompt(items)
    print(f"GENERATED_PROMPT_LENGTH: {len(prompt)}")
    print(f"SOURCES_COUNT: {len(sources)}")
    
    print("Calling Bedrock to generate script...")
    script = _invoke_titan_text(prompt)
    
    print(f"RAW_SCRIPT_LENGTH: {len(script)}")
    print("RAW_SCRIPT_CONTENT:")
    print(script)
    
    print("Cleaning script...")
    script = _clean_script(script)
    
    print(f"CLEANED_SCRIPT_LENGTH: {len(script)}")
    print("CLEANED_SCRIPT_CONTENT:")
    print(script)
    
    if not script: 
        print("ERROR: Script is empty after cleaning")
        raise RuntimeError("No script generated")
    
    print("=== SCRIPT GENERATION SUCCESS ===")

    ts = int(time.time()); day = datetime.utcnow().strftime("%Y-%m-%d"); uid = uuid.uuid4().hex[:8]
    script_key = f"scripts/{day}/script-{ts}-{uid}.txt"
    audio_key  = f"audio/{day}/voice-{ts}-{uid}.mp3"
    meta_key   = f"runs/{day}/run-{ts}-{uid}.json"

    _put_s3(script_key, script.encode("utf-8"), "text/plain")
    audio_bytes = _synthesize_mp3(script)
    _put_s3(audio_key, audio_bytes, "audio/mpeg")

    meta = {
        "started": started, "model": MODEL_ID, "voice": VOICE_ID, "categories": NEWS_CATEGORIES,
        "max_articles": MAX_ARTICLES, "script_key": script_key, "audio_key": audio_key, "sources": sources
    }
    _put_s3(meta_key, json.dumps(meta, indent=2).encode("utf-8"), "application/json")

    return {"statusCode": 200, "body": json.dumps({"message": "OK","script_key": script_key,"audio_key": audio_key,"meta_key": meta_key})}
