#!/usr/bin/env python3
"""ZERO DAY - wxPython interface: terminal, notes, full history, mission and translation editors. Public domain (Unlicense).
pip install wxPython pygame   (optional: accessible-output2, speaks through your screen reader)"""
import os, json, time, queue, threading, glob, re, copy, sys, traceback
import wx
from wx.lib.scrolledpanel import ScrolledPanel
import game
from game import G
def GF(k, **kw):  # like G(k).format(...), but safe when the text has other curly braces in it
    s = G(k)
    for a, b in kw.items(): s = s.replace('{' + a + '}', str(b))
    return s
DATA = os.path.join(os.path.expanduser('~'), '.zeroday'); os.makedirs(DATA, exist_ok=True)
NOTES, HIST = os.path.join(DATA, 'notes.txt'), os.path.join(DATA, 'history.log')
try: import accessible_output2.outputs.auto as _ao; SR = _ao.Auto()
except Exception: SR = None
def show_error(t, v, tb):  # never fail silently: show the error and keep it in ~/.zeroday/error.log
    msg = ''.join(traceback.format_exception(t, v, tb))
    try:
        with open(os.path.join(DATA, 'error.log'), 'a', encoding='utf-8') as f: f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + msg + '\n')
    except OSError: pass
    wx.CallAfter(wx.MessageBox, msg[-1500:] + '\n(saved in ' + os.path.join(DATA, 'error.log') + ')', 'Zero Day error', wx.OK | wx.ICON_ERROR)
sys.excepthook = show_error
threading.excepthook = lambda a: show_error(a.exc_type, a.exc_value, a.exc_traceback)
lineq, kq, want = queue.Queue(), queue.Queue(), threading.Event()
def rd(p):
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''
slug = lambda t: re.sub(r'\W+', '_', t.lower()).strip('_')
class Form(wx.Dialog):
    """Base for the mission editors. Every label is created right before its control (screen readers read
    the label just before a control) and the tab order is set explicitly. The form scrolls, buttons stay in view."""
    def __init__(s, parent, title, size):
        super().__init__(parent, title=title, size=size, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        s.p = ScrolledPanel(s); s.box = wx.BoxSizer(wx.VERTICAL); s.po = []; s.bo = []; s.hb = wx.BoxSizer(wx.HORIZONTAL)
    def field(s, label, make):
        s.box.Add(wx.StaticText(s.p, label=label), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        c = make(s.p); s.box.Add(c, 0, wx.EXPAND | wx.ALL, 6); s.po.append(c); return c
    def check(s, label, on):
        c = wx.CheckBox(s.p, label=label); c.SetValue(bool(on)); s.box.Add(c, 0, wx.ALL, 8); s.po.append(c); return c
    def prow(s, specs):
        h = wx.BoxSizer(wx.HORIZONTAL)
        for k, fn in specs: b = wx.Button(s.p, label=G(k)); b.Bind(wx.EVT_BUTTON, fn); h.Add(b, 0, wx.ALL, 4); s.po.append(b)
        s.box.Add(h)
    def button(s, key, fn=None, id=wx.ID_ANY):
        b = wx.Button(s, id, G(key))
        if fn: b.Bind(wx.EVT_BUTTON, fn)
        s.hb.Add(b, 0, wx.ALL, 6); s.bo.append(b)
    def end(s):
        s.p.SetSizer(s.box); s.p.SetupScrolling(scroll_x=False)
        top = wx.BoxSizer(wx.VERTICAL); top.Add(s.p, 1, wx.EXPAND); top.Add(s.hb, 0, wx.ALIGN_RIGHT); s.SetSizer(top)
        for o in (s.po, s.bo):
            for a, b in zip(o, o[1:]): b.MoveAfterInTabOrder(a)
        if s.po: s.po[0].SetFocus()
    def tx(s, d): return d.get(s.lang) or d.get('en') or next(iter(d.values()), '')
class ServerDialog(Form):
    def __init__(s, parent, node, others, lang):
        super().__init__(parent, G('sv_title'), (620, 620)); n = s.node = node or {}; s.lang = lang; s.others = others
        s.name = s.field(G('sv_name'), lambda p: wx.TextCtrl(p, value=n.get('name', '')))
        s.ip = s.field(G('sv_ip'), lambda p: wx.TextCtrl(p, value=n.get('ip', '10.0.0.1')))
        s.ports = s.field(G('sv_ports'), lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE, size=(-1, 80), value='\n'.join(' '.join(map(str, q)) for q in n.get('ports', []))))
        s.x = s.field(G('sv_x'), lambda p: wx.SpinCtrl(p, min=0, max=65535, initial=n.get('x', 0)))
        s.t = s.check(G('sv_tune'), n.get('t'))
        s.c = s.field(G('sv_c'), lambda p: wx.SpinCtrl(p, min=0, max=8, initial=n.get('c', 0)))
        s.pay = s.field(G('sv_pay'), lambda p: wx.SpinCtrl(p, min=0, max=500, initial=n.get('pay', 0)))
        s.trap = s.check(G('sv_trap'), n.get('trap'))
        s.needs = s.field(G('sv_needs'), lambda p: wx.CheckListBox(p, choices=[o[1] for o in others], size=(-1, 80)))
        s.needs.SetCheckedItems([i for i, o in enumerate(others) if o[0] in n.get('needs', [])])
        s.files = s.field(G('sv_files'), lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE, size=(-1, 110), value=s.ftext()))
        s.button('sv_ok', s.ok); s.button('sv_cancel', None, wx.ID_CANCEL); s.end()
    def ftext(s):
        n = s.node; out = []
        for fid, f in n.get('files', {}).items():
            e = [f['name'], s.tx(f.get('text', {}))]
            if fid == n.get('target'): e.append('target')
            elif n.get('loot', {}).get(fid): e.append(str(n['loot'][fid]))
            out.append(' | '.join(e))
        return '\n'.join(out)
    def ok(s, e):
        try: s.node = s.build()
        except ValueError as x: wx.MessageBox(str(x), G('sv_title'), wx.OK, s); return
        s.EndModal(wx.ID_OK)
    def build(s):
        if not s.name.GetValue().strip(): raise ValueError(G('sv_noname'))
        ports = []
        for l in s.ports.GetValue().splitlines():
            w = l.split(None, 2)
            if not w: continue
            if not w[0].isdigit(): raise ValueError(GF('sv_bad_port', line=l))
            ports.append([int(w[0]), w[1] if len(w) > 1 else '?', w[2] if len(w) > 2 else ''])
        old = s.node.get('files', {}); files, loot, target = {}, {}, ''
        for l in s.files.GetValue().splitlines():
            p = [x.strip() for x in l.split('|')]
            if not p[0]: continue
            fid = slug(p[0]); tx = dict(old.get(fid, {}).get('text', {})); tx[s.lang] = p[1] if len(p) > 1 else ''
            files[fid] = dict(name=p[0], text=tx)
            if len(p) > 2 and p[2].isdigit(): loot[fid] = int(p[2])
            elif len(p) > 2 and p[2].lower() == 'target': target = fid
        return dict(s.node, name=s.name.GetValue().strip(), ip=s.ip.GetValue().strip(), ports=ports, x=s.x.GetValue(), t=int(s.t.GetValue()), c=s.c.GetValue(),
                    pay=s.pay.GetValue(), trap=int(s.trap.GetValue()), needs=[s.others[i][0] for i in s.needs.GetCheckedItems()], files=files, loot=loot, target=target)
def mission_slots(m, src, dst, tag=''):
    """Every text of a mission as (where, original, get_translation, set_translation), in reading order."""
    out = []; m.setdefault('intro', {})
    first = lambda d, z='': d.get(src) or d.get('en') or next(iter(d.values()), z)
    def put(d, v):
        if v: d[dst] = v
        else: d.pop(dst, None)
    def add(where, d): out.append((where, first(d), lambda: d.get(dst, ''), lambda v: put(d, v)))
    add(tag + G('tr_name'), m['name'])
    if m.get('lang_text'): return out  # its story and files are translated through the language file
    tp = m['intro'].setdefault(dst, [])
    for i, t in enumerate(first(m['intro'], [])):
        def get(i=i, t=t):
            v = tp[i] if i < len(tp) else ''; return '' if v == t else v
        def st(v, i=i, t=t):
            while len(tp) <= i: tp.append('')
            tp[i] = v or t
        out.append((tag + GF('tr_intro', n=i + 1), t, get, st))
    if m.get('win'): add(tag + G('tr_win'), m['win'])
    for n in m['nodes'].values():
        for f in n.get('files', {}).values(): add(tag + GF('tr_file', file=f['name'], server=n['name']), f['text'])
    return out
PH = re.compile(r'\{\w*\}')
def lang_slots(en, tg, extra=()):
    """Every text of a language file as (where, original, get, set), in the order a player meets them."""
    out = []
    def sub(*path):
        d = tg
        for k in path: d = d.setdefault(k, {})
        return d
    def peek(*path):
        d = tg
        for k in path: d = d.get(k, {}) if isinstance(d, dict) else {}
        return d
    def table(sec):
        for k, v in en[sec].items():
            def st(x, k=k):
                if x: sub(sec)[k] = x
                else: sub(sec).pop(k, None)
            out.append((f"{G('tt_' + sec)}: {k}", v, lambda k=k: peek(sec).get(k, ''), st))
    def lines(sec):
        for i, v in enumerate(en[sec]):
            def get(i=i):
                l = tg.get(sec); return l[i] if isinstance(l, list) and i < len(l) and l[i] != en[sec][i] else ''
            def st(x, i=i):
                l = tg.setdefault(sec, list(en[sec])); l[:] = (l + en[sec][len(l):])[:len(en[sec])]; l[i] = x or en[sec][i]
            out.append((f"{G('tt_' + sec)} {i + 1}", v, get, st))
    table('ui')
    for sec in ('help', 'intro', 'intro_tip', 'ranks'): lines(sec)
    for k, it in en['items'].items():
        for f in ('name', 'desc'):
            def st(x, k=k, f=f):
                d = sub('items', k)
                if x: d[f] = x
                else: d.pop(f, None)
            out.append((f"{G('tt_items')}: {k} {f}", it[f], lambda k=k, f=f: peek('items', k).get(f, ''), st))
    for c, ws in en['cmd'].items():
        def st(x, c=c):
            w = [t.strip().lower() for t in x.split(',') if t.strip() and ' ' not in t.strip()]
            if w: sub('cmd')[c] = w
            else: sub('cmd').pop(c, None)
        out.append((f"{G('tt_cmd')}: {c}", ', '.join(ws), lambda c=c: ', '.join(peek('cmd').get(c, [])), st))
    for nk, n in en['nodes'].items():
        for fid, (fn, tx) in n['files'].items():
            def get(nk=nk, fid=fid): e = peek('nodes', nk, 'files').get(fid); return e[1] if e else ''
            def st(x, nk=nk, fid=fid, fn=fn):
                d = sub('nodes', nk, 'files')
                if x: d[fid] = [fn, x]
                else: d.pop(fid, None)
            out.append((f"{G('tt_nodes')}: {fn} ({n['name']})", tx, get, st))
    out.extend(extra); table('gui'); return out  # extra: mission texts, before the window texts
def prune(d):  # drop empty leftovers so the file only holds real translations
    for k in list(d):
        if isinstance(d[k], dict): prune(d[k])
        if d[k] in ({}, []): del d[k]
def finish_translation(code, tg, ms, before):
    """Write the language file, and the missions that gained a translation. Returns how many files changed."""
    H = game.HERE
    def put(sub, name, data):
        os.makedirs(os.path.join(H, sub), exist_ok=True)
        with open(os.path.join(H, sub, name + '.json'), 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
    for sec in ('help', 'intro', 'intro_tip', 'ranks'):
        if tg.get(sec) == game.EN.get(sec): tg.pop(sec, None)
    prune(tg); put('lang', code, tg); n = 0
    for m, b in zip(ms, before):
        ip = m.get('intro', {}); l = ip.get(code)
        if l is not None and (not any(l) or l == ip.get('en')): ip.pop(code, None)
        if not ip: m.pop('intro', None)
        if json.dumps(m, sort_keys=True) != b: put('missions', m['id'], m); n += 1
    return n
class LanguageDialog(Form):
    def __init__(s, parent):
        super().__init__(parent, G('tl_title'), (480, 240))
        s.code = s.field(G('tl_code'), lambda p: wx.TextCtrl(p, value=game.LANG if game.LANG != 'en' else ''))
        s.button('tl_ok', s.ok); s.button('tr_cancel', None, wx.ID_CANCEL); s.end()
    def ok(s, e):
        c = s.code.GetValue().strip().lower()
        if not re.fullmatch(r'[a-z]{2,3}(-[a-z]{2})?', c) or c == 'en': wx.MessageBox(G('tl_bad'), G('tl_title'), wx.OK, s); return
        s.c = c; s.EndModal(wx.ID_OK)
class TranslateDialog(Form):
    """One text at a time: the original, then a box for your translation. Next and Previous move along."""
    def __init__(s, parent, slots, lang):
        super().__init__(parent, G('tr_title'), (640, 520)); s.slots = slots; s.i = 0
        s.where = s.field(G('tr_where'), lambda p: wx.TextCtrl(p, style=wx.TE_READONLY))
        s.orig = s.field(G('tr_orig'), lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 110)))
        s.new = s.field(GF('tr_new', lang=lang), lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE, size=(-1, 110)))
        s.button('tr_prev', lambda e: s.go(-1)); s.button('tr_next', lambda e: s.go(1)); s.button('tr_done', s.done); s.button('tr_cancel', None, wx.ID_CANCEL)
        s.i = next((i for i, x in enumerate(slots) if not x[2]()), 0)  # start at the first untranslated text
        s.end(); s.show()
    def show(s):
        w, src, get, st = s.slots[s.i]; s.where.SetValue(GF('tr_count', i=s.i + 1, n=len(s.slots), where=w)); s.orig.SetValue(src); s.new.SetValue(get()); s.orig.SetFocus()
    def keep(s):  # a word in {curly braces} must exist in the original, or the game could not fill it in
        v = s.new.GetValue().strip(); bad = set(PH.findall(v)) - set(PH.findall(s.slots[s.i][1]))
        if bad: wx.MessageBox(GF('tr_ph', ph=', '.join(sorted(bad))), G('tr_title'), wx.OK, s); s.new.SetFocus(); return False
        s.slots[s.i][3](v); return True
    def go(s, d):
        if s.keep(): s.i = max(0, min(len(s.slots) - 1, s.i + d)); s.show()
    def done(s, e):
        if s.keep(): s.EndModal(wx.ID_OK)
class MissionEditor(Form):
    def __init__(s, parent):
        super().__init__(parent, G('ms_title'), (660, 660))
        s.dir = os.path.join(game.HERE, 'missions'); os.makedirs(s.dir, exist_ok=True)
        s.langs = game.langs(); s.lang = game.LANG if game.LANG in s.langs else 'en'; s.m = s.blank(); s.ms = []; s.keys = []
        s.lst = s.field(G('ms_list'), lambda p: wx.ListBox(p, size=(-1, 70)))
        s.cl = s.field(G('ms_lang'), lambda p: wx.Choice(p, choices=s.langs)); s.cl.SetStringSelection(s.lang)
        s.name = s.field(G('ms_name'), lambda p: wx.TextCtrl(p))
        s.intro = s.field(G('ms_intro'), lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE, size=(-1, 90)))
        s.svl = s.field(G('ms_servers'), lambda p: wx.ListBox(p, size=(-1, 90)))
        s.prow([('sv_add', s.add), ('sv_edit', s.edit), ('sv_remove', s.remove)])
        s.start = s.field(G('ms_start'), lambda p: wx.Choice(p))
        s.win = s.field(G('ms_win'), lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE, size=(-1, 60)))
        for k, fn in (('ms_save', s.save), ('ms_translate', s.translate), ('ms_new', s.new), ('ms_delete', s.delete)): s.button(k, fn)
        s.button('ms_close', None, wx.ID_CANCEL); s.end()
        s.lst.Bind(wx.EVT_LISTBOX, s.load); s.cl.Bind(wx.EVT_CHOICE, s.switch); s.refresh_list(); s.show()
    def blank(s): return dict(id='', name={}, intro={}, win={}, start='', nodes={})
    def store(s):  # copy the form into the mission, for the language that is selected now
        m = s.m; m['name'][s.lang] = s.name.GetValue().strip(); m['intro'][s.lang] = [l.strip() for l in s.intro.GetValue().splitlines() if l.strip()]
        m.setdefault('win', {})[s.lang] = s.win.GetValue().strip(); i = s.start.GetSelection()
        if 0 <= i < len(s.keys): m['start'] = s.keys[i]
    def show(s):
        m = s.m; s.name.SetValue(s.tx(m['name'])); s.intro.SetValue('\n'.join(s.tx(m.get('intro', {})) or [])); s.win.SetValue(s.tx(m.get('win', {})) or '')
        s.keys = list(m['nodes']); names = [m['nodes'][k]['name'] for k in s.keys]; s.svl.Set(names); s.start.Set(names)
        if m.get('start') in s.keys: s.start.SetSelection(s.keys.index(m['start']))
    def refresh_list(s): s.ms = game.mission_files(); s.lst.Set([game.Lx(m.get('name', {}), m['id']) for m in s.ms])
    def switch(s, e): s.store(); s.lang = s.cl.GetStringSelection(); s.show()
    def load(s, e):
        i = s.lst.GetSelection()
        if i < 0: return
        m = copy.deepcopy(s.ms[i])
        if m.pop('lang_text', None) and s.lang == game.LANG:  # built-in text lives in the language file: copy it into the mission
            for k, n in m['nodes'].items():
                for fid, f in n.get('files', {}).items(): f['text'][s.lang] = game.ftext(s.ms[i], k, fid)
            m['intro'][s.lang] = game.D['intro'][1:3]
        s.m = m; s.show()
    def others(s, skip=None): return [(k, n['name']) for k, n in s.m['nodes'].items() if k != skip]
    def pick(s):
        i = s.svl.GetSelection()
        if i < 0: wx.MessageBox(G('sv_select'), G('ms_title'), wx.OK, s)
        return i
    def add(s, e):
        s.store(); d = ServerDialog(s, None, s.others(), s.lang)
        if d.ShowModal() == wx.ID_OK:
            k = slug(d.node['name']) or 'server'
            while k in s.m['nodes']: k += '_2'
            s.m['nodes'][k] = d.node; s.show(); s.svl.SetSelection(len(s.keys) - 1)
        d.Destroy()
    def edit(s, e):
        i = s.pick()
        if i < 0: return
        s.store(); k = s.keys[i]; d = ServerDialog(s, s.m['nodes'][k], s.others(k), s.lang)
        if d.ShowModal() == wx.ID_OK: s.m['nodes'][k] = d.node
        d.Destroy(); s.show(); s.svl.SetSelection(i)
    def remove(s, e):
        i = s.pick()
        if i < 0: return
        s.store(); k = s.keys[i]; del s.m['nodes'][k]
        for n in s.m['nodes'].values(): n['needs'] = [x for x in n.get('needs', []) if x != k]
        if s.m.get('start') == k: s.m['start'] = ''
        s.show()
    def save(s, e):
        s.store(); m = s.m
        for k in ('name', 'intro', 'win'): m[k] = {l: v for l, v in m.get(k, {}).items() if v}
        mid = slug(m['name'].get('en') or next(iter(m['name'].values()), ''))
        if not mid: wx.MessageBox(G('ms_noname'), G('ms_title'), wx.OK, s); return
        pr = game.validate(m)
        if pr: wx.MessageBox('\n'.join(pr), G('ms_title'), wx.OK, s); return
        m['id'] = mid; m.pop('lang_text', None)
        with open(os.path.join(s.dir, mid + '.json'), 'w', encoding='utf-8') as f: json.dump(m, f, indent=2, ensure_ascii=False)
        s.refresh_list(); wx.MessageBox(G('ms_saved'), G('ms_title'), wx.OK, s)
    def translate(s, e):
        s.store()
        if s.lang == 'en': wx.MessageBox(G('tr_same'), G('ms_title'), wx.OK, s); return
        d = TranslateDialog(s, mission_slots(s.m, 'en', s.lang), s.lang); ok = d.ShowModal() == wx.ID_OK; d.Destroy()
        if ok: s.show(); s.save(None)
    def new(s, e=None): s.m = s.blank(); s.lst.SetSelection(wx.NOT_FOUND); s.show(); s.name.SetFocus()
    def delete(s, e):
        i = s.lst.GetSelection()
        if i < 0: return
        p = os.path.join(s.dir, s.ms[i]['id'] + '.json')
        if not os.path.exists(p): wx.MessageBox(G('ms_nodel'), G('ms_title'), wx.OK, s); return
        os.remove(p); s.refresh_list(); s.new()
class Win(wx.Frame):
    def __init__(s):
        super().__init__(None, title=G('title'), size=(900, 650)); s.nb = wx.Notebook(s); s.lines = rd(HIST).splitlines()
        def panel(name, specs):  # specs: (label, factory, stretch)
            p = wx.Panel(s.nb); v = wx.BoxSizer(wx.VERTICAL); cs = []
            for label, mk, st in specs:
                v.Add(wx.StaticText(p, label=label), 0, wx.ALL, 4); c = mk(p); cs.append(c); v.Add(c, st, wx.EXPAND | wx.ALL, 4)
            p.SetSizer(v); s.nb.AddPage(p, name); return cs
        ro = lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE | wx.TE_READONLY)
        s.out, s.inp = panel(G('tab_term'), [(G('out_l'), ro, 1), (G('in_l'), lambda p: wx.TextCtrl(p, style=wx.TE_PROCESS_ENTER), 0)])
        s.notes, = panel(G('tab_notes'), [(G('notes_l'), lambda p: wx.TextCtrl(p, style=wx.TE_MULTILINE), 1)])
        s.flt, s.hv = panel(G('tab_hist'), [(G('search_l'), lambda p: wx.TextCtrl(p), 0), (G('hist_l'), ro, 1)])
        s.notes.SetValue(rd(NOTES)); s.hv.SetValue('\n'.join(s.lines) + '\n' if s.lines else ''); s.timer = wx.Timer(s)
        s.Bind(wx.EVT_TIMER, lambda e: s.savenotes()); s.notes.Bind(wx.EVT_TEXT, lambda e: s.timer.StartOnce(800))
        s.inp.Bind(wx.EVT_TEXT_ENTER, s.enter); s.flt.Bind(wx.EVT_TEXT, lambda e: s.refilter()); s.Bind(wx.EVT_CHAR_HOOK, s.hook); s.Bind(wx.EVT_CLOSE, s.close)
        mb = wx.MenuBar()
        def menu(title, items):
            m = wx.Menu()
            for label, fn in items: i = m.Append(wx.ID_ANY, label); s.Bind(wx.EVT_MENU, fn, i)
            mb.Append(m, title)
        goto = lambda n: (lambda e: (s.nb.SetSelection(n), [s.inp, s.notes, s.flt][n].SetFocus()))
        menu(G('m_file'), [(G('m_quit') + '\tCtrl+Q', lambda e: s.Close())])
        menu(G('m_view'), [(G('tab_term') + '\tCtrl+1', goto(0)), (G('tab_notes') + '\tCtrl+2', goto(1)), (G('tab_hist') + '\tCtrl+3', goto(2)), (G('m_focus') + '\tCtrl+L', goto(0))])
        menu(G('m_tools'), [(G('m_ms') + '\tCtrl+M', lambda e: s.mission_editor()), (G('m_tr') + '\tCtrl+T', lambda e: s.translator())]); s.SetMenuBar(mb); s.inp.SetFocus()
    def translator(s):
        d = LanguageDialog(s); ok = d.ShowModal() == wx.ID_OK; code = getattr(d, 'c', ''); d.Destroy()
        if not ok: return
        p = game.res('lang', code + '.json'); tg = json.loads(rd(p)) if os.path.exists(p) else {}
        ms = [copy.deepcopy(m) for m in game.mission_files()]; before = [json.dumps(m, sort_keys=True) for m in ms]; extra = []
        for m in ms: extra += mission_slots(m, 'en', code, (m['name'].get('en') or next(iter(m['name'].values()), m['id'])) + ': ')
        d = TranslateDialog(s, lang_slots(game.EN, tg, extra), code); ok = d.ShowModal() == wx.ID_OK; d.Destroy()
        if ok:
            finish_translation(code, tg, ms, before)
            wx.MessageBox(GF('tl_saved', code=code), G('tl_title'), wx.OK, s)
    def mission_editor(s):
        d = MissionEditor(s); d.ShowModal(); d.Destroy()
    def savenotes(s):
        with open(NOTES, 'w', encoding='utf-8') as f: f.write(s.notes.GetValue())
    def refilter(s):
        q = s.flt.GetValue().lower(); s.hv.SetValue('\n'.join(l for l in s.lines if q in l.lower()) + '\n')
    def add(s, t, tag=''):  # every message goes to the terminal and to the permanent history
        s.out.AppendText(tag + t + '\n'); l = time.strftime('%Y-%m-%d %H:%M:%S ') + tag + t; s.lines.append(l)
        with open(HIST, 'a', encoding='utf-8') as f: f.write(l + '\n')
        if s.flt.GetValue(): s.refilter()
        else: s.hv.AppendText(l + '\n')
        if SR and not tag:
            try: SR.speak(t, interrupt=False)
            except Exception: pass
    def enter(s, e):
        v = s.inp.GetValue(); s.inp.Clear()
        if not want.is_set(): s.add(v, '> '); lineq.put(v)
    def hook(s, e):  # during tone/frequency/firewall minigames single keys go to the game
        if want.is_set() and s.nb.GetSelection() == 0 and not (e.ControlDown() or e.AltDown()):
            k = e.GetKeyCode(); u = e.GetUnicodeKey(); c = 'a' if k == wx.WXK_LEFT else 'd' if k == wx.WXK_RIGHT else chr(u) if u > 31 else None
            if c: kq.put(c)
            return
        e.Skip()
    def close(s, e): s.savenotes(); lineq.put(None); s.Destroy()
def start_engine(w):
    game.OUT = lambda t: wx.CallAfter(w.add, t)
    def read(p):
        if p != '> ': game.OUT(p)
        v = lineq.get()
        if v is None: raise EOFError
        return v
    def key(timeout=None):
        while not kq.empty(): kq.get_nowait()
        want.set()
        try: return kq.get(timeout=timeout)
        except queue.Empty: return None
        finally: want.clear()
    game.READ, game.KEY = read, key; threading.Thread(target=game.main, daemon=True).start()
if __name__ == '__main__':
    app = wx.App(); w = Win(); w.Show(); start_engine(w); app.MainLoop()
