# DFA Simulator for CSET302

An editable complete DFA simulator with a simple browser UI, string testing, replayable traces, three presets, and twelve demonstration tests with downloadable expected/actual CSV results.

## Run locally

Requires Python 3.10+ and a current browser. No npm or pip dependencies are needed to use the site.

```bash
python3 -m http.server 8000
```

Open http://localhost:8000. Keep the terminal running. ES modules require HTTP; do not open index.html directly.

## One quick test

Select **Even number of 1s**, enter **1010** and click **Run simulation**.
Expected: **ACCEPTED**, trace **q0 → q1 → q1 → q0 → q0**.
Also try 111 (REJECTED), blank input (ACCEPTED), and 102 (INVALID INPUT at position 3).
Click Reset trace and Next transition to replay. Run demonstration tests: expected **12 / 12 passed**.

For a custom DFA, change fields, click Build transition table after editing state count/alphabet, then enter destinations. Rebuilding resets transitions to self-loops. Final states are comma-separated; blank means no accepting states. Setting a destination to 9 in a two-state machine must produce a validation error.

## Deploy through GitHub and Vercel

Create a repository named cset302-dfa-simulator and push this folder. Import it into Vercel. Framework: Other. Build: npm run build. Output: dist. Node.js 22+. No environment variables or external npm packages. vercel.json declares these settings.

Status: prepared and verified locally; no live GitHub repository or Vercel URL was created. The connected Humanplant scope refused Vercel project creation. GitHub creation requires completion of authentication.

## Input contract

Browser: 1–12 states numbered from zero; 1–94 unique printable ASCII alphabet symbols without spaces; one destination per state/symbol pair; valid start; distinct final states; input at most 2000 UTF-16 code units with no newline or NUL. Missing transitions are errors, with no implicit trap state. Unknown input symbols yield INVALID INPUT. Empty input is accepted exactly when the start state is accepting.

Presets: even number of ones, contains substring 11, binary divisible by three. Divisibility uses the remainder-zero prefix convention: leading zeros and epsilon are accepted. Nonempty numerals require a separate nonaccepting start state.

## Source map and API

- index.html: entry point, editing, results, trace replay and CSV export. User values use textContent.
- dfa.js: validate(data) throws Error for malformed definitions; simulate(data) returns status, ordered steps and a readable log. Both are documented with JSDoc.
- demo-cases.js: presets and 12 hand-derived expected outcomes.
- build.mjs, package.json, vercel.json: dependency-free build and hosting settings; only three browser assets go into dist.
- test_browser.mjs: independent language predicates, exact traces, validation, boundary cases and C++ agreement.
- dfa_simulator.cpp: retained C++17 console engine; original_dfa_simulator.cpp is the baseline.
- app.py: optional local launcher and legacy C++ HTTP bridge. The current browser UI runs JavaScript and does not call this API.
- test_simulator.py, test_web.py: C++ checks and legacy HTTP integration tests.
- test_results.csv, evidence/: recorded expected/actual results, execution logs and browser evidence.
- DFA_Simulator_Technical_Report.docx and .pdf: current report.
- FRONTEND_GUIDE.md: demonstration and viva preparation.

## Verify

Requires Node.js 22+, Python 3.10+ and g++ with C++17 support.

```bash
npm test
npm run lint
npm run build
python3 test_simulator.py
python3 -m unittest test_web -v
```

Recorded: 9 Node test groups passed, including all 1533 binary inputs through length eight across three presets and agreement with C++; 1562 C++ checks passed; 7 legacy HTTP integration tests passed. Browser interaction checks confirmed four outcomes, replay, presets, invalid destinations and the 12-case suite. These suites overlap; do not add their counts as unique independent tests. Lint means JavaScript syntax checking.

## C++ version

```bash
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror dfa_simulator.cpp -o dfa_simulator
./dfa_simulator < demo_input.txt
```

C++ supports up to 1000 states. Optional python3 app.py serves the UI and retains POST /api/simulate for C++ comparison tests. The web deployment serves static assets and needs no backend.

## Complexity and limits

Simulation O(L), stored trace O(L), table O(SA). No NFA conversion, minimization, regex conversion, PDA, Turing machine or persistent history. Tests verify the interpreter and selected languages, not every arbitrary language definition. No third-party runtime libraries are used.

## Team and attribution

Twinkle Sahu (S24CSEU0090), Tulsi Sanskrati Tomar (S24CSEU0084), Abhay Raj Verma, Divey Grover and Arnav Tomar. Complete the remaining enrollment numbers, group ID, faculty name and actual contributions before submission. Reused C++ and initial UI come from the earlier DFA_Simulator_Project package. Report format follows the supplied CSET302 Milestone-II guide.
