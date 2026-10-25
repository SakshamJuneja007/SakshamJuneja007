import sys; sys.path.insert(0, '/home/claude/gp/src')
from common import *

H = 360
N = 40
HF = 10
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
rng0 = np.random.default_rng(7)

# static / loop fields
fogA, fogB = fbm(H // 4, W // 4, 1, 3, 4), fbm(H // 4, W // 4, 2, 3, 4)
erA, erB = fbm(H, W, 3, 22, 4), fbm(H, W, 4, 22, 4)
tex = 0.62 + 0.75 * fbm(H, W, 5, 60, 4)
crk = fbm(H, W, 6, 9, 5)
crk2 = fbm(H, W, 8, 14, 4)

# row bands for fragmentation
band = np.zeros(H, int); b = 0; y = 0; bh = []
while y < H:
    h = int(rng0.integers(5, 17)); band[y:y + h] = b; bh.append(rng0.random()); y += h; b += 1
bh = np.array(bh); bamp = np.where(bh > 0.74, rng0.uniform(5, 16, len(bh)) * rng0.choice([-1, 1], len(bh)), 0.0)
bph = rng0.uniform(0, 6.28, len(bh)); bk = rng0.choice([1, 2], len(bh))
bamp[(np.arange(len(bh)) < 3)] = 0

shards = [dict(x=rng0.uniform(330, 780), y=rng0.uniform(0, H), sp=rng0.uniform(0.6, 2.2) * H, s=rng0.uniform(3, 11),
               a=rng0.uniform(0, 6.28), d=rng0.uniform(0.25, 1), ph=rng0.uniform(0, 6.28)) for _ in range(18)]

fT = font(MONO, 14); fW = font(ITAL, 46); fS = font(SERIF, 15)

def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1); return b * (1 - h) + a * h - k * h * (1 - h)

def render(i, N=N, text=True):
    t = i / N; phi = 2 * math.pi * t
    rng = np.random.default_rng(1000 + i)
    br = 1 + 0.014 * math.sin(phi)
    # background fog + crimson glow
    fog = loop_field(fogA, fogB, 0.6 + 0.25 * math.sin(phi)); fog = (fog - fog.min()) / (fog.max() - fog.min())
    fog = np.asarray(Image.fromarray((fog * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    bg = np.zeros((H, W, 3), np.float32) + np.array(BLACK, np.float32)
    bg += fog[..., None] * np.array([20, 17, 18], np.float32)
    cx, cy = 572, 168
    d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    glow = np.exp(-(d / (150 * br)) ** 2) * (0.55 + 0.12 * math.sin(phi + 1.0))
    bg += glow[..., None] * np.array([92, 8, 15], np.float32)
    ring = np.exp(-((d - 128 * br) / 1.3) ** 2) * 0.55 + np.exp(-((d - 150 * br) / 0.9) ** 2) * 0.25
    bg += ring[..., None] * np.array([150, 18, 30], np.float32) * (0.6 + 0.2 * math.sin(phi))
    # fragmented coordinates
    dx = bamp[band] * np.sin(phi * bk[band] + bph[band]) + 2.0 * math.sin(phi)
    Xs = X - dx[:, None]
    Xh = Xs + (Y - 150) * 0.10          # head lean
    # sdf
    e1 = np.sqrt(((Xh - 572) / (64 * br)) ** 2 + ((Y - 150) / (84 * br)) ** 2) - 1; e1 *= 62
    e2 = np.sqrt(((Xh - 574) / 50) ** 2 + ((Y - 205) / 70) ** 2) - 1; e2 *= 48
    qx, qy = np.abs(Xs - 574) - 30, np.abs(Y - 275) - 52
    e3 = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0)
    e4 = np.sqrt(((Xs - 574) / 235) ** 2 + ((Y - 430) / 150) ** 2) - 1; e4 *= 150
    sdf = smin(smin(e1, e2, 16), smin(e3, e4, 26), 20)
    chunk = np.sqrt((Xh - 538) ** 2 + (Y - 190) ** 2) - 22
    sdf = np.maximum(sdf, -chunk + 8 * (erA - 0.5))
    chunk2 = np.sqrt((Xs - 700) ** 2 + (Y - 330) ** 2) - 38
    sdf = np.maximum(sdf, -chunk2)
    er = loop_field(erA, erB, phi * 0.0 + 0.9 + 0.5 * math.sin(phi))
    er = (er - 0.5)
    sdf_e = sdf + er * 13
    alpha = 1 - smooth(-1.5, 1.5, sdf_e)
    # shading
    hg = np.clip(-sdf_e / 46, 0, 1) ** 0.55
    hi = Image.fromarray((hg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.2))
    hb = np.asarray(hi, np.float32) / 255
    gy, gx = np.gradient(hb)
    dot = -(gx * 0.78 + gy * 0.62) * 70
    lit = np.clip(0.30 + dot * 1.4, 0, 1.3) * (0.6 + 0.5 * np.clip(hg * 1.5, 0, 1))
    lit *= 0.65 + 0.6 * smooth(520, 330, X)[...] if False else 1.0
    lit *= np.clip((X - 330) / 220, 0.25, 1)  # darker on the far side
    col = lit[..., None] * tex[..., None] * np.array(BONE, np.float32) * 0.98
    col += np.array([6, 5, 6], np.float32)
    # eye sockets
    for ex, ey, rx, ry in ((552, 142, 13, 7.5), (596, 142, 13, 7.5)):
        r = ((Xh - ex) / rx) ** 2 + ((Y - ey) / ry) ** 2
        col *= (1 - 0.94 * smooth(1.3, 0.7, r))[..., None]
    rr = ((Xh - 596) ** 2 + (Y - 142) ** 2)
    pulse = 0.55 + 0.45 * math.sin(phi * 2 + 0.6)
    col += (np.exp(-rr / 9.0) * 230 * pulse)[..., None] * np.array([0.9, 0.12, 0.14], np.float32)
    col += (np.exp(-rr / 80.0) * 70 * pulse)[..., None] * np.array([0.9, 0.1, 0.12], np.float32) * alpha[..., None]
    # cracks
    c = np.abs(crk - 0.5); crack = smooth(0.010, 0.0, c) * (alpha > 0.6) * smooth(10, 24, -sdf_e)
    c2 = np.abs(crk2 - 0.5); crack2 = smooth(0.007, 0.0, c2) * (alpha > 0.6) * smooth(6, 18, -sdf_e)
    cr = np.clip(crack + crack2, 0, 1)
    col = col * (1 - 0.8 * cr[..., None]) + cr[..., None] * np.array([120, 10, 20], np.float32) * (0.5 + 0.5 * pulse)
    out = bg * (1 - alpha[..., None]) + col * alpha[..., None]
    # drifting shards
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    for s in shards:
        yy = (s['y'] - s['sp'] * t) % (H + 40) - 20
        xx = s['x'] + 9 * math.sin(phi + s['ph'])
        a = s['a'] + 0.5 * math.sin(phi + s['ph'])
        pts = [(xx + math.cos(a + k) * s['s'] * f, yy + math.sin(a + k) * s['s'] * f) for k, f in ((0, 1.6), (2.1, 0.7), (4.0, 1.2))]
        dr.polygon(pts, fill=(*BONE, int(150 * s['d'])))
    ov = ov.filter(ImageFilter.GaussianBlur(0.6))
    o = np.asarray(ov, np.float32)
    out = out * (1 - o[..., 3:4] / 255) + o[..., :3] * (o[..., 3:4] / 255)
    img = to_img(out)
    if text:
        img = img.convert('RGBA'); tx = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(tx)
        words = ['perceive.', 'reason.', 'act.']
        for k, wd in enumerate(words):
            ph = (t * 3 - k) % 3
            lvl = max(0.0, 1 - abs(ph - 0.35) / 0.9) if ph < 1.25 or ph > 2.7 else 0
            lvl = max(lvl, 0)
            base = 0.20
            a = base + (0.75 * math.exp(-((((t * 3 - k + 1.5) % 3) - 1.5 - 0.0) / 0.55) ** 2))
            colr = BONE if k < 2 else (200, 40, 50)
            d2.text((46, 92 + k * 58), wd, font=fW, fill=(*(colr if a > 0.6 else BONE), int(255 * min(a, 0.95))))
        d2.text((46, 62), 'i.', font=font(ITAL, 22), fill=(*ASH, 200))
        d2.line([(46, 270), (46 + 140 * ease(clamp01(t * 2) if t < .5 else clamp01(2 - 2 * t)), 270)], fill=(*CRIM, 220), width=1)
        d2.text((46, 280), 'a film in progress', font=fT, fill=(*ASH, 210))
        # crop marks
        for (x, y_, sx, sy) in ((14, 28, 1, 1), (W - 14, 28, -1, 1), (14, H - 28, 1, -1), (W - 14, H - 28, -1, -1)):
            d2.line([(x, y_), (x + 14 * sx, y_)], fill=(*ASH, 150)); d2.line([(x, y_), (x, y_ + 14 * sy)], fill=(*ASH, 150))
        img = Image.alpha_composite(img, tx).convert('RGB')
    a = np.asarray(img, np.float32)
    # gate weave
    sx = int(round(1.2 * math.sin(phi * 3 + i))); sy = int(round(0.8 * math.sin(phi * 5)))
    a = np.roll(np.roll(a, sx, 1), sy, 0)
    a *= vignette(H, W, 0.8)
    a = film(a, rng, grain=11)
    img = to_img(a)
    # cinematic bars with annotations (crisp)
    d3 = ImageDraw.Draw(img)
    d3.rectangle([0, 0, W, 20], fill=(4, 3, 4)); d3.rectangle([0, H - 20, W, H], fill=(4, 3, 4))
    d3.text((14, 3), 'REEL 01 — THE OBSERVER, REIMAGINED', font=font(MONO, 13), fill=ASH)
    fr = f'FR {i + 1:03d}/{N:03d}'; d3.text((W - 14 - d3.textlength(fr, font=font(MONO, 13)), 3), fr, font=font(MONO, 13), fill=ASH)
    tc = f'00:00:{int(t * N / HF):02d}:{int((t * N) % HF):02d}'
    d3.text((14, H - 18), tc, font=font(MONO, 13), fill=ASH)
    lab = 'SAKSHAM JUNEJA'
    d3.text((W - 14 - d3.textlength(lab, font=font(MONO, 13)), H - 18), lab, font=font(MONO, 13), fill=(190, 40, 50))
    return img

if __name__ == '__main__':
    import time; t0 = time.time()
    fr = [render(i) for i in range(N)]
    print('render s', time.time() - t0)
    fr[0].save('/home/claude/gp/header_f0.png')
    fr[30].save('/home/claude/gp/header_f30.png')
    save_gif(fr, 'header.gif', fps=HF, colors=32)
    # avatar crop (sculpture) for preview sidebar
    render(8, text=False).crop((380, 40, 740, 400 if False else 360)).save('/home/claude/gp/avatar_src.png')
