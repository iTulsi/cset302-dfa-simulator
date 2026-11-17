/** Demonstration fixtures with hand-derived expected outcomes. Blank input is epsilon. */
export const machines = {
  parity: {n: 2, alphabet: '01', transitions: [[0, 1], [1, 0]], start: 0, finals: [0]},
  substring: {n: 3, alphabet: '01', transitions: [[0, 1], [0, 2], [2, 2]], start: 0, finals: [2]},
  divisible: {n: 3, alphabet: '01', transitions: [[0, 1], [2, 0], [1, 2]], start: 0, finals: [0]},
};

export const demoCases = [
  {id: 'T01', machine: 'parity', input: '1010', expected: 'ACCEPTED'},
  {id: 'T02', machine: 'parity', input: '111', expected: 'REJECTED'},
  {id: 'T03', machine: 'parity', input: '', expected: 'ACCEPTED'},
  {id: 'T04', machine: 'parity', input: '102', expected: 'INVALID INPUT'},
  {id: 'T05', machine: 'substring', input: '0110', expected: 'ACCEPTED'},
  {id: 'T06', machine: 'substring', input: '1010', expected: 'REJECTED'},
  {id: 'T07', machine: 'substring', input: '', expected: 'REJECTED'},
  {id: 'T08', machine: 'divisible', input: '110', expected: 'ACCEPTED'},
  {id: 'T09', machine: 'divisible', input: '101', expected: 'REJECTED'},
  {id: 'T10', machine: 'divisible', input: '000', expected: 'ACCEPTED'},
  {id: 'T11', machine: 'divisible', input: '', expected: 'ACCEPTED'},
  {id: 'T12', machine: 'parity', input: '0 1', expected: 'INVALID INPUT'},
];
