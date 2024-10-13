# Apportioning cost of Amazon Bedrock InvokeModel requests

## Getting started

### 1. Pre-requisites

Ensure that AWS credentials are configured in your shell before running through the next steps. I like to use the [AWSume](https://awsu.me/) tool to do this. Make sure that you've got the `AWS_REGION` environment variable set also. AWSume will set this for you if you have a region set in the profile in `~/.aws/config`, or run `export AWS_REGION=your-region-1`.

You'll also need to ensure that you've got access to the model through Bedrock that you want to use. This sample is written with the `eu-west-2` region in mind, geared towards the Claude 3 Haiku and Sonnet models.

### 2. Deploying the proxy

The infrastructure is deployed using the AWS SAM (Serverless Application Model) CLI tool. If you don't have it, view the [installation instructions](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).

```sh
sam build

# If deploying for the first time
sam deploy --guided

# Subsequent deploys, after saving your deployment configuration to samconfig.toml
sam deploy
```

### 3. Generating an API key

```sh
cd scripts

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python generate_sample_api_key.py --username "Your Name" --dynamodb-table-name "YourTableName"
```

### 4. Making a request

The SAM template has a CloudFormation output declared that holds the value of the URL you'll be sending a request to. The output is called `BedrockProxyApiEndpoint`. I'd recommend using Postman as an easy way to make this request.

To test your deployed application, send a request to the URL output with the following body and an additional header of `Authorization` with a value of the API key that was generated in step 3.

```json
{
  "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
  "body": {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 2048,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Good morning!"
          }
        ]
      }
    ],
    "temperature": 0.5,
    "top_p": 0.5,
    "top_k": 250
  }
}
```

From this, you'll be returned the normal output from an InvokeModel API call. Behind the scenes, metrics will have been stored to help you apportion the cost.
