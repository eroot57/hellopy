import http.server
import socketserver
from urllib.parse import urlparse

class HelloHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urlparse(self.path)
        
        # Check if it's the homepage
        if parsed_path.path == '/' or parsed_path.path == '':
            # Send response status code
            self.send_response(200)
            
            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Send the HTML content
            html_content = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Hello App</title>
            </head>
            <body>
                <h1>Hello</h1>
            </body>
            </html>
            '''
            self.wfile.write(html_content.encode('utf-8'))
        else:
            # Send 404 for other paths
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Page Not Found</h1>')
    
    def log_message(self, format, *args):
        # Override to customize log messages
        print(f"[{self.address_string()}] {format % args}")

if __name__ == '__main__':
    PORT = 8000
    
    # Create the server
    with socketserver.TCPServer(("", PORT), HelloHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.shutdown()
