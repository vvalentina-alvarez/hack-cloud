#!/usr/bin/env node

const api = process.argv[2];
const total = Number(process.argv[3] || 50);
if (!api) {
  console.error('Uso: node scripts/test-burst.mjs <ApiUrl> [cantidad]');
  process.exit(2);
}

const started = Date.now();
const payloads = Array.from({ length: total }, (_, index) => ({
  documentId: `BURST-${String(index).padStart(4, '0')}`,
  serviceNumber: `TEST-${String(index).padStart(4, '0')}`,
  lat: -12.0464,
  lon: -77.0428,
  occurredAt: new Date().toISOString(),
  problemType: 'LENTITUD',
  description: 'Prueba controlada de rafaga e idempotencia',
  email: '',
  phone: ''
}));

const results = await Promise.all(payloads.map(async (payload) => {
  const response = await fetch(`${api.replace(/\/$/, '')}/reports`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return { status: response.status, body: await response.json() };
}));

const accepted = results.filter((result) => result.status === 202);
const ids = new Set(accepted.map((result) => result.body.reportId));
const summary = {
  sent: total,
  accepted: accepted.length,
  uniqueReportIds: ids.size,
  errors: results.filter((result) => result.status !== 202),
  elapsedMs: Date.now() - started
};
console.log(JSON.stringify(summary, null, 2));
if (accepted.length !== total || ids.size !== total) process.exit(1);
