/**
 * A complete deterministic finite automaton. States are integers 0..n-1.
 * Each ASCII alphabet symbol indexes one column of the transition table.
 * @typedef {{n:number, alphabet:string, transitions:number[][], start:number,
 * finals:number[], input:string}} Definition
 */

/** Validate a complete browser DFA. Throws Error for malformed definitions. */
export function validate(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw Error('Expected a DFA object.');
  const {n, alphabet, transitions, start, finals, input} = data;
  if (!Number.isInteger(n) || n < 1 || n > 12) throw Error('Use 1 to 12 states.');
  if (typeof alphabet !== 'string' || alphabet.length > 94 || !/^[!-~]+$/.test(alphabet)
      || new Set(alphabet).size !== alphabet.length) {
    throw Error('Use distinct printable ASCII alphabet symbols without spaces.');
  }
  const state = value => Number.isInteger(value) && value >= 0 && value < n;
  if (!Array.isArray(transitions) || transitions.length !== n
      || transitions.some(row => !Array.isArray(row) || row.length !== alphabet.length || row.some(value => !state(value)))) {
    throw Error('Every state and symbol needs exactly one valid destination.');
  }
  if (!state(start)) throw Error('Start state is outside the DFA.');
  if (!Array.isArray(finals) || finals.some(value => !state(value)) || new Set(finals).size !== finals.length) {
    throw Error('Final states must be distinct valid states.');
  }
  if (typeof input !== 'string' || input.length > 2000 || /[\r\n\x00]/.test(input)) {
    throw Error('Use a single input line of at most 2000 characters.');
  }
}

/**
 * Evaluate delta*(start, input) in O(input length), retaining a transition trace.
 * Invalid symbols stop processing and return INVALID INPUT with a 1-based position.
 * Empty input performs no transition; acceptance depends on the start state.
 * @param {Definition} data
 * @returns {{status:string, steps:{from:number,symbol:string,to:number}[], output:string}}
 * @throws {Error} If the definition is malformed or exceeds the browser limits.
 */
export function simulate(data) {
  validate(data);
  const columns = new Map([...data.alphabet].map((symbol, index) => [symbol, index]));
  let current = data.start;
  const steps = [];
  const lines = ['Input: ' + (data.input || 'epsilon'), 'Start: q' + current];
  let status;
  for (let position = 0; position < data.input.length; position++) {
    const symbol = data.input[position];
    if (!columns.has(symbol)) {
      lines.push(`Invalid symbol at position ${position + 1}. Input is outside Sigma*.`);
      status = 'INVALID INPUT';
      break;
    }
    const next = data.transitions[current][columns.get(symbol)];
    steps.push({from: current, symbol, to: next});
    lines.push(`q${current} --${symbol}--> q${next}`);
    current = next;
  }
  if (!status) {
    status = data.finals.includes(current) ? 'ACCEPTED' : 'REJECTED';
    lines.push('Final state reached: q' + current);
  }
  lines.push('Result: ' + status);
  return {status, steps, output: lines.join('\n')};
}
