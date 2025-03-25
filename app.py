from flask import Flask, render_template, redirect, url_for, send_from_directory
import redis
import os
from faker import Faker

app = Flask(__name__)
redis_client = redis.Redis(host='redis-service', port=6379, decode_responses=True)
faker = Faker('pt_BR')

@app.route('/')
def index():
    new_name = faker.name()  # Gera um nome aleatório
    redis_client.lpush('names', new_name)  # Adiciona ao Redis
    redis_client.ltrim('names', 0, 9)  # Mantém apenas os últimos 10 nomes
    names = redis_client.lrange('names', 0, 9)  # Obtém os últimos 10 nomes
    return render_template('index.html', names=names)

# Rota para servir o CSS diretamente da pasta templates
@app.route('/style.css')
def serve_css():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'style.css')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
