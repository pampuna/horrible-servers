from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
            self.send_response(200)
            self.send_header('Server', None)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            query_components = parse_qs(urlparse(self.path).query)
            query = query_components.get('q', [''])[0]

            self.wfile.write(bytes("""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Search Results</title></head>
<body>
    <h1>Search Results</h1>
    <input id="demo type="text">
    """ + f"<p>Your search query: <span>{query}</span></p>" if query else "No search term (?q)" + """
</body>
</html>""", 'utf-8'))

if __name__ == '__main__':
    server_address = ('0.0.0.0', 80)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
