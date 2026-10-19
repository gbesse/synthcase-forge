import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
const port = 18767,
  base = `http://127.0.0.1:${port}`;
const server = spawn(process.env.PYTHON || 'python3', ['-m', 'synthcase', 'serve', String(port)], {
  stdio: ['ignore', 'pipe', 'inherit'],
});
let browser;
try {
  for (let i = 0; i < 200; i++) {
    try {
      if ((await fetch(base)).ok) break;
    } catch {}
    if (server.exitCode !== null) throw Error('server exited');
    if (i === 199) throw Error('server timeout');
    await new Promise((r) => setTimeout(r, 100));
  }
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1300, height: 1100 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  for (const lang of ['fr', 'en', 'es']) {
    await page.goto(`${base}/?lang=${lang}`);
    await page.waitForFunction(() => document.getElementById('count').textContent === '12');
    assert.equal(await page.locator('html').getAttribute('lang'), lang);
    assert.equal(await page.locator('#bad').textContent(), '8');
    await page.locator('#pair').click();
    await page.waitForSelector('.pair-verdict');
    assert.match(await page.locator('#pair-result').textContent(), /billed_quantity/);
    assert.equal(await page.locator('.change:not(.derived)').count(), 1);
    const event = page.waitForEvent('download');
    await page.locator('#download').click();
    assert.equal((await event).suggestedFilename(), 'synthcase-dataset.json');
    await page.locator('[data-cohort=ready]').fill('5');
    await page.locator('#generate').click();
    await page.waitForFunction(() => document.getElementById('count').textContent === '13');
    await page.locator('#seed').fill('-1');
    await page.locator('#generate').click();
    await page.waitForFunction(() => !document.getElementById('generate').disabled);
    assert.match(
      await page.locator('#status').textContent(),
      { fr: /Entrée non valide/, en: /Invalid input/, es: /Entrada no válida/ }[lang],
    );
  }
  await page.goto(`${base}/?lang=fr`);
  await page.waitForFunction(() => document.getElementById('count').textContent === '12');
  await page.locator('#pair').click();
  await page.waitForSelector('.pair-verdict');
  await mkdir('.local', { recursive: true });
  await page.screenshot({ path: '.local/preview-fr.png', fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  assert.deepEqual(errors, []);
  assert.equal((await fetch(base + '/.env')).status, 404);
  assert.equal((await fetch(base + '/api/review')).status, 404);
  console.log(
    'FR/EN/ES: exact cohorts, minimal counterfactual, export, quotas, errors, mobile and local-only routes verified.',
  );
} finally {
  if (browser) await browser.close();
  server.kill('SIGTERM');
}
