"""Thanksgiving Charades: a spinning wheel of prompts plus a two-team scoreboard.

Run with:  streamlit run app.py
"""
import html as _html
import math
import random
import time

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Thanksgiving Charades", page_icon="🦃", layout="wide")

CATS = [
    ("The feast", "#e8742a", [
        "Carving the turkey", "Mashing the potatoes", "Basting the turkey", "Stirring lumpy gravy",
        "Sliding cranberry sauce out of the can", "Rolling out pie crust", "Stuffing the turkey",
        "Eating corn on the cob", "Whipping cream by hand", "Pulling hot rolls out of the oven",
        "Chopping onions", "Slicing the pie"]),
    ("After dinner", "#f2b632", [
        "Falling asleep on the couch", "Unbuttoning your pants", "Washing a mountain of dishes",
        "Packing up leftovers", "Sneaking a second slice of pie", "Hunting for a matching Tupperware lid",
        "Hiding from cleanup duty", "Making a leftover turkey sandwich"]),
    ("Family time", "#c8d27a", [
        "Fighting over the last roll", "Sitting at the kids' table", "Grandma pinching your cheeks",
        "Saying grace", "A toddler refusing vegetables", "Posing for the family photo",
        "Uncle telling the same old story", "Sharing what you're thankful for", "Passing food around the table"]),
    ("Football", "#e8742a", [
        "Throwing a touchdown pass", "Backyard football game", "Referee calling a penalty", "Yelling at the TV",
        "Touchdown celebration dance", "Kicking a field goal", "Fumbling the ball", "Napping through the fourth quarter"]),
    ("The parade", "#f2b632", [
        "Holding a giant balloon in the wind", "Marching band drummer", "Waving from a float", "Twirling a baton",
        "Santa arriving at the end of the parade", "Tuba player marching", "Watching the parade in pajamas"]),
    ("Hosting chaos", "#c8d27a", [
        "Stuck in holiday traffic", "Waiting in airport security", "Setting the fancy table",
        "Greeting guests at the door", "Thawing a frozen turkey", "Smoke alarm going off",
        "Running to the store for forgotten butter", "Hiding the burnt rolls"]),
    ("On the farm", "#e8742a", [
        "A turkey strutting", "A turkey escaping the farmer", "The president pardoning a turkey", "Picking pumpkins",
        "Raking leaves", "Jumping into a leaf pile", "Picking apples", "Riding a hay wagon",
        "Hunting a turkey", "Chopping wood", "Building a fire"]),
    ("Traditions", "#f2b632", [
        "Breaking the wishbone", "Pilgrims landing at Plymouth Rock", "Sailing on the Mayflower",
        "Black Friday shopping rush", "Drawing a hand turkey", "Running a turkey trot race",
        "Putting up holiday lights early", "Writing a thank-you note"]),
]
N = len(CATS)
SEG = 360 / N
TOTAL = sum(len(c[2]) for c in CATS)

# ---------- state ----------
ss = st.session_state
ss.setdefault("used", {i: [] for i in range(N)})
ss.setdefault("rot", 0.0)
ss.setdefault("prev_rot", 0.0)
ss.setdefault("cur", None)          # (cat_index, prompt)
ss.setdefault("spin_id", 0)
ss.setdefault("scores", [0, 0])
ss.setdefault("names", ["Team A", "Team B"])
ss.setdefault("last", "")


def left_in(i):
    return [p for p in CATS[i][2] if p not in ss.used[i]]


def take(i):
    p = random.choice(left_in(i))
    ss.used[i].append(p)
    ss.cur = (i, p)
    ss.reveal = False


def spin():
    open_cats = [i for i in range(N) if left_in(i)]
    if not open_cats:
        return
    i = random.choice(open_cats)
    jitter = (random.random() - 0.5) * SEG * 0.7
    target = (-(i * SEG + SEG / 2) + jitter) % 360
    base = ss.rot - (ss.rot % 360)
    ss.prev_rot = ss.rot
    ss.rot = base + 360 * 6 + target
    ss.spin_id += 1
    take(i)


def skip():
    if ss.cur and left_in(ss.cur[0]):
        take(ss.cur[0])


def award(t):
    ss.scores[t] += 1
    ss.last = f"Point to {_html.escape(ss.names[t])}. Now {ss.scores[0]} to {ss.scores[1]}."


def bump(t, d):
    ss.scores[t] = max(0, ss.scores[t] + d)


def reset_deck():
    ss.used = {i: [] for i in range(N)}
    ss.cur = None


def reset_scores():
    ss.scores = [0, 0]
    ss.last = ""


# ---------- styling ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Nunito:wght@600;800&display=swap" rel="stylesheet">
<style>
.stApp{background:#4a0d1a;color:#fff3e2}
.stApp, .stApp p, .stApp label, .stApp span, .stApp div{font-family:Nunito,system-ui,sans-serif}
h1.tg{font-family:"Alfa Slab One",Georgia,serif;color:#f2b632;font-size:clamp(30px,5vw,46px);line-height:1.05;margin:0 0 .3em;font-weight:400}
.stTabs [data-baseweb="tab"]{font-weight:800;font-size:18px;color:#fff3e2}
.stTabs [aria-selected="true"]{color:#f2b632}
.stButton>button{border-radius:12px;font-weight:800;min-height:46px;background:#f2b632;color:#2a0710;border:0}
.stButton>button:hover{filter:brightness(1.08);color:#2a0710;border:0}
.stButton>button:disabled{opacity:.5}
.pcard{border-radius:20px;padding:22px;min-height:200px;display:flex;flex-direction:column;justify-content:space-between;gap:12px;box-shadow:0 8px 0 #2a0710;margin-bottom:14px}
.pcard.down{background:repeating-linear-gradient(45deg,#e8742a 0 14px,#d9631d 14px 28px);color:#2a0710}
.pcard.up{background:#fff3e2;color:#3a0a14}
.pcard .cat b{background:#2a0710;color:#f2b632;padding:3px 10px;border-radius:99px;font-weight:800}
.pcard .pr{font-family:"Alfa Slab One",serif;font-size:clamp(26px,3.4vw,36px);line-height:1.1}
.pcard .hint{font-weight:700;font-size:14px;opacity:.85}
.team{border-radius:22px;padding:20px 22px;box-shadow:0 8px 0 #2a0710;margin-bottom:12px}
.team.a{background:#e8742a;color:#2a0710}.team.b{background:#7d8c34;color:#fff8e8}
.team .nm{font-family:"Alfa Slab One",serif;font-size:28px}
.team .tot{font-family:"Alfa Slab One",serif;font-size:clamp(72px,10vw,110px);line-height:1}
.tallies{display:flex;flex-wrap:wrap;gap:10px 16px;min-height:60px;align-items:center}
.lead{background:#5e1424;border-radius:14px;padding:12px 16px;font-weight:800;margin-bottom:16px}
.small{color:#f3d3c0;font-size:14px}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="tg">Thanksgiving Charades</h1>', unsafe_allow_html=True)


# ---------- wheel svg ----------
def pt(a, r):
    t = math.radians(a - 90)
    return f"{r * math.cos(t):.2f}", f"{r * math.sin(t):.2f}"


def wheel_html():
    parts = []
    for i, (name, color, _) in enumerate(CATS):
        a0, a1 = i * SEG, (i + 1) * SEG
        x0, y0 = pt(a0, 192)
        x1, y1 = pt(a1, 192)
        n_left = len(left_in(i))
        fill = color if n_left else "#8a6a5a"
        words = name.split(" ")
        spans = "".join(f'<tspan x="0" dy="{17 if k else 0}">{w}</tspan>' for k, w in enumerate(words))
        y_main = -4 if len(words) > 1 else 4
        y_sub = 34 if len(words) > 1 else 24
        sub = f"{n_left} left" if n_left else "all done"
        parts.append(
            f'<path d="M0 0L{x0} {y0}A192 192 0 0 1 {x1} {y1}Z" fill="{fill}" stroke="#3a1d0c" stroke-width="3"/>'
            f'<g transform="rotate({i * SEG + SEG / 2}) translate(0 -128)">'
            f'<text text-anchor="middle" y="{y_main}" style="font:800 15px Nunito,sans-serif" fill="#2a0710">{spans}</text>'
            f'<text text-anchor="middle" y="{y_sub}" style="font:700 13px Nunito,sans-serif" fill="#2a0710" opacity=".75">{sub}</text></g>'
        )
    pegs = "".join(
        f'<circle cx="{pt(k * SEG / 2, 200)[0]}" cy="{pt(k * SEG / 2, 200)[1]}" r="4.5" fill="#f2b632" stroke="#3a1d0c" stroke-width="1.5"/>'
        for k in range(N * 2))
    anim = f"spin{ss.spin_id}"
    dur = "4.6s" if ss.spin_id else "0s"
    return f"""
<style>
@keyframes {anim}{{from{{transform:rotate({ss.prev_rot}deg)}}to{{transform:rotate({ss.rot}deg)}}}}
#w{ss.spin_id}{{transform:rotate({ss.rot}deg);animation:{anim} {dur} cubic-bezier(.12,.67,.12,1);transform-origin:0 0}}
@media(prefers-reduced-motion:reduce){{#w{ss.spin_id}{{animation:none}}}}
</style>
<div style="position:relative;max-width:520px;margin:0 auto;aspect-ratio:1">
<svg viewBox="0 0 44 56" style="position:absolute;left:50%;top:-6px;width:44px;height:56px;transform:translateX(-50%);z-index:2">
<path d="M4 4h36L22 52z" fill="#fff3e2" stroke="#2a0710" stroke-width="4" stroke-linejoin="round"/></svg>
<svg viewBox="-210 -210 420 420" style="width:100%;height:100%">
<circle r="206" fill="#6b3a1f" stroke="#3a1d0c" stroke-width="4"/>{pegs}
<g id="w{ss.spin_id}">{''.join(parts)}</g>
<circle r="52" fill="#f2b632" stroke="#6b3a1f" stroke-width="10"/>
<text text-anchor="middle" y="8" style="font:400 22px 'Alfa Slab One',serif" fill="#3a0a14">🦃</text>
</svg></div>"""


def tally_svg(k):
    lines = "".join(f'<line x1="{8 + j * 11}" y1="6" x2="{8 + j * 11}" y2="50"/>' for j in range(min(k, 4)))
    slash = '<line x1="2" y1="44" x2="50" y2="12"/>' if k == 5 else ""
    return (f'<svg viewBox="0 0 54 56" width="54" height="56"><g stroke="currentColor" stroke-width="5" '
            f'stroke-linecap="round">{lines}{slash}</g></svg>')


TIMER_HTML = """
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:#5e1424;border-radius:16px;padding:12px 14px;font-family:Nunito,sans-serif;color:#fff3e2">
<span id="c" style="font:400 34px/1 'Alfa Slab One',serif;color:#f2b632;min-width:3.4ch">60</span>
<span style="flex:1 1 100px;height:10px;border-radius:99px;background:#7a3a48;overflow:hidden"><i id="f" style="display:block;height:100%;width:100%;background:#f2b632"></i></span>
<button id="b" style="font:800 15px Nunito;border:0;border-radius:12px;min-height:44px;padding:0 16px;background:#f2b632;color:#2a0710;cursor:pointer">Start timer</button>
<button id="l" style="font:800 15px Nunito;border:0;border-radius:12px;min-height:44px;padding:0 14px;background:transparent;color:#fff3e2;box-shadow:inset 0 0 0 2px #b98a8a;cursor:pointer">60s</button>
</div>
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Nunito:wght@800&display=swap" rel="stylesheet">
<script>
let len=60,left=60,id=null;const L=[30,60,90,120];
const c=document.getElementById('c'),f=document.getElementById('f'),b=document.getElementById('b'),l=document.getElementById('l');
function draw(){c.textContent=left===0?'Time!':left;c.style.color=(left<=10&&id)?'#ff8a7a':'#f2b632';f.style.width=(left/len*100)+'%';l.textContent=len+'s';b.textContent=id?'Pause':(left===0?'Restart':left<len?'Resume':'Start timer')}
function stop(){clearInterval(id);id=null;draw()}
function beep(){try{const a=new AudioContext(),o=a.createOscillator(),g=a.createGain();o.frequency.value=520;o.connect(g);g.connect(a.destination);g.gain.setValueAtTime(.25,a.currentTime);g.gain.exponentialRampToValueAtTime(.001,a.currentTime+.9);o.start();o.stop(a.currentTime+.9)}catch(e){}}
b.onclick=()=>{if(id){stop();return}if(left===0)left=len;id=setInterval(()=>{left--;if(left<=0){left=0;stop();beep()}else draw()},1000);draw()};
l.onclick=()=>{len=L[(L.indexOf(len)+1)%L.length];stop();left=len;draw()};
draw();
</script>"""

# ---------- layout ----------
spin_tab, score_tab = st.tabs(["Spin", "Score"])

with spin_tab:
    used_count = sum(len(v) for v in ss.used.values())
    left_col, right_col = st.columns([1.1, 1], gap="large")
    with left_col:
        st.markdown(wheel_html(), unsafe_allow_html=True)
    with right_col:
        out = used_count >= TOTAL
        c1, c2 = st.columns(2)
        spun = c1.button("Spin" if not out else "Out of prompts", on_click=spin, disabled=out,
                         use_container_width=True, type="primary")
        c2.button("New prompt, same category", on_click=skip,
                  disabled=not (ss.cur and left_in(ss.cur[0])), use_container_width=True)

        card = st.empty()
        if spun:
            # let the wheel finish turning before showing the category
            card.markdown('<div class="pcard down"><div class="cat"><b>Spinning…</b></div>'
                          '<div class="pr">Round and round</div><div class="hint">&nbsp;</div></div>',
                          unsafe_allow_html=True)
            time.sleep(4.6)

        if ss.cur:
            i, p = ss.cur
            reveal = st.toggle("Show prompt (actor only)", key="reveal")
            if reveal:
                html = (f'<div class="pcard up"><div class="cat"><b>{CATS[i][0]}</b></div>'
                        f'<div class="pr">{p}</div><div class="hint">Memorize it, switch this off, then start the timer.</div></div>')
            else:
                html = (f'<div class="pcard down"><div class="cat"><b>{CATS[i][0]}</b></div>'
                        f'<div class="pr">Actor only</div><div class="hint">Flip the switch above to peek. '
                        f'No talking, no pointing at objects!</div></div>')
        else:
            html = ('<div class="pcard down"><div class="cat"><b>Ready?</b></div><div class="pr">Spin the wheel</div>'
                    '<div class="hint">The actor peeks at the prompt. Everyone else, look away.</div></div>')
        card.markdown(html, unsafe_allow_html=True)

        if hasattr(st, "iframe"):
            st.iframe(TIMER_HTML, height=80)
        else:
            components.html(TIMER_HTML, height=80)

        st.markdown("**Who guessed it?**")
        a1, a2 = st.columns(2)
        a1.button(f"{ss.names[0]} +1", on_click=award, args=(0,), use_container_width=True)
        a2.button(f"{ss.names[1]} +1", on_click=award, args=(1,), use_container_width=True)
        if ss.last:
            st.markdown(f'<span class="small">{ss.last}</span>', unsafe_allow_html=True)

        st.markdown(f'<p class="small">{TOTAL - used_count} of {TOTAL} prompts left, '
                    f'no repeats until you reshuffle.</p>', unsafe_allow_html=True)
        with st.popover("Reshuffle all prompts"):
            st.write("Put every prompt back in the deck?")
            st.button("Yes, reshuffle", on_click=reset_deck)

with score_tab:
    a, b = ss.scores
    if a == b:
        lead = f"Tied at {a}" if a else "All tied up"
    else:
        lead = f"{_html.escape(ss.names[0 if a > b else 1])} leads by {abs(a - b)}"
    st.markdown(f'<div class="lead">{lead}</div>', unsafe_allow_html=True)

    cols = st.columns(2, gap="large")
    for t, col in enumerate(cols):
        with col:
            ss.names[t] = st.text_input("Team name", value=ss.names[t], key=f"name{t}", max_chars=24) or f"Team {'AB'[t]}"
            n = ss.scores[t]
            groups = [min(5, n - g) for g in range(0, n, 5)]
            tallies = "".join(tally_svg(k) for k in groups) or "<em>No points yet</em>"
            st.markdown(
                f'<div class="team {"ab"[t]}"><div class="nm">{_html.escape(ss.names[t])}</div>'
                f'<div class="tot">{n}</div><div class="tallies">{tallies}</div></div>',
                unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            b1.button("+1", key=f"plus{t}", on_click=bump, args=(t, 1), use_container_width=True)
            b2.button("−1", key=f"minus{t}", on_click=bump, args=(t, -1), use_container_width=True)

    with st.popover("Reset scores"):
        st.write("Reset both teams to zero?")
        st.button("Yes, reset", on_click=reset_scores)
