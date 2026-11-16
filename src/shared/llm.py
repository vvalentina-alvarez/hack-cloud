import os
_client = None


def get_client():
    global _client
    if _client is None:
        from anthropic import AnthropicBedrock

        _client = AnthropicBedrock(aws_region=os.environ["AWS_REGION"])
    return _client


def model_id():
    return os.environ["BEDROCK_MODEL_ID"]
