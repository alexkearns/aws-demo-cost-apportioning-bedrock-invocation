from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.api_gateway_authorizer_event import (
    APIGatewayAuthorizerTokenEvent,
    APIGatewayAuthorizerResponse,
)


@event_source(data_class=APIGatewayAuthorizerTokenEvent)
def lambda_handler(event: APIGatewayAuthorizerTokenEvent, context):
    arn = event.parsed_arn

    policy = APIGatewayAuthorizerResponse(
        principal_id="example-user",
        region=arn.region,
        aws_account_id=arn.aws_account_id,
        api_id=arn.api_id,
        stage=arn.stage,
    )

    policy.allow_all_routes()
    return policy.asdict()
