"""Black-box tests with independent language predicates; Python standard library only."""
import csv
import itertools
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def definition(table, finals, alphabet="01", start=0):
    values = [len(table), alphabet]
    values.extend(value for row in table for value in row)
    values.extend([start, len(finals), *finals])
    return "\n".join(map(str, values)) + "\n"


def run_tests():
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        binary = str(Path(directory) / "dfa_simulator")
        subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
                        "-Werror", str(ROOT / "dfa_simulator.cpp"), "-o", binary], check=True)

        def execute(data):
            return subprocess.run([binary], input=data, text=True, capture_output=True, timeout=10)

        def check(name, expected, actual):
            rows.append([name, expected, actual, "PASS" if expected == actual else "FAIL"])

        words = ["".join(bits) for length in range(9)
                 for bits in itertools.product("01", repeat=length)]
        models = [
            ("even number of ones", [[0, 1], [1, 0]], [0], lambda s: s.count("1") % 2 == 0),
            ("contains 11", [[0, 1], [0, 2], [2, 2]], [2], lambda s: "11" in s),
            ("binary divisible by 3", [[0, 1], [2, 0], [1, 2]], [0],
             lambda s: int(s or "0", 2) % 3 == 0),
        ]
        for name, table, finals, predicate in models:
            payload = definition(table, finals) + "\ny\n".join(words) + "\nn\n"
            result = execute(payload)
            assert result.returncode == 0, result.stderr
            actual = re.findall(r"Result: ([A-Z ]+)", result.stdout)
            assert len(actual) == len(words)
            for word, observed in zip(words, actual):
                check(name + ": " + (word or "epsilon"),
                      "ACCEPTED" if predicate(word) else "REJECTED", observed)

        focused = [
            ("empty final set", definition([[0, 0]], []), "", "REJECTED"),
            ("all final states", definition([[0, 0]], [0]), "101", "ACCEPTED"),
            ("nonzero start state", definition([[0, 0], [1, 1]], [1], start=1), "", "ACCEPTED"),
            ("alphabet ab", definition([[0, 1], [1, 1]], [1], "ab"), "aab", "ACCEPTED"),
            ("invalid symbol", definition([[0, 0]], [0]), "102", "INVALID INPUT"),
            ("space in input", definition([[0, 0]], [0]), "0 1", "INVALID INPUT"),
            ("UTF8 outside alphabet", definition([[0, 0]], [0]), "é", "INVALID INPUT"),
            ("long input", definition([[0, 1], [1, 0]], [0]), "1" * 10000, "ACCEPTED"),
        ]
        for name, config, word, expected in focused:
            result = execute(config + word + "\nn\n")
            assert result.returncode == 0
            check(name, expected, re.findall(r"Result: ([A-Z ]+)", result.stdout)[0])

        invalid = ["0\n", "-1\n", "1001\n", "abc\n", "2abc\n", "2 3\n",
                   "99999999999999999999999999\n", "1\n\n", "1\n00\n",
                   "1\n0 1\n", "1\né\n", "1\n01\n1\n", "1\n01\n-1\n",
                   "1\n01\n0\n0\n1\n", "1\n01\n0\n0\n0\n2\n",
                   "1\n01\n0\n0\n0\n1\n1\n",
                   "2\n01\n0\n0\n0\n0\n0\n2\n0\n0\n", "2\n01\n",
                   definition([[0, 0]], [0]) + "\nmaybe\n", ""]
        for index, payload in enumerate(invalid, 1):
            result = execute(payload)
            check(f"malformed configuration or session {index}", "error exit with diagnostic",
                  "error exit with diagnostic" if result.returncode == 1 and
                  "Configuration/input error:" in result.stderr else "unexpected behavior")

        evidence = ROOT / "evidence"
        evidence.mkdir(exist_ok=True)
        demo = definition([[0, 1], [1, 0]], [0]) + "1010\ny\n111\ny\n\ny\n102\nn\n"
        (ROOT / "demo_input.txt").write_text(demo)
        result = execute(demo)
        (evidence / "demo_output.txt").write_text(result.stdout + result.stderr)
        expected_trace = "q0 --1--> q1\nq1 --0--> q1\nq1 --1--> q0\nq0 --0--> q0"
        check("ordered transition trace", "correct trace",
              "correct trace" if expected_trace in result.stdout else "wrong trace")

    with (ROOT / "test_results.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Test", "Expected", "Actual", "Status"])
        writer.writerows(rows)
    failed = [row for row in rows if row[-1] == "FAIL"]
    summary = f"{len(rows)} checks: {len(rows) - len(failed)} passed, {len(failed)} failed.\n"
    (ROOT / "evidence" / "test_summary.txt").write_text(summary)
    print(summary, end="")
    assert not failed, failed


if __name__ == "__main__":
    run_tests()
