from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import os
from models.processors import DocumentProcessor
from database.connection import DatabaseManager
from utils.logger_config import fund_extractor as logger

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure static files and templates
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

templates = Jinja2Templates(directory="templates")

# Initialize processor and database
logger.info("Initializing DocumentProcessor and DatabaseManager")
processor = DocumentProcessor()
db_manager = DatabaseManager()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        
        # Save the uploaded file
        file_path = uploads_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved file to: {file_path}")
        
        # Process the file
        logger.info("Processing file with DocumentProcessor")
        result = await processor.process_file(file_path)
        
        # Store results in database
        logger.info("Storing results in database")
        db_manager.store_results(result)
        
        # Return the raw response
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": f"Error processing file: {str(e)}"}
        )

@app.get("/query")
async def query_data(request: Request):
    try:
        # Get query parameters
        params = dict(request.query_params)
        
        # Query database
        results = db_manager.query_data(params)
        
        return JSONResponse(content={"results": results})
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": f"Error processing query: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Fund Data Extractor application")
    uvicorn.run(app, host="0.0.0.0", port=8000)
