from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import json
from datetime import datetime

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/':
            self.send_html('index.html')
        elif url.path == '/message':
            self.send_html('message.html')
        elif url.path == '/style.css':
            self.send_static('style.css')
        elif url.path == '/logo.png':
            self.send_static('logo.png')
        else:
            self.send_html('error.html')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)
        
        if self.path == '/submit':
            self.handle_form_submission(form_data)
            self.send_response(302)
            self.send_header('Location', '/message')
            self.end_headers()
        else:
            self.send_error(404, 'Not Found')

    def send_html(self, html_filename):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(html_filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_static(self, static_filename):
        self.send_response(200)
        if static_filename.endswith('.css'):
            self.send_header('Content-type', 'text/css')
        elif static_filename.endswith('.png'):
            self.send_header('Content-type', 'image/png')
        self.end_headers()
        with open(static_filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f'<h1>{code} - {message}</h1>'.encode())

    def handle_form_submission(self, form_data):
        if 'username' in form_data and 'message' in form_data:
            username = form_data['username'][0]
            message = form_data['message'][0]
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            data = {
                timestamp: {
                    'username': username,
                    'message': message
                }
            }
            
            self.save_to_json(data)
        else:
            self.send_error(400, 'Bad Request')

    def save_to_json(self, data):
        storage_dir = 'storage'
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        json_filename = os.path.join(storage_dir, 'data.json')
        with open(json_filename, 'a+') as json_file:
            json.dump(data, json_file, indent=4)
            json_file.write('\n')

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    httpd = server_class(server_address, handler_class)
    print('Starting HTTP server on port 3000...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()