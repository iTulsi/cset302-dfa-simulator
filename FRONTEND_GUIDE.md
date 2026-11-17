# DFA Simulator demonstration

Run python3 -m http.server 8000 in this folder. Open http://localhost:8000.

1. Default Even number of 1s: q0 is even and accepting; q1 is odd. Zero preserves parity; one switches it.
2. Run 1010: ACCEPTED. Reset trace and step four times: q0 → q1 → q1 → q0 → q0.
3. Run 111: REJECTED at q1.
4. Clear input: ACCEPTED at q0, zero transitions. Blank input means epsilon.
5. Run 102: INVALID INPUT, position 3. Show View simulation log.
6. Set a destination to 9: validation error. Reload a preset to restore it.
7. Contains substring 11 with 0110: ACCEPTED at q2. Binary divisible by 3 with 110: ACCEPTED at q0.
8. Run demonstration tests: 12 / 12 passed. Download the expected/actual CSV.

## Explain it

M = (Q, Sigma, delta, q0, F). Each symbol selects one table column in the current state's row. Update current, then check membership in F after all symbols. Invariant: current = delta*(q0, processed prefix). Epsilon leaves current at q0.

dfa.js implements the browser algorithm; index.html presents results. The original C++ version is retained and cross-checked. Vercel serves static files; no C++ runs on web requests. Complexity: O(L) time, O(L) trace memory, O(SA) table storage. Reset and Next replay the stored trace; the result card shows the complete decision.

## Viva questions

- Determinism: one destination for every state/symbol pair.
- Why acceptance at the end: accepting a prefix does not guarantee acceptance of the full string.
- Missing transition: configuration error; no implicit trap state.
- No final states: all valid strings reject.
- Unknown symbol: invalid input, distinct from valid language rejection.
- Nonzero start: supported; each run resets to it.
- Divisible-by-three epsilon: accepted under the remainder-prefix convention; nonempty numerals need a different start state.
- Correctness: the interpreter follows the definition; the table still needs to represent the intended language.

Confirm actual member contributions, group ID, faculty name and three missing enrollment numbers before submission.
