#!/usr/bin/env node
// Screenshot an HTML file with Playwright's Chromium.
//   node render.js INPUT.html OUTPUT.png [--width 1320] [--scale 2] [--wait 1500]
// Uses the pre-installed Playwright if require('playwright') works; otherwise
// tries the executable at PLAYWRIGHT_CHROMIUM or /opt/pw-browsers/chromium.
// Use --scale 2 for images a person will see, 1 for your own checks.
const path = require('path');
const fs = require('fs');

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  return i > -1 ? process.argv[i + 1] : def;
}

(async () => {
  const [input, output] = process.argv.slice(2).filter((a, i, all) => !a.startsWith('--') && !(all[i - 1] || '').startsWith('--'));
  if (!input || !output) {
    console.error('usage: node render.js INPUT.html OUTPUT.png [--width 1320] [--scale 2] [--wait 1500]');
    process.exit(2);
  }
  let playwright;
  try { playwright = require('playwright'); } catch (e) {
    console.error('Playwright is not available. Install it (npm i -D playwright) or describe the screen as a spec and say it was not rendered.');
    process.exit(3);
  }
  const launch = {};
  const exe = process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
  let browser;
  try { browser = await playwright.chromium.launch(launch); } catch (e) {
    if (!fs.existsSync(exe)) throw e;
    browser = await playwright.chromium.launch({ executablePath: exe });
  }
  const page = await browser.newPage({
    viewport: { width: parseInt(arg('width', '1320'), 10), height: 900 },
    deviceScaleFactor: parseFloat(arg('scale', '2')),
  });
  const failed = [];
  page.on('requestfailed', r => failed.push(r.url()));
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(parseInt(arg('wait', '800'), 10));
  // Report which requested font families actually loaded, so a fallback is never mistaken for the real face.
  const fonts = await page.evaluate(() => {
    const out = {};
    document.fonts.forEach(f => { out[f.family.replace(/"/g, '')] = out[f.family.replace(/"/g, '')] || f.status; if (f.status === 'loaded') out[f.family.replace(/"/g, '')] = 'loaded'; });
    return out;
  });
  await page.screenshot({ path: output, fullPage: true });
  await browser.close();
  console.log('wrote ' + output);
  const entries = Object.entries(fonts);
  if (entries.length) console.log('fonts: ' + entries.map(([k, v]) => `${k}=${v}`).join(', '));
  if (failed.length) console.log('WARNING failed requests (fonts may have fallen back): ' + [...new Set(failed)].slice(0, 6).join(' '));
})().catch(e => { console.error(e.message); process.exit(1); });
