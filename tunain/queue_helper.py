
import boto3
import json
import logging

logger = logging.getLogger(__name__)

# Create SQS client
sqs = boto3.client('sqs', endpoint_url='http://sqs.eu-west-1.localhost.localstack.cloud:4566')
queue_url = 'http://sqs.eu-west-1.localhost.localstack.cloud:4566/000000000000/page_tasks'


def build_prompt(book, pages):
    prompt = [
        {"role": "system", "content": book.system_prompt},
        {"role": "user", "content": book.initial_input},
    ]
    for p in pages:
        if p.content:
            prompt.append({"role": "assistant", "content": json.dumps(p.content)})
        if p.user_input:
            prompt.append({"role": "user", "content": p.user_input})

    prompt_str = json.dumps(prompt)
    logger.info(f"prompt_str {prompt_str}")
    return prompt_str

def create_page_task(book, pages):
    logger.info('create_page_task called')
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageAttributes={
            'BookId': {
                'DataType': 'Number',
                'StringValue': str(book.id)
            },
            'PageId': {
                'DataType': 'Number',
                'StringValue': str(pages[-1].id)
            },
            'PageNumber': {
                'DataType': 'Number',
                'StringValue': str(pages[-1].number)
            }
        },
        MessageBody=build_prompt(book, pages)
    )

    logger.info(f"sqs send_message response: {response}")
    try:
        return response['MessageId']
    except:
        return 'error'
