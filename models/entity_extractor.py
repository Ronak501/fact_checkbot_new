import spacy
from typing import List, Dict, Tuple
import re
from datetime import datetime
from config.settings import settings

class EntityExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load(settings.ENTITY_MODEL)
        except IOError:
            print("spaCy model not found. Please install: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return self.extract_entities_fallback(text)
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            # Filter out very short entities and numbers
            if len(ent.text) > 1 and not ent.text.isdigit():
                entities.append((ent.text, ent.label_))
        
        return entities
    
    def extract_entities_fallback(self, text: str) -> List[Tuple[str, str]]:
        """Fallback method for entity extraction when spaCy is not available"""
        entities = []
        
        # Common entity patterns
        patterns = {
            'PERSON': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names
            'GPE': r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b',  # Places
            'ORG': r'\b[A-Z][A-Za-z]+\b',  # Organizations
            'DATE': r'\b\d{1,2}(?:st|nd|rd|th)? [A-Z][a-z]+ \d{4}\b',  # Dates
            'TIME': r'\b\d{1,2}:\d{2}(?: [AP]M)?\b'  # Times
        }
        
        # Extract entities using patterns
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entity_text = match.group()
                # Filter out very short entities and numbers
                if len(entity_text) > 1 and not entity_text.isdigit():
                    entities.append((entity_text, entity_type))
        
        return entities
    
    def extract_temporal_entities(self, text: str) -> List[Dict[str, any]]:
        """Extract time-related entities and expressions"""
        temporal_expressions = []
        
        # Relative time expressions
        relative_patterns = {
            r'\btoday\b': 'TODAY',
            r'\byesterday\b': 'YESTERDAY', 
            r'\btomorrow\b': 'TOMORROW',
            r'\bthis week\b': 'THIS_WEEK',
            r'\blast week\b': 'LAST_WEEK',
            r'\bnext week\b': 'NEXT_WEEK',
            r'\bthis month\b': 'THIS_MONTH',
            r'\blast month\b': 'LAST_MONTH',
            r'\bthis year\b': 'THIS_YEAR',
            r'\blast year\b': 'LAST_YEAR',
            r'\brecently\b': 'RECENT',
            r'\blatest\b': 'LATEST',
            r'\bcurrent\b': 'CURRENT'
        }
        
        for pattern, label in relative_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                temporal_expressions.append({
                    'text': match.group(),
                    'label': label,
                    'start': match.start(),
                    'end': match.end()
                })
        
        return temporal_expressions
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        if not self.nlp:
            return self.extract_keywords_fallback(text)
        
        doc = self.nlp(text)
        keywords = []
        
        # Extract important tokens (nouns, proper nouns, adjectives)
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        return unique_keywords
    
    def extract_keywords_fallback(self, text: str) -> List[str]:
        """Fallback keyword extraction"""
        import string
        
        # Remove punctuation and convert to lowercase
        text_clean = text.translate(str.maketrans('', '', string.punctuation)).lower()
        words = text_clean.split()
        
        # Simple stopwords list
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        # Remove duplicates
        return list(dict.fromkeys(keywords))
    
    def get_entity_summary(self, text: str) -> Dict[str, any]:
        """Get comprehensive entity analysis"""
        entities = self.extract_entities(text)
        temporal_entities = self.extract_temporal_entities(text)
        keywords = self.extract_keywords(text)
        
        # Group entities by type
        entity_groups = {}
        for entity_text, entity_type in entities:
            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity_text)
        
        return {
            'entities': entities,
            'entity_groups': entity_groups,
            'temporal_entities': temporal_entities,
            'keywords': keywords[:10],  # Top 10 keywords
            'entity_count': len(entities),
            'has_temporal_reference': len(temporal_entities) > 0
        }