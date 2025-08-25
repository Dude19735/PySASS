from http.server import BaseHTTPRequestHandler, HTTPServer

# class CORSHandler(BaseHTTPRequestHandler):
#     def send_response(self, *args, **kwargs):
#         BaseHTTPRequestHandler.send_response(self, *args, **kwargs)
#         self.send_header('Access-Control-Allow-Origin', '*')
#         self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
#         self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                ff = 'sql-des.html'
            else:
                ff = self.path
                if ff.startswith('/'):
                    ff = '.' + ff
                else:
                    ff = './' + ff
            with open(ff, 'rb') as file:
                self.send_response(200)
                # self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
                if ff.endswith('.html'):
                    self.send_header('Content-type', 'text/html')
                elif ff.endswith('.js'):
                    self.send_header('Content-type', 'text/javascript')
                elif ff.endswith('.wasm'):
                    self.send_header('Content-type', 'application/wasm')
                else: raise Exception("Unkonwn extension")
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "File Not Found")

def run(server_class=HTTPServer, handler_class=SimpleHandler, port=8200):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
