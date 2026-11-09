/**
 * IELTS Boost Stage 49 — safe backup envelope and import validation.
 * This validates shape and integrity; it is not encryption or malware scanning.
 */
export const BACKUP_FORMAT_VERSION = 2;
export const BACKUP_MAX_BYTES = 40 * 1024 * 1024;
const FORBIDDEN_KEYS = new Set(['__proto__', 'prototype', 'constructor']);
const isRecord = value => !!value && typeof value === 'object' && !Array.isArray(value);

export function scanJsonTree(value, depth = 0, budget = { nodes: 0 }) {
  if (depth > 40) return { valid: false, reason: 'Backup nesting is too deep.' };
  budget.nodes += 1;
  if (budget.nodes > 500000) return { valid: false, reason: 'Backup contains too many values.' };
  if (typeof value === 'string' && value.length > 2_000_000) return { valid: false, reason: 'A single text field is too large.' };
  if (Array.isArray(value)) {
    if (value.length > 100000) return { valid: false, reason: 'A backup list is too large.' };
    for (const item of value) {
      const result = scanJsonTree(item, depth + 1, budget);
      if (!result.valid) return result;
    }
    return { valid: true, nodes: budget.nodes };
  }
  if (isRecord(value)) {
    for (const [key, child] of Object.entries(value)) {
      if (FORBIDDEN_KEYS.has(key)) return { valid: false, reason: `Unsafe object key rejected: ${key}` };
      const result = scanJsonTree(child, depth + 1, budget);
      if (!result.valid) return result;
    }
  }
  return { valid: true, nodes: budget.nodes };
}

export function mergeBackupState(defaultState, importedState) {
  const clone = value => Array.isArray(value) ? value.map(clone) : isRecord(value) ? Object.fromEntries(Object.entries(value).map(([key, child]) => [key, clone(child)])) : value;
  const merge = (base, incoming) => {
    if (incoming === undefined) return base;
    if (Array.isArray(incoming)) return clone(incoming);
    if (isRecord(base) && isRecord(incoming)) {
      const output = { ...base };
      for (const [key, value] of Object.entries(incoming)) {
        if (FORBIDDEN_KEYS.has(key)) throw new Error(`Unsafe object key rejected: ${key}`);
        output[key] = Object.prototype.hasOwnProperty.call(base, key)
          ? merge(base[key], value)
          : clone(value);
      }
      return output;
    }
    return incoming && typeof incoming === 'object' ? clone(incoming) : incoming;
  };
  return merge(defaultState, importedState);
}

export function inspectBackupEnvelope(payload) {
  if (!isRecord(payload) || !isRecord(payload.state)) {
    return { valid: false, reason: 'Backup format is invalid: state object is missing.' };
  }
  const tree = scanJsonTree(payload.state);
  if (!tree.valid) return tree;
  const state = payload.state;
  if (!isRecord(state.completed) || !isRecord(state.scores) || !isRecord(state.drafts)) {
    return { valid: false, reason: 'Backup is missing required progress structures (completed, scores, drafts).' };
  }
  if (state.errors !== undefined && !Array.isArray(state.errors)) {
    return { valid: false, reason: 'Backup error log has an invalid format.' };
  }
  if (state.day !== undefined && (!Number.isInteger(Number(state.day)) || Number(state.day) < 1 || Number(state.day) > 84)) {
    return { valid: false, reason: 'Selected day must be between 1 and 84.' };
  }
  return {
    valid: true,
    state: JSON.parse(JSON.stringify(state)),
    formatVersion: Number(payload.formatVersion) || 1,
    checksum: payload.integrity?.sha256 || null,
    legacy: !payload.integrity?.sha256,
    nodes: tree.nodes
  };
}

export async function sha256Hex(text, cryptoApi = globalThis.crypto) {
  if (!cryptoApi?.subtle || typeof TextEncoder === 'undefined') return null;
  const bytes = new TextEncoder().encode(text);
  const digest = await cryptoApi.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map(x => x.toString(16).padStart(2, '0')).join('');
}

export async function buildBackupEnvelope(state, metadata = {}, cryptoApi = globalThis.crypto) {
  const stateJson = JSON.stringify(state);
  const digest = await sha256Hex(stateJson, cryptoApi);
  return {
    app: 'IELTS Boost',
    formatVersion: BACKUP_FORMAT_VERSION,
    schema: 'ielts-boost-local-progress',
    exportedAt: new Date().toISOString(),
    metadata: {
      appVersion: metadata.appVersion || 'unknown',
      storageKey: metadata.storageKey || 'unknown',
      audioIncluded: false,
      audioNote: 'IndexedDB recordings are stored separately on this device; export them individually from Speaking Studio.',
      integrityAvailable: !!digest
    },
    integrity: digest ? { algorithm: 'SHA-256', sha256: digest } : { algorithm: 'unavailable', sha256: null },
    state
  };
}

export async function verifyBackupEnvelope(payload, cryptoApi = globalThis.crypto) {
  const inspected = inspectBackupEnvelope(payload);
  if (!inspected.valid) return inspected;
  if (!inspected.checksum) return { ...inspected, integrity: 'legacy-unchecksummed' };
  const digest = await sha256Hex(JSON.stringify(inspected.state), cryptoApi);
  if (!digest) return { ...inspected, valid: false, reason: 'This browser cannot verify SHA-256 integrity. Open the backup in a supported secure browser.' };
  if (digest !== inspected.checksum) return { ...inspected, valid: false, reason: 'Backup checksum mismatch. The file may be damaged or modified.' };
  return { ...inspected, integrity: 'sha256-verified' };
}
