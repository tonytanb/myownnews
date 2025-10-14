import os, json, time, uuid, boto3, requests, re, html, botocore
from datetime import datetime, timezone

REGION = os.getenv("AWS_REGION", "us-west-2")
MODEL_ID = os.getenv("MODEL_ID", "amazon.titan-text-lite-v1")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_CATEGORIES = [c.strip() for c in os.getenv("NEWS_CATEGORIES", "general,technology,business").split(",") if c.strip()]
VOICE_ID = os.getenv("VOICE_ID", "Joanna")
VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "polly")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
BUCKET = os.getenv("BUCKET")
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "8"))

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
            "pageSize": 15,  # Get more international stories
            "sortBy": "popularity",
            "language": "en",
            "sources": "bbc-news,reuters,the-guardian-uk,cnn,associated-press,new-scientist,national-geographic"  # Added science sources
        }
        
        response = requests.get(url, params=international_params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "ok":
            for article in data.get("articles", [])[:4]:  # Get 4 international stories
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
    
    # Get some science/health stories for "team favorites"
    try:
        science_params = {
            "apiKey": NEWS_API_KEY,
            "category": "science",
            "pageSize": 10,
            "sortBy": "popularity",
            "language": "en"
        }
        
        response = requests.get(url, params=science_params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "ok":
            for article in data.get("articles", [])[:3]:  # Get 3 science stories
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
                        "category": "science-favorite"
                    })
    except Exception as ex:
        print(f"Science news error: {ex}")
    
    # Then get US news by category
    for category in categories:
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": NEWS_API_KEY,
                "category": category,
                "country": "us", 
                "pageSize": 20,  # Get more articles to choose from
                "sortBy": "popularity"  # Get viral/trending stories
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
        
        # Clean format without source attribution
        bullet = f"- {t}. {s}".strip().rstrip(".") + "."
        parts.append(bullet)

    joined = "\n".join(parts)

    prompt = (
    "You're hosting a 5-minute daily news podcast for millennials (20s-30s). Write a COMPLETE script "
    "covering exactly 5 different stories. Each story should be 2-3 sentences. Total length: 500-600 words.\n\n"
    
    "CRITICAL RULES:\n"
    "- Use ONLY specific details from the stories below\n"
    "- NO source attributions (don't say 'CNN reports' or 'according to BBC')\n"
    "- NO placeholders like '[brief summary]' or '[explain]'\n"
    "- If a story lacks details, skip it\n\n"
    
    "MILLENNIAL TONE:\n"
    "- Smart but fun - like explaining news to your college friends\n"
    "- Use: 'honestly', 'wild', 'get this', 'plot twist', 'lowkey', 'ngl' (not gonna lie)\n"
    "- Casual contractions: 'we're', 'it's', 'can't', 'won't'\n"
    "- Light humor when appropriate, but stay respectful\n"
    "- Make complex stuff relatable\n\n"
    
    "STRUCTURE (MUST include all 5 stories):\n"
    "1. Open: 'Alright, let's dive into what's happening around the world today...'\n"
    "2. Story 1: Biggest news (2-3 sentences with details)\n"
    "3. Story 2: International/political (2-3 sentences)\n"
    "4. Story 3: Business/tech news (2-3 sentences)\n"
    "5. Story 4: General interest (2-3 sentences)\n"
    "6. Story 5: 'Team Favorite' - Something positive/science/discovery\n"
    "   - Introduce as: 'And for our team favorite today...' or 'Before we wrap up, here's something cool...'\n"
    "   - Make it educational and uplifting (2-3 sentences)\n"
    "7. Close: 'And that's what's moving the world today. Stay curious!'\n\n"
    
    f"Today's stories (use specific details only, no source names):\n{joined}\n\n"
    "Write the complete millennial-friendly podcast script covering ALL 5 stories above. "
    "Do not stop early. Include opening, all 5 stories with details, and closing:"
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

def _generate_word_timings(text: str) -> list:
    """Generate estimated word timings based on average speech rate"""
    import re
    
    # Clean text and split into words
    clean_text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    words = [w for w in clean_text.split() if w.strip()]
    
    # Average speech rate: ~150 words per minute = 2.5 words per second
    # So each word takes about 0.4 seconds on average
    words_per_second = 2.2  # Slightly slower for news reading
    
    word_timings = []
    current_time = 0.0
    
    for word in words:
        # Estimate duration based on word length
        # Longer words take more time
        base_duration = 1.0 / words_per_second
        length_factor = max(0.7, min(1.5, len(word) / 6.0))  # Scale by word length
        duration = base_duration * length_factor
        
        word_timings.append({
            'word': word,
            'start': round(current_time, 2),
            'end': round(current_time + duration, 2)
        })
        
        current_time += duration
        
        # Add small pauses for punctuation in original text
        if any(punct in text[text.find(word):text.find(word) + len(word) + 5] 
               for punct in ['.', '!', '?']):
            current_time += 0.3  # Sentence pause
        elif ',' in text[text.find(word):text.find(word) + len(word) + 3]:
            current_time += 0.15  # Comma pause
    
    print(f"Generated {len(word_timings)} estimated word timings")
    return word_timings

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

def _synthesize_mp3(text: str) -> tuple[bytes, list]:
    print(f"Using voice provider: {VOICE_PROVIDER}")
    
    if VOICE_PROVIDER == "elevenlabs" and ELEVENLABS_API_KEY:
        return _synthesize_elevenlabs(text)
    else:
        return _synthesize_polly(text)

def _synthesize_elevenlabs(text: str) -> tuple[bytes, list]:
    """Synthesize speech using ElevenLabs API and generate word timings"""
    print("Using ElevenLabs for speech synthesis...")
    
    # ElevenLabs can handle longer text
    if len(text) > 5000:
        print(f"WARNING: Text too long ({len(text)} chars), truncating...")
        text = text[:5000] + "... and that's your news update!"
    
    try:
        import requests
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        
        print(f"ElevenLabs response size: {len(response.content)} bytes")
        audio_bytes = response.content
        
        # Generate estimated word timings
        word_timings = _generate_word_timings(text)
        
        return audio_bytes, word_timings
        
    except Exception as e:
        print(f"ElevenLabs failed: {e}, falling back to Polly...")
        return _synthesize_polly(text)

def _synthesize_polly(text: str) -> tuple[bytes, list]:
    """Synthesize speech using Amazon Polly and get word timings"""
    print("Using Amazon Polly for speech synthesis...")
    
    # Polly has a 3000 character limit for SSML
    if len(text) > 1800:  # Leave room for SSML tags and be more conservative
        print(f"WARNING: Text too long ({len(text)} chars), truncating...")
        text = text[:1800] + "... and that's your news update!"
    
    ssml = _to_ssml(text)
    print("SSML_PREVIEW:", ssml[:300])
    print(f"SSML_LENGTH: {len(ssml)} characters")

    try:
        # First, get word timings using speech marks
        print("Getting word timings from Polly...")
        marks_response = polly.synthesize_speech(
            Text=ssml,
            TextType="ssml",
            VoiceId=VOICE_ID,
            Engine="neural",
            OutputFormat="json",
            SpeechMarkTypes=["word"]
        )
        
        # Parse word timings
        word_timings = []
        marks_data = marks_response["AudioStream"].read().decode('utf-8')
        for line in marks_data.strip().split('\n'):
            if line.strip():
                mark = json.loads(line)
                if mark.get('type') == 'word':
                    word_timings.append({
                        'word': mark.get('value', ''),
                        'start': mark.get('time', 0) / 1000.0,  # Convert ms to seconds
                        'end': (mark.get('time', 0) + 500) / 1000.0  # Estimate end time
                    })
        
        print(f"Got {len(word_timings)} word timings")
        
        # Then get the actual audio
        print("Getting audio from Polly...")
        audio_response = polly.synthesize_speech(
            Text=ssml,
            TextType="ssml",
            VoiceId=VOICE_ID,
            Engine="neural",
            OutputFormat="mp3"
        )
        
        return audio_response["AudioStream"].read(), word_timings
        
    except botocore.exceptions.ClientError as e:
        # Fallback 1: strip prosody, keep plain <speak>
        if e.response.get("Error", {}).get("Code") in ("InvalidSsmlException", "UnsupportedPlsAlphabet"):
            basic_ssml = f"<speak>{html.escape(text, quote=False)}</speak>"
            print("Retrying Polly with basic SSML…")
            
            # Get timings with basic SSML
            marks_response = polly.synthesize_speech(
                Text=basic_ssml,
                TextType="ssml",
                VoiceId=VOICE_ID,
                Engine="neural",
                OutputFormat="json",
                SpeechMarkTypes=["word"]
            )
            
            word_timings = []
            marks_data = marks_response["AudioStream"].read().decode('utf-8')
            for line in marks_data.strip().split('\n'):
                if line.strip():
                    mark = json.loads(line)
                    if mark.get('type') == 'word':
                        word_timings.append({
                            'word': mark.get('value', ''),
                            'start': mark.get('time', 0) / 1000.0,
                            'end': (mark.get('time', 0) + 500) / 1000.0
                        })
            
            # Get audio with basic SSML
            audio_response = polly.synthesize_speech(
                Text=basic_ssml,
                TextType="ssml",
                VoiceId=VOICE_ID,
                Engine="neural",
                OutputFormat="mp3"
            )
            
            return audio_response["AudioStream"].read(), word_timings
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
    audio_bytes, word_timings = _synthesize_mp3(script)
    _put_s3(audio_key, audio_bytes, "audio/mpeg")

    meta = {
        "started": started, "model": MODEL_ID, "voice": VOICE_ID, "categories": NEWS_CATEGORIES,
        "max_articles": MAX_ARTICLES, "script_key": script_key, "audio_key": audio_key, "sources": sources
    }
    _put_s3(meta_key, json.dumps(meta, indent=2).encode("utf-8"), "application/json")

    # Generate public S3 URL
    audio_url = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{audio_key}"
    
    # Format news for frontend
    news_items = []
    for item in items[:3]:
        news_items.append({
            "title": item.get("title", ""),
            "category": item.get("category", "").upper().replace("-", " "),
            "summary": item.get("summary", ""),
            "full_text": item.get("summary", "")
        })
    
    # Return format for frontend with CORS
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({
            "script": script,
            "audio_url": audio_url,
            "word_timings": word_timings,
            "news_items": news_items,
            "generated_at": started
        })
    } 
