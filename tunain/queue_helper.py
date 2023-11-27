
import boto3
import json

# Create SQS client
sqs = boto3.client('sqs')

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
    print(prompt_str)
    return prompt_str

def create_page_task(book, pages):
    print('create_page_task called')
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
    print(response['MessageId'])
