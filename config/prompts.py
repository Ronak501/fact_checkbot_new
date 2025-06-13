class ResponseTemplates:
    
    FACT_CHECK_TEMPLATE = """
🔍 FACT CHECK: {claim}

✅ VERDICT: {verdict}

📊 EVIDENCE:
{evidence}

🏛️ SOURCES:
{sources}

⏰ Last Updated: {timestamp}
"""

    NEWS_SUMMARY_TEMPLATE = """
📰 Latest Updates: {topic}

{summary}

📅 Information as of: {timestamp}
🔗 Sources: {source_count} reliable sources
"""

    VERIFICATION_TEMPLATE = """
🔎 VERIFICATION RESULT

Statement: "{statement}"
Status: {status}
Confidence: {confidence}%

{explanation}

Sources consulted: {sources}
"""

    ERROR_TEMPLATE = """
❌ Unable to verify this information at the moment.

Reason: {reason}

💡 Suggestion: Try rephrasing your question or check back later.
"""

    QUERY_GENERATION_PROMPTS = {
        "news_info": "Generate search keywords for latest news about: {query}",
        "fact_check": "Generate search terms to verify the claim: {query}",
        "general_query": "Extract key search terms from: {query}"
    }
    
    SUMMARIZATION_PROMPTS = {
        "news": "Summarize the latest news about {topic} from the following sources:",
        "fact_check": "Based on the following evidence, determine if this claim is true:",
        "general": "Provide a comprehensive answer based on the following information:"
    }