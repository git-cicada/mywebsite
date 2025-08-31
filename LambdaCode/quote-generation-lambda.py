from datetime import datetime, timezone
from openai import OpenAI
import boto3
import json
import os



# Initialize AWS clients
secrets_client = boto3.client("secretsmanager")
s3_client = boto3.client("s3")

# # Read from ENV (you’ll configure in Lambda console)
# SECRET_NAME = os.environ["OPENAI_SECRET_NAME"]
# S3_BUCKET = os.environ["S3_BUCKET"]

SECRET_NAME = 'prod/openaikey'
S3_BUCKET = 'mydaily-quotes'

def get_openai_api_key():
    """Fetch API Key from Secrets Manager"""
    response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
    secret_dict = json.loads(response["SecretString"])
    return secret_dict["OPENAI_API_KEY"]  # Make sure you stored with this key

def generate_quote(api_key: str) -> str:
    """Generate a daily quote using OpenAI"""
    client = OpenAI(api_key=api_key)
    
    prompt = "Give me an inspiring motivational quote for the day. Keep it short and positive."

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheaper & fast
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0.8
    )

    return response.choices[0].message.content.strip()


def lambda_handler(event, context):
    try:
        # Get API key
        api_key = get_openai_api_key()

        # Generate Quote
        quote = generate_quote(api_key)

        # Save to S3
        file_name = "quote-of-the-day.json"
        s3_body = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "quote": quote
        }

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=file_name,
            Body=json.dumps(s3_body),
            ContentType="application/json"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Quote generated and stored", "quote": quote})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }