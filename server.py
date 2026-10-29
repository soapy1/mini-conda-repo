import base64
import os
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configure your credentials here
USERNAME = "admin"
PASSWORD = "password123"

# Set MCR_NO_AUTH to any non-empty value to disable authentication
NO_AUTH = bool(os.environ.get("MCR_NO_AUTH"))

# Directory to serve, relative to this file
CLASSIC_REPO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mini-conda-repo"
)
SHARDED_REPO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mini-sharded-conda-repo"
)


class AuthHandler(SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        """Sends a 401 Unauthorized status code and the WWW-Authenticate header."""
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Protected Area"')
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Authentication required.")

    def check_auth(self):
        """Validates the Authorization header against your credentials."""
        if NO_AUTH:
            return True

        auth_header = self.headers.get("Authorization")

        if auth_header is None:
            self.do_AUTHHEAD()
            return False

        # Expecting 'Basic <base64_encoded_credentials>'
        if not auth_header.startswith("Basic "):
            self.do_AUTHHEAD()
            return False

        try:
            # Extract and decode the base64 token
            encoded_credentials = auth_header.split(" ")[1]
            decoded_bytes = base64.b64decode(encoded_credentials)
            decoded_str = decoded_bytes.decode("utf-8")

            # Validate format and actual credentials
            user, pwd = decoded_str.split(":", 1)
            if user == USERNAME and pwd == PASSWORD:
                return True
        except Exception:
            pass

        # Fallback if parsing fails or credentials are wrong
        self.do_AUTHHEAD()
        return False

    def do_GET(self):
        """Intercepts GET requests to verify authentication."""
        if self.check_auth():
            super().do_GET()

    def do_HEAD(self):
        """Intercepts HEAD requests to verify authentication."""
        if self.check_auth():
            super().do_HEAD()

    def do_POST(self):
        """Intercepts POST requests to verify authentication."""
        if self.check_auth():
            super().do_POST()


def run(port=8000):
    server_address = ("", port)

    serve_dir = CLASSIC_REPO
    if bool(os.environ.get("MCR_SHARDED")):
        serve_dir = SHARDED_REPO

    handler = partial(AuthHandler, directory=serve_dir)
    httpd = HTTPServer(server_address, handler)
    auth_status = "disabled" if NO_AUTH else "enabled"
    print(
        f"Serving {serve_dir} over HTTP on port {port} with Basic Auth {auth_status}..."
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    run()
