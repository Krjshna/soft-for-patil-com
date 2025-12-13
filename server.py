import http.server
import socketserver
import webbrowser
import os
import time
import threading
import socket
import json

# Define the port you want to use
PORT = 8000
# The directory to serve (current directory)
DIRECTORY = "."
DB_FILE = "inventory_data.json"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Handle API request to get database data
        if self.path == '/api/db':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Allow all origins
            self.end_headers()
            
            if os.path.exists(DB_FILE):
                try:
                    with open(DB_FILE, 'rb') as f:
                        self.wfile.write(f.read())
                except Exception as e:
                    self.wfile.write(b'{}')
            else:
                self.wfile.write(b'{}')
        else:
            # Standard file serving
            super().do_GET()

    def do_POST(self):
        # Handle API request to save database data
        if self.path == '/api/db':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Write to file
                with open(DB_FILE, 'wb') as f:
                    f.write(post_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"ok", "message": "Data saved"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"Error saving data: {e}")
        else:
            super().do_POST()

    def do_OPTIONS(self):
        # Handle preflight CORS check
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def open_browser():
    time.sleep(1)
    url = f"http://localhost:{PORT}/index.html"
    print(f"Opening browser on host machine at {url}...")
    webbrowser.open(url)

if __name__ == "__main__":
    local_ip = get_local_ip()

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        
        print("=" * 60)
        print(f" LIVE SERVER STARTED (WITH LOCAL DATABASE)")
        print("=" * 60)
        print(f" -> Local Access (This PC):   http://localhost:{PORT}")
        print(f" -> Network Access (Mobile):  http://{local_ip}:{PORT}")
        print("=" * 60)
        print(" Instructions:")
        print(" 1. Ensure 'index.html' is in the same folder as this script.")
        print(f" 2. On Mobile, go to: http://{local_ip}:{PORT}")
        print(" 3. Data will now sync automatically between devices.")
        print("=" * 60)
        print("Press Ctrl+C to stop the server.")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")