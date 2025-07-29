import boto3
import os
import uuid
from botocore.exceptions import BotoCoreError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE")

# AWS clients
s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
comprehend_client = boto3.client("comprehend", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMO_TABLE)

def upload_to_s3(file_content: bytes, filename: str):
    """Upload a file to S3 and return file_id + s3_key."""
    try:
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1]
        s3_key = f"uploads/{file_id}{file_ext}"
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_content)
        return file_id, s3_key
    except (BotoCoreError, NoCredentialsError) as e:
        raise Exception(f"S3 upload failed: {str(e)}")

def analyze_sentiment(text: str) -> str:
    """Detect sentiment using Comprehend."""
    try:
        response = comprehend_client.detect_sentiment(Text=text, LanguageCode="en")
        return response["Sentiment"]
    except Exception as e:
        raise Exception(f"Comprehend sentiment analysis failed: {str(e)}")

def analyze_entities(text: str) -> list:
    """Extract entities using Comprehend."""
    try:
        response = comprehend_client.detect_entities(Text=text, LanguageCode="en")
        return [{"Text": e["Text"], "Type": e["Type"]} for e in response["Entities"]]
    except Exception as e:
        raise Exception(f"Comprehend entity analysis failed: {str(e)}")

def save_metadata(file_id: str, filename: str, summary: str, sentiment: str, entities: list):
    """Save document metadata to DynamoDB."""
    try:
        table.put_item(Item={
            "file_id": file_id,
            "filename": filename,
            "summary": summary,
            "sentiment": sentiment,
            "entities": entities
        })
    except Exception as e:
        raise Exception(f"DynamoDB save failed: {str(e)}")
