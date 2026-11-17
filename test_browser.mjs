import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, mkdtempSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {simulate} from './dfa.js';
import {machines, demoCases} from './demo-cases.js';

test('all twelve hand-worked demonstration cases', () => {
  for (const item of demoCases) assert.equal(simulate({...machines[item.machine], input: item.input}).status, item.expected, item.id);
});

const words = [''];
for (let length = 1; length <= 8; length++) {
  for (let value = 0; value < 2 ** length; value++) words.push(value.toString(2).padStart(length, '0'));
}
const predicates = {
  parity: word => [...word].filter(symbol => symbol === '1').length % 2 === 0,
  substring: word => word.includes('11'),
  divisible: word => parseInt(word || '0', 2) % 3 === 0,
};

for (const [name, machine] of Object.entries(machines)) {
  test(name + ': all 511 binary words through length eight', () => {
    for (const input of words) {
      const result = simulate({...machine, input});
      assert.equal(result.status, predicates[name](input) ? 'ACCEPTED' : 'REJECTED', input);
      assert.equal(result.steps.length, input.length);
      assert.equal(result.steps[0]?.from ?? machine.start, machine.start);
      for (let i = 0; i < result.steps.length; i++) {
        const step = result.steps[i];
        assert.equal(step.symbol, input[i]);
        assert.equal(step.to, machine.transitions[step.from][machine.alphabet.indexOf(step.symbol)]);
        if (i) assert.equal(step.from, result.steps[i - 1].to);
      }
    }
  });
}

test('browser decisions agree with original C++ on 1533 inputs', () => {
  const directory = mkdtempSync(join(tmpdir(), 'dfa-cross-check-'));
  try {
    const binary = join(directory, 'dfa');
    const compile = spawnSync('g++', ['-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror', 'dfa_simulator.cpp', '-o', binary], {encoding: 'utf8'});
    assert.equal(compile.status, 0, compile.stderr);
    for (const machine of Object.values(machines)) {
      const definition = [machine.n, machine.alphabet, ...machine.transitions.flat(), machine.start, machine.finals.length, ...machine.finals].join('\n') + '\n';
      const payload = definition + words.join('\ny\n') + '\nn\n';
      const cpp = spawnSync(binary, [], {input: payload, encoding: 'utf8', maxBuffer: 5_000_000, timeout: 10000});
      assert.equal(cpp.status, 0, cpp.stderr);
      const statuses = [...cpp.stdout.matchAll(/Result: ([A-Z ]+)/g)].map(match => match[1]);
      assert.equal(statuses.length, words.length);
      for (let i = 0; i < words.length; i++) assert.equal(statuses[i], simulate({...machine, input: words[i]}).status);
    }
  } finally { rmSync(directory, {recursive: true, force: true}); }
});

test('malformed definitions fail explicitly', () => {
  const original = {...machines.parity, input: '1010'};
  const changes = [{n: true}, {n: 0}, {n: 13}, {n: 1.5}, {alphabet: ''}, {alphabet: '00'},
    {alphabet: '0 1'}, {alphabet: 'é'}, {transitions: [[0]]}, {transitions: [[9, 1], [1, 0]]},
    {transitions: [[null, 1], [1, 0]]}, {start: -1}, {start: 2}, {start: true},
    {finals: [0, 0]}, {finals: ['0']}, {finals: [2]}, {input: 'x\ny'}, {input: '\0'}, {input: '0'.repeat(2001)}, {input: null}];
  for (const change of changes) assert.throws(() => simulate({...original, ...change}), Error, JSON.stringify(change));
  for (const value of [null, [], false]) assert.throws(() => simulate(value));
});

test('empty, custom, nonzero start, repeated runs and resource boundaries', () => {
  assert.equal(simulate({...machines.parity, finals: [], input: ''}).status, 'REJECTED');
  assert.equal(simulate({...machines.parity, finals: [0, 1], input: '1'}).status, 'ACCEPTED');
  assert.equal(simulate({...machines.parity, start: 1, input: ''}).status, 'REJECTED');
  assert.equal(simulate({n: 1, alphabet: 'ab', transitions: [[0, 0]], start: 0, finals: [0], input: 'abba'}).status, 'ACCEPTED');
  assert.equal(simulate({...machines.parity, input: '1'.repeat(2000)}).status, 'ACCEPTED');
  assert.equal(simulate({...machines.parity, input: '1'}).status, 'REJECTED');
  assert.equal(simulate({...machines.parity, input: ''}).status, 'ACCEPTED');
  assert.equal(simulate({...machines.parity, input: 'é'}).status, 'INVALID INPUT');
  const alphabet=Array.from({length:94},(_,i)=>String.fromCharCode(33+i)).join('');
  assert.equal(simulate({n:12,alphabet,transitions:Array.from({length:12},()=>Array(94).fill(11)),start:0,finals:[11],input:'~'}).status,'ACCEPTED');
});

test('exact trace and invalid symbol position', () => {
  assert.deepEqual(simulate({...machines.parity, input: '1010'}).steps, [
    {from: 0, symbol: '1', to: 1}, {from: 1, symbol: '0', to: 1},
    {from: 1, symbol: '1', to: 0}, {from: 0, symbol: '0', to: 0},
  ]);
  const invalid=simulate({...machines.parity, input: '102'});
  assert.equal(invalid.steps.length, 2);
  assert.match(invalid.output, /Invalid symbol at position 3/);
});

test('inline UI module parses without executing browser code', () => {
  const html=readFileSync('index.html','utf8');
  const script=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
  const checked=spawnSync(process.execPath,['--check','--input-type=module'],{input:script,encoding:'utf8'});
  assert.equal(checked.status,0,checked.stderr);
});
