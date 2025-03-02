from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

dummy_data = [ 'example 1', 'item 2', 'something else 3' ]

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            query_components = parse_qs(urlparse(self.path).query)
            query = query_components.get('q', [''])[0]
            data = str.join('', [ f"<li class='list-group-item'>{item}</li>" for item in dummy_data if (query or '').lower() in item ])
            results = f"<ul class='list-group'>{data}</ul>" if len(data) > 0 else '<span>No search results</span>'
            self.wfile.write(bytes("""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>XSS Example Page</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body>
    <div class="container mt-4">
        <h1 class="text-center mb-4">XSS Example Page</h1>
        <form action="/" class="d-flex justify-content-center mb-4">
            <input id="q" name="q" type="text" class="form-control me-2" placeholder="Search..." value=\"""" + query + """\">
            <button type="submit" class="btn btn-primary">Search</button>
        </form>
        <br /><div id="results"><h2>Search results</h2>"""+results+"""</div>
    </div>
</body>
</html>""", 'utf-8'))

if __name__ == '__main__':
    server_address = ('0.0.0.0', 80)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    finally: httpd.server_close()
