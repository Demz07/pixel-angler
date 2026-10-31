#!/usr/bin/env python3
"""pxkit.py v2 - procedural studio-style pixel-art UI kit (Aseprite-look).
Icons, frames, panel, plaque, rope divider, pixel-font game logo. All code-drawn."""
from PIL import Image
import base64, io, json, math

OUT = (26, 14, 6)
RAMPS = {
    'C': ((255, 248, 232), (244, 228, 192), (198, 166, 118)),
    'R': ((244, 130, 110), (226, 88, 74), (168, 48, 40)),
    'W': ((255, 255, 255), (246, 246, 238), (206, 206, 192)),
    'G': ((255, 236, 160), (255, 215, 94), (198, 156, 46)),
    'B': ((210, 164, 100), (178, 128, 66), (132, 90, 42)),
    'b': ((172, 122, 64), (140, 96, 46), (102, 66, 30)),
    'K': ((70, 52, 40), (30, 20, 14), (16, 10, 6)),
    'M': ((190, 190, 204), (90, 90, 102), (52, 52, 64)),
    'V': ((150, 214, 120), (92, 162, 82), (52, 112, 52)),
    'v': ((96, 150, 80), (58, 110, 55), (34, 74, 36)),
    'P': ((255, 205, 224), (240, 150, 180), (198, 96, 138)),
    'U': ((168, 224, 244), (96, 164, 214), (52, 112, 172)),
}

def render(rows, shade=True, hilite=True, ocol=OUT):
    h = len(rows); w = max(len(r) for r in rows)
    grid = [[None] * w for _ in range(h)]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.':
                grid[y][x] = ch
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); px = im.load()
    def at(x, y):
        return grid[y][x] if 0 <= x < w and 0 <= y < h else None
    for y in range(h):
        for x in range(w):
            ch = grid[y][x]
            if not ch:
                continue
            hi, base, sh = RAMPS[ch]
            col = base
            if shade and not at(x, y + 1):
                col = sh
            elif hilite and not at(x, y - 1):
                col = hi
            px[x, y] = (*col, 255)
    for y in range(h):
        for x in range(w):
            if grid[y][x]:
                continue
            nb = any(at(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0))
            if nb:
                px[x, y] = (*ocol, 255)
    return im

ICONS = {}
ICONS['arrow'] = [
 '................','................','......C.........','.....CC.........',
 '....CCC.........','...CCCC.........','..CCCCC.........','.CCCCCCCCCCCCC..',
 '.CCCCCCCCCCCCC..','..CCCCC.........','...CCCC.........','....CCC.........',
 '.....CC.........','......C.........','................','................']
ICONS['hook'] = [
 '................','.....CCC........','....C...C.......','....C...C.......',
 '.....CCC........','......CC........','......CC........','......CC........',
 '......CC........','......CCC.......','.....CC.........','....CC.....C....',
 '....CC....CC....','.....CC..CC.....','......CCCC......','................']
ICONS['bobber'] = [
 '................','.......KK.......','.......KK.......','......RRRR......',
 '.....RRRRRR.....','....RRRRRRRR....','....RRRRRRRR....','....WWWWWWWW....',
 '....WWWWWWWW....','.....WWWWWW.....','......WWWW......','.......KK.......',
 '................','................','................','................']
ICONS['note'] = [
 '................','....CCCCCCC.....','....CCCCCCC.....','....CC...CC.....',
 '....CC...CC.....','....CC...CC.....','....CC...CC.....','....CC...CC.....',
 '..CCCC...CCCC...','.CCCCC..CCCCC...','.CCCCC..CCCCC...','..CCC....CCC....',
 '................','................','................','................']
ICONS['speak'] = [
 '................','................','...CC...........', '...CCC..........',
 '...CCCC.........','...CCCC..C......','...CCCC.C.C.....','...CCCC.C.C.....',
 '...CCCC..C......','...CCC..........','...CC...........','................',
 '................','................','................','................']
ICONS['bag'] = [
 '................','......CC........','.....C..C.......','....C....C......',
 '...BBBBBBBB.....','...BBBBBBBB.....','....BbBBbB......','....BBBBBB......',
 '....BbBBbB......','....BBBBBB......','.....BBBB.......','................',
 '................','................','................','................']
ICONS['book'] = [
 '................','...RRRRRRRR.....','...RRRRRRRR.....','...RRCCRRRR.....',
 '...RRCCRRRR.....','...RR.C.RRR.....','...RRRRRRRR.....','...RRRRRRRR.....',
 '...WWWWWWWW.....','...WWWWWWWW.....','................','................',
 '................','................','................','................']
ICONS['scroll'] = [
 '................','.CC........CC...','.CbCCCCCCCbCC...','.CCCCCCCCCCCC...',
 '.CCbbCCCbbCCC...','.CCCCCCCCCCCC...','.CCbbCCCbbCCC...','.CCCCCCCCCCCC...',
 '.CbCCCCCCCbCC...','.CC........CC...','................','................',
 '................','................','................','................']
ICONS['x'] = [
 '................','................','..CC......CC....','..CCC....CCC....',
 '...CCC..CCC.....','....CCCCCC......','.....CCCC.......','.....CCCC.......',
 '....CCCCCC......','...CCC..CCC.....','..CCC....CCC....','..CC......CC....',
 '................','................','................','................']
ICONS['coin'] = [
 '................','......GGGG......','....GGGGGGGG....','...GGGGGGGGGG...',
 '...GGbbbGGGGG...','...GGbGGbGGGG...','...GGbGGbGGGG...','...GGbbbGGGGG...',
 '...GGbGGGGGGG...','...GGbGGGGGGG...','...GGGGGGGGGG...','....GGGGGGGG....',
 '......GGGG......','................','................','................']

# ---------------- 5x7 pixel font ----------------
FONT = {
 'P': ['CCCC.','CC..C','CC..C','CCCC.','CC...','CC...','CC...'],
 'I': ['CCCCC','..CC.','..CC.','..CC.','..CC.','..CC.','CCCCC'],
 'X': ['CC.CC','CC.CC','.CCC.','..C..','.CCC.','CC.CC','CC.CC'],
 'E': ['CCCCC','CCCCC','CC...','CCCC.','CCCC.','CC...','CCCCC'],
 'L': ['CC...','CC...','CC...','CC...','CC...','CC...','CCCCC'],
 'A': ['.CCC.','CC.CC','CC.CC','CCCCC','CCCCC','CC.CC','CC.CC'],
 'N': ['CC.CC','CCC.C','CCC.C','CCCCC','C.CCC','C.CCC','CC.CC'],
 'G': ['.CCCC','CC...','CC...','CC.CC','CC.CC','CC.CC','.CCCC'],
 'R': ['CCCC.','CC.CC','CC.CC','CCCC.','CCC.C','CC.CC','CC.CC'],
 'S': ['.CCCC','CC...','CC...','.CCCC','...CC','...CC','CCCC.'],
 'D': ['CCCC.','CC.CC','CC.CC','CC.CC','CC.CC','CC.CC','CCCC.'],
 '!': ['..CC.','..CC.','..CC.','..CC.','..CC.','.....','..CC.'],
 'C': ['.CCCC','CC...','CC...','CC...','CC...','CC...','.CCCC'],
 'K': ['CC.CC','CC.CC','CCCC.','CCC..','CC.CC','CC.CC','CC.CC'],
 'W': ['CC.CC','CC.CC','CC.CC','C.C.C','C.C.C','CCCCC','CC.CC'],
 'Y': ['CC.CC','CC.CC','.CCC.','..CC.','..CC.','..CC.','..CC.'],
 'F': ['CCCCC','CCCCC','CC...','CCCC.','CCCC.','CC...','CC...'],
 'V': ['CC.CC','CC.CC','CC.CC','CC.CC','CC.CC','.CCC.','..CC.'],
 'H': ['CC.CC','CC.CC','CC.CC','CCCCC','CCCCC','CC.CC','CC.CC'],
 'Q': ['.CCC.','CC.CC','CC.CC','CC.CC','C.CCC','CC.CC','.CCCC'],
 'T': ['CCCCC','CCCCC','..CC.','..CC.','..CC.','..CC.','..CC.'],
 'O': ['.CCC.','CC.CC','CC.CC','CC.CC','CC.CC','CC.CC','.CCC.'],
 'U': ['CC.CC','CC.CC','CC.CC','CC.CC','CC.CC','CC.CC','.CCC.'],
 'M': ['CC.CC','CCCCC','CCCCC','C.C.C','C.C.C','C.C.C','C.C.C'],
 ' ': ['.....','.....','.....','.....','.....','.....','.....'],
}

def logo(text):
    import math as _m
    chars = list(text)
    rows = ['...'.join(FONT[c][y] for c in chars) for y in range(7)]
    w = len(rows[0])
    PAD = 2
    h = 7 + PAD * 2
    grid = [[None] * w for _ in range(h)]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.':
                grid[y + PAD][x] = ch
    # wavy baseline: shift each letter block vertically in the padded grid
    for ci in range(len(chars)):
        x0 = ci * 8
        off = round(_m.sin(ci * 0.9) * 1.2)
        if off == 0: continue
        blk = [row[x0:x0 + 5] for row in grid]
        nb = [[None] * 5 for _ in range(h)]
        for y in range(h):
            sy = y - off
            for x in range(5):
                nb[y][x] = blk[sy][x] if 0 <= sy < h else None
        for y in range(h):
            for x in range(5):
                grid[y][x0 + x] = nb[y][x]
    GOLDS = [(255, 246, 200), (255, 236, 160), (255, 215, 94), (224, 178, 64)]
    im = Image.new('RGBA', (w, h), T); px = im.load()
    def at(x, y):
        return grid[y][x] if 0 <= x < w and 0 <= y < h else None
    for y in range(h):
        for x in range(w):
            if not grid[y][x]: continue
            ci = x // 8
            gy = y - PAD - round(_m.sin(ci * 0.9) * 1.2)
            band = 0 if gy < 2 else (1 if gy < 4 else (2 if gy < 5 else 3))
            px[x, y] = (*GOLDS[max(0, min(3, band))], 255)
    for y in range(h):
        for x in range(w):
            if grid[y][x]: continue
            if any(at(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)):
                px[x, y] = (*OUT, 255)
    sh = Image.new('RGBA', (w + 2, h + 5), T)
    mask = im.split()[3]
    shadow = Image.new('RGBA', im.size, (22, 28, 58, 255))
    sh.paste(shadow, (2, 2), mask)
    sh.paste(im, (0, 0), im)
    px = sh.load()
    uy = sh.height - 3
    for x in range(sh.width):
        crest = (x % 8) < 3
        wcol = (168, 224, 244) if crest else (96, 164, 214)
        px[x, uy] = (*wcol, 255)
        px[x, uy + 1] = (52, 112, 172, 255)
        px[x, uy + 2] = (30, 70, 120, 255)
        if x % 16 == 2 and crest:
            px[x, uy - 1] = (246, 252, 255, 255)
    fx = w // 2 - 3
    for dx, dy in ((0, 1), (1, 0), (1, 1), (1, 2), (2, 1), (3, 1), (4, 0), (4, 2), (5, 1)):
        px[fx + dx, uy + dy] = (20, 40, 80, 255)
    return sh

# ---------------- frames (v2 detail) ----------------
W1 = (210, 164, 100); W2 = (178, 128, 66); W3 = (140, 96, 46); W4 = (102, 66, 30)
C1 = (255, 248, 232); C2 = (244, 228, 192); C3 = (198, 166, 118)
M1 = (150, 150, 164); M2 = (52, 52, 64); MH = (190, 190, 204); G2 = (206, 164, 52)
REC = (46, 26, 12); RECI = (24, 12, 6); REC2 = (66, 40, 18)
T = (0, 0, 0, 0)

def btn(pressed):
    im = Image.new('RGBA', (24, 24), T); px = im.load(); c = 11.5
    hi, sh = (W4, W1) if pressed else (W1, W4)
    rec = REC2 if pressed else REC
    for y in range(24):
        for x in range(24):
            d = math.hypot(x - c, y - c)
            if d <= 11.5:
                if d > 9.8: px[x, y] = (*OUT, 255)
                elif d > 8.2: px[x, y] = (*(hi if (x + y) < 23 else sh), 255)
                elif d > 6.4:
                    px[x, y] = (*W2, 255)
                    if (x * 7 + y * 11) % 17 == 0: px[x, y] = (*W3, 255)
                else:
                    px[x, y] = (*rec, 255)
                    if d > 4.6 and y < c - 3.0: px[x, y] = (*(RECI if not pressed else REC), 255)
    for sx, sy in ((6, 4), (4, 6)):  # specular glints on the bevel
        px[sx, sy] = (*C1, 255)
    for rx, ry in ((5, 5), (18, 5), (5, 18), (18, 18)):  # rivets w/ highlight
        px[rx, ry] = (*MH, 255); px[rx + 1, ry] = (*M1, 255)
        px[rx, ry + 1] = (*M1, 255); px[rx + 1, ry + 1] = (*M2, 255)
    return im

def plank():
    im = Image.new('RGBA', (16, 16), T); px = im.load()
    for y in range(16):
        for x in range(16):
            cut = (x < 2 and y < 2) or (x > 13 and y < 2) or (x < 2 and y > 13) or (x > 13 and y > 13)
            cut |= (x < 1 and y < 3) or (x > 14 and y < 3) or (x < 1 and y > 12) or (x > 14 and y > 12)
            cut |= (y < 1 and x < 3) or (y < 1 and x > 12) or (y > 14 and x < 3) or (y > 14 and x > 12)
            if cut: continue
            edge = x == 0 or y == 0 or x == 15 or y == 15 or (x == 1 and (y < 3 or y > 12)) or (y == 1 and (x < 3 or x > 12)) or (x == 14 and (y < 3 or y > 12)) or (y == 14 and (x < 3 or x > 12))
            if edge: px[x, y] = (*OUT, 255)
            elif y <= 3: px[x, y] = (*W1, 255)
            elif y >= 12: px[x, y] = (*W4, 255)
            elif y == 8: px[x, y] = (*W3, 255) if x != 8 else (*W2, 255)  # plank seam
            else:
                px[x, y] = (*W2, 255)
                if (x * 7 + y * 13) % 11 == 0: px[x, y] = (*W3, 255)
    for nx, ny in ((3, 3), (12, 3), (3, 12), (12, 12)):
        px[nx, ny] = (*MH, 255); px[nx, ny + 1] = (*M2, 255)
    return im

def rock():
    im = Image.new('RGBA', (48, 24), T); px = im.load()
    def inside(x, y):
        if 12 <= x <= 35: return 0 <= y <= 23
        cx = 12 if x < 12 else 35
        return math.hypot(x - cx, y - 11.5) <= 11.5
    for y in range(24):
        for x in range(48):
            if not inside(x, y): continue
            nb = not (inside(x - 1, y) and inside(x + 1, y) and inside(x, y - 1) and inside(x, y + 1))
            nb2 = not (inside(x - 2, y) and inside(x + 2, y) and inside(x, y - 2) and inside(x, y + 2))
            if x in (23, 24): px[x, y] = (*OUT, 255)
            elif x == 22: px[x, y] = (*W4, 255)
            elif x == 25: px[x, y] = (*W1, 255)
            elif nb or nb2: px[x, y] = (*OUT, 255)
            elif y <= 3: px[x, y] = (*W1, 255)
            elif y >= 20: px[x, y] = (*W4, 255)
            elif x in (4, 5) or x in (42, 43): px[x, y] = (*W3, 255)  # end caps
            else:
                px[x, y] = (*W2, 255)
                if (x * 5 + y * 9) % 13 == 0: px[x, y] = (*W3, 255)
    for nx, ny in ((6, 11), (41, 11)):
        px[nx, ny] = (*MH, 255); px[nx, ny + 1] = (*M2, 255)
    px[8, 4] = (*C1, 255); px[39, 4] = (*C1, 255)
    return im

def panel():
    im = Image.new('RGBA', (24, 24), T); px = im.load()
    for y in range(24):
        for x in range(24):
            m = min(x, y, 23 - x, 23 - y)
            if m == 0: px[x, y] = (*OUT, 255)
            elif m == 1: px[x, y] = (*(W1 if (x + y) < 23 else W4), 255)
            elif m == 2: px[x, y] = (*W2, 255) if (x + y) % 6 else (*W3, 255)  # plank seams
            elif m == 3: px[x, y] = (*W3, 255)
            elif m == 4: px[x, y] = (*OUT, 255)
            elif m == 5: px[x, y] = (*W4, 255)
            else:
                px[x, y] = (*W2, 255)
                if (x * 3 + y * 7) % 23 == 0: px[x, y] = (*W3, 255)
    for bx, by in ((1, 1), (21, 1), (1, 21), (21, 21)):
        px[bx, by] = (*MH, 255); px[bx + 1, by] = (*M1, 255)
        px[bx, by + 1] = (*M1, 255); px[bx + 1, by + 1] = (*M2, 255)
    return im

def plaque():
    im = Image.new('RGBA', (32, 16), T); px = im.load()
    for y in range(16):
        for x in range(32):
            m = min(x, y, 31 - x, 15 - y)
            cut = (x < 2 and y < 2) or (x > 29 and y < 2) or (x < 2 and y > 13) or (x > 29 and y > 13)
            if cut: continue
            if m == 0: px[x, y] = (*OUT, 255)
            elif m == 1: px[x, y] = (*W2, 255)
            elif m == 2: px[x, y] = (*(W1 if y < 8 else W3), 255)
            else:
                px[x, y] = (*C2, 255)
                if y == 3: px[x, y] = (*C1, 255)
                elif y == 12: px[x, y] = (*C3, 255)
                elif y in (4, 11) and 3 < x < 28: px[x, y] = (*(232, 214, 176), 255)  # inner pinline
    for nx, ny in ((1, 1), (29, 1), (1, 13), (29, 13)):
        px[nx, ny] = (*G2, 255)
    return im

def sep():
    im = Image.new('RGBA', (6, 24), T); px = im.load()
    for y in range(24):
        col = (178, 128, 66) if (y % 4) < 2 else (140, 96, 46)
        col2 = (198, 166, 118) if (y % 4) < 2 else (178, 128, 66)
        px[2, y] = (*col, 255); px[3, y] = (*col2, 255)
    for y in (10, 11, 12, 13):  # knot
        px[1, y] = (*OUT, 255); px[4, y] = (*OUT, 255)
        px[2, y] = (198, 166, 118, 255); px[3, y] = (178, 128, 66, 255)
    px[2, 11] = (140, 96, 46, 255); px[3, 12] = (140, 96, 46, 255)
    return im


def banner():
    im = Image.new('RGBA', (48, 16), T); px = im.load()
    for y in range(16):
        for x in range(48):
            # tails with notch
            if x < 8 or x > 39:
                if y < 3 or y > 12: continue
                notch = (x < 3 and (y == 7 or y == 8)) or (x > 44 and (y == 7 or y == 8))
                if notch: continue
                if x in (0, 1) or x in (46, 47) or y in (3, 12):
                    px[x, y] = (*OUT, 255)
                elif y == 4: px[x, y] = (*W1, 255)
                elif y == 11: px[x, y] = (*W4, 255)
                else: px[x, y] = (*W3, 255)
            elif x in (8, 9) or x in (38, 39):   # fold
                if y < 2 or y > 13: continue
                px[x, y] = (*OUT, 255) if (x in (8, 39) and (y in (2, 13))) else (*W4, 255)
            else:                                 # parchment face
                if y < 2 or y > 13: continue
                if y == 2 or x == 10 or x == 37: px[x, y] = (*OUT, 255)
                elif y == 13 or x == 11 or x == 36: px[x, y] = (*OUT, 255)
                elif y == 3: px[x, y] = (*C1, 255)
                elif y == 12: px[x, y] = (*C3, 255)
                else: px[x, y] = (*C2, 255)
    for nx, ny in ((10, 3), (37, 3), (10, 12), (37, 12)):
        px[nx, ny] = (*G2, 255)
    return im


def joybase():
    im = Image.new('RGBA', (28, 28), T); px = im.load(); c = 13.5
    for y in range(28):
        for x in range(28):
            d = math.hypot(x - c, y - c)
            if d <= 13.5:
                if d > 11.8: px[x, y] = (*OUT, 255)
                elif d > 10.2: px[x, y] = (*(W1 if (x + y) < 27 else W4), 255)
                elif d > 8.8: px[x, y] = (*W3, 255)
                else:
                    px[x, y] = (*REC, 255)
                    if d > 6.8 and y < c - 2: px[x, y] = (*RECI, 255)
    # cream arrow hints left/right inside the recess
    for i in range(4):
        for yy in range(-i, i + 1):
            px[6 + i, 13 + yy] = (*C3, 255)
            px[21 - i, 13 + yy] = (*C3, 255)
    px[6, 13] = (*C2, 255); px[21, 13] = (*C2, 255)
    return im

def joyknob():
    im = Image.new('RGBA', (16, 16), T); px = im.load(); c = 7.5
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - c, y - c)
            if d <= 7.5:
                if d > 6.2: px[x, y] = (*OUT, 255)
                elif d > 4.6: px[x, y] = (*(W1 if (x + y) < 15 else W4), 255)
                else: px[x, y] = (*W2, 255)
    px[5, 4] = (*C1, 255); px[4, 5] = (*C1, 255)
    return im

def geartab():
    """Vertical wood drawer-tab (18x40) with a cream gear/settings icon."""
    Wd, Ht = 18, 40
    im = Image.new('RGBA', (Wd, Ht), T); px = im.load()
    for y in range(Ht):
        for x in range(Wd):
            cut = (y < 3 and x < 3 - y) or (y > Ht - 4 and x < y - (Ht - 4))
            if cut: continue
            edge = (x == 0 and y >= 3 and y <= Ht - 4) or y == 0 or y == Ht - 1 or \
                   (x == 1 and (y == 1 or y == Ht - 2)) or (x == 2 and (y == 0 or y == Ht - 1))
            if edge: px[x, y] = (*OUT, 255); continue
            if x <= 2: px[x, y] = (*W1, 255)
            elif y <= 2: px[x, y] = (*W1, 255)
            elif y >= Ht - 3: px[x, y] = (*W4, 255)
            elif x >= Wd - 1: px[x, y] = (*W3, 255)
            else:
                px[x, y] = (*W2, 255)
                if (x * 7 + y * 13) % 11 == 0: px[x, y] = (*W3, 255)
    # plank seams + nails
    for x in range(3, Wd):
        px[x, 8] = (*W3, 255); px[x, Ht - 9] = (*W3, 255)
    for ny in (5, Ht - 6):
        px[5, ny] = (*OUT, 255); px[6, ny] = (*W4, 255)
        px[12, ny] = (*OUT, 255); px[13, ny] = (*W4, 255)
    # gear: cream ring + dark hub
    gx, gy = 8.5, 19.5
    for y in range(Ht):
        for x in range(Wd):
            d = math.hypot(x - gx, y - gy)
            if 3.0 <= d <= 5.2:
                px[x, y] = (*(C1 if (x + y) < gx + gy - 2 else C2), 255)
            elif d <= 1.7:
                px[x, y] = (*OUT, 255)
    # 8 teeth (2x2 blocks)
    for k in range(8):
        a = k * math.pi / 4
        tx = int(round(gx + math.cos(a) * 5.9)) - (1 if math.cos(a) > 0.3 else 0)
        ty = int(round(gy + math.sin(a) * 5.9)) - (1 if math.sin(a) > 0.3 else 0)
        for dy in (0, 1):
            for dx in (0, 1):
                if 0 <= tx + dx < Wd and 0 <= ty + dy < Ht:
                    px[tx + dx, ty + dy] = (*(C1 if dx == 0 and dy == 0 else C2), 255)
    return im

def uri(im):
    b = io.BytesIO(); im.save(b, format='PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

ctrl = {}
for name, rows in ICONS.items():
    im = render(rows)
    ctrl[name] = uri(im)
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(f'assets/ic-{name}.png')
ICONS['fishJ'] = [
 '...RRRR.......','..RRRRRRR.RR..','.RKWRRRRRRRRR.','.RWRRRRRRRRR..',
 '..RRRRRRRR....','...RR..RR.....']
ctrl['fishJ'] = uri(render(ICONS['fishJ']))
ctrl['joyb'] = uri(joybase())
ctrl['joyk'] = uri(joyknob())
ctrl['geartab'] = uri(geartab())

# ---------------- 8 generated water lily variants ----------------
import random as _rnd
def gen_lily(seed):
    rnd = _rnd.Random(seed)
    size = rnd.choice([10, 12, 13, 14])
    notch = rnd.choice([0, 1, 2, 3])          # 0=right 1=left 2=top 3=bottom
    flower = rnd.choice([None, 'P', 'W', 'G', 'P'])
    w = h = size + 4
    cx = cy = (size + 3) / 2
    rows = [['.' for _ in range(w)] for _ in range(h)]
    import math
    na = notch * math.pi / 2
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            if d > size / 2: continue
            ang = math.atan2(dy, dx)
            if abs((ang - na + math.pi) % (2 * math.pi) - math.pi) < 0.5 and d > size * 0.18:
                continue
            ch = 'V'
            if 1 < d < size / 2 - 1:
                for k in range(4):
                    va = k * math.pi / 4 + 0.4
                    if abs((ang - va + math.pi) % (2 * math.pi) - math.pi) < 0.16:
                        ch = 'v'
            rows[y][x] = ch
    if flower:
        fc = rnd.randrange(-1, 2)
        fx, fy = int(cx) + fc, int(cy) - 1
        pet = [(0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2), (0, -1), (0, 1), (-1, 0), (1, 0)]
        for px_, py_ in pet:
            xx, yy = fx + px_, fy + py_
            if 0 <= xx < w and 0 <= yy < h:
                rows[yy][xx] = flower if (px_, py_) != (0, 0) else ('G' if flower != 'G' else 'W')
    return [''.join(r) for r in rows]

SOFT = (44, 92, 48)
for i in range(8):
    ctrl['lily%d' % i] = uri(render(gen_lily(i), ocol=SOFT))
for k in [k for k in ctrl if k.startswith(('frog', 'snail'))]:
    del ctrl[k]
ctrl['fr'] = uri(btn(False)); ctrl['frp'] = uri(btn(True))
ctrl['plank'] = uri(plank()); ctrl['rock'] = uri(rock())
ctrl['sep'] = uri(sep())
lg = logo('PIXEL ANGLER')
ctrl['logo'] = uri(lg)
json.dump(ctrl, open('assets/ctrl.json', 'w'))
ui = {'panel': uri(panel()), 'plaque': uri(plaque()), 'banner': uri(banner())}
json.dump(ui, open('assets/ui.json', 'w'))
lg.resize((lg.width * 5, lg.height * 5), Image.NEAREST).save('assets/px-logo.png')
btn(False).resize((96, 96), Image.NEAREST).save('assets/px-btn.png')
joybase().resize((112, 112), Image.NEAREST).save('assets/px-joybase.png')
joyknob().resize((64, 64), Image.NEAREST).save('assets/px-joyknob.png')
panel().resize((96, 96), Image.NEAREST).save('assets/px-panel.png')
print('pxkit v2 baked; logo', lg.size)
