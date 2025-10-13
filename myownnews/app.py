import os, json, time, uuid, boto3, requests, re, html, botocore
from datetime import datetime, timezone

REGION = os.getenv("AWS_REGION", "us-west-2")
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
    
    # First, get some international headlines for global perspective
    try:
        url = "https://newsapi.org/v2/top-headlines"
        international_params = {
            "apiKey": NEWS_API_KEY,
            "pageSize": limit,
            "sortBy": "popularity",
            "language": "en",
            "sources": "bbc-news,reuters,al-jazeera-english,the-guardian-uk"  # Global sources
        }
        
        response = requests.get(url, params=international_params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "ok":
            for article in data.get("articles", [])[:2]:  # Just 2 international stories
                title = article.get("title", "")
                description = article.get("description", "")
                source = article.get("source", {}).get("name", "")
                
                if (title and description and len(description) > 50 and
                    not title.lower().startswith("[removed]") and
                    source not in ["Google News", "[Removed]"]):
                    
                    items.append({
                        "title": title,
                        "summary": description,
                        "link": article.get("url", ""),
                        "published": article.get("publishedAt", ""),
                        "source": source,
                        "category": "international"
                    })
    except Exception as ex:
        print(f"International news error: {ex}")
    
    # Then get US news by category
    for category in categories:
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": NEWS_API_KEY,
                "category": category,
                "country": "us",
                "pageSize": limit * 2,
                "sortBy": "popularity"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                for article in data.get("articles", []):
                    title = article.get("title", "")
                    description = article.get("description", "")
                    source = article.get("source", {}).get("name", "")
                    
                    # Filter out low-quality articles
                    if (title and description and 
                        len(description) > 50 and  # Substantial description
                        not title.lower().startswith("[removed]") and
                        source not in ["Google News", "[Removed]"] and
                        "..." not in title[-10:]):  # Avoid truncated titles
                        
                        items.append({
                            "title": title,
                            "summary": description,
                            "link": article.get("url", ""),
                            "published": article.get("publishedAt", ""),
                            "source": source,
                            "category": category
                        })
                        
                        if len(items) >= limit * len(categories):  # Stop when we have enough
                            break
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
    "You're hosting a daily international news podcast inspired by AM Podcast style. Write a 160-word conversational script "
    "covering today's 2 biggest global stories. Sound like that witty friend who makes world news actually interesting.\n\n"
    
    "AM Podcast Structure:\n"
    "- Open with energy: 'Alright, let's dive into what's happening around the world today...'\n"
    "- Story 1: 'So, first up...' [explain + why it matters globally]\n"
    "- Smooth transition: 'And speaking of [theme]...' or 'Meanwhile, in [location]...'\n"
    "- Story 2: Brief setup + context + impact\n"
    "- Close with: 'And that's what's moving the world today. Stay curious!'\n\n"
    
    "Tone (AM Podcast meets Ángel Martín):\n"
    "- Conversational but smart - explain complex stuff simply\n"
    "- Add personality: 'honestly', 'wild', 'get this', 'plot twist'\n"
    "- Make global news feel relevant and engaging\n"
    "- Never boring, always human\n\n"
    
    f"Today's international stories:\n{joined}\n\n"
    "Your AM-style podcast script:"
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

def _invoke_bedrock_text(prompt: str) -> str:
    print("=== BEDROCK DEBUG START ===")
    print(f"MODEL_ID: {MODEL_ID}")
    print(f"REGION: {REGION}")
    print(f"PROMPT_LENGTH: {len(prompt)} characters")
    print("PROMPT_PREVIEW (first 500 chars):")
    print(prompt[:500])
    print("PROMPT_PREVIEW (last 200 chars):")
    print(prompt[-200:])
    
    # Check if using Claude or Titan
    if "claude" in MODEL_ID.lower():
        # Claude format
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    else:
        # Titan format
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
        
        # Parse response based on model type
        if "claude" in MODEL_ID.lower():
            # Claude response format
            content = body.get("content", [])
            if not content:
                raise RuntimeError(f"Claude returned no content: {body}")
            output_text = content[0].get("text", "").strip()
        else:
            # Titan response format
            results = body.get("results", [])
            if not results:
                raise RuntimeError(f"Titan returned no results: {body}")
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
    
    # Add natural conversational pauses
    safe = safe.replace("...", "<break time='500ms'/>")  # Dramatic pauses
    safe = safe.replace(", ", ", <break time='200ms'/>")  # Comma pauses
    safe = safe.replace(". ", ". <break time='400ms'/>")  # Sentence breaks
    safe = safe.replace("? ", "? <break time='350ms'/>")  # Question pauses
    safe = safe.replace("! ", "! <break time='300ms'/>")  # Exclamation pauses
    
    # Paragraph breaks for topic transitions
    safe = safe.replace("\n\n", "<break time='600ms'/>")
    safe = safe.replace("\n", "<break time='250ms'/>")
    
    # Slightly slower, more conversational pace for neural voices
    return f"<speak><prosody rate='95%'>{safe}</prosody></speak>"

def _synthesize_mp3(text: str) -> bytes:
    # Polly has a 3000 character limit for SSML
    if len(text) > 1800:  # Leave room for SSML tags and be more conservative
        print(f"WARNING: Text too long ({len(text)} chars), truncating...")
        text = text[:1800] + "... and that's your news update!"
    
    ssml = _to_ssml(text)
    print("SSML_PREVIEW:", ssml[:300])
    print(f"SSML_LENGTH: {len(ssml)} characters")

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
    script = _invoke_bedrock_text(prompt)
    
    print(f"RAW_SCRIPT_LENGTH: {len(script)}")
    print("RAW_SCRIPT_CONTENT:")
    print(script)
    
    print("Cleaning script...")
    script = _clean_script(script)
    
    print(f"CLEANED_SCRIPT_LENGTH: {len(script)}")
    print("CLEANED_SCRIPT_CONTENT:")
    print(script)
    
    # Aggressive length check - Polly limit is ~3000 chars for SSML
    if len(script) > 1200:  # Very conservative limit
        print(f"WARNING: Script too long ({len(script)} chars), truncating to 1200...")
        # Find a good place to cut (end of sentence)
        truncated = script[:1200]
        last_period = truncated.rfind('.')
        if last_period > 800:  # Make sure we don't cut too short
            script = truncated[:last_period + 1] + " That's your news update!"
        else:
            script = truncated + "... That's your news update!"
        print(f"TRUNCATED_SCRIPT_LENGTH: {len(script)}")
    
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
