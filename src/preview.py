"""Render the scrolling GitHub-profile preview (MP4) from the real generated GIF files.
Project slots use /mnt/user-data/outputs/github-profile/project-gifs/<name>.gif when present,
otherwise the labeled placeholder GIFs."""
import sys, os, bisect, subprocess
sys.path.insert(0, '/home/claude/gp/src')
from common import *

ROOT = '/mnt/user-data/outputs/github-profile'
A = ROOT + '/assets/'; P = ROOT + '/preview/placeholders/'; U = ROOT + '/project-gifs/'
VW, VH, FPSV = 1280, 720, 24
BG = (13, 17, 23); BORDER = (48, 54, 61); TXT = (230, 237, 243); MUTED = (125, 133, 144)
CW = 626; S = CW / W
LIB = '/usr/share/fonts/truetype/liberation/'

def load(path, size=None, cover=False):
    g = Image.open(path); fr = []; ms = []
    for f in ImageSequence.Iterator(g):
        im = f.convert('RGB')
        if cover:  # fit to 800x450 cover
            r = max(800 / im.width, 450 / im.height); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
            l, t = (im.width - 800) // 2, (im.height - 450) // 2; im = im.crop((l, t, l + 800, t + 450))
        im = im.resize((CW, round(im.height * S)), Image.LANCZOS)
        fr.append(np.asarray(im)); ms.append(max(20, f.info.get('duration', 80)))
    cum = np.cumsum(ms).tolist()
    return dict(frames=fr, cum=cum, total=cum[-1], h=fr[0].shape[0], path=path)

def pick(t, a):
    tm = (t * 1000) % a['total']; return a['frames'][min(bisect.bisect_right(a['cum'], tm), len(a['frames']) - 1)]

def project(i, key, ph):
    p = U + key + '.gif'
    if os.path.exists(p): return load(p, cover=True), True
    return load(P + f'slot-{i}.gif'), False

def build():
    names = [('deimos', 'DEIMOS'), ('chess-ai', 'CHESS AI'), ('tai', 'TAI'), ('saksham-persona', 'SAKSHAM PERSONA')]
    seq = [('header', load(A + 'header.gif'), 6), ('name', load(A + 'name.gif'), 6), ('panel', load(A + 'panel.gif'), 6),
           ('social', load(A + 'social.gif'), 14), ('ta1', load(A + 'transition-a.gif'), 6), ('section', load(A + 'section-featured.gif'), 18)]
    real = []
    for i, (k, nm) in enumerate(names, 1):
        seq.append((f'cap{i}', load(A + f'caption-{i}.gif'), 22 if i > 1 else 6))
        a, isreal = project(i, k, nm); real.append(isreal); seq.append((f'proj{i}', a, 4))
    seq += [('ta2', load(A + 'transition-a.gif'), 22), ('interests', load(A + 'interests.gif'), 6),
            ('tb', load(A + 'transition-b.gif'), 6), ('closing', load(A + 'closing.gif'), 6)]
    return seq, real

def layout(seq):
    x = 454 + 1 + 32 - 0; y = 150 + 46 + 28; pos = {}
    for k, a, gap in seq:
        y += gap; pos[k] = y; y += a['h']
    end = y + 28
    page_h = end + 140
    return pos, end, page_h

def static_page(seq, pos, end, page_h):
    im = Image.new('RGB', (VW, page_h), BG); d = ImageDraw.Draw(im)
    fb = ImageFont.truetype(LIB + 'LiberationSans-Bold.ttf', 24); fr = ImageFont.truetype(LIB + 'LiberationSans-Regular.ttf', 20)
    fs = ImageFont.truetype(LIB + 'LiberationSans-Regular.ttf', 14); fsb = ImageFont.truetype(LIB + 'LiberationSans-Bold.ttf', 14)
    d.rectangle([0, 0, VW, 64], fill=(1, 4, 9)); d.line([(0, 64), (VW, 64)], fill=BORDER)
    for k in range(3): d.rounded_rectangle([24, 24 + k * 7, 44, 26 + k * 7], 1, fill=TXT)
    d.text((64, 22), 'SakshamJuneja007', font=fsb, fill=TXT)
    d.rounded_rectangle([VW - 380, 16, VW - 108, 48], 6, outline=BORDER, fill=(13, 17, 23)); d.text((VW - 366, 24), 'Type / to search', font=fs, fill=MUTED)
    d.ellipse([VW - 64, 16, VW - 32, 48], fill=(40, 36, 40), outline=BORDER)
    tabs = ['Overview', 'Repositories', 'Projects', 'Packages', 'Stars']; x = 454
    for k, tname in enumerate(tabs):
        d.text((x, 84), tname, font=fsb if k == 0 else fs, fill=TXT if k == 0 else MUTED)
        w = d.textlength(tname, font=fsb if k == 0 else fs)
        if k == 0: d.rectangle([x - 8, 116, x + w + 8, 118], fill=(247, 129, 102))
        x += w + 36
    d.line([(0, 118), (VW, 118)], fill=BORDER)
    # sidebar
    ax, ay = 134, 150
    av = Image.open('/home/claude/gp/avatar_src.png').convert('RGB'); r = max(296 / av.width, 296 / av.height)
    av = av.resize((round(av.width * r), round(av.height * r)), Image.LANCZOS); l = (av.width - 296) // 2; av = av.crop((l, 0, l + 296, 296))
    m = Image.new('L', (296, 296), 0); ImageDraw.Draw(m).ellipse([0, 0, 295, 295], fill=255); im.paste(av, (ax, ay), m)
    d.ellipse([ax, ay, ax + 296, ay + 296], outline=BORDER, width=1)
    d.text((ax, ay + 312), 'Saksham Juneja', font=fb, fill=TXT); d.text((ax, ay + 344), 'SakshamJuneja007', font=fr, fill=MUTED)
    d.rounded_rectangle([ax, ay + 386, ax + 296, ay + 418], 6, outline=BORDER, fill=(33, 38, 45)); d.text((ax + 108, ay + 394), 'Edit profile', font=fsb, fill=TXT)
    # README box
    bx0, bx1 = 454, 454 + 692
    d.rounded_rectangle([bx0, 150, bx1, end], 6, outline=BORDER, fill=BG)
    d.rounded_rectangle([bx0, 150, bx1, 196], 6, fill=(22, 27, 34)); d.rectangle([bx0, 180, bx1, 196], fill=(22, 27, 34)); d.line([(bx0, 196), (bx1, 196)], fill=BORDER)
    d.text((bx0 + 16, 163), 'SakshamJuneja007', font=fsb, fill=TXT); d.text((bx0 + 16 + d.textlength('SakshamJuneja007', font=fsb) + 8, 163), '/  README.md', font=fs, fill=MUTED)
    d.text((bx0, end + 40), '', font=fs)
    return np.asarray(im)

def smoother(u): return u * u * u * (u * (u * 6 - 15) + 10)

def main(out_mp4, limit=None):
    seq, real = build(); pos, end, page_h = layout(seq)
    page = static_page(seq, pos, end, page_h)
    el = {k: (pos[k], a) for k, a, _ in seq}
    maxs = page_h - VH
    def cen(k, off=0): y, a = el[k]; return int(np.clip(y + a['h'] / 2 - VH / 2 + off, 0, maxs))
    keys = [(0, 3.4), (cen('name', 150), 3.0), (int(np.clip((pos['social'] + pos['section'] + el['section'][1]['h']) / 2 - VH / 2, 0, maxs)), 2.8),
            (cen('proj1', -30), 3.6), (cen('proj2', -30), 3.6), (cen('proj3', -30), 3.6), (cen('proj4', -30), 3.6),
            (cen('interests', 60), 3.0), (maxs, 4.2)]
    TR = 1.6; tl = []; t = 0.0
    for k, (sy, dw) in enumerate(keys):
        tl.append((t, t + dw, sy)); t += dw
        if k < len(keys) - 1: t += TR
    total = t
    def scroll_at(t):
        for k, (a, b, sy) in enumerate(tl):
            if t <= b: return sy
            if k < len(tl) - 1 and t < tl[k + 1][0]:
                u = (t - b) / (tl[k + 1][0] - b); return sy + (tl[k + 1][2] - sy) * smoother(u)
        return tl[-1][2]
    n = int(total * FPSV); 
    if limit: n = min(n, limit)
    print(f'page {VW}x{page_h}, duration {total:.1f}s, {n} frames, real project gifs: {real}', flush=True)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{VW}x{VH}', '-r', str(FPSV), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_mp4], stdin=subprocess.PIPE)
    cx = 454 + 1 + 32
    for i in range(n):
        t = i / FPSV; sy = int(round(scroll_at(t)))
        fr = page[sy:sy + VH].copy()
        for k, (y0, a) in el.items():
            ry = y0 - sy
            if ry + a['h'] <= 0 or ry >= VH: continue
            src = pick(t, a); a0 = max(0, -ry); b0 = min(a['h'], VH - ry)
            fr[ry + a0:ry + b0, cx:cx + CW] = src[a0:b0]
        th = max(40, int(VH * VH / page_h)); ty = int((VH - th) * sy / maxs)
        fr[ty:ty + th, VW - 10:VW - 4] = (60, 66, 74)
        f = min(1, t / 0.5) * min(1, (total - t) / 0.6)
        if f < 1: fr = (fr * f).astype(np.uint8)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); print('done', flush=True)
    return total

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)
