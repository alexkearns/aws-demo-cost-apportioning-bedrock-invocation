import boto3
import argparse
from keycove import generate_token, hash

parser = argparse.ArgumentParser()
parser.add_argument("--dynamodb-table-name", required=True)
parser.add_argument("--username", required=True)
args = parser.parse_args()

table = boto3.resource("dynamodb").Table(args.dynamodb_table_name)


def main():
    token = generate_token()
    table.put_item(
        Item={
            "ApiKey": hash(token),
            "Username": args.username,
        }
    )

    print(f"Your API key generated is {token}")


if __name__ == "__main__":
    main()
