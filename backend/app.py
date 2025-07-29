from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import logging
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, NoCredentialsError
from aws_utils import upload_to_s3, analyze_sentiment, analyze_entities, save_metadata

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE")

# Load summarizer
try:
    from transformers import pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    logger.info("Summarizer model loaded successfully.")
except Exception as e:
    summarizer = None
    logger.error(f"Failed to load summarizer: {e}")

# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: set to ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response model
class Entity(BaseModel):
    Text: str
    Type: str

class AnalysisResult(BaseModel):
    summary: str
    sentiment: str
    entities: list[Entity]

@app.get("/")
def health_check():
    return {"status": "Backend running"}

@app.post("/upload", response_model=AnalysisResult)
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")

        # Upload to S3
        _, s3_key = upload_to_s3(content, file.filename)

        # Summarization
        if summarizer:
            try:
                summary = summarizer(text_content[:2000], max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                summary = "Summarization unavailable."
        else:
            summary = "Summarizer not loaded."

        # Sentiment & Entities
        sentiment = analyze_sentiment(text_content)
        entities = analyze_entities(text_content)

        # Save metadata in DynamoDB
        save_metadata(file_id, file.filename, summary, sentiment, entities)

        return AnalysisResult(summary=summary, sentiment=sentiment, entities=entities)

    except (BotoCoreError, NoCredentialsError):
        raise HTTPException(status_code=500, detail="AWS credentials error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
