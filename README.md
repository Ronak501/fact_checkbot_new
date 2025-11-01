# Fact Check Bot

An intelligent fact-checking bot that uses advanced NLP and machine learning techniques to verify claims and provide accurate information. Features a modern web interface for easy interaction.

## Features

- 🤖 Automated fact-checking using machine learning models
- 🔍 Web scraping capabilities for source verification
- 📊 Data analysis and processing
- 🚀 Fast API endpoints for easy integration
- 💾 Redis caching for improved performance
- 🔄 Asynchronous operations for better scalability
- 💻 Modern web interface with chat-like UI
- 📱 Responsive design for all devices

## Prerequisites

- Python 3.8 or higher
- Redis server
- Virtual environment (recommended)
- Modern web browser

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd fact_check_bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required NLP models:
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt
python -m nltk.downloader stopwords
```

5. Set up environment variables:
Create a `config.env` file in the root directory with the following variables:
```
SERP_API_KEY=your_serp_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Usage

1. Start the Redis server:
```bash
redis-server
```

2. Run the FastAPI application:
```bash
uvicorn api:app --reload
```

3. Access the web interface at:
```
http://localhost:8000
```

4. Access the API documentation at:
```
http://localhost:8000/docs
```

## Frontend Features

- Modern chat-like interface
- Real-time fact checking
- Message history
- Typing indicators
- Responsive design
- Error handling
- Loading states

## Backend API Endpoints

- `POST /fact-check`: Submit a claim for fact-checking
- `GET /`: Serve the web interface
- `GET /static/*`: Serve static files (CSS, JavaScript)

## Project Structure

```
fact_check_bot2/
├── static/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── services/
│   ├── search_service.py
│   ├── fact_checker.py
│   └── cache_service.py
├── utils/
│   ├── source_validator.py
│   ├── confidence_scorer.py
│   └── input_cleaning.py
├── models/
│   ├── response_generator.py
│   ├── query_generator.py
│   ├── intent_classifier.py
│   └── entity_extractor.py
├── config/
│   ├── settings.py
│   └── logging_config.py
├── api.py
├── main.py
├── config.env
├── requirements.txt
└── README.md
```

## Dependencies

### Web Framework and API
- FastAPI
- Uvicorn
- Python-multipart
- Requests

### Frontend
- Modern HTML5
- CSS3
- JavaScript (ES6+)

### Data Processing and ML
- NumPy
- Pandas
- Scikit-learn
- PyTorch
- Transformers
- Sentence-transformers
- KeyBERT

### NLP Libraries
- spaCy
- NLTK
- BeautifulSoup4
- lxml

### Caching and Database
- Redis

### Utilities
- python-dotenv
- python-dateutil
- aiohttp
- asyncio
- Pydantic

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hugging Face for the transformer models
- spaCy and NLTK for NLP capabilities
- FastAPI for the web framework
- All other open-source contributors

## Contact

Your Name - [prathamrajput709@gmail.com]
Project Link: [https://github.com/Prathamesh603/fact_check_bot2]
