from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configurations
MONGODB_URL = "mongodb://localhost:27017"  # Default MongoDB Docker port
MONGODB_DB = "testDb"
POSTGRESQL_URL = "postgresql://postgres:password@localhost:5432/postgres"

# Model configurations
BERT_MODEL_NAME = "ProsusAI/finbert"
SPACY_MODEL = "en_core_web_trf"

# File processing
ALLOWED_EXTENSIONS = {'.xls', '.xlsx', '.csv', '.pdf'}
UPLOAD_FOLDER = BASE_DIR / "uploads"
PROCESSED_FOLDER = BASE_DIR / "processed"

# Create necessary directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
PROCESSED_FOLDER.mkdir(exist_ok=True)

# OCR Configuration
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path as needed
