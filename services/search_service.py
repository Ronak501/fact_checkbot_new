import requests
from typing import List, Dict, Any
import logging
import json
from dotenv import load_dotenv
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


load_dotenv(dotenv_path="config.env")  # load from .env

print("Loaded SERP_API_KEY:", os.getenv("SERP_API_KEY"))

class SearchService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"  # Fixed endpoint URL

    def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform a search based on the provided query using the Serp API."""
        try:
            # Extract the actual query string from the query dictionary
            search_query = query.get('query', '')
            
            # Log the search attempt
            logging.info(f"Attempting search with query: {search_query}")
            
            params = {
                "q": search_query,
                "api_key": self.api_key,
                "engine": "google",  # Use Google engine (change if you use Bing or others)
                "num": 5,            # Limit to 5 results
                "gl": "us",          # Location: US
                "hl": "en"           # Language: English
            }
            
            # Log the API request (excluding api_key for security)
            logging.info(f"Making request to Serp API with params: {json.dumps({k: v for k, v in params.items() if k != 'api_key'})}")
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            # Log the response status
            logging.info(f"Serp API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Log the response keys
                logging.info(f"Response keys: {list(data.keys())}")
                
                if "error" in data:
                    error_msg = f"Serp API error: {data['error']}"
                    logging.error(error_msg)
                    return []
                    
                # Extract organic results
                organic_results = data.get("organic_results", [])
                if not organic_results:
                    logging.warning("No organic results found in Serp API response")
                    # Try knowledge graph fallback
                    knowledge_graph = data.get("knowledge_graph", {})
                    if knowledge_graph:
                        return [{
                            'title': knowledge_graph.get('title', ''),
                            'snippet': knowledge_graph.get('description', ''),
                            'link': knowledge_graph.get('source', {}).get('link', ''),
                            'source': 'Knowledge Graph'
                        }]
                    return []
                    
                # Format results
                formatted_results = []
                for result in organic_results:
                    formatted_result = {
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'link': result.get('link', ''),
                        'source': result.get('source', '')
                    }
                    # Only add if title or snippet exists
                    if formatted_result['title'] or formatted_result['snippet']:
                        formatted_results.append(formatted_result)
                
                logging.info(f"Found {len(formatted_results)} valid results")
                return formatted_results
            else:
                error_msg = f"Serp API request failed with status code: {response.status_code}"
                logging.error(error_msg)
                logging.error(f"Response content: {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logging.error("Search request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during search: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in search service: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="config.env")
    
    API_KEY = os.getenv("SERP_API_KEY")
    
    if not API_KEY:
        print("Error: SERP_API_KEY not found in environment variables.")
    else:
        search_service = SearchService(api_key=API_KEY)
        results = search_service.search({"query": "example query"})
        print(results)
