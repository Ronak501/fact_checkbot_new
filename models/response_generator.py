from typing import List, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import re
from datetime import datetime
from config.settings import settings
from config.prompts import ResponseTemplates

class ResponseGenerator:
    def __init__(self):
        self.templates = ResponseTemplates()
        
        # Initialize summarization model
        try:
            self.summarizer = pipeline(
                "summarization",
                model=settings.SUMMARIZATION_MODEL,
                tokenizer=settings.SUMMARIZATION_MODEL,
                max_length=settings.MAX_SUMMARY_LENGTH,
                min_length=settings.MIN_SUMMARY_LENGTH,
                do_sample=False
            )
        except Exception as e:
            print(f"Summarization model loading failed: {e}")
            self.summarizer = None
    
    def generate_response(self, query: str, intent: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Generate final response based on intent and search results"""
        if not search_results:
            return self.generate_error_response(
                "No search results found. This could be due to API limitations or no relevant information available."
            )
        
        if intent == "fact_check":
            return self.generate_fact_check_response(query, search_results)
        elif intent == "news_info":
            return self.generate_news_response(query, search_results)
        else:
            return self.generate_general_response(query, search_results)
    
    def generate_fact_check_response(self, query: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Generate response for fact-checking queries"""
        # Extract claim from query
        claim = query.lower().replace("is it true that", "").replace("is this true that", "").strip()
        
        # Analyze search results for evidence
        evidence = []
        sources = []
        for result in search_results:
            evidence.append(result.get('snippet', ''))
            sources.append({
                'title': result.get('title', ''),
                'url': result.get('link', '')
            })
        
        # Determine verdict based on evidence
        verdict = "UNVERIFIED"  # Default verdict
        if evidence:
            # Simple rule-based verification
            positive_terms = ['confirmed', 'verified', 'true', 'correct', 'accurate']
            negative_terms = ['false', 'incorrect', 'inaccurate', 'debunked', 'misleading']
            
            evidence_text = ' '.join(evidence).lower()
            positive_count = sum(1 for term in positive_terms if term in evidence_text)
            negative_count = sum(1 for term in negative_terms if term in evidence_text)
            
            if positive_count > negative_count:
                verdict = "TRUE"
            elif negative_count > positive_count:
                verdict = "FALSE"
            elif positive_count == negative_count and positive_count > 0:
                verdict = "PARTIALLY_TRUE"
        
        return {
            'response': self.templates.FACT_CHECK_TEMPLATE.format(
                claim=claim,
                verdict=verdict,
                evidence='\n'.join(evidence) if evidence else "No specific evidence found.",
                sources='\n'.join(f"• {s['title']} - {s['url']}" for s in sources) if sources else "No sources available.",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            'sources': sources
        }
    
    def generate_news_response(self, query: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Generate response for news queries"""
        # Extract topic from query
        topic = query.lower().replace("latest news about", "").replace("what's happening with", "").strip()
        
        # Combine search results
        summaries = []
        sources = []
        for result in search_results:
            summaries.append(result.get('snippet', ''))
            sources.append({
                'title': result.get('title', ''),
                'url': result.get('link', '')
            })
        
        # Generate summary if model is available
        if self.summarizer and summaries:
            try:
                combined_text = ' '.join(summaries)
                summary = self.summarizer(combined_text, max_length=settings.MAX_SUMMARY_LENGTH, min_length=settings.MIN_SUMMARY_LENGTH)[0]['summary_text']
            except Exception as e:
                print(f"Summarization failed: {e}")
                summary = ' '.join(summaries)
        else:
            summary = ' '.join(summaries)
        
        return {
            'response': self.templates.NEWS_SUMMARY_TEMPLATE.format(
                topic=topic,
                summary=summary if summary else "No recent news found on this topic.",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                source_count=len(sources)
            ),
            'sources': sources
        }
    
    def generate_general_response(self, query: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Generate response for general queries"""
        # Combine search results
        answers = []
        sources = []
        for result in search_results:
            answers.append(result.get('snippet', ''))
            sources.append({
                'title': result.get('title', ''),
                'url': result.get('link', '')
            })
        
        # Generate summary if model is available
        if self.summarizer and answers:
            try:
                combined_text = ' '.join(answers)
                answer = self.summarizer(combined_text, max_length=settings.MAX_SUMMARY_LENGTH, min_length=settings.MIN_SUMMARY_LENGTH)[0]['summary_text']
            except Exception as e:
                print(f"Summarization failed: {e}")
                answer = ' '.join(answers)
        else:
            answer = ' '.join(answers)
        
        if not answer:
            return self.generate_error_response("No relevant information found for your query.")
        
        return {
            'response': answer,
            'sources': sources
        }
    
    def generate_error_response(self, reason: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'response': self.templates.ERROR_TEMPLATE.format(reason=reason),
            'sources': []
        }