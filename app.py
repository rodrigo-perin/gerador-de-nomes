from flask import Flask, render_template, redirect, url_for, send_from_directory
import redis
import os
import random
from faker import Faker

app = Flask(__name__)
redis_client = redis.Redis(host='redis-service', port=6379, decode_responses=True)
faker = Faker('pt_BR')

@app.route('/')
def index():
    generated_names = [faker.name() for _ in range(30)]
    
    if generated_names: 
        new_name = random.choice(generated_names)
    else:
        new_name = "Nome Padrão"

    print(f"Gerando nomes: {generated_names}")
    print(f"### Nome selecionado para gravação: {new_name}")

    redis_client.lpush('names', new_name)
    
    names = redis_client.lrange('names', 0, 9)
    count = redis_client.llen('names')
    
    return render_template('index.html', names=names, count=count)

@app.route('/style.css')
def serve_css():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'style.css')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
