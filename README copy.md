# AI-Powered Financial Data Extraction

This application uses AI and NLP models to extract financial data from mutual fund reports in various formats.

## Features
- AI-powered data extraction from multiple file formats (.xls, .xlsx, .csv, PDF)
- Dynamic parsing and layout detection
- Data standardization and normalization
- Structured and unstructured data storage
- Query and analysis capabilities

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to system PATH

3. Start the application:
```bash
uvicorn app:app --reload
```

## Project Structure
- `app.py`: Main FastAPI application
- `models/`: AI/NLP models and processors
- `database/`: Database models and connections
- `utils/`: Helper functions and utilities
- `config.py`: Configuration settings
