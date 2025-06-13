import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="config.env")

class Settings:
    # API Configuration
    SERP_API_KEY = os.getenv("SERP_API_KEY")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    
    # Model Configuration
    INTENT_MODEL = "distilbert-base-uncased"
    ENTITY_MODEL = "en_core_web_sm"
    SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
    SENTENCE_TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Search Configuration
    MAX_SEARCH_RESULTS = 5
    CONFIDENCE_THRESHOLD = 0.6
    CACHE_EXPIRY = 3600  # 1 hour
    
    # Response Configuration
    MAX_SUMMARY_LENGTH = 200
    MIN_SUMMARY_LENGTH = 50
    
    # Source Credibility Scores
    SOURCE_CREDIBILITY = {
        "reuters.com": 0.95,
        "ap.org": 0.95,
        "bbc.com": 0.90,
        "cnn.com": 0.85,
        "theguardian.com": 0.85,
        "npr.org": 0.90,
        "nytimes.com": 0.85,
        "washingtonpost.com": 0.85,
        "politico.com": 0.80,
        "factcheck.org": 0.95,
        "snopes.com": 0.90,
        "nobelprize.org": 0.98,
        "who.int": 0.95,
        "gov": 0.90,  # Any .gov domain
        "edu": 0.85,  # Any .edu domain
    }
    
    # Intent Classes
    INTENT_CLASSES = [
        "news_info",
        "fact_check", 
        "general_query",
        "clarification"
    ]
    
    # Fact Check Verdicts
    FACT_CHECK_VERDICTS = [
        "TRUE",
        "FALSE", 
        "PARTIALLY_TRUE",
        "MISLEADING",
        "UNVERIFIED"
    ]

settings = Settings()

print("SERP_API_KEY loaded:", settings.SERP_API_KEY)
