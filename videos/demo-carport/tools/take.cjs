// One continuous take of the real Carport tool, driven frame by frame and piped to ffmpeg.
// Usage: CARPORT_DIR=... node take.cjs <photo> <out.mp4> <rects.json> [maxFrames]
const { open, setPhoto, setSlider } = require('./lib.cjs');
const { spawn } = require('child_process');
const fs = require('fs');

const FPS = 30, DPR = 2, VW = 1920, VH = 1080;
const [photo, outMp4, rectsOut, maxF] = process.argv.slice(2);

const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const prog = (t, a, b) => clamp((t - a) / (b - a), 0, 1);
const ease = {
  inOut: u => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2),
  out: u => 1 - Math.pow(1 - u, 3),
  expoOut: u => (u === 1 ? 1 : 1 - Math.pow(2, -10 * u)),
};
const lerp = (a, b, u) => a + (b - a) * u;

// Starting state: the carport hovers 3 m up, then is lowered, dragged and turned into place.
const START = { pitch: 2, fov: 68, camH: 1.6, yaw: 60, dist: 9.5, lat: 1.2, elev: 3, L: 6, W: 5, sunAz: 210, sunEl: 40 };

const TARGET = { lat: 4.9, dist: 14.5, yaw: 90 };

(async () => {
  const { b, p } = await open({ width: VW, height: VH, dpr: DPR });
  // Panel scrolls inside the window so the stage never leaves the frame.
  await p.addStyleTag({ content: `.panel{max-height:calc(100vh - 66px);overflow:auto;scrollbar-width:thin}
    #democursor{position:fixed;left:0;top:0;width:46px;height:46px;z-index:99;pointer-events:none;transform-origin:4px 3px}` });
  await setPhoto(p, photo);
  for (const [k, v] of Object.entries(START)) await setSlider(p, k, v);
  await p.evaluate(() => {
    const d = document.createElement('div'); d.id = 'democursor';
    d.innerHTML = '<svg viewBox="0 0 24 24" width="46" height="46"><path d="M4 3 L4 19 L8.6 14.8 L11.6 21.4 L14.4 20.2 L11.5 13.7 L17.6 13.4 Z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    document.body.appendChild(d);
    document.getElementById('hint').style.display = 'none';
  });

  const rect = sel => p.evaluate(s => { const r = document.querySelector(s).getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; }, sel);
  const stage = await rect('#stage');
  // Where the carport sits on screen at the start, and where the drag should end.
  // Project a ground point (world metres) to screen, with the tool's own camera model, so the drag lands exactly.
  const project = (x, z) => {
    const pr = START.pitch * Math.PI / 180, th = Math.tan(START.fov * Math.PI / 360), asp = stage.w / stage.h;
    const vy = -START.camH, yc = Math.cos(pr) * vy + Math.sin(pr) * z, zc = -Math.sin(pr) * vy + Math.cos(pr) * z;
    return { x: stage.x + (x / (-zc * th * asp) + 1) / 2 * stage.w, y: stage.y + (1 - yc / (-zc * th)) / 2 * stage.h };
  };
  // Grab the slab at its centre, release it at the final spot: beside the house, open end to the street.
  const dragFrom = project(START.lat, -START.dist);
  const dragTo = project(TARGET.lat, -TARGET.dist);

  const panelScroll = async sel => p.evaluate(s => {
    const pn = document.querySelector('.panel'), el = document.querySelector(s);
    return el.getBoundingClientRect().top - pn.getBoundingClientRect().top + pn.scrollTop - 8;
  }, sel);
  const S_DIM = await panelScroll('#g-dim');

  // Cursor path keyframes [t, x, y] (CSS px); clicks at given times.
  const offX = VW + 60, offY = VH * 0.8;
  const state = { scroll: 0, cursor: { x: offX, y: offY }, press: 0 };
  const log = [];
  const ffmpeg = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-g', '15', outMp4], { stdio: ['pipe', 'inherit', 'inherit'] });

  let mouseDown = false, wheelDone = 0, done = {};
  const once = async (key, fn) => { if (!done[key]) { done[key] = true; await fn(); } };
  const thumb = async (k, v) => p.evaluate(([k, v]) => {
    const i = document.getElementById('s-' + k), r = i.getBoundingClientRect();
    const f = (v - +i.min) / (+i.max - +i.min); return { x: r.left + 8 + f * (r.width - 16), y: r.top + r.height / 2 };
  }, [k, v]);
  const center = async sel => { const r = await rect(sel); return { x: r.x + r.w / 2, y: r.y + r.h / 2 }; };

  const TOTAL = 17.4, N = Math.min(Math.round(TOTAL * FPS), maxF ? +maxF : 1e9);
  let pos = {};
  for (let f = 0; f < N; f++) {
    const t = f / FPS;
    // 1. Lower the carport into place.
    if (t <= 1.4) await setSlider(p, 'elev', +(lerp(3, 0, ease.expoOut(prog(t, 0.4, 1.3)))).toFixed(2));
    // 2. Cursor enters and drags the carport across the gravel (real pointer events).
    let c = { x: offX, y: offY };
    if (t >= 1.5 && t < 2.3) { const u = ease.out(prog(t, 1.5, 2.2)); c = { x: lerp(offX, dragFrom.x, u), y: lerp(offY, dragFrom.y, u) }; }
    if (t >= 2.3 && t < 3.8) {
      const u = ease.inOut(prog(t, 2.4, 3.7)); c = { x: lerp(dragFrom.x, dragTo.x, u), y: lerp(dragFrom.y, dragTo.y, u) };
      if (!mouseDown) { await p.mouse.move(dragFrom.x, dragFrom.y); await p.mouse.down(); mouseDown = true; }
      await p.mouse.move(c.x, c.y);
    }
    if (t >= 3.8 && mouseDown) { await p.mouse.up(); mouseDown = false; }
    // 3. Mouse wheel turns it: 10 notches of 3 degrees.
    if (t >= 3.8 && t < 5.6) {
      c = { ...dragTo };
      const want = Math.min(10, Math.floor(prog(t, 4.0, 5.3) * 10.999));
      while (wheelDone < want) { await p.mouse.move(c.x, c.y); await p.mouse.wheel(0, 100); wheelDone++; }
    }
    // 4. Panel scrolls to the dimensions; switch to a gable roof, 3 posts, longer, wood fascia.
    if (t >= 5.6) state.scroll = lerp(0, S_DIM, ease.inOut(prog(t, 5.8, 6.5)));
    await p.evaluate(s => { document.querySelector('.panel').scrollTop = s; }, state.scroll);
    if (t >= 5.6 && t < 7.4) { pos.gable = pos.gable || null; const tgt = await center('[data-roof="gable"]'); const u = ease.inOut(prog(t, 6.2, 7.0)); c = { x: lerp(dragTo.x, tgt.x, u), y: lerp(dragTo.y, tgt.y, u) }; }
    if (t >= 7.1) await once('gable', () => p.click('[data-roof="gable"]'));
    if (t >= 7.4 && t < 8.3) { const a = await center('[data-roof="gable"]'), tgt = await center('[data-np="3"]'); const u = ease.inOut(prog(t, 7.4, 7.9)); c = { x: lerp(a.x, tgt.x, u), y: lerp(a.y, tgt.y, u) }; }
    if (t >= 8.0) await once('np3', () => p.click('[data-np="3"]'));
    if (t >= 8.3 && t < 10.2) {
      const a = await center('[data-np="3"]'), th0 = await thumb('L', 6);
      if (t < 8.8) { const u = ease.inOut(prog(t, 8.3, 8.8)); c = { x: lerp(a.x, th0.x, u), y: lerp(a.y, th0.y, u) }; }
      else { const v = +(lerp(6, 7.5, ease.inOut(prog(t, 8.9, 10.0)))).toFixed(1); await setSlider(p, 'L', v); c = await thumb('L', v); }
    }
    if (t >= 10.2 && t < 11.0) { const a = await thumb('L', 7.5), tgt = await center('#fmat'); const u = ease.inOut(prog(t, 10.2, 10.7)); c = { x: lerp(a.x, tgt.x, u), y: lerp(a.y, tgt.y, u) }; }
    if (t >= 10.8) await once('wood', () => p.evaluate(() => { const s = document.getElementById('fmat'); s.value = 'bois'; s.dispatchEvent(new Event('change')); }));
    if (t >= 11.0 && t < 11.7) c = await center('#fmat');
    // 5. Sun: scroll to it and sweep the shadow.
    const S_SUN = await panelScroll('#g-sun');
    if (t >= 11.7) state.scroll = lerp(S_DIM, S_SUN, ease.inOut(prog(t, 11.7, 12.4)));
    if (t >= 11.7 && t < 14.7) {
      await p.evaluate(s => { document.querySelector('.panel').scrollTop = s; }, state.scroll);
      const a = await center('#fmat'), th0 = await thumb('sunAz', 210);
      if (t < 12.7) { const u = ease.inOut(prog(t, 12.0, 12.6)); c = { x: lerp(a.x, th0.x, u), y: lerp(a.y, th0.y, u) }; }
      else { const v = Math.round(lerp(210, 140, ease.inOut(prog(t, 12.8, 14.5)))); await setSlider(p, 'sunAz', v); c = await thumb('sunAz', v); }
    }
    // 6. Generate the image.
    const S_END = await p.evaluate(() => { const pn = document.querySelector('.panel'); return pn.scrollHeight - pn.clientHeight; });
    if (t >= 14.7) {
      state.scroll = lerp(S_SUN, S_END, ease.inOut(prog(t, 14.7, 15.3)));
      await p.evaluate(s => { document.querySelector('.panel').scrollTop = s; }, state.scroll);
      const a = await thumb('sunAz', 140), tgt = await center('#export');
      const u = ease.inOut(prog(t, 15.0, 15.6)); c = { x: lerp(a.x, tgt.x, u), y: lerp(a.y, tgt.y, u) };
    }
    if (t >= 15.75) await once('export', async () => { await p.click('#export'); await p.waitForTimeout(200); });
    // Press feedback on clicks.
    const clicks = [7.1, 8.0, 10.8, 15.75], drag = t >= 2.3 && t < 3.8;
    const press = drag || clicks.some(ct => t >= ct - 0.05 && t < ct + 0.1) ? 0.86 : 1;
    await p.evaluate(([x, y, s]) => { document.getElementById('democursor').style.transform = `translate(${x - 4}px,${y - 3}px) scale(${s})`; }, [c.x, c.y, press]);
    await p.waitForTimeout(16);
    const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
    if (!ffmpeg.stdin.write(buf)) await new Promise(r => ffmpeg.stdin.once('drain', r));
    log.push({ t: +t.toFixed(3), cursor: { x: +c.x.toFixed(1), y: +c.y.toFixed(1) } });
    if (f % 60 === 0) process.stderr.write(`frame ${f}/${N}\n`);
  }
  ffmpeg.stdin.end();
  await new Promise(r => ffmpeg.on('close', r));
  const finalRects = { stage: await rect('#stage'), panel: await rect('.panel'), result: await rect('#result').catch(() => null) };
  const sliders = await p.evaluate(() => Object.fromEntries([...document.querySelectorAll('.row input')].map(i => [i.id, i.value])));
  const resultSrc = await p.evaluate(() => document.getElementById('result').src);
  if (resultSrc.startsWith('data:image/jpeg')) fs.writeFileSync(rectsOut.replace(/\.json$/, '-result.jpg'), Buffer.from(resultSrc.split(',')[1], 'base64'));
  fs.writeFileSync(rectsOut, JSON.stringify({ fps: FPS, dpr: DPR, start: { stage }, final: finalRects, sliders, log }, null, 1));
  await b.close();
})();
