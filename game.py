#!/usr/bin/env python3
"""ZERO DAY - an audio hacking game for blind and low-vision players. Public domain (Unlicense).
Run: pip install pygame ; python game.py [--lang en]"""
import sys, os, json, math, random, time, threading, array, glob
FROZEN = getattr(sys, 'frozen', False)  # True inside the PyInstaller program
HERE = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))  # the game folder
BUNDLE = HERE  # nothing is packed inside the exe: lang, missions and sounds are real folders next to it
def res(*p):  # a file next to the exe wins over the packed one, so players can add languages and sounds
    a = os.path.join(HERE, *p); return a if os.path.exists(a) else os.path.join(BUNDLE, *p)
def langs(): return sorted({os.path.basename(p)[:-5] for d in (BUNDLE, HERE) for p in glob.glob(os.path.join(d, 'lang', '*.json'))} | {'en'})
# ---------------- i18n: add lang/xx.json and run with --lang xx ----------------
import locale, glob, re
def _detect():  # candidates, best first: --lang, then language.txt, then the device language (pt_BR gives pt-br, then pt)
    if '--lang' in sys.argv: return [sys.argv[sys.argv.index('--lang') + 1].lower()]
    try:
        with open(os.path.join(HERE, 'language.txt'), encoding='utf-8') as f: c = f.read().strip().lower()
        if c: return [c, c.split('-')[0]]
    except OSError: pass
    try:
        import warnings; warnings.simplefilter('ignore'); l = locale.getdefaultlocale()[0] or ''
    except Exception: l = ''
    a = re.split(r'[_-]', (l or os.environ.get('LANG', 'en')).split('.')[0].lower())
    return [a[0] + '-' + a[1], a[0]] if len(a) > 1 else [a[0]]
def _load(c):
    with open(res('lang', c + '.json'), encoding='utf-8') as f: return json.load(f)
def _merge(a, b):  # missing keys fall back to English; command words are added, not replaced
    for k, v in b.items():
        if k == 'cmd':
            for c, ws in v.items(): a[k][c] = list(dict.fromkeys(a[k].get(c, []) + ws))
        elif isinstance(v, dict) and isinstance(a.get(k), dict): _merge(a[k], v)
        else: a[k] = v
EN = _load('en'); D = _load('en')
LANG = next((c for c in _detect() if c != 'en' and os.path.exists(res('lang', c + '.json'))), 'en')
if LANG != 'en': _merge(D, _load(LANG))
def G(k): return D.get('gui', {}).get(k, k)
def Lx(d, z=''):  # pick the text for the player's language, else English, else the first one
    if not isinstance(d, dict): return d
    return d.get(LANG) or d.get('en') or next(iter(d.values()), z)
def T(k, **kw):
    s = D['ui'].get(k, k)
    if not kw: return s
    try: return s.format(**kw)
    except (KeyError, IndexError, ValueError): return EN['ui'].get(k, k).format(**kw)  # a broken translation never crashes the game
CMD = {w: c for c, ws in D['cmd'].items() for w in ws}
# ---------------- audio (files in sounds/ override the built-in synth) ----------------
SR = 44100; MASTER = .8; TTS = None
try:
    import pygame; pygame.mixer.pre_init(SR, -16, 2, 512); pygame.mixer.init(); pygame.mixer.set_num_channels(24); AUDIO = True
except Exception: AUDIO = False; print("Sound disabled (pip install pygame).")
def tone(f, d, kind='sine', v=.4, to=None):
    n = int(SR * d); o = []; ph = 0
    for i in range(n):
        x = i / n; ph += (f if to is None else f * (to / f) ** x) / SR; p = ph % 1
        s = math.sin(6.2832 * ph) if kind == 'sine' else (1 if p < .5 else -1) if kind == 'square' else 2 * p - 1 if kind == 'saw' else 4 * abs(p - .5) - 1
        o.append(s * v * (1 - x) ** 2)
    return o
def noise(d, v=.3): n = int(SR * d); return [(random.random() * 2 - 1) * v * (1 - i / n) ** 2 for i in range(n)]
def lay(*parts):
    r = [0.0] * max(int(o * SR) + len(s) for o, s in parts)
    for o, s in parts:
        a = int(o * SR)
        for i, x in enumerate(s): r[a + i] += x
    return r
arp = lambda fs, d=.15, st=.09, k='tri': lay(*[(i * st, tone(f, d, k)) for i, f in enumerate(fs)])
SYN = {'click': lambda r: tone(1800, .03, 'square', .15),
 'error': lambda r: lay((0, tone(140, .35, 'saw', .5, 70)), (0, tone(100, .35, 'square', .3))),
 'ok': lambda r: arp((523, 659, 784)), 'ping': lambda r: tone(700 * r, .18, 'sine', .5),
 'connect': lambda r: lay(*[(i * .08, tone(2200 if i % 2 else 1200, .07, 'square', .2)) for i in range(10)], (0, noise(.8, .15))),
 'tick': lambda r: tone(1100 * r, .03, 'square', .18),
 'alarm': lambda r: lay(*[(t, tone(880, .2, 'saw', .4)) for t in (0, .25, .5)], *[(t + .1, tone(660, .2, 'saw', .3)) for t in (0, .25, .5)]),
 'exploit': lambda r: lay((0, noise(.6, .6)), (.05, tone(80, .5, 'sine', .9, 30))),
 'unlock': lambda r: arp((392, 523, 659, 784, 1047), .25, .1),
 'dl': lambda r: lay(*[(i * .07, tone(400 * r + i * 80, .05, 'square', .15)) for i in range(4)]),
 'warn': lambda r: lay((0, tone(1500, .1, 'square', .5)), (.16, tone(1500, .1, 'square', .5))),
 'block': lambda r: lay((0, noise(.15, .6)), (.05, tone(1800, .1, 'sine', .5))),
 'win': lambda r: arp((523, 659, 784, 1047, 784, 1047, 1319), .3, .14),
 'lose': lambda r: lay((0, tone(400, 1.2, 'saw', .5, 40)), (0, noise(1.2, .4))),
 'boot': lambda r: lay((0, tone(100, 1, 'saw', .3, 800)), (.5, noise(.5, .2))), 'clear': lambda r: noise(.7, .5),
 'coin': lambda r: lay((0, tone(988, .1, 'square', .3)), (.08, tone(1319, .35, 'square', .3))),
 'lock': lambda r: lay((0, noise(.05, .6)), (.05, tone(1568, .5, 'sine', .5))),
 'ambient': lambda r: [(math.sin(6.2832 * 55 * i / SR) + math.sin(6.2832 * 82.5 * i / SR)) * .08 for i in range(2 * SR)]}
TF = (0, 262, 330, 415, 523); PAN = (0, -.7, -.25, .25, .7)
for _i in (1, 2, 3, 4): SYN['t%d' % _i] = lambda r, f=TF[_i]: tone(f, .4, 'tri', .5)
_cache = {}
def snd(n, r=1.0):
    if (n, r) in _cache: return _cache[(n, r)]
    for e in ('ogg', 'mp3', 'wav'):
        p = res('sounds', f'{n}.{e}')
        if os.path.exists(p): _cache[(n, r)] = pygame.mixer.Sound(p); return _cache[(n, r)]
    a = array.array('h')
    for x in SYN[n](r): v = int(max(-1, min(1, x)) * 32767); a.extend((v, v))
    _cache[(n, r)] = pygame.mixer.Sound(buffer=a.tobytes()); return _cache[(n, r)]
def play(n, pan=0, rate=1.0, loops=0, vol=1):
    if not AUDIO: return
    ch = snd(n, round(rate, 1)).play(loops=loops)
    if ch: ch.set_volume(vol * MASTER * min(1, 1 - pan), vol * MASTER * min(1, 1 + pan))
OUT = lambda t: print(t, flush=True)  # the GUI replaces OUT, READ and KEY
READ = input
KEY = None
def say(t):
    OUT(t)
    if TTS:
        try: TTS.say(t); TTS.runAndWait()
        except Exception: pass
def getkey(timeout=None):
    if KEY: return KEY(timeout)
    if os.name == 'nt':
        import msvcrt; end = time.time() + (timeout or 1e9)
        while time.time() < end:
            if msvcrt.kbhit(): return msvcrt.getwch()
            time.sleep(.01)
        return None
    import termios, tty, select
    fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd); r, _, _ = select.select([sys.stdin], [], [], timeout)
        return sys.stdin.read(1) if r else None
    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
# ---------------- world (mechanics here, all text in lang/*.json) ----------------
M, NODES = {}, {}
def validate(m):  # returns a list of problems, empty when the mission can be played
    N = m.get('nodes') or {}; st = m.get('start'); p = []
    if not N: return [T('v_none')]
    if st not in N: p.append(T('v_start'))
    if not any(n.get('target') for n in N.values()): p.append(T('v_target'))
    for k, n in N.items():
        w = n.get('name', k); pt = [q[0] for q in n.get('ports', [])]
        if not pt: p.append(T('v_ports', name=w))
        if n.get('x') and n['x'] not in pt: p.append(T('v_x', name=w))
        if n.get('c') and not 3 <= n['c'] <= 8: p.append(T('v_c', name=w))
        if not (n.get('x') or n.get('t') or n.get('c') or n.get('trap')): p.append(T('v_lock', name=w))
        if k != st and not n.get('needs'): p.append(T('v_needs', name=w))
    ok = {st} if st in N and not N[st].get('trap') else set(); ch = True
    while ch:
        ch = False
        for k, n in N.items():
            if k not in ok and not n.get('trap') and n.get('needs') and set(n['needs']) <= ok: ok.add(k); ch = True
    for k, n in N.items():
        if k not in ok and not n.get('trap') and n.get('needs'): p.append(T('v_unreach', name=n.get('name', k)))
    if not any(n.get('target') for k, n in N.items() if k in ok): p.append(T('v_goal'))
    return p
def mission_files():  # missions/*.json packed in the exe and next to it (same file name: the one next to the exe wins)
    seen = {}
    for d in (BUNDLE, HERE):
        for p in glob.glob(os.path.join(d, 'missions', '*.json')): seen[os.path.basename(p)] = p
    out = []
    for k in sorted(seen):
        try:
            with open(seen[k], encoding='utf-8') as f: m = json.load(f)
            m.setdefault('id', k[:-5])
            if not validate(m): out.append(m)
        except Exception: pass
    return sorted(out, key=lambda m: (m.get('order', 50), m['id']))
def ftext(m, k, fid):
    f = m['nodes'][k]['files'][fid]; t = D['nodes'].get(k, {}).get('files', {}).get(fid) if m.get('lang_text') else None
    return t[1] if t else Lx(f.get('text', {}))
def pick():
    global M, NODES
    ms = mission_files()
    if len(ms) > 1:
        say(T('pick_h'))
        for i, m in enumerate(ms, 1): say(f"{i}. {Lx(m.get('name', {}), m['id'])}")
        try: i = int(READ(T('pick')).strip()) - 1
        except ValueError: i = 0
        ms = [ms[i] if 0 <= i < len(ms) else ms[0]]
    M = ms[0]; NODES = M['nodes']
PRICE = {'vpn': 60, 'decoder': 40, 'jammer': 35, 'ghost': 30}
trace = 0; cur = None; S = {}
nm = lambda k: NODES[k]['name']
def reset():
    global S, trace, cur
    S = dict(disc={M['start']}, root=set(), done={}, clr=set(), cr=40, inv={}, n=0, auto=0, jam=0, live=1); trace = 0; cur = None
def addt(n):
    global trace
    if n > 0 and S['inv'].get('vpn'): n = round(n * .7)
    o = trace; trace = max(0, min(100, trace + n))
    if trace >= 100: S['live'] = 0; play('lose'); say(T('lose')); raise Over()
    for t in (50, 75, 90):
        if o < t <= trace: play('alarm'); say(T('warn', p=t))
class Over(Exception): pass
def ticker():
    while True:
        time.sleep(max(.16, 1.5 - trace * .013))
        if S.get('live') and trace > 0: play('tick', rate=.8 + trace / 60, vol=.5)
def check_root(k):
    n = NODES[k]; need = {m for m in 'xtc' if n.get(m)}
    if need <= S['done'].setdefault(k, set()):
        S['root'].add(k); S['cr'] += n.get('pay', 0); play('unlock'); say(T('rooted', name=nm(k), cr=n.get('pay', 0)))
        for x, m in NODES.items():  # a server appears when every server it needs has been taken over
            if x not in S['disc'] and m.get('needs') and set(m['needs']) <= S['root']: S['disc'].add(x); say(T('newnode', name=nm(x)))
def simon(k):
    seq = [random.randint(1, 4) for _ in range(k)]
    if S['auto']: S['auto'] = 0; play('ok'); say(T('simon_auto')); return True
    def pl():
        time.sleep(.4)
        for d in seq: play('t%d' % d, pan=PAN[d]); time.sleep(.55)
        say(T('your_turn'))
    say(T('simon_intro', n=k)); pl(); got = []
    while True:
        c = getkey()
        if c in ('r', 'R'): addt(2); got = []; pl()
        elif c and c in '1234':
            d = int(c); play('t%d' % d, pan=PAN[d]); got.append(d)
            if d != seq[len(got) - 1]: play('error'); say(T('simon_fail')); addt(12); return False
            if len(got) == k: time.sleep(.4); play('ok'); say(T('simon_ok')); return True
def tune():
    tgt = random.randint(1, 20); pos = 10; tries = 0; say(T('tune_intro'))
    while tries < 14:
        c = getkey()
        if c in ('a', 'A'): pos = max(1, pos - 1)
        elif c in ('d', 'D'): pos = min(20, pos + 1)
        else: continue
        tries += 1; d = abs(pos - tgt)
        if d == 0: play('lock'); say(T('tune_ok')); return True
        play('ping', pan=(.9 if tgt > pos else -.9), rate=max(.5, 2 - d / 10)); addt(1)
    say(T('tune_fail')); addt(10); return False
def download(fid):
    n = NODES[cur]; jam = S['jam']; S['jam'] = 0; say(T('dl_start'))
    for i in range(1, 11):
        play('dl', rate=.8 + i * .08)
        if not jam and 3 <= i <= 9 and random.random() < .45:
            time.sleep(.5); side = random.choice((-1, 1)); play('warn', pan=side); c = getkey(1.5)
            if (c in ('a', 'A') and side < 0) or (c in ('d', 'D') and side > 0): play('block', pan=side); say(T('dl_block'))
            else: play('error'); say(T('dl_caught')); addt(20)
            time.sleep(.5)
        else: time.sleep(1)
        addt(2)
        if i % 3 == 0: say(T('pct', p=i * 10))
    if fid == n.get('target'):
        S['live'] = 0; play('win'); r = D['ranks'][0 if trace < 30 else 1 if trace < 65 else 2]
        M.get('win') and say(Lx(M['win'])); say(T('win', rank=r, t=trace, n=S['n'], cr=S['cr'])); raise Over()
    c = n.get('loot', {}).get(fid, 0); S['cr'] += c; play('coin' if c else 'ok'); say(T('dl_other', cr=c) if c else T('dl_none'))
def event():  # a small random surprise after some commands, once the trace is above 10
    if trace < 10 or random.random() > .12: return
    e = random.choice(('admin', 'patrol', 'lucky'))
    if e == 'lucky': S['cr'] += 15; play('coin'); say(T('ev_lucky'))
    else: play('alarm'); say(T('ev_' + e)); addt(8 if e == 'admin' else 4)
def run(line):
    global cur, MASTER, TTS
    w = line.lower().replace('\u0307', '').split()
    if not w: return
    c = CMD.get(w[0]); a = ' '.join(w[1:]); n = NODES[cur] if cur else None; S['n'] += 1
    def need():
        if not cur: play('error'); say(T('no_conn')); return 1
    def rooted():
        if need(): return 1
        if cur not in S['root']: play('error'); say(T('denied')); return 1
    def file():
        fs = n.get('files', {}); f = next((k for k, v in fs.items() if a and v['name'].startswith(a)), None)
        if not f: play('error'); say(T('no_file'))
        return f
    if c == 'help': [say(l) for l in D['help']]
    elif c == 'scan':
        for i, k in enumerate(sorted(S['disc'])): play('ping', pan=-.8 + 1.6 * i / max(1, len(S['disc']) - 1), rate=1 + i * .2); time.sleep(.3)
        say(T('scan_h'))
        for i, k in enumerate(sorted(S['disc'])): say(T('scan_row', n=i + 1, name=nm(k), ip=NODES[k]['ip'], tag=T('tag_root') if k in S['root'] else ''))
        addt(2)
    elif c == 'connect':
        k = next((k for k in S['disc'] if a and (k == a or nm(k).startswith(a) or NODES[k]['ip'] == a)), None)
        if not k: play('error'); say(T('no_node')); return
        play('connect'); time.sleep(.8); cur = k; say(T('conn_root' if k in S['root'] else 'conn_ok', name=nm(k))); addt(3)
    elif c == 'disconnect': cur = None; play('click'); say(T('bye'))
    elif c == 'ports':
        if need(): return
        say(T('ports_h', name=nm(cur)))
        for i, (p, s, v) in enumerate(n['ports']): play('ping', pan=-.8 + 1.6 * i / max(1, len(n['ports']) - 1), rate=1 + i * .15); say(T('port_row', p=p, s=s, v=v)); time.sleep(.25)
        addt(4)
    elif c == 'exploit':
        if need(): return
        if not a.isdigit(): say(T('usage_exploit')); return
        p = int(a)
        if cur in S['root'] or 'x' in S['done'].get(cur, ()): say(T('root_already')); return
        if not any(q[0] == p for q in n['ports']): play('error'); say(T('port_closed')); addt(8)
        elif n.get('trap'): play('alarm'); say(T('trap')); addt(40)
        elif n.get('x') == p: S['done'].setdefault(cur, set()).add('x'); play('exploit'); say(T('x_ok', p=p)); addt(5); check_root(cur)
        else: play('error'); say(T('x_fail')); addt(15)
    elif c in ('crack', 'tune'):
        if need(): return
        m = 'c' if c == 'crack' else 't'
        if cur in S['root'] or m in S['done'].get(cur, ()): say(T('root_already')); return
        if not n.get(m): play('error'); say(T('no_lock')); return
        if n.get('x') and 'x' not in S['done'].get(cur, ()): play('error'); say(T('need_x')); return
        if (simon(n['c']) if m == 'c' else tune()): S['done'].setdefault(cur, set()).add(m); check_root(cur)
    elif c == 'ls':
        if rooted(): return
        play('click'); say(T('ls', f=', '.join(v['name'] for v in n.get('files', {}).values()) or '-'))
    elif c == 'read':
        if rooted(): return
        f = file()
        if f: play('click'); say(ftext(M, cur, f)); addt(1)
    elif c == 'get':
        if rooted(): return
        f = file()
        if f: download(f)
    elif c == 'wipe':
        if rooted(): return
        if cur in S['clr']: say(T('wipe_done')); return
        S['clr'].add(cur); play('clear'); addt(-25); say(T('wipe_ok'))
    elif c == 'status': say(T('status', t=trace, cr=S['cr'], where=T('where_in', name=nm(cur)) if cur else T('where_none')))
    elif c == 'shop':
        say(T('shop_h', cr=S['cr']))
        for k, v in PRICE.items(): say(T('shop_row', id=k, name=D['items'][k]['name'], price=v, desc=D['items'][k]['desc']))
    elif c == 'buy':
        if a not in PRICE: play('error'); say(T('noitem')); return
        if a == 'vpn' and S['inv'].get('vpn'): say(T('own')); return
        if S['cr'] < PRICE[a]: play('error'); say(T('nofunds')); return
        S['cr'] -= PRICE[a]; S['inv'][a] = S['inv'].get(a, 0) + 1; play('coin'); say(T('bought', name=D['items'][a]['name']))
    elif c == 'inv':
        its = [f"{D['items'][k]['name']} x{v}" for k, v in S['inv'].items() if v]; say(T('inv_row', f=', '.join(its)) if its else T('inv_empty'))
    elif c == 'use':
        if not S['inv'].get(a): play('error'); say(T('noitem')); return
        if a == 'vpn': say(T('own')); return
        S['inv'][a] -= 1
        if a == 'decoder': S['auto'] = 1
        elif a == 'jammer': S['jam'] = 1
        elif a == 'ghost': play('clear'); addt(-30)
        say(T('used', name=D['items'][a]['name']))
    elif c == 'voice':
        try: import pyttsx3; TTS = pyttsx3.init() if a == 'on' else None; say(T('voice_' + ('on' if TTS else 'off')))
        except Exception: say(T('voice_off'))
    elif c == 'vol':
        if a.isdigit() and int(a) <= 10: MASTER = int(a) / 10; play('ok'); say(T('vol', v=a))
    elif c == 'quit': return 'quit'
    else: play('error'); say(T('unknown')); return
    event()
def main():
    threading.Thread(target=ticker, daemon=True).start()
    if AUDIO: [snd(k) for k in SYN]; play('ambient', loops=-1, vol=.3)
    while True:
        try: pick()
        except (EOFError, KeyboardInterrupt): return
        reset(); play('boot'); [say(l) for l in (D['intro'] if M.get('lang_text') else [Lx(M.get('name', {}))] + Lx(M.get('intro', {}), []) + D['intro_tip'])]
        try:
            while True:
                try: line = READ('> ')
                except (EOFError, KeyboardInterrupt): return
                if run(line) == 'quit': return
        except Over: pass
        try: READ(T('restart_q'))
        except (EOFError, KeyboardInterrupt): return
if __name__ == '__main__': main()
