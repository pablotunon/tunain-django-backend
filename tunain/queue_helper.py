
import boto3
import json
import logging

logger = logging.getLogger(__name__)

# Create SQS client
sqs = boto3.client('sqs', endpoint_url='http://sqs.eu-west-1.localhost.localstack.cloud:4566')
page_queue_url = 'http://sqs.eu-west-1.localhost.localstack.cloud:4566/000000000000/page_tasks'
image_queue_url = 'http://sqs.eu-west-1.localhost.localstack.cloud:4566/000000000000/image_tasks'


def build_single_prompt(book, pages):
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

def build_multi_prompt(book, pages, system_dict):
    prompt_dict = {
        'text': [
            {"role": "system", "content": system_dict['text']},
            {"role": "user", "content": book.initial_input},
        ],
        'illustration': [
            {"role": "system", "content": system_dict['illustration']}
        ]
    }
    for p in pages:
        if p.content:
            prompt_dict['text'].append({"role": "assistant", "content": json.dumps(p.content['text'])})
        if p.user_input:
            prompt_dict['text'].append({"role": "user", "content": p.user_input})

    prompt_str = json.dumps(prompt_dict)
    logger.info(f"prompt_str {prompt_str}")
    return prompt_str


def build_prompt(book, pages):
    system_dict = {}
    try:
        system_dict = json.loads(book.system_prompt)
        return build_multi_prompt(book, pages, system_dict)
    except:
        return build_single_prompt(book, pages)


def create_page_task(book, pages):
    logger.info('create_page_task called')
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=page_queue_url,
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

def create_image_task(page):
    logger.info('create_image_task called')
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=image_queue_url,
        MessageAttributes={
            'PageId': {
                'DataType': 'Number',
                'StringValue': str(page.id)
            },
        },
        MessageBody=page.content['illustration']
    )

    logger.info(f"sqs send_message response: {response}")
    try:
        return response['MessageId']
    except:
        return 'error'