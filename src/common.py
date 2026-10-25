import numpy as np, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageSequence

W = 800
FPS = 15
BLACK = (9, 8, 9); CHAR = (26, 24, 26); BONE = (226, 219, 204)
CRIM = (158, 20, 32); CRIM_D = (92, 10, 18); ASH = (150, 143, 134); CRIM_T = (208, 46, 58)
OUT = '/mnt/user-data/outputs/github-profile/assets'
F = '/usr/share/fonts/truetype/'
SERIF = F + 'google-fonts/Lora-Variable.ttf'
ITAL = F + 'freefont/FreeSerifItalic.ttf'
MONO = F + 'liberation/LiberationMono-Regular.ttf'
LORA = F + 'google-fonts/Lora-Variable.ttf'

def font(path, size): return ImageFont.truetype(path, size)

def fbm(h, w, seed, base=6, octaves=4, persistence=0.5):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        gh, gw = max(2, base * 2 ** o * h // w + 2), base * 2 ** o + 2
        g = rng.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += amp * (np.asarray(im, np.float32) / 255); tot += amp; amp *= persistence
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)

def loop_field(a, b, phi):
    return a * math.cos(phi) + b * math.sin(phi)

def vignette(h, w, strength=0.75):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w * 0.62)) ** 2 + ((y - h / 2) / (h * 0.75)) ** 2)
    return np.clip(1 - strength * d ** 2.2, 0.15, 1)[..., None]

def film(img, rng, grain=7.0, scratches=True, dust=True, flicker=0.03, density=0.09):
    """img float HxWx3 0..255 -> float with grain/scratches/dust."""
    h, w, _ = img.shape
    img = img * (1 + flicker * (rng.random() - 0.5) * 2)
    if grain > 0:
        n = (rng.normal(0, grain, (h, w, 1)) * (rng.random((h, w, 1)) < density)).astype(np.float32)
        img = img + n
    if scratches:
        for _ in range(rng.integers(0, 3)):
            x = rng.integers(0, w); y0 = rng.integers(0, h); L = rng.integers(h // 5, h)
            a = rng.uniform(25, 70)
            img[y0:y0 + L, x:x + 1] += a
            if rng.random() < 0.3 and x + 1 < w: img[y0:y0 + L // 2, x + 1:x + 2] += a * 0.4
    if dust:
        for _ in range(rng.integers(0, 6)):
            x = rng.integers(0, w - 3); y = rng.integers(0, h - 3); s = rng.integers(1, 3)
            img[y:y + s, x:x + s] += rng.uniform(40, 90)
    return img

def to_img(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def tw(draw, text, fnt, spacing=0):
    return sum(draw.textlength(c, font=fnt) + spacing for c in text) - spacing

def spaced(draw, xy, text, fnt, fill, spacing=0, anchor_x='l'):
    x, y = xy
    total = tw(draw, text, fnt, spacing)
    if anchor_x == 'c': x -= total / 2
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill)
        x += draw.textlength(c, font=fnt) + spacing
    return total

def save_gif(frames, name, fps=FPS, colors=64, outdir=OUT):
    """frames: list of PIL RGB. Global palette, no dither (grain already dithers)."""
    path = os.path.join(outdir, name)
    step = max(1, len(frames) // 8)
    w, h = frames[0].size
    sheet = Image.new('RGB', (w, h * min(8, len(frames[::step]))))
    for i, f in enumerate(frames[::step][:8]): sheet.paste(f, (0, i * h))
    pal = sheet.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
    p = pal.getpalette()
    res = [BONE, (246, 240, 226), CRIM_T, (215, 38, 50), ASH, (186, 179, 167)]
    for j, col in enumerate(res):
        idx = colors - 1 - j
        p[idx * 3:idx * 3 + 3] = list(col)
    pal.putpalette(p)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=False, disposal=1)
    kb = os.path.getsize(path) / 1024
    print(f'{name}: {len(frames)} frames {w}x{h} {kb:.0f} KB')
    return path

def ease(t): return t * t * (3 - 2 * t)
def clamp01(t): return max(0.0, min(1.0, t))
