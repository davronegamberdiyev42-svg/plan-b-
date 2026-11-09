import assert from 'node:assert/strict';
import { buildBackupEnvelope, verifyBackupEnvelope, inspectBackupEnvelope, mergeBackupState, BACKUP_MAX_BYTES } from '../assets/js/core/backup-engine.js';

const sample = { version: 2, day: 8, completed: { '1:reading': true }, scores: {}, drafts: { 'writing:1:task1': 'A preserved draft.' }, errors: [] };
const envelope = await buildBackupEnvelope(sample, { appVersion: '49.0.0', storageKey: 'ielts-boost-rebuilt-1.0' });
assert.equal(envelope.formatVersion, 2);
assert.equal(envelope.integrity.algorithm, 'SHA-256');
assert.match(envelope.integrity.sha256, /^[a-f0-9]{64}$/);
const verified = await verifyBackupEnvelope(JSON.parse(JSON.stringify(envelope)));
assert.equal(verified.valid, true);
assert.equal(verified.integrity, 'sha256-verified');
assert.equal(verified.state.drafts['writing:1:task1'], 'A preserved draft.');

const changed = JSON.parse(JSON.stringify(envelope));
changed.state.day = 9;
assert.equal((await verifyBackupEnvelope(changed)).valid, false, 'tampered backup must be rejected');

const unsafe = JSON.parse(JSON.stringify(envelope));
unsafe.state = JSON.parse('{"completed":{},"scores":{},"drafts":{},"__proto__":{"polluted":true}}');
assert.equal(inspectBackupEnvelope(unsafe).valid, false, 'prototype-sensitive keys must be rejected');

const tooDeep = JSON.parse(JSON.stringify(envelope));
let cursor = tooDeep.state;
for (let i = 0; i < 45; i++) { cursor.nested = {}; cursor = cursor.nested; }
assert.equal(inspectBackupEnvelope(tooDeep).valid, false, 'excessive nesting must be rejected');

const invalidShape = { app: 'IELTS Boost', state: { completed: {}, scores: {} } };
assert.equal(inspectBackupEnvelope(invalidShape).valid, false, 'missing drafts map must be rejected');

const legacy = { app: 'IELTS Boost Rebuilt', version: '48.0.0', state: sample };
const legacyResult = await verifyBackupEnvelope(legacy);
assert.equal(legacyResult.valid, true, 'legacy backups remain importable after shape validation');
assert.equal(legacyResult.integrity, 'legacy-unchecksummed');
assert.equal(BACKUP_MAX_BYTES, 40 * 1024 * 1024);
const merged = mergeBackupState({ settings: { theme: 'dark', language: 'uz' }, scores: {}, newFeature: true }, { settings: { theme: 'light' }, scores: { '1:reading': 8 } });
assert.deepEqual(merged, { settings: { theme: 'light', language: 'uz' }, scores: { '1:reading': 8 }, newFeature: true }, 'older backup import must preserve newer default keys');

console.log('STAGE 49 BACKUP ENGINE TESTS: 10/10 PASS');
