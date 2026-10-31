#!/usr/bin/env python3
"""Pagkatapos mag-build (python3 assets/build.py), patakbuhin ito sa dev/:
   python3 make_pages.py   ->  isinusulat ang bagong index.html sa repo root
   (swaps inline manifest -> external manifest.webmanifest + sw.js registration)"""
import re, os
h = open(os.path.join(os.path.dirname(__file__), 'fishing-sim.html')).read()
h, n = re.subn(r'<link rel="manifest" href="data:application/manifest\+json,[^"]*">',
               '<link rel="manifest" href="manifest.webmanifest">', h)
assert n == 1, 'manifest link not found - bada build?'
if 'serviceWorker' not in h:
    h = h.replace('</body>', "<script>\nif ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js');\n</script>\n</body>", 1)
out = os.path.join(os.path.dirname(__file__), '..', 'index.html')
open(out, 'w').write(h)
print('root index.html updated:', len(h), 'bytes')
