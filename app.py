import boto3
import os
from flask import Flask, render_template, request, send_from_directory, jsonify
from faker import Faker
import json

app = Flask(__name__)

SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']  # Definido no docker-compose.yml
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

# Configuração boto3
sqs_client = boto3.client('sqs', region_name=os.environ['AWS_REGION'],
                   aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                   aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])


# Cliente DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

table = dynamodb.Table(DYNAMODB_TABLE_NAME)

@app.route('/')
def index():
    # Buscar os 10 nomes mais recentes
    response = table.scan()
    items = response.get('Items', [])
    items.sort(key=lambda x: x['timestamp'], reverse=True)
    names = [item['name'] for item in items]
    count = len(items)
    return render_template('index.html', names=names, count=count)

@app.route('/generate', methods=['POST'])
def generate():
    faker = Faker('pt_BR')
    new_name = faker.name()
    print(f"[APP] Gerado nome: {new_name}")

    response = sqs_client.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps({'name': new_name})
    )
    print(f"[APP] Mensagem enviada para SQS: {response}")

    return jsonify({'generated_name': new_name})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
