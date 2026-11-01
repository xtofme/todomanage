# REVIEW — Démo « Carport sur site »

- Scénario 1 « Avant / après », orienté dossier en mairie, 31 s, 1920×1080, 30 fps, musique Pixabay (vlog intro, prettyjohn1) calée sur sa vraie fin.
- Carport final calé sur l'image de référence de la personne : toit plat, 2 poteaux, 6 m, habillage anthracite, devant la haie à droite (orientation 65°, décalage 8,7 m, distance 10,5 m, inclinaison 1°, champ 64°). Fin : cyberplourin.github.io/carport-3d.
- Capture faite avec la version de l'outil qui ajoute Basculer / Pencher (`tools/carport-outil.html`).
- Images de l'outil : capture réelle de la page, pilotée image par image (`tools/take.cjs`) dans Chromium, avec la photo du terrain.
  Seul changement de mise en page pour la capture : le panneau de réglages défile à l'intérieur de la fenêtre au lieu de la page entière.
- Scènes générées par `build.py` (titres, cadrages, timings) : modifier là, puis `python3 build.py`.
- Mesuré : `check` OK, durée 31,0 s, -13,7 LUFS, crête -1,5 dBTP, sans saturation. Son mesuré, pas écouté.
- Plus faible : le texte du panneau reste petit (environ 18 px) dans les plans de réglages ; les titres portent le sens.
