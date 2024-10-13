import boto3
import json
import os

from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from get_model_usage import ModelUsageDriverManager

CLOUDWATCH_CUSTOM_METRIC_NAMESPACE = os.environ["CLOUDWATCH_CUSTOM_METRIC_NAMESPACE"]

bedrock_runtime = boto3.client("bedrock-runtime")
cloudwatch = boto3.client("cloudwatch")

app = APIGatewayRestResolver()


@app.post("/invoke-model")
def invoke_model():
    # Take the body from the API GW proxy event, and re-serialise the body as
    # the Bedrock Runtime API expects `body` as a string
    bedrock_request: dict = app.current_event.json_body
    bedrock_request["body"] = json.dumps(bedrock_request["body"])

    # Make a request against the Bedrock Runtime API
    response = bedrock_runtime.invoke_model(**bedrock_request)
    response_body = response["body"].read().decode("utf-8")

    # Determine the model usage driver based on the model ID, and then use it
    # to get the model usage
    model_id = bedrock_request["modelId"]
    model_usage_driver = ModelUsageDriverManager(model_id).get_model_usage_driver()
    model_usage = model_usage_driver(model_id).get_model_usage(
        json.loads(response_body)
    )

    # Extract the user information from the event
    principal_id = app.current_event.request_context.authorizer.principal_id

    # Put metric data to CloudWatch to store model usage
    cloudwatch.put_metric_data(
        Namespace=CLOUDWATCH_CUSTOM_METRIC_NAMESPACE,
        MetricData=[
            {
                "MetricName": "InputTokensUsed",
                "Value": model_usage["input"]["tokens"],
                "Unit": "Count",
                "Dimensions": [
                    {"Name": "ModelId", "Value": model_id},
                    {"Name": "PrincipalId", "Value": principal_id},
                ],
            },
            {
                "MetricName": "InputTokensCost",
                "Value": model_usage["input"]["cost"],
                "Unit": "Count",
                "Dimensions": [
                    {"Name": "ModelId", "Value": model_id},
                    {"Name": "PrincipalId", "Value": principal_id},
                ],
            },
            {
                "MetricName": "OutputTokensUsed",
                "Value": model_usage["output"]["tokens"],
                "Unit": "Count",
                "Dimensions": [
                    {"Name": "ModelId", "Value": model_id},
                    {"Name": "PrincipalId", "Value": principal_id},
                ],
            },
            {
                "MetricName": "OutputTokensCost",
                "Value": model_usage["output"]["cost"],
                "Unit": "Count",
                "Dimensions": [
                    {"Name": "ModelId", "Value": model_id},
                    {"Name": "PrincipalId", "Value": principal_id},
                ],
            },
        ],
    )

    return response_body


def lambda_handler(event, context: LambdaContext):
    return app.resolve(event, context)
