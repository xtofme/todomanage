"""Generates the Cyberespace de Plourin HyperFrames project files (index + scenes)."""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
AMBER, SLATE, PAPER = "#EFB55B", "#3F427E", "#FFF6E6"
os.makedirs(f"{ROOT}/compositions", exist_ok=True)

# id, image, start, duration, ken-burns origin, kb scale, entrance, exit, alt
SCENES = [
    ("accueil", "salle-postes", 0.0, 3.4, "63% 66%", (1.0, 1.05), None, "punch", "La salle du cyberespace, rangée d'ordinateurs et écran projeté"),
    ("apprendre", "postes", 3.4, 2.8, "40% 50%", (1.02, 1.08), "punch", "whipL", "Postes informatiques"),
    ("fabriquer", "fablab", 6.2, 2.8, "65% 45%", (1.0, 1.07), "whipR", None, "Établi et imprimante 3D du fablab"),
    ("coudre", "couture", 9.0, 2.4, "50% 45%", (1.0, 1.07), None, "whipUp", "Machine à coudre sur une table de l'atelier"),
    ("decouper", "decoupe", 11.4, 2.4, "45% 40%", (1.0, 1.07), "whipV", None, "Une participante prépare une découpe vinyle"),
    ("personnaliser", "tshirts", 13.8, 2.4, "35% 50%", (1.0, 1.07), None, "whipL", "T-shirts imprimés au cyberespace"),
    ("graver", "gravure", 16.2, 2.4, "40% 50%", (1.0, 1.06), "whipR", None, "Planches à découper gravées"),
    ("ensemble", "atelier-resine", 18.6, 3.0, "50% 45%", (1.0, 1.06), None, None, "Atelier bijoux en résine avec les participantes"),
    ("bijoux", "bijoux", 21.6, 1.8, "45% 40%", (1.03, 1.10), None, None, "Porte-clés et boucles d'oreilles en résine"),
]

ENTER = {
    "punch": '{scale: 1.16, filter: "blur(10px)"}, {scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out"}',
    "whipR": '{x: 420, filter: "blur(24px)"}, {x: 0, filter: "blur(0px)", duration: 0.32, ease: "expo.out"}',
    "whipV": '{y: 320, filter: "blur(24px)"}, {y: 0, filter: "blur(0px)", duration: 0.32, ease: "expo.out"}',
}
EXIT = {
    "punch": ('{scale: 1, filter: "blur(0px)"}, {scale: 1.7, filter: "blur(6px)", immediateRender: false, duration: 0.35, ease: "power3.in"}', 0.35),
    "whipL": ('{x: 0, filter: "blur(0px)"}, {x: -420, filter: "blur(24px)", immediateRender: false, duration: 0.2, ease: "power3.in"}', 0.2),
    "whipUp": ('{y: 0, filter: "blur(0px)"}, {y: -320, filter: "blur(24px)", immediateRender: false, duration: 0.2, ease: "power3.in"}', 0.2),
}


def photo_scene(sid, img, dur, origin, kb, enter, exit_, alt):
    js = [f'tl.fromTo("#{sid}-kb", {{scale: {kb[0]}}}, {{scale: {kb[1]}, duration: {dur}, ease: "none"}}, 0);']
    if enter:
        js.append(f'tl.fromTo("#{sid}-cam", {ENTER[enter]}, 0);')
    if exit_:
        tween, d = EXIT[exit_]
        js.append(f'tl.fromTo("#{sid}-cam", {tween}, {round(dur - d, 3)});')
    body = "\n      ".join(js)
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {SLATE}; }}
    #{sid}-cam, #{sid}-kb {{ position: absolute; inset: 0; transform-origin: {origin}; }}
    #{sid}-img {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
    <div id="{sid}-cam">
      <div id="{sid}-kb">
        <img id="{sid}-img" class="clip" data-start="0" data-duration="{dur}" src="assets/photos/{img}.jpg" alt="{alt}" />
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {body}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


# The plunge into the projected slide: slide centre in frame px, from the 4080x2295 photo.
SLIDE_C = (1254, 96.5)
ZOOM = 7.3


def retour_scene():
    sid, dur = "retour", 2.8
    tx = round(960 - ZOOM * SLIDE_C[0], 1)
    ty = round(540 - ZOOM * SLIDE_C[1], 1)
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {AMBER}; }}
    #retour-kb {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }}
    #retour-img {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
    #retour-amber {{ position: absolute; inset: 0; background: {AMBER}; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
    <div id="retour-kb">
      <img id="retour-img" class="clip" data-start="0" data-duration="{dur}" src="assets/photos/salle-couture.jpg" alt="La salle et l'écran projeté « Cyberespace de Plourin »" />
    </div>
    <div id="retour-amber"></div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      // Linear path of the slide centre to frame centre while scaling: both tweens share one ease.
      tl.fromTo("#retour-kb", {{scale: 1, x: 0, y: 0, filter: "blur(0px)"}},
        {{scale: {ZOOM}, x: {tx}, y: {ty}, duration: 1.9, ease: "power2.in"}}, 0.6);
      tl.fromTo("#retour-kb", {{filter: "blur(0px)"}}, {{filter: "blur(10px)", immediateRender: false, duration: 0.5, ease: "power2.in"}}, 2.0);
      tl.fromTo("#retour-amber", {{opacity: 0}}, {{opacity: 1, duration: 0.3, ease: "power2.in"}}, 2.25);
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


# Overlay: the amber label that carries every verb. (start, end, word, facts, side)
WORDS = [
    (3.5, 6.05, "APPRENDRE", [(3.8, "Médiation et accompagnement numérique")], "left"),
    (6.3, 8.85, "FABRIQUER", [(6.6, "Fablab : imprimante 3D et outillage")], "left"),
    (9.05, 11.25, "COUDRE", [(9.35, "Couture et textile")], "left"),
    (11.5, 13.65, "DÉCOUPER", [(11.8, "Découpe vinyle et papier")], "left"),
    (13.9, 16.05, "PERSONNALISER", [(14.2, "T-shirts imprimés sur place")], "right"),
    (16.3, 18.3, "GRAVER", [(16.6, "Gravure sur bois")], "right"),
    (19.0, 23.25, "CRÉER ENSEMBLE", [(19.3, "Ateliers en groupe"), (21.7, "Bijoux en résine")], "left"),
]


def titres_scene():
    html, js = [], []
    # Hook: two stacked labels.
    html.append(f'<div id="t-h1" class="lab big" style="left:192px;top:520px"><span>UN LIEU</span></div>')
    html.append(f'<div id="t-h2" class="lab big" style="left:192px;top:700px"><span>MILLE USAGES</span></div>')
    for i, (t, sel) in enumerate([(0.15, "#t-h1"), (1.3, "#t-h2")]):
        js.append(label_in(sel, t))
    js.append(f'tl.fromTo(["#t-h1", "#t-h2"], {{clipPath: "inset(0% 0% 0% 0%)"}}, {{clipPath: "inset(0% 0% 0% 100%)", immediateRender: false, duration: 0.18, ease: "power3.in"}}, 3.1);')

    for n, (s, e, word, facts, side) in enumerate(WORDS):
        pos = "left:192px" if side == "left" else "right:192px"
        wid = f"t-w{n}"
        html.append(f'<div id="{wid}" class="lab" style="{pos};top:700px"><span>{word}</span></div>')
        js.append(label_in(f"#{wid}", s))
        fids = []
        for k, (ft, text) in enumerate(facts):
            fid = f"t-f{n}{k}"
            fids.append(fid)
            html.append(f'<p id="{fid}" class="fact" style="{pos};top:848px">{text}</p>')
            js.append(f'tl.fromTo("#{fid}", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power2.out"}}, {ft});')
            if k + 1 < len(facts):  # the next fact replaces this one
                js.append(f'tl.fromTo("#{fid}", {{opacity: 1, filter: "blur(0px)"}}, {{opacity: 0, filter: "blur(6px)", immediateRender: false, duration: 0.15, ease: "power2.in"}}, {facts[k + 1][0] - 0.18});')
        if word == "GRAVER":
            # The label grows into an amber curtain, then lifts onto the workshop.
            js.append(f'tl.fromTo(["#{wid} span", "#{fids[-1]}"], {{opacity: 1}}, {{opacity: 0, immediateRender: false, duration: 0.1}}, {e - 0.12});')
            js.append(f'tl.set("#{wid}", {{opacity: 0}}, {e + 0.02});')
            js.append(f'tl.set("#t-flood", {{opacity: 1}}, {e - 0.02});')
            js.append(f'tl.fromTo("#t-flood", {{clipPath: "inset(700px 192px 244px 1210px)"}}, {{clipPath: "inset(0px 0px 0px 0px)", immediateRender: false, duration: 0.3, ease: "power3.in"}}, {e - 0.02});')
            js.append(f'tl.fromTo("#t-flood", {{clipPath: "inset(0px 0px 0px 0px)"}}, {{clipPath: "inset(0px 0px 1080px 0px)", immediateRender: false, duration: 0.42, ease: "power3.inOut"}}, 18.62);')
        else:
            js.append(f'tl.fromTo(["#{wid}", {", ".join(chr(34) + "#" + f + chr(34) for f in fids)}], {{clipPath: "inset(0% 0% 0% 0%)"}}, {{clipPath: "inset(0% 0% 0% 100%)", immediateRender: false, duration: 0.18, ease: "power3.in"}}, {e - 0.18});')

    body = "\n    ".join(html)
    script = "\n      ".join(js)
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; }}
    #root .lab {{ position: absolute; background: {AMBER}; color: {SLATE}; padding: 18px 30px 14px;
      font-family: "Archivo Black"; font-size: 104px; line-height: 1; letter-spacing: -0.01em; white-space: nowrap;
      clip-path: inset(0% 100% 0% 0%); }}
    #root .lab.big {{ font-size: 132px; }}
    #root .lab span {{ display: inline-block; }}
    #root .fact {{ position: absolute; margin: 0; background: {SLATE}; color: {PAPER}; padding: 12px 24px;
      font-family: "Inter"; font-weight: 700; font-size: 40px; line-height: 1.2; white-space: nowrap; opacity: 0; }}
    #t-flood {{ position: absolute; inset: 0; background: {AMBER}; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="titres" data-width="1920" data-height="1080">
    {body}
    <div id="t-flood"></div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {script}
      window.__timelines["titres"] = tl;
    }})();
  </script>
</template>
"""


def label_in(sel, t):
    return (f'tl.fromTo("{sel}", {{clipPath: "inset(0% 100% 0% 0%)"}}, {{clipPath: "inset(0% 0% 0% 0%)", duration: 0.3, ease: "expo.out"}}, {t});\n      '
            f'tl.fromTo("{sel} span", {{y: 40, opacity: 0, filter: "blur(8px)"}}, {{y: 0, opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "expo.out"}}, {round(t + 0.08, 3)});')


def letters(text, cls):
    return "".join(f'<span class="{cls}">{c if c != " " else "&nbsp;"}</span>' for c in text)


def fin_scene():
    dur = 5.0
    variables = json.dumps([
        {"id": "telephone", "type": "string", "label": "Téléphone", "default": "02 98 04 37 44"},
        {"id": "email", "type": "string", "label": "E-mail", "default": "cyber@plourin.fr"},
    ], ensure_ascii=False)
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {AMBER}; color: {SLATE}; }}
    #fin-title {{ position: absolute; left: 150px; top: 130px; margin: 0; font-family: "Archivo Black";
      font-size: 170px; line-height: 1.08; letter-spacing: -0.01em; white-space: nowrap; font-weight: 400; }}
    #fin-title .l {{ display: inline-block; }}
    #fin-sub {{ position: absolute; left: 156px; top: 548px; margin: 0; font-family: "Inter"; font-weight: 800; font-size: 58px; }}
    #fin-list {{ position: absolute; left: 156px; top: 636px; width: 1080px; margin: 0; font-family: "Inter"; font-weight: 600;
      font-size: 38px; line-height: 1.3; }}
    #fin-contact {{ position: absolute; left: 150px; top: 806px; background: {SLATE}; color: {PAPER}; padding: 20px 34px;
      font-family: "Inter"; font-weight: 800; font-size: 52px; white-space: nowrap; clip-path: inset(0% 100% 0% 0%); }}
    #fin-contact .sep {{ color: {AMBER}; padding: 0 18px; }}
    #fin-icons {{ position: absolute; left: 1330px; top: 560px; width: 440px; height: 260px; }}
    #fin-icons .ic {{ fill: none; stroke: {SLATE}; stroke-width: 12; stroke-linejoin: round; stroke-linecap: round; }}
  </style>
  <div id="root" data-composition-id="fin" data-width="1920" data-height="1080" data-composition-variables='{variables}'>
    <h1 id="fin-title">{letters("CYBERESPACE", "l")}<br />{letters("DE PLOURIN", "l")}</h1>
    <p id="fin-sub">espace public numérique</p>
    <p id="fin-list">médiation, accompagnements, ateliers, travaux, copies, fablab…</p>
    <svg id="fin-icons" viewBox="0 0 440 260" aria-hidden="true">
      <path class="ic" d="M70 20 H330 V190 H70 Z M200 190 V232 M140 240 H260" />
      <path class="ic" d="M300 90 H390 Q400 90 400 100 V238 Q400 248 390 248 H300 Q290 248 290 238 V100 Q290 90 300 90 Z" />
      <path class="ic" d="M18 140 H64 Q72 140 72 148 V240 Q72 248 64 248 H18 Q10 248 10 240 V148 Q10 140 18 140 Z" />
    </svg>
    <div id="fin-contact"><span data-var-text="telephone">02 98 04 37 44</span><span class="sep">·</span><span data-var-text="email">cyber@plourin.fr</span></div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#fin-title .l", {{opacity: 0, y: -60, filter: "blur(8px)"}},
        {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "expo.out", stagger: 0.03}}, 0.1);
      tl.fromTo("#fin-sub", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power2.out"}}, 0.85);
      tl.fromTo("#fin-list", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power2.out"}}, 1.15);
      tl.fromTo("#fin-icons .ic", {{strokeDasharray: 1200, strokeDashoffset: 1200}},
        {{strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut", stagger: 0.12}}, 1.0);
      tl.fromTo("#fin-contact", {{clipPath: "inset(0% 100% 0% 0%)"}}, {{clipPath: "inset(0% 0% 0% 0%)", duration: 0.4, ease: "expo.out"}}, 1.55);
      window.__timelines["fin"] = tl;
    }})();
  </script>
</template>
"""


def host(sid, start, dur, track):
    return (f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
            f'data-start="{start}" data-duration="{dur}" data-track-index="{track}" data-track-kind="graphics" '
            f'data-width="1920" data-height="1080" style="z-index:{track}"></div>')


# (id, file, start, duration, volume, rate, fade-out)
SOUNDS = [
    ("sx-whoosh1", "whoosh", 3.24, 0.6, 0.55, None, None),
    ("sx-whoosh2", "whoosh", 6.06, 0.5, 0.5, 1.15, None),
    ("sx-pop1", "pop", 9.05, 0.7, 0.5, None, None),
    ("sx-whoosh3", "whoosh", 11.22, 0.65, 0.5, 0.9, None),
    ("sx-pop2", "pop", 13.86, 0.65, 0.45, 1.1, None),
    ("sx-riser", "riser", 15.13, 4.3, 0.35, None, 0.6),
    ("sx-whoosh4", "whoosh", 16.06, 0.6, 0.5, None, None),
    ("sx-whoosh5", "whoosh", 25.7, 0.72, 0.6, 0.8, None),
    ("sx-impact", "impact-bass-1", 26.58, 2.1, 0.7, None, 0.5),
]

TOTAL = 31.2


def index():
    hosts = [host(s[0], s[2], s[3], 1) for s in SCENES]
    hosts.append(host("retour", 23.4, 2.8, 1))
    hosts.append(host("fin", 26.2, 5.0, 1))
    hosts.append(host("titres", 0, 26.2, 2))
    audio = []
    for i, (aid, f, st, d, vol, rate, fo) in enumerate(SOUNDS):
        extra = (f' data-playback-rate="{rate}"' if rate else "") + (f' data-fade-out="{fo}"' if fo else "")
        audio.append(f'<audio id="{aid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{st}" data-duration="{d}" '
                     f'data-track-index="{3 + i % 2}" data-volume="{vol}"{extra}></audio>')
    inner = "\n      ".join(hosts + audio)
    return f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Cyberespace de Plourin — Un lieu, mille usages</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: {SLATE}; }}
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


for sid, img, start, dur, origin, kb, enter, exit_, alt in SCENES:
    open(f"{ROOT}/compositions/{sid}.html", "w").write(photo_scene(sid, img, dur, origin, kb, enter, exit_, alt))
open(f"{ROOT}/compositions/retour.html", "w").write(retour_scene())
open(f"{ROOT}/compositions/titres.html", "w").write(titres_scene())
open(f"{ROOT}/compositions/fin.html", "w").write(fin_scene())
open(f"{ROOT}/index.html", "w").write(index())
print("ok")
