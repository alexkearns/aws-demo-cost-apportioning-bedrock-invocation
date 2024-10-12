import os

AWS_REGION = os.environ["AWS_REGION"]


class AbstractModelUsageDriver:
    # Example format:
    # MODEL_PRICE_PER_1K_TOKENS = {
    #     "REGION": {
    #         "MODEL_ID": {
    #             "input": 0.00025,
    #             "output": 0.00125,
    #         }
    #     }
    # }
    MODEL_PRICE_PER_1K_TOKENS = None
    MODEL_ID = None

    def __init__(self, model_id):
        self.MODEL_ID = model_id

    def get_model_usage(self, bedrock_response):
        raise NotImplementedError("invoke_model method must be implemented")


class AnthropicClaudeDriver(AbstractModelUsageDriver):
    MODEL_PRICE_PER_1K_TOKENS = {
        "eu-west-2": {
            "anthropic.claude-3-haiku-20240307-v1:0": {
                "input": 0.00025,
                "output": 0.00125,
            },
            "anthropic.claude-3-sonnet-20240229-v1:0": {
                "input": 0.003,
                "output": 0.015,
            },
        }
    }

    def __calculate_cost_of_tokens(self, direction, tokens):
        region = AWS_REGION
        model_id = self.MODEL_ID

        price_per_1k_tokens = self.MODEL_PRICE_PER_1K_TOKENS[region][model_id][
            direction
        ]
        cost = (tokens / 1000) * price_per_1k_tokens

        return cost

    def get_model_usage(self, bedrock_response):
        input_tokens_used = bedrock_response["usage"]["input_tokens"]
        output_tokens_used = bedrock_response["usage"]["output_tokens"]

        response = {
            "input": {
                "tokens": input_tokens_used,
                "cost": self.__calculate_cost_of_tokens("input", input_tokens_used),
            },
            "output": {
                "tokens": output_tokens_used,
                "cost": self.__calculate_cost_of_tokens("output", output_tokens_used),
            },
        }

        return response


class ModelUsageDriverManager:
    # Find model IDs on this page
    # https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html#model-ids-arns
    MODEL_USAGE_DRIVERS = {
        "anthropic.claude-3-haiku-20240307-v1:0": AnthropicClaudeDriver,
        "anthropic.claude-3-sonnet-20240229-v1:0": AnthropicClaudeDriver,
    }

    def __init__(self, model_id):
        self.model_id = model_id

    def get_model_usage_driver(self):
        return self.MODEL_USAGE_DRIVERS[self.model_id]
