const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

function readSource() {
  return fs.readFileSync(path.resolve(__dirname, '../../assets/animations.jsx'), 'utf8');
}

test('Stage recording mode uses the full viewport instead of reserving preview controls space', () => {
  const source = readSource();

  assert.match(source, /const isRecording = typeof window !== 'undefined' && window\.__recording;/);
  assert.match(source, /const vh = window\.innerHeight - \(isRecording \? 0 : 56\);/);
});

test('Stage controls are marked as recorder-hidden chrome and omitted while recording', () => {
  const source = readSource();

  assert.match(source, /!\s*isRecording && \(/);
  assert.match(source, /className="no-record"/);
  assert.match(source, /data-role="chrome"/);
});
