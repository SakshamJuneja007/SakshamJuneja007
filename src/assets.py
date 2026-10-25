import sys; sys.path.insert(0, '/home/claude/gp/src')
from common import *

def plate(h, seed, vig=0.7, tint=(14, 12, 13)):
    f = fbm(h // 3 + 2, W // 3, seed, 4, 3)
    f = np.asarray(Image.fromarray((f * 255).astype(np.uint8)).resize((W, h), Image.BICUBIC), np.float32) / 255
    b = np.zeros((h, W, 3), np.float32) + np.array(BLACK, np.float32) + f[..., None] * np.array(tint, np.float32)
    return b * vignette(h, W, vig)

def compose(base, layers, rng, grain=11, **kw):
    img = to_img(base).convert('RGBA')
    for l in layers: img = Image.alpha_composite(img, l)
    a = film(np.asarray(img.convert('RGB'), np.float32), rng, grain=grain, **kw)
    return to_img(a)

def layer(h): 
    im = Image.new('RGBA', (W, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

# ---------------------------------------------------------------- NAME + HEADLINE
def name_gif():
    H = 230; N = 72; base = plate(H, 11)
    fN = font(SERIF, 56); sp = 7; name = 'SAKSHAM JUNEJA'
    dm = ImageDraw.Draw(Image.new('L', (10, 10)))
    total = tw(dm, name, fN, sp); x0 = 46
    while total > W - 92: fN = font(SERIF, fN.size - 2); total = tw(dm, name, fN, sp)
    xs = []; x = x0
    for c in name: xs.append(x); x += dm.textlength(c, font=fN) + sp
    sharp, blur = [], []
    for c, x in zip(name, xs):
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).text((x, 28), c, font=fN, fill=255)
        sharp.append(np.asarray(m, np.float32) / 255); blur.append(np.asarray(m.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255)
    fH = font(ITAL, 31); fM = font(MONO, 15)
    head = 'I build systems that perceive, reason, and act.'
    words = head.split(' ')
    frames = []
    for i in range(N):
        rng = np.random.default_rng(200 + i)
        mask = np.zeros((H, W), np.float32)
        for k in range(len(name)):
            p = ease(clamp01((i - 2 - k * 1.6) / 9)); 
            mask = np.maximum(mask, np.maximum(sharp[k] * p, blur[k] * (1 - p) * min(1, p * 4) * 0.7))
        fade = 1 - ease(clamp01((i - (N - 9)) / 8))
        col = np.zeros((H, W, 3), np.float32) + np.array(BONE, np.float32)
        ghost_amt = 0.45 * (1 - ease(clamp01((i - 10) / 30))) + (0.25 if i % 17 in (3, 4) else 0)
        ghost = np.roll(mask, int(3 + (6 if i % 17 in (3, 4) else 0)), 1) * ghost_amt
        out = base.copy()
        out = out * (1 - ghost[..., None] * fade) + np.array(CRIM, np.float32) * ghost[..., None] * fade
        out = out * (1 - mask[..., None] * fade) + col * mask[..., None] * fade
        ov, d = layer(H)
        # rule
        rl = ease(clamp01((i - 22) / 14)) * (W - 92)
        d.line([(46, 108), (46 + rl, 108)], fill=(*CRIM, int(230 * fade)), width=1)
        # headline words
        x = 46
        for k, w in enumerate(words):
            a = ease(clamp01((i - 26 - k * 2.2) / 6)) * fade
            colr = (205, 38, 50) if w.startswith('act') else BONE
            d.text((x, 124 + (1 - a) * 8), w, font=fH, fill=(*colr, int(255 * a)))
            x += d.textlength(w + ' ', font=fH)
        a2 = ease(clamp01((i - 46) / 8)) * fade
        sub = 'AI/ML  ·  AGENTIC SYSTEMS  ·  COMPUTER VISION  ·  GAME AI'
        spaced(d, (46, 184), sub, fM, (*ASH, int(255 * a2)), 1.5)
        cur = '▌' if (i // 4) % 2 == 0 and 46 <= i < N - 9 else ''
        frames.append(compose(out, [ov], rng, grain=9))
    return frames

# ---------------------------------------------------------------- DOSSIER PANEL
def panel_gif():
    H = 210; N = 60; base = plate(H, 21)
    rows = [('SUBJECT', 'Saksham Juneja'), ('DISCIPLINE', 'AI / ML Engineering'),
            ('FOCUS', 'Agentic Systems · Computer Vision · Game AI'), ('ONLINE', 'github.com/SakshamJuneja007')]
    fL = font(MONO, 15); fV = font(MONO, 17); fH = font(MONO, 13)
    frames = []
    for i in range(N):
        t = i / N; phi = 2 * math.pi * t
        rng = np.random.default_rng(300 + i)
        ov, d = layer(H)
        fade = 1 - ease(clamp01((i - (N - 7)) / 6))
        d.text((46, 22), 'FILE 001  /  SUBJECT RECORD', font=fH, fill=(*CRIM_T, int(255 * fade)))
        d.line([(46, 44), (46 + ease(clamp01(i / 12)) * 470, 44)], fill=(*ASH, int(160 * fade)))
        for r, (lab, val) in enumerate(rows):
            start = 8 + r * 7
            n = int(max(0, (i - start)) * 2.6)
            y = 60 + r * 34
            d.text((46, y + 2), lab, font=fL, fill=(*ASH, int(255 * fade)))
            d.text((176, y), val[:n], font=fV, fill=(*BONE, int(255 * fade)))
            if 0 < n < len(val) or (r == len(rows) - 1 and n >= len(val) and (i // 5) % 2 == 0 and i < N - 7):
                cx = 176 + d.textlength(val[:n], font=fV)
                d.rectangle([cx + 2, y + 2, cx + 10, y + 19], fill=(*CRIM, int(230 * fade)))
        d.line([(46, 198), (46 + ease(clamp01((i - 30) / 14)) * 470, 198)], fill=(*CRIM_D, int(220 * fade)))
        # shutter / aperture
        cx, cy, R = 716, 108, 54
        for k in range(48):
            a = k / 48 * 2 * math.pi + phi * 0.25
            L = 9 if k % 4 else 16
            d.line([(cx + math.cos(a) * (R - L), cy + math.sin(a) * (R - L)), (cx + math.cos(a) * R, cy + math.sin(a) * R)],
                   fill=(*ASH, int(150 * fade)), width=1)
        r1 = 24 + 6 * math.sin(phi)
        for k in range(8):
            a = k / 8 * 2 * math.pi - phi * 0.5
            pts = [(cx + math.cos(a) * 44, cy + math.sin(a) * 44), (cx + math.cos(a + 0.62) * 44, cy + math.sin(a + 0.62) * 44),
                   (cx + math.cos(a + 0.62 + 0.18) * r1, cy + math.sin(a + 0.62 + 0.18) * r1)]
            d.line(pts + [pts[0]], fill=(*BONE, int(170 * fade)), width=1)
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], outline=(*CRIM, int(255 * fade)), width=2)
        pr = 4 + 2 * (0.5 + 0.5 * math.sin(phi * 2))
        d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(215, 35, 48, int(255 * fade)))
        frames.append(compose(base, [ov], rng, grain=9))
    return frames

# ---------------------------------------------------------------- INTEREST PLATES
def interests_gif():
    H = 112; N = 48; base = plate(H, 31, vig=0.5)
    labels = ['AI / ML', 'AGENTIC SYSTEMS', 'COMPUTER VISION', 'GAME AI']
    pw, gap = 184, 10; x0 = (W - (4 * pw + 3 * gap)) // 2
    frames = []
    for i in range(N):
        t = i / N; rng = np.random.default_rng(400 + i)
        ov, d = layer(H)
        act = (t * 4)
        for k, lab in enumerate(labels):
            x = x0 + k * (pw + gap); y0, y1 = 18, 94
            on = math.exp(-(((act - k - 0.5 + 2) % 4 - 2) / 0.55) ** 2)
            d.rectangle([x, y0, x + pw, y1], fill=(*CRIM_D, int(90 * on)), outline=(*(CRIM if on > 0.4 else ASH), int(110 + 140 * on)))
            for cxk, cyk, sx, sy in ((x, y0, 1, 1), (x + pw, y0, -1, 1), (x, y1, 1, -1), (x + pw, y1, -1, -1)):
                d.line([(cxk, cyk), (cxk + 8 * sx, cyk)], fill=(*BONE, int(80 + 150 * on))); d.line([(cxk, cyk), (cxk, cyk + 8 * sy)], fill=(*BONE, int(80 + 150 * on)))
            d.text((x + 12, y0 + 8), f'0{k + 1}', font=font(MONO, 13), fill=(*CRIM_T, 255))
            fs = 17
            f = font(SERIF, fs)
            while tw(d, lab, f, 1.5) > pw - 26: fs -= 1; f = font(SERIF, fs)
            spaced(d, (x + 12, y0 + 36), lab, f, (*BONE, int(150 + 105 * on)), 1.5)
            sw = (pw - 24) * ease(on)
            d.line([(x + 12, y1 - 12), (x + 12 + sw, y1 - 12)], fill=(215, 38, 50, 255), width=1)
        frames.append(compose(base, [ov], rng, grain=8))
    return frames

# ---------------------------------------------------------------- SOCIAL STRIP
def social_gif():
    H = 92; N = 48; base = plate(H, 41, vig=0.5)
    frames = []
    for i in range(N):
        t = i / N; phi = 2 * math.pi * t; rng = np.random.default_rng(500 + i)
        ov, d = layer(H)
        pw = 440; x0 = (W - pw) // 2; y0, y1 = 16, 76
        d.line([(30, 46), (x0 - 18, 46)], fill=(*ASH, 120)); d.line([(x0 + pw + 18, 46), (W - 30, 46)], fill=(*ASH, 120))
        d.rectangle([x0, y0, x0 + pw, y1], outline=(*ASH, 200), fill=(*CRIM_D, 40))
        d.text((x0 + 18, y0 + 9), 'GITHUB', font=font(SERIF, 24), fill=(*BONE, 255))
        d.text((x0 + 18, y0 + 38), 'github.com/SakshamJuneja007', font=font(MONO, 15), fill=(*ASH, 255))
        # arrow nudging
        nud = 6 * (0.5 + 0.5 * math.sin(phi)); ax = x0 + pw - 62 + nud; ay = 46
        d.line([(ax, ay), (ax + 34, ay)], fill=(215, 38, 50, 255), width=2)
        d.line([(ax + 24, ay - 9), (ax + 34, ay), (ax + 24, ay + 9)], fill=(215, 38, 50, 255), width=2)
        sw = ((t * 2) % 1) * pw
        d.line([(x0 + sw - 40, y1), (x0 + sw, y1)], fill=(*CRIM, 255), width=2)
        frames.append(compose(base, [ov], rng, grain=8))
    return frames

# ---------------------------------------------------------------- TRANSITIONS
def transition_a():
    H = 58; N = 28; base = plate(H, 51, vig=0.4)
    frames = []
    for i in range(N):
        rng = np.random.default_rng(600 + i)
        ov, d = layer(H)
        for k in range(-2, W // 28 + 3):
            x = k * 28 + i
            d.rounded_rectangle([x, 6, x + 14, 14], 2, fill=(*ASH, 150)); d.rounded_rectangle([x, H - 15, x + 14, H - 7], 2, fill=(*ASH, 150))
        d.line([(0, 20), (W, 20)], fill=(*ASH, 90)); d.line([(0, H - 21), (W, H - 21)], fill=(*ASH, 90))
        d.line([(0, H // 2), (W, H // 2)], fill=(*CRIM_D, 160))
        frames.append(compose(base, [ov], rng, grain=8))
    return frames

def transition_b():
    H = 74; N = 48; base = plate(H, 61, vig=0.5)
    dust = np.random.default_rng(9); P = [(dust.uniform(0, W), dust.uniform(10, H - 10), dust.uniform(0.5, 1.6), dust.uniform(0, 6.28)) for _ in range(34)]
    frames = []
    for i in range(N):
        t = i / N; phi = 2 * math.pi * t; rng = np.random.default_rng(700 + i)
        ov, d = layer(H)
        pts = [(x, 37 + 3.5 * math.sin(x / 55 + phi) + 1.8 * math.sin(x / 17 - 2 * phi)) for x in range(0, W + 1, 8)]
        d.line(pts, fill=(*CRIM, 235), width=1)
        d.line([(x, y + 1) for x, y in pts], fill=(*CRIM_D, 120), width=1)
        for x, y, s, ph in P:
            xx = (x + t * W * s * 0.0 + t * W * (1 if s > 1 else 2) * (1 if False else 1)) % W
            xx = (x + W * t * round(s)) % W
            d.ellipse([xx, y + 3 * math.sin(phi + ph), xx + 1.5 * s, y + 1.5 * s + 3 * math.sin(phi + ph)], fill=(*BONE, int(70 + 70 * s / 1.6)))
        r = 6 + 1.5 * math.sin(phi)
        d.polygon([(W / 2, 37 - r), (W / 2 + r, 37), (W / 2, 37 + r), (W / 2 - r, 37)], fill=BLACK, outline=BONE)
        frames.append(compose(base, [ov], rng, grain=8))
    return frames

# ---------------------------------------------------------------- SECTION TITLE + CAPTIONS
def section_gif():
    H = 124; N = 48; base = plate(H, 71, vig=0.55)
    fT = font(SERIF, 40); title = 'FEATURED WORK'; sp = 9
    dm = ImageDraw.Draw(Image.new('L', (4, 4))); total = tw(dm, title, fT, sp); x0 = (W - total) / 2
    frames = []
    for i in range(N):
        t = i / N; rng = np.random.default_rng(800 + i)
        ov, d = layer(H)
        x = x0
        for k, c in enumerate(title):
            a = ease(clamp01((i - 1 - k * 1.1) / 6)); a *= 0.93 + 0.07 * (1 if (i + k) % 11 else -1)
            d.text((x, 30 + (1 - a) * 6), c, font=fT, fill=(*BONE, int(255 * clamp01(a))))
            x += dm.textlength(c, font=fT) + sp
        w = ease(clamp01((i - 6) / 18)) * 120
        d.line([(W / 2 - w, 94), (W / 2 + w, 94)], fill=(*CRIM, 255))
        d.text((W / 2 - 44, 100), '04 REELS', font=font(MONO, 14), fill=(*ASH, int(255 * ease(clamp01((i - 16) / 8)))))
        frames.append(compose(base, [ov], rng, grain=8))
    return frames

def caption_gif(idx, numeral, title, repo):
    H = 66; N = 36; base = plate(H, 80 + idx, vig=0.4)
    fT = font(SERIF, 28); fR = font(MONO, 15); fN = font(ITAL, 34)
    frames = []
    for i in range(N):
        t = i / N; phi = 2 * math.pi * t; rng = np.random.default_rng(900 + idx * 50 + i)
        ov, d = layer(H)
        d.text((30, 12), numeral, font=fN, fill=(205, 38, 50, 255))
        d.text((92, 17), title, font=fT, fill=(*BONE, 255))
        rt = f'SakshamJuneja007/{repo}'
        wr = d.textlength(rt, font=fR)
        d.text((W - 30 - 40 - wr, 26), rt, font=fR, fill=(*ASH, 255))
        nud = 4 * (0.5 + 0.5 * math.sin(phi)); ax = W - 56 + nud
        d.line([(ax, 33), (ax + 24, 33)], fill=(215, 38, 50, 255), width=2); d.line([(ax + 16, 25), (ax + 24, 33), (ax + 16, 41)], fill=(215, 38, 50, 255), width=2)
        sw = ((t * 1) % 1) * (W - 60)
        d.line([(30, H - 5), (W - 30, H - 5)], fill=(*ASH, 70))
        d.line([(30 + sw - 70, H - 5), (30 + sw, H - 5)], fill=(*CRIM, 255), width=1)
        frames.append(compose(base, [ov], rng, grain=8))
    return frames

# ---------------------------------------------------------------- CLOSING SIGNATURE
def closing_gif():
    H = 300; N = 72; base = plate(H, 91, vig=0.7)
    fS = font(ITAL, 78); fM = font(MONO, 16)
    sig = 'Saksham Juneja'
    dm = ImageDraw.Draw(Image.new('L', (4, 4))); sw_ = dm.textlength(sig, font=fS); sx = (W - sw_) / 2; sy = 78
    mk = Image.new('L', (W, H), 0); ImageDraw.Draw(mk).text((sx, sy), sig, font=fS, fill=255); mk = np.asarray(mk, np.float32) / 255
    Xg = np.arange(W, dtype=np.float32)[None, :]; Yg, Xg2 = np.mgrid[0:H, 0:W].astype(np.float32)
    ccx, ccy = W / 2, 130
    dist = np.sqrt((Xg2 - ccx) ** 2 + (Yg - ccy) ** 2)
    frames = []
    for i in range(N):
        t = i / N; rng = np.random.default_rng(1100 + i)
        wipe = ease(clamp01((i - 8) / 28)) * (sw_ + 30) + sx - 15
        m = mk * np.clip((wipe - Xg) / 14 + 0.5, 0, 1)
        out = base.copy(); out = out * (1 - m[..., None]) + np.array(BONE, np.float32) * m[..., None]
        ov, d = layer(H)
        if i >= 8 and wipe < sx + sw_ + 15:
            d.ellipse([wipe - 3, sy + 64, wipe + 3, sy + 70], fill=(215, 38, 50, 255))
        fl = ease(clamp01((i - 30) / 12))
        pts = []
        for k in range(0, 41):
            u = k / 40; x = sx + u * (sw_ + 20) - 10; y = sy + 104 + 7 * math.sin(u * 3.2 * math.pi) * (1 - u) + 10 * u
            if u <= fl: pts.append((x, y))
        if len(pts) > 1: d.line(pts, fill=(*CRIM, 255), width=2)
        a1 = ease(clamp01((i - 40) / 8)); a2 = ease(clamp01((i - 46) / 8))
        d.text((W / 2 - d.textlength('— F I N —', font=fM) / 2, 204), '— F I N —', font=fM, fill=(*ASH, int(255 * a1)))
        u = 'github.com/SakshamJuneja007'
        d.text((W / 2 - d.textlength(u, font=fM) / 2, 238), u, font=fM, fill=(*BONE, int(255 * a2)))
        out_img = to_img(out).convert('RGBA'); out_img = Image.alpha_composite(out_img, ov)
        arr = np.asarray(out_img.convert('RGB'), np.float32)
        Rm = 640
        if i < 8: R = ease(i / 8) * Rm
        elif i < 54: R = Rm
        else: R = (1 - ease((i - 54) / 17)) * Rm
        iris = np.clip((R - dist) / 10, 0, 1)[..., None]
        arr = arr * iris
        frames.append(to_img(film(arr, rng, grain=9)))
    return frames

# ---------------------------------------------------------------- PROJECT SLOT PLACEHOLDERS (preview only)
def slot_gif(idx, name):
    H = 450; N = 36; base = plate(H, 120 + idx, vig=0.8, tint=(10, 9, 10))
    frames = []
    for i in range(N):
        t = i / N; phi = 2 * math.pi * t; rng = np.random.default_rng(1300 + idx * 60 + i)
        ov, d = layer(H)
        d.rectangle([14, 14, W - 14, H - 14], outline=(*ASH, 110))
        for (x, y, sx, sy) in ((30, 30, 1, 1), (W - 30, 30, -1, 1), (30, H - 30, 1, -1), (W - 30, H - 30, -1, -1)):
            d.line([(x, y), (x + 26 * sx, y)], fill=(*BONE, 160)); d.line([(x, y), (x, y + 26 * sy)], fill=(*BONE, 160))
        cx, cy = W / 2, H / 2 - 12
        d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=(*ASH, 150)); d.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], outline=(*ASH, 90))
        d.line([(cx - 90, cy), (cx + 90, cy)], fill=(*ASH, 90)); d.line([(cx, cy - 90), (cx, cy + 90)], fill=(*ASH, 90))
        a = phi - math.pi / 2
        for s in range(14):
            aa = a - s * 0.05
            d.line([(cx, cy), (cx + math.cos(aa) * 70, cy + math.sin(aa) * 70)], fill=(*CRIM, int(210 * (1 - s / 14))), width=1)
        num = 3 - int(t * 3)
        d.text((cx - 10, cy - 24), str(num), font=font(SERIF, 52), fill=(*BONE, 120)) 
        txt = f'PROJECT GIF  0{idx} — {name}'
        d.text((W / 2 - d.textlength(txt, font=font(MONO, 21)) / 2, cy + 100), txt, font=font(MONO, 21), fill=(*BONE, 255))
        t2 = 'AWAITING REEL  ·  800 × 450  ·  PLACEHOLDER'
        d.text((W / 2 - d.textlength(t2, font=font(MONO, 16)) / 2, cy + 136), t2, font=font(MONO, 16), fill=(*CRIM_T, 255))
        frames.append(compose(base, [ov], rng, grain=9))
    return frames

if __name__ == '__main__':
    import time
    which = sys.argv[1:] or ['all']
    jobs = {
        'name': lambda: save_gif(name_gif(), 'name.gif', fps=12, colors=32),
        'panel': lambda: save_gif(panel_gif(), 'panel.gif', fps=10, colors=32),
        'interests': lambda: save_gif(interests_gif(), 'interests.gif', fps=12, colors=32),
        'social': lambda: save_gif(social_gif(), 'social.gif', fps=12, colors=32),
        'trans_a': lambda: save_gif(transition_a(), 'transition-a.gif', fps=14, colors=24),
        'trans_b': lambda: save_gif(transition_b(), 'transition-b.gif', fps=12, colors=24),
        'section': lambda: save_gif(section_gif(), 'section-featured.gif', fps=12, colors=32),
        'closing': lambda: save_gif(closing_gif(), 'closing.gif', fps=12, colors=32),
    }
    for i, (n, r) in enumerate([('I', 'freaky-monkey'), ('II', 'Chess-ai'), ('III', 'TAI-Tekken-AI-Motion-Control-System'), ('IV', 'saksham-persona')], 1):
        title = ['DEIMOS', 'Chess AI', 'TAI', 'Saksham Persona'][i - 1]
        jobs[f'cap{i}'] = (lambda i=i, n=n, r=r, title=title: save_gif(caption_gif(i, n, title, r), f'caption-{i}.gif', fps=12, colors=24))
    os.makedirs('/mnt/user-data/outputs/github-profile/preview/placeholders', exist_ok=True)
    for i, nm in enumerate(['DEIMOS', 'CHESS AI', 'TAI', 'SAKSHAM PERSONA'], 1):
        jobs[f'slot{i}'] = (lambda i=i, nm=nm: save_gif(slot_gif(i, nm), f'slot-{i}.gif', fps=12, colors=32,
                                                         outdir='/mnt/user-data/outputs/github-profile/preview/placeholders'))
    for k, j in jobs.items():
        if which == ['all'] or k in which:
            t0 = time.time(); j(); print('  ', k, f'{time.time() - t0:.1f}s', flush=True)
