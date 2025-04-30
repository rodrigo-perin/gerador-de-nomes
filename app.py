import boto3
import os
from flask import Flask, render_template, request, send_from_directory, jsonify
from faker import Faker
import json

app = Flask(__name__)

SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

sqs_client = boto3.client('sqs', region_name=os.environ['AWS_REGION'],
                   aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                   aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

try:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
except Exception as e:
    print(f"[APP] Erro ao inicializar DynamoDB: {e}")
    table = None

@app.route('/')
def index():
    names = []
    count = 0

    if table:
        try:
            response = table.scan()
            items = response.get('Items', [])
            items.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            names = [item['name'] for item in items]
            count = len(items)
        except botocore.exceptions.ClientError as e:
            print(f"[APP] Erro ao acessar o DynamoDB: {e}")
        except Exception as e:
            print(f"[APP] Erro inesperado: {e}")
    else:
        print("[APP] Tabela DynamoDB não inicializada.")

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
