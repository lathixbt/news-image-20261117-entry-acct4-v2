"""News front page: Tuesday 17 November 2026. 30 verified stories.

Draws a 1024x1024 newspaper front page with PIL only. Deterministic:
fixed story list, fixed layout, no network, no randomness, no time.
Run: python3 draw.py  ->  writes entry.png next to this file.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- colours ----------
NAVY = (15, 36, 64)
NAVY2 = (22, 52, 92)
GOLD = (212, 175, 88)
PAPER = (250, 247, 238)
PANEL = (255, 255, 255)
INK = (24, 24, 24)
GREY = (92, 92, 92)
LGREY = (150, 150, 150)
LINE = (200, 196, 186)
OCEAN = (216, 232, 238)
LAND = (233, 216, 182)
LANDLINE = (168, 140, 96)
RED = (178, 34, 34)

REGION = {
    "Europe": (31, 79, 163),
    "Middle East": (201, 110, 24),
    "Asia": (178, 44, 36),
    "Africa": (38, 122, 52),
    "Americas": (117, 58, 158),
    "Oceania": (14, 124, 123),
    "Global": (96, 96, 96),
}

# ---------- fonts ----------
FD = "/usr/share/fonts/truetype/dejavu/"
_font_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FD + name, size)
    return _font_cache[key]


def serif_b(s):
    return F("DejaVuSerif-Bold.ttf", s)


def serif(s):
    return F("DejaVuSerif.ttf", s)


def sans_b(s):
    return F("DejaVuSans-Bold.ttf", s)


def sans(s):
    return F("DejaVuSans.ttf", s)


# ---------- text helpers ----------
def wrap(d, text, font, max_w):
    """Greedy word wrap by pixel width; hard-breaks overlong words."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        while d.textlength(w, font=font) > max_w:
            # split the long word itself
            cut = len(w)
            while cut > 1 and d.textlength(w[:cut], font=font) > max_w:
                cut -= 1
            lines.append(w[:cut])
            w = w[cut:]
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, font, fill, lh=None, align="left", width=None):
    if lh is None:
        lh = font.size + 3
    for i, ln in enumerate(lines):
        xx = x
        if align == "center" and width is not None:
            xx = x + (width - d.textlength(ln, font=font)) / 2
        d.text((xx, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def trunc(d, text, font, max_w):
    if d.textlength(text, font=font) <= max_w:
        return text
    while text and d.textlength(text + "…", font=font) > max_w:
        text = text[:-1]
    return text + "…"


def star(d, cx, cy, r_out, r_in, n=5, fill=None, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def burst(d, cx, cy, r, fill):
    """Explosion burst: jagged star + core."""
    pts = []
    for i in range(16):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(i * 22.5)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)
    d.ellipse([cx - r * 0.32, cy - r * 0.32, cx + r * 0.32, cy + r * 0.32],
              fill=(255, 214, 90))


# ---------- flags (simple, accurate geometry) ----------
def flag_us(d, x, y, w, h):
    sh = h / 13.0
    for i in range(13):
        d.rectangle([x, y + i * sh, x + w, y + (i + 1) * sh],
                    fill=(178, 34, 34) if i % 2 == 0 else (255, 255, 255))
    cw, ch = w * 0.4, sh * 7
    d.rectangle([x, y, x + cw, y + ch], fill=(30, 50, 110))
    for r in range(5):
        for c in range(6):
            px = x + cw * (c + 0.5) / 6.0
            py = y + ch * (r + 0.5) / 5.0
            d.ellipse([px - 1.2, py - 1.2, px + 1.2, py + 1.2], fill=(255, 255, 255))


def flag_mx(d, x, y, w, h):
    d.rectangle([x, y, x + w / 3, y + h], fill=(0, 104, 71))
    d.rectangle([x + w / 3, y, x + 2 * w / 3, y + h], fill=(255, 255, 255))
    d.rectangle([x + 2 * w / 3, y, x + w, y + h], fill=(206, 17, 38))
    d.ellipse([x + w / 2 - 3, y + h / 2 - 3, x + w / 2 + 3, y + h / 2 + 3],
              fill=(120, 70, 20))


def flag_bo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(213, 0, 50))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(247, 219, 0))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(0, 122, 61))


def flag_il(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.12, x + w, y + h * 0.28], fill=(0, 56, 184))
    d.rectangle([x, y + h * 0.72, x + w, y + h * 0.88], fill=(0, 56, 184))
    cx, cy, r = x + w / 2, y + h / 2, h * 0.30
    for sgn in (1, -1):
        pts = []
        for i in range(3):
            a = math.radians(-90 + sgn * i * 120)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, outline=(0, 56, 184), width=2)


def flag_fr(d, x, y, w, h):
    d.rectangle([x, y, x + w / 3, y + h], fill=(0, 60, 140))
    d.rectangle([x + w / 3, y, x + 2 * w / 3, y + h], fill=(255, 255, 255))
    d.rectangle([x + 2 * w / 3, y, x + w, y + h], fill=(210, 30, 40))


def flag_tr(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(227, 10, 23))
    cx, cy, r = x + w * 0.42, y + h / 2, h * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    d.ellipse([cx - r * 0.82 + r * 0.25, cy - r * 0.82,
               cx + r * 0.82 + r * 0.25, cy + r * 0.82], fill=(227, 10, 23))
    star(d, x + w * 0.66, cy, h * 0.17, h * 0.07, fill=(255, 255, 255))


def flag_mn(d, x, y, w, h):
    d.rectangle([x, y, x + w / 3, y + h], fill=(197, 30, 36))
    d.rectangle([x + w / 3, y, x + 2 * w / 3, y + h], fill=(0, 80, 160))
    d.rectangle([x + 2 * w / 3, y, x + w, y + h], fill=(197, 30, 36))
    cx = x + w / 6
    d.ellipse([cx - 2.5, y + h * 0.14, cx + 2.5, y + h * 0.14 + 5],
              fill=(247, 219, 0))
    d.rectangle([cx - 1, y + h * 0.30, cx + 1, y + h * 0.72],
                fill=(247, 219, 0))
    d.rectangle([cx - 4, y + h * 0.78, cx + 4, y + h * 0.86],
                fill=(247, 219, 0))


def flag_bd(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 106, 78))
    cx, cy, r = x + w * 0.45, y + h / 2, h * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(244, 42, 65))


def flag_ph(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 2], fill=(0, 56, 147))
    d.rectangle([x, y + h / 2, x + w, y + h], fill=(206, 17, 38))
    d.polygon([(x, y), (x, y + h), (x + w * 0.45, y + h / 2)],
              fill=(255, 255, 255))
    star(d, x + w * 0.16, y + h / 2, 3.2, 1.4, fill=(247, 219, 0))


FLAGS = {"US": flag_us, "MX": flag_mx, "BO": flag_bo, "IL": flag_il,
         "FR": flag_fr, "TR": flag_tr, "MN": flag_mn, "BD": flag_bd,
         "PH": flag_ph}


def draw_flag(d, code, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=(120, 120, 120), width=1)
    FLAGS[code](d, x + 1, y + 1, w - 2, h - 2)


# ---------- story data ----------
# lon/lat are the true locations; None = placeless (GLOBAL box on map).
MAINS = [
    dict(n=1, region="Europe", kicker="EUROPE · UKRAINE WAR",
         head="Ukraine strikes Crimean Bridge for a second day",
         desc="Two killed, road shut; road section fell into the Kerch Strait",
         lon=37.5, lat=45.3),
    dict(n=2, region="Middle East", kicker="MIDDLE EAST · IRAN WAR",
         head="Iran fires drones at US radar in Bahrain",
         desc="Bahrain says all intercepted; US strikes Qeshm Island",
         lon=50.6, lat=26.2),
    dict(n=3, region="Europe", kicker="EUROPE · UKRAINE WAR",
         head="Russian strikes hit Kyiv bridges",
         desc="Water, power hit; UN toll worst since 2022",
         lon=30.5, lat=50.45),
    dict(n=4, region="Americas", kicker="AMERICAS · HEALTH",
         head="Americas lose measles-free status",
         desc="PAHO: US held it 26 years; 5,400+ cases",
         lon=-77.0, lat=39.0),
    dict(n=5, region="Africa", kicker="AFRICA · HEALTH",
         head="DR Congo Ebola cases double",
         desc="WHO: 11,000+ cases, 5,400 deaths",
         lon=23.0, lat=-2.5),
    dict(n=6, region="Asia", kicker="ASIA · DIPLOMACY",
         head="Manila minerals deals",
         desc="Trump's Manila announcement",
         lon=121.0, lat=14.6),
    dict(n=7, region="Middle East", kicker="MIDDLE EAST · POLITICS",
         head="Eisenkot ally elected speaker",
         desc="Kahana wins 66-52 after six-hour filibuster",
         lon=35.2, lat=31.8),
    dict(n=8, region="Global", kicker="GLOBAL · CLIMATE",
         head="COP31 final days split on fossil fuels",
         desc="Antalya split; Robinson: 'vital'",
         lon=30.7, lat=36.9),
    dict(n=9, region="Asia", kicker="ASIA · POLITICS",
         head="Mongolia's president to resign",
         desc="$25m rail link alleged; he denies",
         lon=106.9, lat=47.9),
    dict(n=10, region="Europe", kicker="EUROPE · LABOUR",
         head="French public workers strike over pay",
         desc="146,000 march; CGT claims 500,000+",
         lon=2.35, lat=48.85),
    dict(n=11, region="Asia", kicker="ASIA · LABOUR",
         head="Police tear-gas Dhaka workers",
         desc="Wage to 30,000 taka; 525 factories halted",
         lon=90.4, lat=23.8),
    dict(n=12, region="Global", kicker="GLOBAL · SPACE",
         head="Two black holes in one early galaxy",
         desc="Pair of quasars in one galaxy",
         lon=None, lat=None),
]

BRIEFS = [
    (13, "Asia", "Suspected Russian jets enter Japanese airspace",
     "Tokyo scrambles fighters and protests.", 139.7, 35.7),
    (14, "Africa", "Five EU states plan migrant return hub in Rwanda",
     "First transfers in 2027; HRW warns of law risk.", 30.0, -2.0),
    (15, "Asia", "Xi and Carney agree new tariff cuts",
     "China cuts duties on C$400m pork and seafood.", 116.4, 39.9),
    (16, "Europe", "UK sanctions eight settlement builders and Tzav 9",
     "Asset freezes target West Bank builders.", -0.1, 51.5),
    (17, "Europe", "Turkey takes Sozcu TV off air",
     "Raid on opposition channel; four executives held.", 29.0, 41.0),
    (18, "Asia", "An-12 crash in Siberia kills all 19",
     "Military transport down in Kemerovo region.", 86.0, 55.3),
    (19, "Asia", "Macron visit seals Malaysia partnership",
     "Rare-earths curbs eased; defence deals signed.", 101.7, 3.1),
    (20, "Middle East", "West Bank settlers kill woman, 72",
     "Settlers shoot Fadha Wadha near Jericho.", 35.5, 31.9),
    (21, "Middle East", "Gaza winter rains flood shelters",
     "UN: one day of rain damaged tens of thousands of tents.", 34.5, 31.5),
    (22, "Americas", "Venezuela frees 39 political prisoners",
     "Freed after US-backed talks; 344 still held.", -66.9, 10.5),
    (23, "Oceania", "Australia sanctions Israeli settlers",
     "Canberra sanctions settler leader Daniella Weiss.", 149.1, -35.3),
    (24, "Asia", "Bus plunges into gorge in Uttarakhand",
     "At least eight killed; bus falls 100 metres.", 78.0, 30.3),
    (25, "Europe", "Equinor hit by cyberattack",
     "Largest gas supplier hit; output unaffected.", 5.7, 58.9),
    (26, "Europe", "Gas tanker sinks off Bulgaria",
     "LPG tanker Gas Husky sinks; 19 crew rescued.", 28.0, 43.0),
    (27, "Americas", "Wall Street falls for a fourth day",
     "S&P 500 −1.03%, lowest close since July.", -74.0, 40.7),
    (28, "Europe", "Pope Leo XIV returns to Rome after tour",
     "Lands Tuesday after 12-day South America trip.", 12.5, 41.9),
    (29, "Oceania", "Australia backpacker visa curbs eased",
     "Third-year cap raised from 5,000 to 25,000.", 151.2, -33.9),
    (30, "Americas", "Apple outage; firm blames an update",
     "iCloud, App Store, Apple Pay hit.", -122.03, 37.32),
]

ALL = MAINS + [dict(n=n, region=r, head=h, desc=ds, lon=lo, lat=la)
               for (n, r, h, ds, lo, la) in BRIEFS]


# ---------- continents (lon/lat outlines) ----------
N_AMERICA = [(-168, 66), (-161, 58), (-152, 60), (-140, 60), (-135, 58),
             (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
             (-110, 24), (-105, 20), (-97, 16), (-92, 15), (-86, 12),
             (-83, 9), (-79, 9), (-81, 13), (-84, 16), (-87, 15),
             (-88, 18), (-90, 21), (-97, 26), (-93, 30), (-89, 30),
             (-84, 30), (-81, 25), (-80, 32), (-76, 35), (-74, 40),
             (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 47),
             (-60, 52), (-64, 58), (-68, 58), (-72, 62), (-78, 62),
             (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70),
             (-140, 70), (-155, 71), (-165, 68), (-168, 66)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
             (-22, 70), (-20, 74), (-25, 78), (-35, 80), (-50, 80),
             (-58, 76), (-62, 72), (-58, 64)]
S_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
             (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
             (-74, -50), (-70, -54), (-66, -55), (-65, -50), (-62, -42),
             (-57, -38), (-52, -33), (-48, -28), (-41, -23), (-39, -17),
             (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0),
             (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
             (-77, 8), (-79, 9)]
EUROPE = [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 50),
          (2, 51), (4, 53), (8, 54), (8, 57), (10, 58), (7, 59), (5, 60),
          (6, 62), (12, 65), (18, 69), (25, 71), (31, 70), (35, 68),
          (40, 68), (44, 68), (44, 64), (40, 62), (35, 60), (30, 60),
          (28, 58), (24, 58), (21, 55), (19, 54), (16, 54), (13, 54),
          (10, 54), (8, 53), (6, 51), (3, 50), (0, 49), (-2, 47),
          (-2, 44), (-4, 43), (-9, 43)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
      (1, 51), (-3, 50), (-5, 50)]
IRELAND = [(-10, 52), (-8, 51), (-6, 52), (-6, 54), (-8, 55), (-10, 54),
           (-10, 52)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15),
          (-15, 11), (-13, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4),
          (9, 0), (12, -5), (13, -12), (12, -18), (14, -22), (12, -28),
          (16, -33), (20, -35), (26, -34), (32, -29), (35, -24),
          (36, -18), (40, -15), (40, -10), (42, -4), (46, -1), (51, 2),
          (51, 10), (48, 11), (44, 11), (40, 15), (38, 18), (37, 22),
          (35, 28), (32, 31), (30, 32), (25, 32), (20, 32), (15, 32),
          (11, 34), (10, 37), (5, 37), (0, 36), (-6, 35)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25),
              (45, -25), (44, -20), (44, -16)]
ASIA = [(30, 36), (33, 36), (36, 36), (36, 33), (39, 32), (42, 31),
        (44, 30), (48, 30), (50, 29), (54, 27), (57, 25), (61, 25),
        (66, 25), (67, 23), (70, 20), (72, 20), (76, 10), (77, 8),
        (80, 7), (80, 10), (82, 16), (86, 20), (89, 22), (91, 22),
        (92, 21), (94, 17), (97, 16), (98, 10), (100, 8), (101, 6),
        (103, 2), (104, 1), (100, 5), (98, 8), (100, 5), (102, 2),
        (105, -2), (108, -5), (110, -7), (114, -8), (118, -9), (120, -10),
        (125, -9), (128, -5), (130, -2), (132, 0), (135, 1), (138, -2),
        (141, -4), (143, -6), (146, -8), (141, 1), (138, 5), (135, 10),
        (132, 15), (130, 20), (128, 25), (126, 30), (124, 35), (122, 38),
        (120, 40), (122, 42), (126, 45), (130, 48), (135, 50), (138, 52),
        (141, 55), (142, 59), (145, 60), (150, 60), (156, 59), (158, 55),
        (162, 60), (163, 64), (170, 66), (178, 65), (178, 68), (170, 70),
        (160, 70), (150, 72), (140, 72), (130, 72), (120, 73), (110, 74),
        (100, 75), (90, 75), (80, 73), (70, 72), (60, 69), (55, 68),
        (50, 68), (44, 68), (40, 64), (35, 62), (32, 60), (30, 58),
        (30, 55), (28, 50), (26, 46), (24, 44), (22, 42), (20, 41),
        (18, 41), (20, 42), (23, 40), (26, 38), (27, 37), (30, 36)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
         (141, 38), (141, 40), (142, 42), (144, 44), (143, 44), (141, 42),
         (140, 39), (139, 37), (137, 36), (135, 34), (133, 34), (131, 32),
         (130, 31)]
AUSTRALIA = [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
             (114, -22)]
PAPUA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9),
         (147, -9), (143, -8), (138, -8), (134, -5), (131, -1)]
NZ = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
      (175, -41), (172, -43), (168, -46), (167, -45)]
# inland seas drawn back in ocean colour over the land polygons
BALTIC = [(17, 54), (19, 57), (21, 59), (24, 59), (26, 60), (28, 60),
          (30, 60), (28, 58), (24, 58), (21, 55), (19, 54), (17, 54)]
BLACK = [(28, 41), (33, 41), (39, 41), (41, 44), (39, 46), (34, 46),
         (30, 45), (28, 44), (28, 41)]
CASPIAN = [(47, 37), (50, 37), (53, 40), (54, 44), (52, 47), (49, 47),
           (47, 44), (47, 37)]
LAND_POLYS = [N_AMERICA, GREENLAND, S_AMERICA, EUROPE, UK, IRELAND,
              AFRICA, MADAGASCAR, ASIA, JAPAN, AUSTRALIA, PAPUA, NZ]
SEA_POLYS = [BALTIC, BLACK, CASPIAN]

# ---------- map projection ----------
MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 24, 672, 612, 884
LON0, LON1, LAT0, LAT1 = -168, 192, 75, -60


def lonlat_to_xy(lon, lat):
    x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (LAT0 - lat) / (LAT0 - LAT1) * (MAP_Y1 - MAP_Y0)
    return x, y


def spread_dots(positions, min_dist=18.0, iters=400):
    """Repulsion pass: push dot centres apart to >= min_dist, clamped
    inside the map box (10 px margin). Deterministic."""
    pts = [list(p) for p in positions]
    n = len(pts)
    for _ in range(iters):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                dx = pts[j][0] - pts[i][0]
                dy = pts[j][1] - pts[i][1]
                d2 = dx * dx + dy * dy
                if d2 < min_dist * min_dist and d2 > 0.01:
                    d = math.sqrt(d2)
                    push = (min_dist - d) / 2.0
                    ux, uy = dx / d, dy / d
                    pts[i][0] -= ux * push
                    pts[i][1] -= uy * push
                    pts[j][0] += ux * push
                    pts[j][1] += uy * push
                    moved = True
                elif d2 <= 0.01:
                    pts[j][0] += min_dist / 2.0
                    pts[j][1] += min_dist / 2.0
                    moved = True
        for p in pts:
            p[0] = max(MAP_X0 + 10, min(MAP_X1 - 10, p[0]))
            p[1] = max(MAP_Y0 + 10, min(MAP_Y1 - 10, p[1]))
        if not moved:
            break
    return [(p[0], p[1]) for p in pts]


def min_pair_dist(pts):
    best = 1e9
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dx = pts[j][0] - pts[i][0]
            dy = pts[j][1] - pts[i][1]
            best = min(best, math.hypot(dx, dy))
    return best


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=OCEAN)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=LINE, width=1)
    for poly in LAND_POLYS:
        pts = [lonlat_to_xy(lo, la) for lo, la in poly]
        d.polygon(pts, fill=LAND, outline=LANDLINE)
    for poly in SEA_POLYS:
        pts = [lonlat_to_xy(lo, la) for lo, la in poly]
        d.polygon(pts, fill=OCEAN)
    # graticule
    for lon in range(-150, 181, 30):
        x, _ = lonlat_to_xy(lon, 0)
        d.line([(x, MAP_Y0), (x, MAP_Y1)], fill=(190, 205, 212), width=1)
    for lat in (60, 30, 0, -30):
        _, y = lonlat_to_xy(0, lat)
        d.line([(MAP_X0, y), (MAP_X1, y)], fill=(190, 205, 212), width=1)
    # continent labels
    lbl = sans_b(11)
    for txt, lon, lat in [("NORTH AMERICA", -100, 52), ("SOUTH AMERICA", -60, -14),
                          ("EUROPE", -30, 60), ("AFRICA", 18, 8),
                          ("ASIA", 120, 62), ("AUSTRALIA", 134, -25)]:
        x, y = lonlat_to_xy(lon, lat)
        d.text((x - d.textlength(txt, font=lbl) / 2, y - 6), txt,
               font=lbl, fill=(120, 100, 70))


# ---------- illustrations ----------
def illo_crimea(d, x, y, w, h):
    """Hero 1: Crimean Bridge under drone attack."""
    d.rectangle([x, y, x + w, y + h], fill=(207, 227, 238))
    # sky smoke
    for cx, cy, r in [(x + w * 0.62, y + 18, 16), (x + w * 0.70, y + 26, 12),
                      (x + w * 0.58, y + 30, 10)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 160, 168))
    # jets
    for jx, jy in [(x + 26, y + 14), (x + 52, y + 26)]:
        d.polygon([(jx, jy), (jx + 18, jy + 4), (jx, jy + 8)], fill=(40, 40, 48))
        d.line([(jx, jy + 4), (jx - 12, jy + 4)], fill=(40, 40, 48), width=2)
    # bridge deck + pillars
    dy = y + h * 0.42
    d.line([(x + 8, dy), (x + w - 8, dy)], fill=(30, 30, 34), width=5)
    for px in range(0, 11):
        bx = x + 14 + px * (w - 28) / 10.0
        d.line([(bx, dy), (bx, dy + 20)], fill=(30, 30, 34), width=3)
    # arch
    d.arc([x + w * 0.30, dy - 34, x + w * 0.55, dy + 4], 180, 360,
          fill=(30, 30, 34), width=4)
    # broken span
    d.line([(x + w * 0.72, dy), (x + w * 0.78, dy + 16)], fill=(30, 30, 34),
           width=4)
    d.line([(x + w * 0.78, dy + 16), (x + w * 0.84, dy + 22)],
           fill=(30, 30, 34), width=4)
    # explosions
    burst(d, x + w * 0.42, dy - 8, 13, (235, 110, 30))
    burst(d, x + w * 0.76, dy - 2, 11, (235, 110, 30))
    # water
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(140, 185, 215))
    for wy in (0.80, 0.88):
        for k in range(6):
            wx = x + 20 + k * (w - 40) / 5.0
            d.arc([wx - 12, y + h * wy - 4, wx + 12, y + h * wy + 4],
                  180, 360, fill=(255, 255, 255), width=2)
    lab = sans_b(11)
    d.text((x + 10, y + 4), "CRIMEA", font=lab, fill=(40, 60, 80))
    d.text((x + w / 2 - 34, y + h - 15), "KERCH STRAIT", font=lab,
           fill=(255, 255, 255))
    d.text((x + w - 62, y + 4), "RUSSIA", font=lab, fill=(40, 60, 80))


def illo_gulf(d, x, y, w, h):
    """Hero 2: Gulf map — drones from Iran toward Bahrain radar."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 224))
    # Gulf water
    d.polygon([(x + w * 0.42, y + 6), (x + w * 0.72, y + 6),
               (x + w * 0.62, y + h - 8), (x + w * 0.30, y + h - 8)],
              fill=(168, 203, 222))
    # Iran land (top right)
    d.polygon([(x + w * 0.55, y + 4), (x + w, y + 4), (x + w, y + h * 0.52),
               (x + w * 0.78, y + h * 0.42), (x + w * 0.62, y + h * 0.30),
               (x + w * 0.55, y + h * 0.18)], fill=(234, 217, 184),
              outline=(168, 140, 96))
    # Saudi land (bottom)
    d.polygon([(x, y + h - 6), (x + w, y + h - 6), (x + w, y + h),
               (x, y + h)], fill=(234, 217, 184))
    # Bahrain island
    bx, by = x + w * 0.50, y + h * 0.62
    d.ellipse([bx - 9, by - 6, bx + 9, by + 6], fill=(200, 170, 120),
              outline=(120, 90, 50))
    # Qeshm island
    qx, qy = x + w * 0.66, y + h * 0.44
    d.ellipse([qx - 16, qy - 5, qx + 16, qy + 5], fill=(200, 170, 120),
              outline=(120, 90, 50))
    # radar arcs at Bahrain
    for r in (14, 22, 30):
        d.arc([bx - r, by - r, bx + r, by + r], 200, 340,
              fill=(178, 44, 36), width=2)
    # drone path (dashed) Iran -> Bahrain
    sx, sy = x + w * 0.80, y + h * 0.20
    for t in range(0, 11):
        px = sx + (bx - sx) * t / 10.0
        py = sy + (by - sy) * t / 10.0 + math.sin(t * 0.9) * 5
        if t % 2 == 0:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(235, 110, 30))
    d.polygon([(bx + 12, by - 4), (bx + 22, by), (bx + 12, by + 4)],
              fill=(235, 110, 30))
    # drone glyphs
    for dx, dy in [(sx, sy), (x + w * 0.70, y + h * 0.30)]:
        d.polygon([(dx, dy), (dx + 12, dy + 3), (dx, dy + 6)],
                  fill=(40, 40, 48))
    lab = sans_b(11)
    d.text((x + w * 0.74, y + 6), "IRAN", font=lab, fill=(60, 50, 40))
    d.text((bx - 30, by + 12), "BAHRAIN", font=lab, fill=(40, 60, 80))
    d.text((x + w * 0.28, y + h * 0.60), "GULF", font=lab, fill=(40, 60, 80))
    d.text((qx - 14, qy + 8), "QESHM", font=lab, fill=(40, 60, 80))
    d.text((x + 8, y + h - 16), "SAUDI ARABIA", font=lab,
           fill=(60, 50, 40))


def illo_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(205, 224, 238))
    # skyline
    for bx, bw, bh in [(4, 18, 22), (26, 12, 30), (42, 16, 18),
                       (62, 12, 26), (78, 14, 20)]:
        d.rectangle([x + bx, y + h - 14 - bh, x + bx + bw, y + h - 14],
                    fill=(70, 90, 110))
    # bridge
    dy = y + h - 14
    d.line([(x + 4, dy), (x + w - 4, dy)], fill=(30, 30, 34), width=3)
    for px in range(5):
        bx = x + 14 + px * (w - 28) / 4.0
        d.line([(bx, dy), (bx, dy - 12)], fill=(30, 30, 34), width=2)
    burst(d, x + w * 0.68, dy - 8, 10, (235, 110, 30))


def illo_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 228))
    fw = (w - 16) / 3
    draw_flag(d, "US", x + 4, y + 6, fw, 22)
    draw_flag(d, "MX", x + 8 + fw, y + 6, fw, 22)
    draw_flag(d, "BO", x + 12 + 2 * fw, y + 6, fw, 22)
    # virus disc
    cx, cy = x + w - 26, y + h - 14
    for k in range(8):
        a = math.radians(k * 45)
        d.line([(cx + 8 * math.cos(a), cy + 8 * math.sin(a)),
                (cx + 13 * math.cos(a), cy + 13 * math.sin(a))],
               fill=(140, 40, 160), width=2)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(160, 60, 180))


def illo_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 240, 224))
    # rising bars
    bars = [10, 16, 24, 34]
    for i, bh in enumerate(bars):
        bx = x + 10 + i * 20
        d.rectangle([bx, y + h - 8 - bh, bx + 14, y + h - 8],
                    fill=(30, 120, 60) if i < 3 else (178, 44, 36))
    # virus spiral
    cx, cy = x + w - 30, y + 18
    for k in range(10):
        a = math.radians(k * 36)
        d.line([(cx + 7 * math.cos(a), cy + 7 * math.sin(a)),
                (cx + 12 * math.cos(a), cy + 12 * math.sin(a))],
               fill=(30, 120, 60), width=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(30, 120, 60))


def illo_manila(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 238, 244))
    draw_flag(d, "PH", x + 6, y + 6, 46, 24)
    # handshake: two interlocking blocks
    d.rounded_rectangle([x + 62, y + 8, x + 108, y + 30], radius=8,
                        fill=(200, 150, 100))
    d.rounded_rectangle([x + 96, y + 18, x + 142, y + 40], radius=8,
                        fill=(150, 100, 70))
    d.line([(x + 96, y + 19), (x + 108, y + 29)], fill=(255, 255, 255),
           width=3)
    # document
    d.rectangle([x + w - 34, y + 8, x + w - 8, y + 38], fill=(255, 255, 255),
                outline=(120, 120, 120))
    for ly in (14, 20, 26):
        d.line([(x + w - 30, y + ly), (x + w - 12, y + ly)],
               fill=(60, 60, 60), width=2)


def illo_knesset(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 238, 246))
    draw_flag(d, "IL", x + 6, y + 6, 46, 24)
    # gavel
    d.line([(x + 70, y + 12), (x + 108, y + 30)], fill=(90, 60, 30), width=5)
    d.rectangle([x + 96, y + 8, x + 116, y + 20], fill=(120, 80, 40))
    d.rectangle([x + 62, y + 24, x + 82, y + 36], fill=(120, 80, 40))
    # vote bars 66 / 52
    d.rectangle([x + 126, y + 10, x + 132, y + 38], fill=(31, 79, 163))
    d.rectangle([x + 136, y + 16, x + 142, y + 38], fill=(178, 44, 36))
    f = sans_b(11)
    d.text((x + 122, y + h - 14), "66–52", font=f, fill=(40, 40, 40))


def illo_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 230))
    draw_flag(d, "TR", x + 6, y + 6, 46, 24)
    # scales
    cx, cy = x + w / 2 + 16, y + 14
    d.line([(cx, cy - 8), (cx, cy + 22)], fill=(40, 40, 40), width=3)
    d.line([(cx - 22, cy - 4), (cx + 22, cy - 4)], fill=(40, 40, 40),
           width=3)
    d.arc([cx - 26, cy + 2, cx - 10, cy + 16], 0, 180, fill=(40, 40, 40),
          width=2)
    d.arc([cx + 10, cy + 2, cx + 26, cy + 16], 0, 180, fill=(40, 40, 40),
          width=2)
    d.line([(cx - 24, cy + 16), (cx + 24, cy + 16)], fill=(40, 40, 40),
           width=3)
    # leaf
    d.ellipse([x + w - 26, y + h - 20, x + w - 10, y + h - 6],
              fill=(40, 130, 60))


def illo_mongolia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 236, 228))
    draw_flag(d, "MN", x + 6, y + 6, 46, 24)
    # railway tracks
    for k in range(4):
        tx = x + 62 + k * 24
        d.line([(tx, y + 8), (tx + 12, y + 38)], fill=(60, 60, 60), width=2)
    d.line([(x + 62, y + 30), (x + 150, y + 30)], fill=(60, 60, 60), width=2)
    # $25m coin
    d.ellipse([x + w - 36, y + 6, x + w - 8, y + 34], fill=(212, 175, 88),
              outline=(150, 110, 40))
    f = sans_b(10)
    d.text((x + w - 33, y + 15), "$25m", font=f, fill=(80, 60, 10))


def illo_france(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 238, 246))
    draw_flag(d, "FR", x + 6, y + 6, 46, 24)
    # crowd silhouettes
    for i, cx in enumerate(range(64, 168, 16)):
        d.ellipse([x + cx - 5, y + 8, x + cx + 5, y + 18], fill=(40, 40, 48))
        d.rectangle([x + cx - 6, y + 18, x + cx + 6, y + 34],
                    fill=(40, 40, 48))
    # banner
    d.rectangle([x + 60, y + h - 16, x + w - 8, y + h - 4],
                fill=(31, 79, 163))
    f = sans_b(10)
    d.text((x + 66, y + h - 15), "GRÈVE", font=f, fill=(255, 255, 255))


def illo_bangladesh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 240, 232))
    draw_flag(d, "BD", x + 6, y + 6, 46, 24)
    # tear-gas cloud
    for cx, cy, r in [(x + 92, y + 16, 12), (x + 106, y + 12, 14),
                      (x + 120, y + 18, 11)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(190, 190, 190))
    # factory
    d.rectangle([x + 130, y + 22, x + w - 8, y + 38], fill=(90, 90, 100))
    d.rectangle([x + 134, y + 12, x + 140, y + 22], fill=(90, 90, 100))
    d.rectangle([x + 144, y + 16, x + 150, y + 22], fill=(90, 90, 100))


def illo_blackholes(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 14, 34))
    # stars
    for sx, sy, r in [(14, 8, 1), (40, 16, 1), (90, 6, 1), (130, 12, 1),
                      (160, 8, 1), (60, 30, 1), (110, 34, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(255, 255, 255))
    # two accretion discs
    for cx, cy, col in [(x + w * 0.32, y + h * 0.55, (255, 170, 60)),
                        (x + w * 0.68, y + h * 0.48, (120, 180, 255))]:
        d.ellipse([cx - 22, cy - 9, cx + 22, cy + 9], outline=col, width=3)
        d.ellipse([cx - 13, cy - 5, cx + 13, cy + 5], outline=col, width=2)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(0, 0, 0),
                  outline=col, width=1)


ILLOS = {3: illo_kyiv, 4: illo_measles, 5: illo_ebola, 6: illo_manila,
         7: illo_knesset, 8: illo_cop, 9: illo_mongolia, 10: illo_france,
         11: illo_bangladesh, 12: illo_blackholes}


# ---------- page layout ----------
def draw_masthead(d):
    d.rectangle([0, 0, W, 86], fill=NAVY)
    d.text((24, 12), "THE DAY IN WORLD NEWS", font=sans_b(13), fill=GOLD)
    d.text((24, 28), "Tuesday 17 November 2026", font=serif_b(46),
           fill=(255, 255, 255))
    r1 = "30 STORIES · 6 CONTINENTS · ONE DAY"
    d.text((W - 24 - d.textlength(r1, font=sans_b(15)), 14), r1,
           font=sans_b(15), fill=GOLD)
    cols = [REGION["Europe"], REGION["Middle East"], REGION["Asia"],
            REGION["Africa"], REGION["Americas"], REGION["Oceania"],
            REGION["Global"]]
    sw = W / len(cols)
    for i, c in enumerate(cols):
        d.rectangle([i * sw, 86, (i + 1) * sw, 92], fill=c)


def kicker_row(d, x, y, w, story):
    col = REGION[story["region"]]
    n = story["n"]
    d.ellipse([x, y, x + 17, y + 17], fill=col)
    ns = str(n)
    f = sans_b(11)
    d.text((x + 8.5 - d.textlength(ns, font=f) / 2, y + 2.5), ns,
           font=f, fill=(255, 255, 255))
    d.text((x + 22, y + 2), story["kicker"], font=sans_b(10), fill=col)


def draw_hero(d, x, y, w, h, story, illo_fn):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=LINE, width=1)
    col = REGION[story["region"]]
    d.rectangle([x, y, x + w, y + 3], fill=col)
    illo_fn(d, x + 1, y + 4, w - 2, 70)
    ty = y + 78
    kicker_row(d, x + 12, ty, w, story)
    hf = serif_b(25)
    hl = wrap(d, story["head"], hf, w - 24)
    text_lines(d, x + 12, ty + 22, hl[:2], hf, INK, lh=26)
    df = sans(15)
    dl = wrap(d, story["desc"], df, w - 24)
    text_lines(d, x + 12, ty + 22 + 2 * 26 + 2, dl[:2], df, (60, 60, 60),
               lh=15)


def draw_grid_panel(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=LINE, width=1)
    col = REGION[story["region"]]
    d.rectangle([x, y, x + w, y + 3], fill=col)
    kicker_row(d, x + 8, y + 6, w, story)
    ILLOS[story["n"]](d, x + 1, y + 24, w - 2, 38)
    hf = serif_b(22)
    hl = wrap(d, story["head"], hf, w - 16)
    text_lines(d, x + 8, y + 66, hl[:3], hf, INK, lh=23)
    df = sans(15)
    dl = wrap(d, story["desc"], df, w - 16)
    text_lines(d, x + 8, y + 66 + len(hl[:3]) * 23 + 2, dl[:2], df,
               (60, 60, 60), lh=15)


def draw_dots(d, positions):
    for story, (px, py) in zip([s for s in ALL if s["lon"] is not None],
                               positions):
        col = REGION[story["region"]]
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=col,
                  outline=(255, 255, 255), width=2)
        ns = str(story["n"])
        f = sans_b(11)
        d.text((px - d.textlength(ns, font=f) / 2, py - 6), ns, font=f,
               fill=(255, 255, 255))


def draw_briefs(d, x, y, col_w):
    d.text((x, y - 20), "ALSO ON TUESDAY 17 NOVEMBER",
           font=sans_b(13), fill=INK)
    d.line([(x, y - 4), (x + 2 * col_w + 12, y - 4)], fill=INK, width=2)
    rows = 9
    rh = 39
    for idx, (n, region, head, desc, lo, la) in enumerate(BRIEFS):
        col_i = idx // rows
        row_i = idx % rows
        bx = x + col_i * (col_w + 12)
        by = y + row_i * rh
        col = REGION[region]
        d.ellipse([bx, by, bx + 15, by + 15], fill=col)
        ns = str(n)
        f = sans_b(10)
        d.text((bx + 7.5 - d.textlength(ns, font=f) / 2, by + 2), ns,
               font=f, fill=(255, 255, 255))
        tx = bx + 20
        tw = col_w - 20
        hf = sans_b(11)
        df = sans(11)
        hl = wrap(d, head, hf, tw)[:2]
        dl = wrap(d, desc, df, tw)
        # headline up to 2 lines, description 1 line (truncated)
        used = text_lines(d, tx, by, hl, hf, INK, lh=13)
        d.text((tx, used), trunc(d, " ".join(dl), df, tw), font=df,
               fill=(70, 70, 70))


def draw_legend_footer(d):
    tally = [("Europe", 8), ("Middle East", 4), ("Asia", 8), ("Africa", 2),
             ("Americas", 4), ("Oceania", 2), ("Global", 2)]
    f = sans_b(11)
    for row_i, group in enumerate([tally[:4], tally[4:]]):
        y = 890 + row_i * 18
        xx = 24
        for name, cnt in group:
            col = REGION[name]
            d.ellipse([xx, y, xx + 12, y + 12], fill=col)
            t = "%s %d" % (name.upper(), cnt)
            d.text((xx + 16, y + 1), t, font=f, fill=(60, 60, 60))
            xx += 16 + d.textlength(t, font=f) + 14
    nf = sans(11)
    y = 930
    for ln in wrap(d, "Numbered dots = all 30 stories. Grey dot 8 sits at "
                      "Antalya; story 12 (black holes) has no place on Earth.",
                   nf, 588):
        d.text((24, y), ln, font=nf, fill=GREY)
        y += 14
    for ln in wrap(d, "Every story was reported on Tuesday 17 November 2026; "
                      "disputed claims are attributed. Sources: Reuters, AP, "
                      "AFP, BBC, Al Jazeera, UN News and others. Original "
                      "drawings.", nf, 588):
        d.text((24, y), ln, font=nf, fill=GREY)
        y += 14


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)

    # heroes
    hw = (W - 48 - 20) // 2
    draw_hero(d, 24, 92, hw, 184, MAINS[0], illo_crimea)
    draw_hero(d, 24 + hw + 20, 92, hw, 184, MAINS[1], illo_gulf)

    # grid: 10 panels, 5 cols x 2 rows
    gw = (W - 48 - 4 * 8) // 5
    for i, story in enumerate(MAINS[2:]):
        cx = i % 5
        cy = i // 5
        px = 24 + cx * (gw + 8)
        py = 282 + cy * (168 + 6)
        draw_grid_panel(d, px, py, gw, 168, story)

    # map
    d.text((24, 630), "WHERE IT HAPPENED", font=sans_b(13), fill=INK)
    d.line([(24, 648), (612, 648)], fill=INK, width=2)
    draw_map(d)
    placed = [s for s in ALL if s["lon"] is not None]
    init = [lonlat_to_xy(s["lon"], s["lat"]) for s in placed]
    positions = spread_dots(init, min_dist=21.0)
    draw_dots(d, positions)
    # GLOBAL box: story 12 (no earthly place)
    d.rounded_rectangle([MAP_X0 + 6, MAP_Y1 - 34, MAP_X0 + 128, MAP_Y1 - 6],
                        radius=6, fill=(255, 255, 255),
                        outline=REGION["Global"], width=1)
    d.ellipse([MAP_X0 + 14, MAP_Y1 - 27, MAP_X0 + 28, MAP_Y1 - 13],
              fill=REGION["Global"])
    gf = sans_b(11)
    d.text((MAP_X0 + 21 - d.textlength("12", font=gf) / 2, MAP_Y1 - 25),
           "12", font=gf, fill=(255, 255, 255))
    d.text((MAP_X0 + 32, MAP_Y1 - 25), "GLOBAL 12", font=gf, fill=INK)

    # briefs
    draw_briefs(d, 624, 670, 182)

    # legend + footer
    draw_legend_footer(d)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
    print("map min dot distance: %.1f px" % min_pair_dist(positions))
    return out


if __name__ == "__main__":
    build()
