import asyncio
import json
import re
from server.config import settings
from server.database import get_unsummarized_articles, insert_summary


async def summarize_articles():
    """
    Summarize all unsummarized articles using Gemini 2.5 Flash.
    Processes in batches with delays to respect rate limits.
    Falls back to smart extractive summarization if Gemini fails.
    """
    articles = await get_unsummarized_articles()
    if not articles:
        print("[Summarizer] No articles to summarize")
        return 0

    print(f"[Summarizer] Processing {len(articles)} unsummarized articles...")
    processed = 0

    # Process in batches
    batch_size = settings.summarizer_batch_size
    for i in range(0, len(articles), batch_size):
        batch = articles[i : i + batch_size]

        for article in batch:
            try:
                summary, sentiment = await _summarize_single(article)
                await insert_summary(article["id"], summary, sentiment)
                processed += 1
            except Exception as e:
                print(f"[Summarizer] Error on article {article['id']}: {e}")
                # Use fallback
                summary = _extractive_fallback(article)
                await insert_summary(article["id"], summary, "neutral")
                processed += 1

        # Delay between batches to respect rate limits
        if i + batch_size < len(articles):
            await asyncio.sleep(settings.summarizer_batch_delay_seconds)

    print(f"[Summarizer] Processed {processed}/{len(articles)} articles")
    return processed


async def _summarize_single(article: dict) -> tuple[str, str]:
    """
    Summarize a single article using Gemini.
    Returns (summary_text, sentiment).
    Falls back to extractive if Gemini is unavailable.
    """
    if not settings.gemini_api_key:
        return _extractive_fallback(article), "neutral"

    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)

        content = article.get("content") or article.get("description") or article["title"]
        # Truncate very long content to save tokens
        if len(content) > 3000:
            content = content[:3000]

        prompt = f"""You are a news summarizer. For the following article, provide:
1. A 2-sentence summary capturing the key facts
2. Sentiment: one of [positive, neutral, negative]

Respond ONLY in valid JSON format: {{"summary": "...", "sentiment": "..."}}

Title: {article['title']}
Content: {content}"""

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )

        # Parse JSON from response
        response_text = response.text.strip()
        # Handle markdown code blocks in response
        if response_text.startswith("```"):
            response_text = re.sub(r"```(?:json)?\n?", "", response_text).strip()

        parsed = json.loads(response_text)
        summary = parsed.get("summary", "").strip()
        sentiment = parsed.get("sentiment", "neutral").lower().strip()

        # Validate sentiment
        if sentiment not in ("positive", "neutral", "negative"):
            sentiment = "neutral"

        if not summary:
            return _extractive_fallback(article), sentiment

        return summary, sentiment

    except json.JSONDecodeError:
        print(f"[Summarizer] Failed to parse Gemini JSON for article {article['id']}, using fallback")
        return _extractive_fallback(article), "neutral"

    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "resource exhausted" in error_str:
            print(f"[Summarizer] Rate limited, using fallback for article {article['id']}")
        else:
            print(f"[Summarizer] Gemini error for article {article['id']}: {e}")
        return _extractive_fallback(article), "neutral"


def _extractive_fallback(article: dict) -> str:
    """
    Smart extractive fallback when Gemini is unavailable.
    
    Strategy:
    - Try sentences 2-4 (avoids Guardian-style teaser/hook opening lines)
    - If article is short (< 4 sentences), use sentence 1 + last sentence of first paragraph
    - If very short, return whatever we have
    """
    content = article.get("content") or article.get("description") or article.get("title", "")

    # Split into sentences (handles ., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    # Filter out very short fragments
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        # Last resort: use title + truncated description
        desc = article.get("description", "")
        return f"{article.get('title', 'No summary available.')} {desc[:100]}".strip()

    if len(sentences) >= 4:
        # Take sentences 2-3 (index 1-2) — skips the hook/teaser opening
        return " ".join(sentences[1:3])
    elif len(sentences) >= 2:
        # Short article: first sentence + last sentence
        return f"{sentences[0]} {sentences[-1]}"
    else:
        return sentences[0]
