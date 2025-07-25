import http.server
import socketserver
import urllib.request
import os

PORT = 8000

class DirectoryListingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Generate a simple HTML page with buttons for directories
            dirs = [name for name in os.listdir('.') if os.path.isdir(name)]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # HTML content
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Directory Buttons</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        grid-gap: 20px;
                        align-items: stretch;
                    }
                    button {
                        padding: 40px;
                        font-size: 1.2em;
                        cursor: pointer;
                        border: none;
                        border-radius: 8px;
                        background-color: #4CAF50;
                        color: white;
                        transition: background-color 0.3s ease;
                        width: 100%;
                        height: 100%;
                    }
                    button:hover {
                        background-color: #45a049;
                    }
                </style>
            </head>
            <body>
            """

            for d in dirs:
                # Button opens directory URL
                html += f'<button onclick="location.href=\'/{d}/\'">{d}</button>\n'

            html += """
            </body>
            </html>
            """

            self.wfile.write(html.encode('utf-8'))

        else:
            # Fallback to default handler for other paths/files
            super().do_GET()

import socket
import sys

def is_port_in_use(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            s.listen(1)
            return False  # Port is free
        except OSError:
            return True  # Port is in use

if is_port_in_use(PORT):
    print(f"[ERROR] Another instance is already running on port {PORT}.")
    sys.exit(1)
else:
    print(f"[INFO] Port {PORT} is free. Starting server...")
    with socketserver.TCPServer(("", PORT), DirectoryListingHandler) as httpd:
        print(f"Serving on http://localhost:{PORT}")
        httpd.serve_forever()