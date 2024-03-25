from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import json
from datetime import datetime
import socket
import threading

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

            # Відправка відповіді клієнту з перенаправленням на сторінку message з параметром "success"
            self.send_response(302)
            self.send_header('Location', '/message?success')
            self.end_headers()
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

class SocketServerThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        UDP_IP = self.host
        UDP_PORT = self.port

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            data, addr = sock.recvfrom(1024)
            message = json.loads(data.decode('utf-8'))
            self.handle_message(message)

    def handle_message(self, message):
        if 'username' in message and 'message' in message:
            username = message['username']
            message_text = message['message']
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            data = {
                timestamp: {
                    'username': username,
                    'message': message_text
                }
            }
            
            HttpHandler().save_to_json(data)

def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    httpd = server_class(server_address, handler_class)
    print('Starting HTTP server on port 3000...')
    httpd.serve_forever()

def run_socket_server():
    server_thread = SocketServerThread('127.0.0.1', 5000)
    server_thread.start()

if __name__ == '__main__':
    run_http_server()
    run_socket_server()
