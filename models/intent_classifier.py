import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from typing import Dict, List, Tuple
import re
from config.settings import settings

class IntentClassifier:
    def __init__(self):
        self.model_name = settings.INTENT_MODEL
        self.intent_classes = settings.INTENT_CLASSES
        
        # Load pre-trained model (you would fine-tune this on your data)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.classifier = pipeline("text-classification", 
                                     model=self.model, 
                                     tokenizer=self.tokenizer)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.classifier = None
    
    def classify_intent(self, text: str) -> str:
        """
        Classify the intent of the input text.
        Returns one of: 'news_info', 'fact_check', 'general_query', 'clarification'
        """
        if not self.classifier:
            # Fallback to simple rule-based classification if model is not available
            return self._rule_based_classification(text)
        
        try:
            # Get prediction from the model
            result = self.classifier(text)[0]
            predicted_label = result['label']
            confidence = result['score']
            
            # If confidence is too low, use rule-based classification
            if confidence < 0.6:
                return self._rule_based_classification(text)
                
            return predicted_label
            
        except Exception as e:
            print(f"Error in model classification: {e}")
            return self._rule_based_classification(text)
    
    def _rule_based_classification(self, text: str) -> str:
        """
        Simple rule-based intent classification as fallback.
        """
        text = text.lower()
        
        # Check for fact-checking patterns
        fact_check_patterns = [
            r'is it true',
            r'is this true',
            r'verify',
            r'fact check',
            r'is this correct',
            r'is that correct',
            r'is this accurate',
            r'is that accurate'
        ]
        
        # Check for news patterns
        news_patterns = [
            r'latest news',
            r'recent news',
            r'what\'s happening',
            r'what is happening',
            r'what are the latest',
            r'what are the recent',
            r'what\'s new',
            r'what is new'
        ]
        
        # Check for clarification patterns
        clarification_patterns = [
            r'what do you mean',
            r'can you explain',
            r'could you explain',
            r'i don\'t understand',
            r'i do not understand',
            r'can you clarify',
            r'could you clarify'
        ]
        
        # Check patterns
        for pattern in fact_check_patterns:
            if re.search(pattern, text):
                return 'fact_check'
                
        for pattern in news_patterns:
            if re.search(pattern, text):
                return 'news_info'
                
        for pattern in clarification_patterns:
            if re.search(pattern, text):
                return 'clarification'
        
        # Default to general query if no specific patterns match
        return 'general_query'
    
    def classify_intent_rule_based(self, text: str) -> Tuple[str, float]:
        """Rule-based intent classification as fallback"""
        text_lower = text.lower()
        
        # Fact-checking patterns
        fact_check_patterns = [
            r'\bis it true\b', r'\bfact check\b', r'\bverify\b', r'\bconfirm\b',
            r'\bis this correct\b', r'\breal or fake\b', r'\btrue or false\b',
            r'\bdid .* really\b', r'\bactually happen\b'
        ]
        
        # News/update patterns  
        news_patterns = [
            r'\blatest\b', r'\bupdate\b', r'\bnews\b', r'\brecent\b',
            r'\bcurrent\b', r'\btoday\b', r'\bthis week\b', r'\bthis month\b',
            r'\bwhat.* happening\b', r'\bany updates\b'
        ]
        
        # Check for fact-checking intent
        for pattern in fact_check_patterns:
            if re.search(pattern, text_lower):
                return "fact_check", 0.85
        
        # Check for news intent
        for pattern in news_patterns:
            if re.search(pattern, text_lower):
                return "news_info", 0.80
        
        # Default to general query
        return "general_query", 0.70
    
    def classify_intent_ml(self, text: str) -> Tuple[str, float]:
        """ML-based intent classification"""
        if not self.classifier:
            return self.classify_intent_rule_based(text)
        
        try:
            # This would work with a fine-tuned model
            # For now, using rule-based as the model isn't trained
            result = self.classifier(text)
            intent = result[0]['label']
            confidence = result[0]['score']
            
            # Map to our intent classes if needed
            if intent not in self.intent_classes:
                return self.classify_intent_rule_based(text)
            
            return intent, confidence
        except Exception as e:
            print(f"ML classification failed: {e}")
            return self.classify_intent_rule_based(text)
    
    def classify(self, text: str) -> Dict[str, any]:
        """Main classification method"""
        intent = self.classify_intent(text)
        
        return {
            "intent": intent,
            "confidence": 1.0,  # Rule-based classification has full confidence
            "method": "rule_based"
        }
    
    def get_intent_features(self, text: str) -> Dict[str, any]:
        """Extract features that help with intent classification"""
        text_lower = text.lower()
        
        features = {
            "has_question_mark": "?" in text,
            "starts_with_wh": text_lower.startswith(('who', 'what', 'when', 'where', 'why', 'how')),
            "has_time_reference": any(word in text_lower for word in ['today', 'yesterday', 'recent', 'latest', 'now']),
            "has_verification_words": any(word in text_lower for word in ['true', 'false', 'fact', 'verify', 'confirm']),
            "has_news_keywords": any(word in text_lower for word in ['news', 'update', 'breaking', 'announcement']),
            "word_count": len(text.split()),
            "char_count": len(text)
        }
        
        return features
    
    def explain_classification(self, text: str) -> Dict[str, any]:
        """Provide explanation for the classification"""
        result = self.classify(text)
        features = self.get_intent_features(text)
        
        explanation = []
        
        if result["intent"] == "fact_check":
            explanation.append("Contains fact-checking keywords")
        elif result["intent"] == "news_info":
            explanation.append("Contains news/update keywords")
        elif result["intent"] == "general_query":
            explanation.append("General information request")
        
        if features["has_question_mark"]:
            explanation.append("Question format detected")
        if features["starts_with_wh"]:
            explanation.append("Starts with question word")
        
        return {
            **result,
            "features": features,
            "explanation": explanation
        }