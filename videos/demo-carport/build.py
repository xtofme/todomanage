"""Generates the "Carport sur site" demo film (index + scenes). Run: python3 build.py"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
TEAL, BG, FG, WOOD, WHITE = "#2e5c61", "#eef0ed", "#1d2422", "#c48a52", "#ffffff"
TOTAL = 31.0
T_TOOL, T_APRES, T_FIN = 3.2, 20.6, 26.8   # cuts; 20.6 and 26.8 land on beats of the track
TAKE = 17.4                                 # length of assets/ui/outil.mp4
MUSIC_IN = 57.7                             # the track's own ending lands under the end card

FONTS = "\n".join(
    f'@font-face{{font-family:"Archivo";font-weight:{w};src:url("assets/fonts/archivo-latin-{w}-normal.woff2") format("woff2")}}'
    for w in (500, 600, 700, 800))

# Camera framings on the 1920x1080 capture: view top-left (css px) and scale.
CAM = {
    "stage": (22.5, 42, 1.2315),
    "dim": (541, 30, 1.4),
    "sun": (541, 305, 1.4),
    "result": (428, 220.8, 1.805),
}
# (take time, duration, framing)
MOVES = [(5.8, 0.8, "dim"), (11.7, 0.7, "sun"), (15.9, 0.8, "result")]


def cam(name):
    vx, vy, s = CAM[name]
    return f"{{x: {round(-vx * s, 1)}, y: {round(-vy * s, 1)}, scale: {s}}}"


def scene(cid, css, body, js, extra_attrs=""):
    return f"""<template>
  <style>
    {FONTS}
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    {css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080"{extra_attrs}>
    {body}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {js}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""


def avant():
    d = T_TOOL
    return scene("avant",
        f"#avant-kb {{ position: absolute; inset: 0; transform-origin: 62% 70%; }}\n"
        f"    #avant-img {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}",
        f'<div id="avant-kb"><img id="avant-img" class="clip" data-start="0" data-duration="{d}" src="assets/img/terrain.jpg" alt="Maison et allée de gravier vide" /></div>',
        f'tl.fromTo("#avant-kb", {{scale: 1}}, {{scale: 1.06, duration: {round(d - 0.2, 3)}, ease: "none"}}, 0);\n'
        f'      tl.fromTo("#avant-kb", {{filter: "blur(0px)"}}, {{filter: "blur(10px)", scale: 1.12, immediateRender: false, duration: 0.2, ease: "power3.in"}}, {d - 0.2});')


def outil():
    js = [f'tl.set("#outil-cam", {cam("stage")}, 0);']
    prev = "stage"
    for t, dur, name in MOVES:
        js.append(f'tl.fromTo("#outil-cam", {cam(prev)}, {{...{cam(name)}, immediateRender: false, duration: {dur}, ease: "power2.inOut"}}, {t});')
        prev = name
    js.append('tl.fromTo("#outil-cam", {filter: "blur(10px)"}, {filter: "blur(0px)", immediateRender: false, duration: 0.25, ease: "expo.out"}, 0);')
    return scene("outil",
        f"#root {{ background: {BG}; }}\n"
        f"    #outil-cam {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }}\n"
        f"    #outil-vid {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}",
        f'<div id="outil-cam"><video id="outil-vid" class="clip" data-start="0" data-duration="{TAKE}" src="assets/ui/outil.mp4" muted playsinline></video></div>',
        "\n      ".join(js))


def apres():
    d = T_FIN - T_APRES
    css = f"""#apres-after, #apres-before {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
    #apres-before {{ clip-path: inset(0% 0% 0% 100%); }}
    #apres-line {{ position: absolute; top: 0; left: 0; width: 6px; height: 1080px; background: {WHITE}; margin-left: -3px; }}
    #apres-knob {{ position: absolute; top: 504px; left: -33px; width: 72px; height: 72px; background: {TEAL}; border: 5px solid {WHITE}; }}
    .tag {{ position: absolute; top: 96px; padding: 10px 22px; background: {FG}; color: {WHITE}; font-family: "Archivo"; font-weight: 700; font-size: 40px; opacity: 0; }}
    #apres-tag-a {{ left: 96px; }}
    #apres-tag-b {{ right: 96px; }}"""
    body = f"""<img id="apres-after" class="clip" data-start="0" data-duration="{d}" src="assets/img/resultat.jpg" alt="Photomontage : le carport sur l'allée" />
    <img id="apres-before" class="clip" data-start="0" data-duration="{d}" src="assets/img/terrain.jpg" alt="La même allée, vide" />
    <div id="apres-wipe" style="position:absolute;left:0;top:0;width:0;height:1080px;opacity:0"><div id="apres-line"></div><div id="apres-knob"></div></div>
    <div id="apres-tag-a" class="tag">Après</div>
    <div id="apres-tag-b" class="tag">Avant</div>"""
    # Divider sweeps in from the right to 70 %, through the carport, holds, then returns: the carport disappears and comes back.
    js = """tl.fromTo("#apres-wipe", {opacity: 0}, {opacity: 1, duration: 0.15}, 0.35);
      tl.fromTo("#apres-before", {clipPath: "inset(0% 0% 0% 100%)"}, {clipPath: "inset(0% 0% 0% 70%)", duration: 0.9, ease: "power2.inOut"}, 0.4);
      tl.fromTo("#apres-wipe", {x: 1920}, {x: 1344, duration: 0.9, ease: "power2.inOut"}, 0.4);
      tl.fromTo(["#apres-tag-a", "#apres-tag-b"], {opacity: 0, filter: "blur(8px)"}, {opacity: 1, filter: "blur(0px)", duration: 0.2, stagger: 0.1}, 1.1);
      tl.fromTo(["#apres-tag-a", "#apres-tag-b"], {opacity: 1}, {opacity: 0, immediateRender: false, duration: 0.15}, 2.6);
      tl.fromTo("#apres-before", {clipPath: "inset(0% 0% 0% 70%)"}, {clipPath: "inset(0% 0% 0% 100%)", immediateRender: false, duration: 0.8, ease: "power2.inOut"}, 2.6);
      tl.fromTo("#apres-wipe", {x: 1344}, {x: 1920, immediateRender: false, duration: 0.8, ease: "power2.inOut"}, 2.6);
      tl.fromTo("#apres-wipe", {opacity: 1}, {opacity: 0, immediateRender: false, duration: 0.1}, 3.35);"""
    return scene("apres", css, body, js)


def fin():
    d = TOTAL - T_FIN
    css = f"""#root {{ background: {BG}; color: {FG}; }}
    #fin-img {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; transform-origin: 0 0; }}
    #fin-title {{ position: absolute; left: 96px; top: 200px; margin: 0; font-family: "Archivo"; font-weight: 800; font-size: 132px; line-height: 0.98; letter-spacing: -0.02em; }}
    #fin-title .w {{ display: inline-block; }}
    #fin-sub {{ position: absolute; left: 100px; top: 480px; width: 780px; margin: 0; font-family: "Archivo"; font-weight: 500; font-size: 40px; line-height: 1.25; }}
    #fin-steps {{ position: absolute; left: 96px; top: 700px; padding: 16px 28px; background: {TEAL}; color: {WHITE};
      font-family: "Archivo"; font-weight: 700; font-size: 40px; white-space: nowrap; clip-path: inset(0% 100% 0% 0%); }}
    #fin-url {{ position: absolute; left: 96px; top: 850px; margin: 0; font-family: "Archivo"; font-weight: 700; font-size: 48px; color: {TEAL}; }}
    #fin-steps .sep {{ color: {WHITE}; padding: 0 14px; }}"""
    body = f"""<img id="fin-img" class="clip" data-start="0" data-duration="{d}" src="assets/img/resultat.jpg" alt="Photomontage du carport" />
    <h1 id="fin-title"><span class="w">Carport</span><br /><span class="w">sur</span> <span class="w">site</span></h1>
    <p id="fin-sub">La vue 3D de votre projet, pour le dossier en mairie</p>
    <div id="fin-steps">Chargez<span class="sep">›</span>placez<span class="sep">›</span>générez</div>
    <p id="fin-url">cyberplourin.github.io/carport-3d</p>"""
    js = """tl.fromTo("#fin-img", {x: 0, y: 0, scale: 1}, {x: 940, y: 300, scale: 0.46, duration: 0.7, ease: "power3.inOut"}, 0.05);
      tl.fromTo("#fin-title .w", {opacity: 0, filter: "blur(8px)"}, {opacity: 1, filter: "blur(0px)", duration: 0.2, stagger: 0.09, ease: "power2.out"}, 0.55);
      tl.fromTo("#fin-sub", {opacity: 0, filter: "blur(8px)"}, {opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power2.out"}, 0.95);
      tl.fromTo("#fin-steps", {clipPath: "inset(0% 100% 0% 0%)"}, {clipPath: "inset(0% 0% 0% 0%)", duration: 0.4, ease: "expo.out"}, 1.3);
      tl.fromTo("#fin-url", {opacity: 0, filter: "blur(8px)"}, {opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out"}, 1.65);"""
    return scene("fin", css, body, js)


# Overlay titles: (start, end, text, position)
TITLES = [
    (0.3, 3.0, "Un carport à déclarer en mairie ?", "hook"),
    (T_TOOL + 0.3, T_TOOL + 2.4, "Posez-le sur votre photo", "low"),
    (T_TOOL + 2.6, T_TOOL + 5.5, "Placez-le, tournez-le", "low"),
    (T_TOOL + 6.9, T_TOOL + 11.4, "Toit, poteaux, longueur, habillage", "low"),
    (T_TOOL + 12.1, T_TOOL + 14.5, "Réglez le soleil", "low"),
    (T_TOOL + 15.0, T_TOOL + 16.2, "Générez l'image", "low"),
    (T_APRES + 3.45, T_FIN - 0.15, "L'image pour votre dossier en mairie", "low"),
]


def titres():
    html, js = [], []
    for i, (s, e, text, kind) in enumerate(TITLES):
        tid = f"ti-{i}"
        cls = "lab hook" if kind == "hook" else "lab"
        words = "".join(f'<span class="w">{w}</span> ' for w in text.split())
        html.append(f'<div id="{tid}" class="{cls}">{words.strip()}</div>')
        js.append(f'tl.fromTo("#{tid}", {{clipPath: "inset(0% 100% 0% 0%)"}}, {{clipPath: "inset(0% 0% 0% 0%)", duration: 0.3, ease: "expo.out"}}, {s});')
        js.append(f'tl.fromTo("#{tid} .w", {{opacity: 0, filter: "blur(6px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.14, stagger: 0.067, ease: "power2.out"}}, {round(s + 0.08, 3)});')
        js.append(f'tl.fromTo("#{tid}", {{clipPath: "inset(0% 0% 0% 0%)"}}, {{clipPath: "inset(0% 0% 0% 100%)", immediateRender: false, duration: 0.18, ease: "power3.in"}}, {round(e - 0.18, 3)});')
    return scene("titres",
        f"""#root .lab {{ position: absolute; left: 96px; top: 868px; padding: 14px 26px 16px; background: {TEAL}; color: {WHITE};
      font-family: "Archivo"; font-weight: 800; font-size: 64px; line-height: 1.05; letter-spacing: -0.01em; white-space: nowrap;
      clip-path: inset(0% 100% 0% 0%); }}
    #root .lab.hook {{ top: 150px; font-size: 88px; }}
    #root .lab .w {{ display: inline-block; }}""",
        "\n    ".join(html), "\n      ".join(js))


def host(cid, start, dur, z):
    return (f'<div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{start}" '
            f'data-duration="{round(dur, 3)}" data-track-index="{z}" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:{z}"></div>')


# (id, file, start, duration, volume)
CLICKS = [7.1, 8.0, 10.8, 15.75]
SOUNDS = [("sx-whoosh1", "whoosh", T_TOOL - 0.16, 0.57, 0.35)]
SOUNDS += [(f"sx-click{i}", "click-soft", round(T_TOOL + c - 0.04, 3), 0.36, 0.6) for i, c in enumerate(CLICKS)]
SOUNDS += [("sx-whoosh2", "whoosh", T_APRES + 0.55, 0.57, 0.3), ("sx-impact", "impact-bass-1", T_FIN + 0.55, 2.1, 0.45)]


def index():
    hosts = [host("avant", 0, T_TOOL, 1), host("outil", T_TOOL, T_APRES - T_TOOL, 1), host("apres", T_APRES, T_FIN - T_APRES, 1),
             host("fin", T_FIN, TOTAL - T_FIN, 1), host("titres", 0, T_FIN, 2)]
    audio = [f'<audio id="musique" class="clip" src="assets/audio/musique.mp3" data-start="0" data-duration="{TOTAL}" '
             f'data-media-start="{MUSIC_IN}" data-track-index="3" data-volume="0.85" data-fade-in="0.2" data-fade-out="1.2"></audio>']
    for i, (aid, f, st, d, vol) in enumerate(SOUNDS):
        audio.append(f'<audio id="{aid}" class="clip" src="assets/audio/{f}.mp3" data-start="{round(st, 3)}" data-duration="{d}" '
                     f'data-track-index="{4 + i % 2}" data-volume="{vol}"></audio>')
    inner = "\n      ".join(hosts + audio)
    return f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Carport sur site — démo</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: {BG}; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
      {inner}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


os.makedirs(f"{ROOT}/compositions", exist_ok=True)
for name, fn in [("avant", avant), ("outil", outil), ("apres", apres), ("fin", fin), ("titres", titres)]:
    open(f"{ROOT}/compositions/{name}.html", "w").write(fn())
open(f"{ROOT}/index.html", "w").write(index())
print("ok")
