"""Integration checks for the browser to C++ bridge using the standard library."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import Handler, ThreadingHTTPServer, make_input, simulate

MODEL = {"n": 2, "alphabet": "01", "transitions": [[0, 1], [1, 0]],
         "start": 0, "finals": [0], "input": "1010"}


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.directory.name) / "dfa"
        subprocess.run([shutil.which("g++") or "clang++", "-std=c++17", "-Wall",
                        "-Wextra", "-Wpedantic", "-Werror", "dfa_simulator.cpp",
                        "-o", str(cls.binary)], check=True, cwd=Path(__file__).parent)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.server.binary = cls.binary
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.directory.cleanup()

    def test_cpp_results_and_trace(self):
        for word, status in [("1010", "ACCEPTED"), ("111", "REJECTED"),
                             ("", "ACCEPTED"), ("102", "INVALID INPUT")]:
            with self.subTest(word=word):
                model = dict(MODEL, input=word)
                self.assertEqual(simulate(model, self.binary)["status"], status)
        steps = simulate(MODEL, self.binary)["steps"]
        self.assertEqual([step["to"] for step in steps], [1, 1, 0, 0])

    def test_invalid_boundary(self):
        changes = [{"n": True}, {"n": 13}, {"alphabet": "00"},
                   {"transitions": [[9, 1], [1, 0]]}, {"transitions": [[0]]},
                   {"start": -1}, {"finals": [0, 0]}, {"input": "a\nn\n"},
                   {"input": "0" * 2001}, {"finals": ["0"]}]
        for change in changes:
            with self.subTest(change=change):
                model = copy.deepcopy(MODEL)
                model.update(change)
                with self.assertRaises(ValueError):
                    make_input(model)

    def test_page(self):
        with urlopen(self.url) as response:
            self.assertIn(b"DFA Simulator", response.read())

    def test_http_simulation(self):
        req = Request(self.url + "/api/simulate", data=json.dumps(MODEL).encode(),
                      headers={"Content-Type": "application/json", "Origin": self.url})
        with urlopen(req) as response:
            self.assertEqual(json.load(response)["status"], "ACCEPTED")

    def test_bad_json(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(self.url + "/api/simulate", data=b"{"))
        self.assertEqual(caught.exception.code, 400)

    def test_cross_origin(self):
        req = Request(self.url + "/api/simulate", data=b"{}", headers={"Origin": "http://example.com"})
        with self.assertRaises(HTTPError) as caught:
            urlopen(req)
        self.assertEqual(caught.exception.code, 403)

    def test_missing_route(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.url + "/missing")
        self.assertEqual(caught.exception.code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
