import os
import boto3

client = boto3.client('sns')
topic_arn = os.getenv('TOPIC_ARN')


def publish(message):
    client.publish(
        TopicArn=topic_arn,
        Message=str(message),
        Subject='RESULTADO LOTERIA'
    )
