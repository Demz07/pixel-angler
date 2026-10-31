# PIXEL ANGLER — self-contained fishing game kit

Isang self-contained na pixel-art fishing game (`fishing-sim.html`) — walang external
dependencies, lahat ng sprites/audio/code nasa loob ng iisang HTML file.

## Mga file

| File | Ano ito |
|---|---|
| `fishing-sim.html` | **ANG LARO.** Buksan lang sa kahit anong browser. Self-contained (sprites = data URIs, music = WebAudio code). |
| `template.html` | Source template ng laro (may `__PLACEHOLDER__` tokens). Ito ang e-edit mo pag magbabago ng code/UI. |
| `assets/build.py` | Build script: pinagsasama ang `template.html` + lahat ng JSON assets → `fishing-sim.html`. |
| `assets/pxkit.py` | Procedural pixel-art studio kit (Python/PIL): icons, button frames, panel, plaque, banner, logo, lilies, rope, atbp. Nagre-regenerate ng `ctrl.json` + `ui.json`. |
| `assets/*.json` | Baked sprite data (frames, anchors, background layers, UI sprites, control icons, title tiles). |
| `assets/harness.js` | Headless test rig (Node): nagpa-run ng game logic sa stub canvas at nag-a-assert ng state flow (idle→cast→wait→bite→reel→panel, day/night, shop, atbp). |
| `assets/shoot.js` | Screenshot rig (Node): 11 test shots papuntang `assets/shots/*.ppm`. |
| `assets/minicanvas.js` | Tiny canvas emulator para sa Node rigs. |
| `assets/*.raw.json` | Raw pixel buffers para sa shoot/harness rigs. |

## Requirements
- **Python 3** + `Pillow` (para sa `build.py` at `pxkit.py`)
- **Node.js** (optional, para sa test/screenshot rigs lang)

## Commands
```bash
# 1. I-build ang laro pagkatapos mong i-edit ang template.html:
python3 assets/build.py          # → fishing-sim.html

# 2. I-regenerate ang lahat ng procedural pixel sprites (icons/frames/panel/logo/lilies):
python3 assets/pxkit.py          # → assets/ctrl.json, assets/ui.json (+ preview PNGs)

# 3. Headless tests (walang browser kailangan):
node assets/harness.js           # → "=== ALL TESTS PASSED ==="

# 4. Test screenshots (convert muna ng .ppm → .png pag gusto mong tingnan):
node assets/shoot.js
```

## Workflow sa IDE mo
1. Buksan ang `template.html` — dito ang buong game code (CSS + JS + HTML).
2. Hanapin ang `__PLACEHOLDER__` tokens — pinapalitan yan ng `build.py` ng sprite data.
3. Pag tapos ng edit: `python3 assets/build.py`, tapos `node assets/harness.js` para sa regression tests.
4. Pag gusto mong baguhin ang pixel art ng buttons/icons/logo: i-edit ang pixel maps sa
   `assets/pxkit.py` (strings ng characters = pixel rows), then `python3 assets/pxkit.py`
   at `python3 assets/build.py`.

## Paano gumagana ang layers ng background (sa `draw()` ng template)
1. Baked base scene (day/night crossfade)
2. Stars / shooting star / birds / sun v2 / moon v2
3. **Ridge layer** (mountains+trees, alpha) — lumulubad sa likod nito ang sun/moon
4. Water: mirrored scene reflection slices, wave crests, foam, sparkles, sun/moon glitter
5. Fish shadow → ripples
6. **Shore layer** (grass+bank, alpha) — dumaan sa ilalim ng damo ang shadow
7. Reeds / drifting leaf / fireflies
8. Line+bobber → character → HUD plaques

Enjoy! 🎣

## Optional: full offline PWA
See `pwa/README-PWA.md`. The single HTML already ships an inline manifest +
icons (PWA-ready); the `pwa/` folder adds `sw.js` + external manifest so a
hosted copy becomes installable and fully offline.
