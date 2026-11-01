// Shared helpers to drive the real Carport tool page in headless Chromium.
const { chromium } = require('playwright');
const fs = require('fs');
const C = process.env.CARPORT_DIR;
async function open({ width = 1920, height = 1080, dpr = 4 / 3 } = {}) {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files'] });
  const ctx = await b.newContext({ viewport: { width, height }, deviceScaleFactor: dpr });
  const p = await ctx.newPage();
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ contentType: 'text/css', body: fs.readFileSync(C + '/fonts.css', 'utf8') }));
  await p.route('https://fonts.gstatic.com/**', r => r.abort());
  await p.goto('file://' + C + '/' + (process.env.CARPORT_PAGE || 'page.html'));
  await p.evaluate(() => document.fonts.ready);
  return { b, p };
}
async function setPhoto(p, file) {
  await p.setInputFiles('#upload', file);
  await p.waitForFunction(() => document.getElementById('photo').src.startsWith('data:image/jpeg') && document.getElementById('photo').complete);
  await p.waitForTimeout(300);
}
// Set a slider exactly as a user drag would end: value + input event.
async function setSlider(p, k, v) {
  await p.evaluate(([k, v]) => { const i = document.getElementById('s-' + k); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })); }, [k, v]);
}
module.exports = { open, setPhoto, setSlider };
