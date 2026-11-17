"""Local browser interface for the existing C++ DFA simulator. No pip packages."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import webbrowser

ROOT = Path(__file__).resolve().parent


def make_input(data):
    """Validate the HTTP boundary, then serialize the existing console protocol."""
    if not isinstance(data, dict):
        raise ValueError("Expected a DFA object.")
    n, alphabet = data.get("n"), data.get("alphabet")
    if type(n) is not int or not 1 <= n <= 12:
        raise ValueError("Use 1 to 12 states in the browser demo.")
    if (not isinstance(alphabet, str) or not 1 <= len(alphabet) <= 94
            or len(set(alphabet)) != len(alphabet)
            or any(not 33 <= ord(c) <= 126 for c in alphabet)):
        raise ValueError("Use distinct printable ASCII alphabet symbols without spaces.")
    table, start, finals, word = (data.get(k) for k in ("transitions", "start", "finals", "input"))
    def state(x):
        return type(x) is int and 0 <= x < n
    if (not isinstance(table, list) or len(table) != n
            or any(not isinstance(row, list) or len(row) != len(alphabet)
                   or any(not state(x) for x in row) for row in table)):
        raise ValueError("Every state and symbol needs one valid destination.")
    if not state(start):
        raise ValueError("Start state is outside the DFA.")
    if (not isinstance(finals, list) or any(not state(x) for x in finals)
            or len(set(finals)) != len(finals)):
        raise ValueError("Final states must be distinct valid states.")
    if (not isinstance(word, str) or len(word) > 2000
            or any(c in word for c in "\r\n\x00")):
        raise ValueError("Use a single input line of at most 2000 characters.")
    values = [n, alphabet, *(x for row in table for x in row), start, len(finals), *finals, word, "n"]
    return "\n".join(map(str, values)) + "\n"


def simulate(data, binary):
    result = subprocess.run([str(binary)], input=make_input(data), text=True,
                            capture_output=True, timeout=5)
    if result.returncode:
        raise ValueError(result.stderr.strip())
    output = result.stdout.split("--- Simulation ---", 1)[1].split("Test another string?", 1)[0].strip()
    status = re.search(r"^Result: (.+)$", output, re.M)
    if status is None:
        raise RuntimeError("C++ simulator returned an unexpected response.")
    steps = [{"from": int(a), "symbol": b, "to": int(c)}
             for a, b, c in re.findall(r"^q(\d+) --(.)--> q(\d+)$", output, re.M)]
    return {"status": status[1], "steps": steps, "output": output}


class Handler(BaseHTTPRequestHandler):
    def send(self, status, content, content_type="application/json"):
        body = content if isinstance(content, bytes) else json.dumps(content).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path in ("/dfa.js", "/demo-cases.js"):
            self.send(200, (ROOT / self.path[1:]).read_bytes(), "text/javascript; charset=utf-8")
        else:
            self.send(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/simulate":
            self.send(404, {"error": "Not found"})
            return
        # The endpoint is only intended for its own local frontend.
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + self.headers.get("Host", ""):
            self.send(403, {"error": "Use the simulator's own browser page."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 100000:
                raise ValueError("Request size must be between 1 and 100000 bytes.")
            data = json.loads(self.rfile.read(length))
            self.send(200, simulate(data, self.server.binary))
        except (ValueError, UnicodeError) as error:
            self.send(400, {"error": str(error)})
        except (subprocess.TimeoutExpired, RuntimeError):
            self.send(500, {"error": "Simulation could not finish. Check the local terminal."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--strictPort", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        parser.exit(1, "Install a C++ compiler first. On macOS run: xcode-select --install\n")
    with tempfile.TemporaryDirectory(prefix="dfa-demo-") as directory:
        binary = Path(directory) / "dfa_simulator"
        subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                        str(ROOT / "dfa_simulator.cpp"), "-o", str(binary)], check=True)
        with ThreadingHTTPServer((args.host, args.port), Handler) as server:
            server.binary = binary
            print(f"DFA simulator running at http://{args.host}:{server.server_port}", flush=True)
            print("Press Ctrl+C to stop. The browser uses your compiled C++ simulator.", flush=True)
            if not args.no_browser:
                webbrowser.open(f"http://127.0.0.1:{server.server_port}")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
