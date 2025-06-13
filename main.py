from typing import Dict, Any
from services.search_service import SearchService
from services.fact_checker import FactChecker
from services.cache_service import CacheService
from utils.source_validator import SourceValidator
from utils.confidence_scorer import ConfidenceScorer
from utils.input_cleaning import preprocess
from models.response_generator import ResponseGenerator
from models.query_generator import QueryGenerator
from models.intent_classifier import IntentClassifier
from models.entity_extractor import EntityExtractor
import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

def setup_environment():
    current_dir = os.getcwd()
    logging.info(f"Current working directory: {current_dir}")

    env_path = os.path.join(current_dir, 'config.env')

    if not os.path.exists(env_path):
        logging.error("No config.env file found in the current directory")
        print(f"\n{Fore.RED}Error: No config.env file found!{Style.RESET_ALL}")
        print(f"Please create a config.env file in: {current_dir}")
        print("\nRequired content:")
        print("""
SERP_API_KEY=your_serp_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
        """)
        raise FileNotFoundError(f"No config.env file found at: {env_path}")

    try:
        with open(env_path, 'r') as f:
            env_content = f.read().strip()

        env_vars = {}
        for line in env_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

        for key, value in env_vars.items():
            os.environ[key] = value

        logging.info(f"Loaded environment variables from: {env_path}")

        api_key = os.getenv('SERP_API_KEY')
        if not api_key or len(api_key) < 32:
            raise ValueError("SERP_API_KEY is not set or is invalid")

    except Exception as e:
        logging.error(f"Failed to load config.env file from: {env_path}. Error: {e}")
        raise ValueError(f"Failed to load config.env file from: {env_path}")

    required_vars = {
        'SERP_API_KEY': 'Serp API key for web searches',
        'REDIS_HOST': 'Redis server host (default: localhost)',
        'REDIS_PORT': 'Redis server port (default: 6379)',
        'REDIS_DB': 'Redis database number (default: 0)'
    }

    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")

    if missing_vars:
        error_msg = "Missing required environment variables:\n"
        error_msg += "\n".join(f"- {var}" for var in missing_vars)
        error_msg += f"\n\nPlease add these variables to your config.env file at: {env_path}"
        logging.error(error_msg)
        raise ValueError(error_msg)


class FactCheckBot:
    def __init__(self):
        try:
            setup_environment()
            self.search_service = SearchService(api_key=os.getenv('SERP_API_KEY'))
            self.cache_service = CacheService(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0))
            )
            self.fact_checker = FactChecker()
            self.source_validator = SourceValidator()
            self.confidence_scorer = ConfidenceScorer()
            self.response_generator = ResponseGenerator()
            self.query_generator = QueryGenerator()
            self.intent_classifier = IntentClassifier()
            self.entity_extractor = EntityExtractor()
            logging.info("Fact Check Bot initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing Fact Check Bot: {str(e)}")
            raise

    def process_query(self, query: str) -> Dict[str, Any]:
        try:
            logging.info(f"Original user query: {query}")
            cleaned_query = preprocess(query)
            logging.info(f"Cleaned query: {cleaned_query}")

            cached_response = self.cache_service.get(cleaned_query)
            if cached_response:
                try:
                    response = json.loads(cached_response.decode('utf-8'))
                    logging.info("Retrieved response from cache")
                    return response
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logging.warning(f"Failed to deserialize cached response: {e}")

            intent = self.intent_classifier.classify_intent(cleaned_query)
            logging.info(f"Classified intent: {intent}")

            entities = self.entity_extractor.extract_entities(cleaned_query)
            logging.info(f"Extracted entities: {entities}")

            search_query = self.query_generator.generate_search_query(cleaned_query, intent, entities)
            logging.info(f"Generated search query: {search_query}")

            search_results = self.search_service.search(search_query)
            logging.info(f"Search results raw data: {json.dumps(search_results, indent=2)}")

            validated_results = []
            for result in search_results:
                url = result.get('link') or result.get('url') or ''
                if self.source_validator.is_credible(url):
                    validated_results.append(result)
                else:
                    logging.debug(f"Rejected source: {url}")

            if not validated_results:
                logging.warning("No validated sources found. Using fallback to include all search results.")
                validated_results = search_results.copy()
            else:
                logging.info(f"Validated {len(validated_results)} sources out of {len(search_results)}")

            if intent == "fact_check":
                response = self.fact_checker.verify_claim(cleaned_query)
            else:
                response = self.response_generator.generate_response(
                    query=cleaned_query,
                    intent=intent,
                    search_results=validated_results
                )

            response['raw_search_results'] = search_results

            try:
                self.cache_service.set(cleaned_query, json.dumps(response).encode('utf-8'))
                logging.info("Response cached successfully")
            except Exception as e:
                logging.warning(f"Failed to cache response: {e}")

            return response

        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            return {
                "error": str(e),
                "response": "I apologize, but I encountered an error while processing your query. Please try again."
            }


def print_welcome():
    print(f"\n{Fore.CYAN}=== Fact Check Bot ==={Style.RESET_ALL}")
    print(f"{Fore.GREEN}Welcome to the Fact Check Bot!{Style.RESET_ALL}")
    print("\nYou can ask me to:")
    print(f"{Fore.YELLOW}•{Style.RESET_ALL} Fact-check claims")
    print(f"{Fore.YELLOW}•{Style.RESET_ALL} Get news summaries")
    print(f"{Fore.YELLOW}•{Style.RESET_ALL} Answer general questions")
    print(f"\nType {Fore.RED}'quit'{Style.RESET_ALL} to exit")
    print(f"Type {Fore.RED}'help'{Style.RESET_ALL} to see this message again\n")


def print_help():
    print(f"\n{Fore.CYAN}=== Example Queries ==={Style.RESET_ALL}")
    print(f"{Fore.GREEN}Fact-checking:{Style.RESET_ALL}")
    print("• Is it true that the Earth is flat?")
    print("• Did NASA really land on the moon?")
    print(f"\n{Fore.GREEN}News:{Style.RESET_ALL}")
    print("• What are the latest developments in AI?")
    print("• What's happening in Ukraine?")
    print(f"\n{Fore.GREEN}General:{Style.RESET_ALL}")
    print("• What is the capital of France?")
    print("• Who is the current president of the United States?\n")

_fact_check_instance = FactCheckBot()

def fact_check_bot(query: str) -> dict:
    return _fact_check_instance.process_query(query)

def main():
    try:
        bot = FactCheckBot()
        print_welcome()

        while True:
            try:
                user_input = input(f"{Fore.GREEN}Enter your query: {Style.RESET_ALL}").strip()

                if not user_input:
                    continue

                lower_input = user_input.lower()

                # Greeting responses
                if lower_input in ['hi', 'hello', 'hey','hii','hey there']:
                    print(f"{Fore.BLUE}Hello! How can I help you today? 😊{Style.RESET_ALL}")
                    continue

                # Gratitude responses
                elif any(kw in lower_input for kw in ['thank you', 'thanks', 'thx']):
                    print(f"{Fore.BLUE}You're welcome! Let me know if you need anything else. 🙌{Style.RESET_ALL}")
                    continue

                # Help command
                elif lower_input == 'help':
                    print_help()
                    continue

                # Exit command
                elif lower_input == 'quit':
                    print(f"\n{Fore.YELLOW}Thank you for using Fact Check Bot! Goodbye!{Style.RESET_ALL}")
                    break

                # Follow-up questions
                elif any(kw in lower_input for kw in ['tell me more', 'more details', 'explain further', 'what else']):
                    print(f"{Fore.BLUE}Sure! Can you please clarify what you'd like to know more about? 🧐{Style.RESET_ALL}")
                    continue

                # Process actual query
                response = bot.process_query(user_input)

                if isinstance(response, dict):
                    if "error" in response:
                        print(f"\n{Fore.RED}Error: {response['error']}{Style.RESET_ALL}")
                    print(f"\n{Fore.CYAN}Response:{Style.RESET_ALL}")
                    print(response.get('response', 'No response generated.'))

                    if 'sources' in response:
                        print(f"\n{Fore.YELLOW}Sources:{Style.RESET_ALL}")
                        for source in response['sources']:
                            title = source.get('title', 'No title')
                            url = source.get('url') or source.get('link') or 'No URL'
                            print(f"• {title} - {url}")

                    if 'raw_search_results' in response:
                        print(f"\n{Fore.MAGENTA}Raw API Search Results:{Style.RESET_ALL}")
                        for i, res in enumerate(response['raw_search_results'], start=1):
                            title = res.get('title', 'No Title')
                            url = res.get('link') or res.get('url') or 'No URL'
                            snippet = res.get('snippet', '')
                            print(f"{i}. {title}\n   {url}\n   {snippet}\n")
                else:
                    print(f"\n{Fore.CYAN}Response:{Style.RESET_ALL}")
                    print(response)

            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Thank you for using Fact Check Bot! Goodbye!{Style.RESET_ALL}")
                break
            except Exception as e:
                logging.error(f"Error processing user input: {str(e)}")
                print(f"\n{Fore.RED}An error occurred. Please try again.{Style.RESET_ALL}")


    except Exception as e:
        logging.error(f"Critical error in main: {str(e)}")
        print(f"\n{Fore.RED}A critical error occurred. Please check the logs for details.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
