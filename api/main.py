import os
import time
import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
timestamp = int(time.time())


def increment_counter(pk ="web_counter"):
    try:
        response = table.update_item(
            Key={"id": pk},
            UpdateExpression="SET visits = if_not_exists(visits, :start) + :inc, updated_at = :timestamp",
            ExpressionAttributeValues={":inc": 1, ":start": 0, ":timestamp": timestamp},
            ReturnValues="UPDATED_NEW",
        )
        return {"status": "success", "visits": f"{response["Attributes"]["visits"]}"}
    except Exception as e:
        print(f"Error incrementing counter: {str(e)}")
        return {"status": "error", "message": "Could not increment counter"}


def handler(event=None, _context=None):
    visit_count = increment_counter()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"visits": visit_count, "timestamp": timestamp}),
    }
