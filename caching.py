import argparse
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json
import threading

CACHE = {}
cache_lock = threading.Lock()

def get_cache_key(origin_url, path):
    if origin_url.endswith('/'):
        origin_url = origin_url[:-1]

    return f"{origin_url}{path}"

def clear_cache():
    global CACHE
    with cache_lock:
        CACHE = {}
    print("\nCache telah berhasil dibersihkan.")

class CachingProxyHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.origin_url = server.origin_url
        super().__init__(request, client_address, server)

    def do_request(self):
        cache_key = get_cache_key(self.origin_url, self.path)

        with cache_lock:
            cached_response = CACHE.get(cache_key)

        if cached_response:
            print(f"[{self.command}] {self.path} -> HIT (Served from Cache)")
            
            self.send_response(cached_response['status_code'])
            self.send_header('X-Cache', 'HIT')

            for key, value in cached_response['headers'].items():
                if key.lower() not in ['content-encoding', 'transfer-encoding']:
                    self.send_header(key, value)

            self.end_headers()
            self.wfile.write(cached_response['content'])
            return
        
        print(f"[{self.command}] {self.path} -> MISS (Forwarding to Origin: {cache_key})")

        try:
            origin_full_url = cache_key
            headers_to_send = {
                k: v for k, v in self.headers.items()
                if k.lower() not in ['host', 'accept-encoding', 'connection']
            }

            content_length = int(self.headers.get('content-length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None

            origin_response = requests.request(
                method=self.command,
                url=origin_full_url,
                headers=headers_to_send,
                data=request_body,
                allow_redirects=False,
                stream=True
            )

            response_content = origin_response.content
            self.send_response(origin_response.status_code)
            
            self.send_header('X-Cache', 'MISS') 
            
            response_headers_for_cache = {}
            for key, value in origin_response.headers.items():
                self.send_header(key, value)
                response_headers_for_cache[key] = value

            self.end_headers()
            self.wfile.write(response_content)

            if self.command == 'GET' and origin_response.status_code == 200:
                with cache_lock:
                    CACHE[cache_key] = {
                        'status_code': origin_response.status_code,
                        'headers': response_headers_for_cache,
                        'content': response_content
                    }
                print(f"   -> Cached response for {self.path}")

        except requests.exceptions.RequestException as e:
            print(f"   -> ERROR: Failed to forward request to origin: {e}")
            self.send_error(503, f"Could not connect to origin server: {self.origin_url}")

    do_GET = do_request
    do_POST = do_request
    do_PUT = do_request
    do_DELETE = do_request
    do_HEAD = do_request
    do_OPTIONS = do_request

class ProxyServer (HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, origin_url):
        self.origin_url = origin_url
        super().__init__(server_address, RequestHandlerClass)

def main():
    parser = argparse.ArgumentParser(description='Caching Proxy Server CLI Tool')

    parser.add_argument('--port', type=int, help='Port on which the caching proxy server will run.')
    parser.add_argument('--origin', type=str, help='URL of the server to which the requests will be forwarded (e.g., http://dummyjson.com).')
    parser.add_argument('--clear-cache', action='store_true', help='Clear the existing cache and exit.')

    args = parser.parse_args()

    if args.clear_cache:
        clear_cache()
        sys.exit(0)

    if args.port is None or args.origin is None:
        if args.clear_cache is False:
            parser.error("The --port and --origin arguments are required to start the server.")

    port = args.port
    origin = args.origin

    server_address = ('', port)

    httpd = ProxyServer(server_address, CachingProxyHandler, origin)

    print(f"Starting Caching Proxy on http://localhost:{port}")
    print(f"Origin server set to: {origin}")
    print("Press Ctrl+C to stop the server.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    main()