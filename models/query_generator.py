from typing import List, Dict, Tuple
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from config.settings import settings
from config.prompts import ResponseTemplates

class QueryGenerator:
    def __init__(self):
        try:
            self.keybert = KeyBERT(model=settings.SENTENCE_TRANSFORMER_MODEL)
        except Exception as e:
            print(f"KeyBERT initialization failed: {e}")
            self.keybert = None
        
        self.tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def extract_keywords_keybert(self, text: str, num_keywords: int = 5) -> List[Tuple[str, float]]:
        """Extract keywords using KeyBERT"""
        if not self.keybert:
            return []
        
        try:
            keywords = self.keybert.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                nr_candidates=num_keywords,
                use_mmr=True,
                diversity=0.5
            )
            return keywords
        except Exception as e:
            print(f"KeyBERT extraction failed: {e}")
            return []
    
    def extract_keywords_tfidf(self, text: str, num_keywords: int = 5) -> List[str]:
        """Extract keywords using TF-IDF"""
        try:
            # Fit and transform
            tfidf_matrix = self.tfidf.fit_transform([text])
            feature_names = self.tfidf.get_feature_names_out()
            
            # Get scores
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            top_indices = scores.argsort()[-num_keywords:][::-1]
            keywords = [feature_names[i] for i in top_indices if scores[i] > 0]
            
            return keywords
        except Exception as e:
            print(f"TF-IDF extraction failed: {e}")
            return []
    
    def generate_general_query(self, text: str) -> str:
        """Generate search query for general questions"""
        # Extract entities and keywords
        keywords = self.extract_keywords_keybert(text)
        
        # If KeyBERT fails, use simple word extraction
        if not keywords:
            # Remove common words and keep important terms
            words = text.lower().split()
            important_words = [w for w in words if len(w) > 3 and w not in ['what', 'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how']]
            if important_words:
                return ' '.join(important_words)
            return text
        
        # Use the top keywords for the query
        query_terms = [k[0] for k in keywords[:3]]
        return ' '.join(query_terms)
    
    def generate_fact_check_query(self, text: str) -> str:
        """Generate search query for fact-checking"""
        # Remove question words and common phrases
        text = re.sub(r'^(is|are|was|were|does|do|did|can|could|will|would|should|has|have|had)\s+', '', text.lower())
        text = re.sub(r'\?$', '', text)
        
        # Extract keywords
        keywords = self.extract_keywords_keybert(text)
        if not keywords:
            return text
        
        # Combine keywords with fact-checking terms
        query_terms = [k[0] for k in keywords[:3]]
        return ' '.join(query_terms)
    
    def generate_news_query(self, text: str) -> str:
        """Generate search query for news information"""
        # Extract keywords
        keywords = self.extract_keywords_keybert(text)
        if not keywords:
            return text
        
        # Add news-related terms
        query_terms = [k[0] for k in keywords[:3]]
        return ' '.join(query_terms) + ' latest news'
    
    def generate_search_query(self, text: str, intent: str, entities: List[Tuple[str, str]]) -> Dict[str, any]:
        """Generate optimized search query based on intent and entities"""
        
        # Extract keywords using multiple methods
        keybert_keywords = self.extract_keywords_keybert(text)
        tfidf_keywords = self.extract_keywords_tfidf(text)
        
        # Combine and prioritize keywords
        all_keywords = []
        
        # Add KeyBERT keywords with scores
        for keyword, score in keybert_keywords:
            all_keywords.append({
                'term': keyword,
                'score': score,
                'source': 'keybert'
            })
        
        # Add TF-IDF keywords
        for keyword in tfidf_keywords:
            all_keywords.append({
                'term': keyword,
                'score': 0.5,  # Default score for TF-IDF
                'source': 'tfidf'
            })
        
        # Add entity keywords
        for entity_text, entity_type in entities:
            # Give higher scores to certain entity types
            entity_score = 0.8 if entity_type in ['PERSON', 'ORG', 'GPE'] else 0.6
            all_keywords.append({
                'term': entity_text.lower(),
                'score': entity_score,
                'source': 'entity'
            })
        
        # Remove duplicates and sort by score
        unique_keywords = {}
        for kw in all_keywords:
            term = kw['term']
            if term not in unique_keywords or kw['score'] > unique_keywords[term]['score']:
                unique_keywords[term] = kw
        
        sorted_keywords = sorted(unique_keywords.values(), key=lambda x: x['score'], reverse=True)
        
        # Generate query based on intent
        if intent == "fact_check":
            query = self.generate_fact_check_query(text)
        elif intent == "news_info":
            query = self.generate_news_query(text)
        else:
            query = self.generate_general_query(text)
        
        return {
            'query': query,
            'keywords': [kw['term'] for kw in sorted_keywords[:10]],
            'keyword_details': sorted_keywords[:10],
            'intent': intent
        }
    
    