import json
import os

import boto3

PROVIDER = os.environ.get("LLM_PROVIDER", "bedrock")
_client = None


def get_client():
    # Claude via Amazon Bedrock (AWS) o Vertex AI, segun LLM_PROVIDER.
    global _client
    if _client is not None:
        return _client

    if PROVIDER == "bedrock":
        from anthropic import AnthropicBedrock

        _client = AnthropicBedrock(aws_region=os.environ["AWS_REGION"])
    else:
        from anthropic import AnthropicVertex
        from google.oauth2 import service_account

        cfg = json.loads(boto3.client("secretsmanager").get_secret_value(
            SecretId=os.environ["CLOUD_CREDS_SECRET"])["SecretString"])
        creds = service_account.Credentials.from_service_account_info(
            cfg["gcp_service_account"], scopes=["https://www.googleapis.com/auth/cloud-platform"])
        # El SDK renueva el token automáticamente cuando expira
        _client = AnthropicVertex(project_id=cfg["gcp_project"],
                                  region=os.environ["VERTEX_REGION"],
                                  credentials=creds)
    return _client


def model_id():
    if PROVIDER == "bedrock":
        return os.environ["BEDROCK_MODEL_ID"]
    return os.environ["VERTEX_MODEL_ID"]
