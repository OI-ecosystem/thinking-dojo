#!/usr/bin/env python3
"""Builds the Thinking Dojo's article, questions, teachers and free-cards pages.

Run from the repository root:  python3 _build/build_pages.py

- Every page is plain static HTML with its styles inline, like index.html.
- BASE is the public address of the site. If the site moves to its own domain,
  change BASE here, run this script again, and commit the result.
- The script also adds links and sharing tags to index.html. Those edits are
  applied once and skipped on later runs.
- The folder name starts with an underscore so GitHub Pages does not publish it.
"""
import html
import json
import os
import re
import sys

BASE = "https://thinkingdojo.co.uk/"
PUBLISHED = "2026-11-15"
PUBLISHED_HUMAN = "15 November 2026"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = "hello@alpha333.org"
LINKEDIN = "https://www.linkedin.com/in/oisuite/"
FOUNDER = "Garry Short"
OPERATOR = "SIGNAL333 Ventures"

# The seven belts, copied from index.html. Card questions are the ones shown publicly there.
BELTS = [
    ("White", "Notice", "h-white", "Sees what is happening and can describe it clearly.", "What did you notice today?"),
    ("Yellow", "Pattern", "h-yellow", "Begins to recognise repetition and simple connections.", "What usually happens when you are in a rush?"),
    ("Orange", "Choice", "h-orange", "Makes simple decisions and starts thinking about what might happen next.", "What might happen if you choose this?"),
    ("Green", "Plan", "h-green", "Thinks ahead and begins to organise actions step by step.", "What is your goal?"),
    ("Blue", "Act", "h-blue", "Acts with intention and adjusts while doing.", "What is one small step?"),
    ("Brown", "Review", "h-brown", "Understands what happened and begins learning from outcomes.", "What would you do differently next time?"),
    ("Black", "Independent Thinker", "h-black", "Thinks clearly, independently, and with structure.", "What do you think, and why?"),
]

CSS = """
:root{color-scheme:light;--paper:#FBF7EE;--paper-2:#F4EEE1;--card:#FFFFFF;--ink:#1B1D24;--ink-2:#3D3F47;--ink-3:#5E6068;--line:#E4DCCB;--navy:#1F2B40;--navy-hi:#2C3B57;--white-belt:#DCDCDC;--yellow:#EFC84A;--orange:#E07E2A;--green:#5FA348;--blue:#3E76BB;--brown:#7A5230;--black:#252525;--display:"Fraunces",Georgia,"Times New Roman",serif;--body:"Figtree",-apple-system,"Helvetica Neue",Arial,sans-serif;--wrap:1120px;--gutter:clamp(18px,4vw,40px)}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased}
img{max-width:100%;height:auto;display:block}
a{color:inherit}
h1,h2,h3{font-family:var(--display);font-variation-settings:"SOFT" 50;font-weight:600;line-height:1.12;letter-spacing:-.015em;margin:0;text-wrap:balance}
p{margin:0}
.wrap{max-width:var(--wrap);margin:0 auto;padding-inline:var(--gutter)}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3)}
.lede{font-size:20px;color:var(--ink-2);max-width:34em}
:focus-visible{outline:3px solid var(--blue);outline-offset:3px;border-radius:6px}
.strip{display:flex;height:6px}.strip span{flex:1}
.strip .s1{background:var(--white-belt)}.strip .s2{background:var(--yellow)}.strip .s3{background:var(--orange)}.strip .s4{background:var(--green)}.strip .s5{background:var(--blue)}.strip .s6{background:var(--brown)}.strip .s7{background:var(--black)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:52px;padding:0 26px;border-radius:999px;font-family:var(--body);font-size:16px;font-weight:700;text-decoration:none;letter-spacing:.01em;cursor:pointer;border:2px solid transparent;transition:transform .15s ease,background .15s ease}
.btn:hover{transform:translateY(-2px)}
.btn-primary{background:var(--navy);color:#fff}.btn-primary:hover{background:var(--navy-hi)}
.btn-ghost{background:transparent;color:var(--ink);border-color:var(--ink)}.btn-ghost:hover{background:rgba(27,29,36,.06)}
.btn-light{background:#fff;color:var(--navy)}
.topbar{position:sticky;top:0;z-index:20;background:rgba(251,247,238,.94);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topbar-inner{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:64px}
.wordmark{font-family:var(--display);font-weight:600;font-size:21px;text-decoration:none;letter-spacing:-.01em}
.topbar-right{display:flex;align-items:center;gap:22px}
.toplink{font-size:15px;font-weight:600;color:var(--ink-2);text-decoration:none;padding:10px 0}
.toplink:hover,.toplink[aria-current="page"]{color:var(--ink);text-decoration:underline;text-underline-offset:5px}
.topbar .btn{min-height:42px;padding:0 18px;font-size:15px}
@media (max-width:760px){.toplink{display:none}}
.subnav{display:none;gap:4px 20px;flex-wrap:wrap;padding:10px 0 12px;border-top:1px solid var(--line)}
.subnav a{font-size:15px;font-weight:600;color:var(--ink-2);text-decoration:none;padding:8px 0}
@media (max-width:760px){.subnav{display:flex}}
.page-head{background:linear-gradient(180deg,#FBEFD6 0%,var(--paper) 100%);padding-block:clamp(36px,6vw,72px) clamp(28px,4vw,48px)}
.page-head h1{font-size:clamp(36px,5.4vw,62px);margin-top:16px;max-width:17em}
.page-head .lede{margin-top:20px}
.crumbs{font-size:14.5px;color:var(--ink-3);display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.crumbs a{color:var(--ink-2);font-weight:600;padding:8px 0}
.meta{margin-top:18px;font-size:14.5px;color:var(--ink-3)}
.chip{display:inline-flex;align-items:center;gap:8px;font-size:13.5px;font-weight:700;padding:5px 12px;border-radius:999px;background:#fff;border:1px solid var(--line);color:var(--ink-2)}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block;box-shadow:0 0 0 1px rgba(0,0,0,.12)}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:clamp(32px,6vw,80px);align-items:start;padding-block:clamp(28px,4vw,48px) clamp(56px,8vw,96px)}
@media (max-width:900px){.layout{grid-template-columns:minmax(0,1fr)}}
.prose{max-width:680px}
.prose>*+*{margin-top:18px}
.prose h2{font-size:clamp(25px,3vw,32px);margin-top:44px}
.prose h3{font-size:21px;margin-top:30px}
.prose p,.prose li{color:var(--ink-2);font-size:18px}
.prose strong{color:var(--ink)}
.prose a{color:var(--navy);font-weight:600;text-underline-offset:3px}
.prose ul,.prose ol{padding-left:22px;margin-bottom:0}
.prose li+li{margin-top:10px}
.ask{display:block;background:var(--card);border-radius:14px;box-shadow:0 0 0 1px var(--line);padding:18px 22px;font-family:var(--display);font-size:23px;line-height:1.3;color:var(--ink)}
.ask small{display:block;font-family:var(--body);font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-bottom:6px}
.note{font-size:15.5px;color:var(--ink-3)}
.skill-list{list-style:none;padding:0;display:grid;gap:12px}
.skill-list li{background:var(--card);border-radius:14px;box-shadow:0 0 0 1px var(--line);padding:16px 20px;margin:0}
.skill-list .nm{font-family:var(--display);font-size:22px;color:var(--ink);display:flex;align-items:center;gap:10px}
.skill-list .q{font-family:var(--display);font-style:italic;color:var(--ink);font-size:19px;margin-top:6px;display:block}
.side{position:sticky;top:96px;display:grid;gap:22px}
@media (max-width:900px){.side{position:static}}
.tcard{background:var(--card);border-radius:12px;overflow:hidden;box-shadow:0 12px 28px -12px rgba(0,0,0,.28),0 0 0 1px rgba(0,0,0,.05);display:flex;flex-direction:column}
.tcard-head{padding:9px 14px;font-size:13px;font-weight:700;letter-spacing:.02em}
.tcard-q{font-family:var(--display);font-size:23px;line-height:1.25;padding:20px 16px 14px;flex:1;font-weight:500;min-height:120px}
.tcard-foot{font-size:11.5px;color:var(--ink-3);padding:0 16px 12px}
.h-white{background:#E8E8E5;color:var(--ink)}.h-yellow{background:var(--yellow);color:var(--ink)}.h-orange{background:var(--orange);color:var(--ink)}.h-green{background:var(--green);color:var(--ink)}.h-blue{background:var(--blue);color:#fff}.h-brown{background:var(--brown);color:#fff}.h-black{background:var(--black);color:#fff}
.side .tcard{transform:rotate(-2deg);max-width:280px}
.side-box{background:var(--paper-2);border-radius:14px;padding:20px;display:grid;gap:12px;max-width:280px}
.side-box h3{font-size:20px}
.side-box p{font-size:15.5px;color:var(--ink-2)}
.side-box .btn{min-height:46px;padding:0 18px;font-size:15px}
.band{background:var(--navy);color:#fff;padding-block:clamp(48px,7vw,80px)}
.band-inner{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:28px 48px}
.band h2{font-size:clamp(28px,3.6vw,42px);max-width:16em}
.band p{color:#D2D5DD;margin-top:12px;max-width:34em}
.band-actions{display:flex;flex-wrap:wrap;gap:12px}
.band .btn-ghost{color:#fff;border-color:#fff}
.more{padding-block:clamp(40px,6vw,72px)}
.more h2{font-size:clamp(24px,3vw,32px);margin-bottom:20px}
.rows{display:grid;gap:0;border-top:1px solid var(--line)}
.row{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 24px;padding:22px 4px;border-bottom:1px solid var(--line);text-decoration:none}
.row:hover .row-t{text-decoration:underline;text-underline-offset:5px}
.row-t{flex:1 1 380px;font-family:var(--display);font-size:clamp(22px,2.6vw,28px);line-height:1.2;display:flex;align-items:baseline;gap:14px}
.row-t .dot{flex:0 0 10px;position:relative;top:-3px}
.row-d{flex:1.2 1 340px;color:var(--ink-2);font-size:16.5px}
.group{padding-block:clamp(28px,4vw,44px)}
.group h2{font-size:clamp(26px,3.2vw,36px);margin-bottom:8px}
.group>p{color:var(--ink-2);margin-bottom:22px;max-width:36em}
.faq{display:grid;gap:10px;max-width:820px}
.faq details{background:var(--card);border-radius:14px;box-shadow:0 0 0 1px var(--line)}
.faq summary{cursor:pointer;list-style:none;padding:18px 22px;font-weight:700;font-size:17.5px;display:flex;justify-content:space-between;gap:16px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-size:24px;line-height:1;color:var(--ink-3)}
.faq details[open] summary::after{content:"\\2013"}
.faq details>div{padding:0 22px 20px;color:var(--ink-2)}
.faq details>div>*+*{margin-top:12px}
.faq a{color:var(--navy);font-weight:600}
.deck{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(230px,100%),1fr));gap:24px;padding-block:8px 8px}
.deck .tcard:nth-child(odd){transform:rotate(-1.2deg)}
.deck .tcard:nth-child(even){transform:rotate(1.2deg)}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:18px;list-style:none;padding:0;margin:0}
.steps li{background:var(--card);border-radius:14px;box-shadow:0 0 0 1px var(--line);padding:20px 22px}
.steps b{display:block;font-family:var(--display);font-size:21px;font-weight:600;margin-bottom:6px}
.steps span{color:var(--ink-2);font-size:16.5px}
.contact{background:var(--card);border-radius:18px;box-shadow:0 0 0 1px var(--line);padding:clamp(22px,3vw,34px);max-width:820px;display:grid;gap:14px}
.contact h2{font-size:clamp(26px,3.2vw,36px)}
.contact p{color:var(--ink-2)}
.contact .addr{font-family:var(--display);font-size:clamp(22px,2.8vw,30px);color:var(--ink);word-break:break-word}
.contact a{color:var(--navy);font-weight:600;text-underline-offset:3px}
.legal{max-width:720px;padding-block:clamp(24px,4vw,40px) clamp(56px,8vw,96px)}
footer{padding-block:36px 44px;border-top:1px solid var(--line)}
.foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;color:var(--ink-3);font-size:14.5px}
.foot-links{display:flex;flex-wrap:wrap;gap:4px 22px}
.foot-links a{font-weight:600;color:var(--ink-2);padding:8px 0}
.badge{display:inline-flex;align-items:center;background:#1B2340;color:#fff;font-weight:700;font-size:13px;padding:6px 11px;border-radius:6px;text-decoration:none}
.badge em{color:#E4B84A;font-style:italic}
@media print{
  .topbar,.band,footer,.no-print,.page-head .crumbs{display:none!important}
  body{background:#fff;font-size:12pt}
  .page-head{background:none;padding:0 0 12pt}
  .page-head h1{font-size:22pt}
  .deck{grid-template-columns:1fr 1fr;gap:14pt}
  .deck .tcard{transform:none!important;box-shadow:none;border:1.5pt dashed #777;break-inside:avoid}
  .tcard-head{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
"""

FEED_LINK = '<link rel="alternate" type="application/rss+xml" title="The Thinking Dojo articles" href="%sarticles/feed.xml">\n' % BASE
GOAT = ('<script>window.goatcounter = {path: function(p) { return "/dojo" + p }}</script>\n'
        '<script data-goatcounter="https://signal333.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>')
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,400..700,50&family=Figtree:wght@400;500;600;700&display=swap">')


def esc(s):
    return html.escape(s, quote=True)


def tcard(i, question=None):
    belt, name, cls, _skill, q = BELTS[i]
    label = "Independent" if name == "Independent Thinker" else name
    return ('<div class="tcard"><div class="tcard-head %s">%s Belt · %s</div>'
            '<div class="tcard-q">%s</div><div class="tcard-foot">The Thinking Dojo</div></div>'
            % (cls, belt, label, question or q))


def dot(i):
    colours = ["var(--white-belt)", "var(--yellow)", "var(--orange)", "var(--green)", "var(--blue)", "var(--brown)", "var(--black)"]
    return '<span class="dot" style="background:%s" aria-hidden="true"></span>' % colours[i]


def page(path, title, description, body, depth, current="", jsonld=None, og_type="website", extra_head=""):
    """path is the folder under the site root, e.g. 'articles/some-slug'."""
    up = "../" * depth
    url = BASE + path.strip("/") + "/"
    links = [("articles/", "Articles", "articles"), ("questions/", "Questions", "questions"),
             ("teachers/", "For teachers", "teachers"), ("free-cards/", "Free cards", "free-cards")]
    top = "".join('<a class="toplink" href="%s%s"%s>%s</a>' % (up, href, ' aria-current="page"' if key == current else "", label)
                  for href, label, key in links)
    sub = "".join('<a href="%s%s">%s</a>' % (up, href, label) for href, label, _k in links)
    foot = "".join('<a href="%s%s">%s</a>' % (up, href, label) for href, label, _k in links)
    foot += ('<a href="%squestions/#ask">Contact</a><a href="%sprivacy/">Privacy</a><a href="%sterms/">Terms</a>' % (up, up, up))
    ld = ""
    for block in (jsonld or []):
        ld += '<script type="application/ld+json">%s</script>\n' % json.dumps(block, ensure_ascii=False)
    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | The Thinking Dojo</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="The Thinking Dojo">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}hero-poster.jpg">
<meta name="twitter:card" content="summary_large_image">
{fonts}
{extra_head}<style>{css}</style>
{ld}</head>
<body>
<header class="topbar">
  <div class="strip" aria-hidden="true"><span class="s1"></span><span class="s2"></span><span class="s3"></span><span class="s4"></span><span class="s5"></span><span class="s6"></span><span class="s7"></span></div>
  <div class="wrap">
    <div class="topbar-inner">
      <a class="wordmark" href="{up}">The Thinking Dojo</a>
      <nav class="topbar-right" aria-label="Main">
        {top}
        <a class="btn btn-primary" href="{up}#plans">Choose a pack</a>
      </nav>
    </div>
    <nav class="subnav" aria-label="Sections">{sub}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer>
  <div class="wrap foot">
    <span>The Thinking Dojo · For children aged 7–13</span>
    <span class="foot-links"><a href="{up}">Home</a>{foot}</span>
    <span class="badge">B-<em>Useful</em></span>
  </div>
</footer>
{goat}
</body>
</html>
""".format(title=esc(title), desc=esc(description), url=url, base=BASE, fonts=FONTS, css=CSS, ld=ld,
           up=up or "./", top=top, sub=sub, body=body, foot=foot, goat=GOAT, og_type=og_type, extra_head=extra_head)
    out_dir = os.path.join(ROOT, path)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    return url


def band(up, heading="Try it tonight with seven free cards.",
         text="One card from every belt. Print them, cut them out, and ask one at dinner."):
    return """
<section class="band no-print">
  <div class="wrap band-inner">
    <div>
      <h2>%s</h2>
      <p>%s</p>
    </div>
    <div class="band-actions">
      <a class="btn btn-light" href="%sfree-cards/">Print the free cards</a>
      <a class="btn btn-ghost" href="%s#plans">See the packs</a>
    </div>
  </div>
</section>""" % (heading, text, up, up)


# ---------------------------------------------------------------- articles

ARTICLES = [
    {
        "slug": "three-questions-for-anti-bullying-week",
        "group": "teachers", "belt": 0,
        "date": "2026-11-16", "date_human": "16 November 2026", "rss_date": "Mon, 16 Nov 2026 09:00:00 +0000",
        "title": "Three questions for Anti-Bullying Week: notice, choose, act",
        "desc": "Anti-Bullying Week 2026 runs from 16 to 20 November with the theme Break the Silence. Three five-minute questions that help children aged 7 to 13 notice, choose and act.",
        "lede": "Anti-Bullying Week runs from Monday 16 to Friday 20 November 2026, and this year’s theme is Break the Silence. Speaking up starts earlier than it looks, with noticing. Here are three questions for the week, five minutes each, for a classroom or a kitchen table.",
        "body": """
<h2>What the week is</h2>
<p>Anti-Bullying Week is run each November by the Anti-Bullying Alliance. The 2026 theme, Break the Silence, asks children and adults to start conversations about bullying, to speak up, to listen and to act together. The week opens with Odd Socks Day on Monday 16 November.</p>
<p>The Alliance publishes its own school resources, and those come first. You can find them on <a href="https://anti-bullyingalliance.org.uk/" rel="noopener">the Anti-Bullying Alliance website</a>.</p>
<p>The Thinking Dojo is not part of the campaign and is not an anti-bullying programme. What follows is a short thinking routine that sits beside the week’s own materials and your school’s policy.</p>

<h2>Why start with noticing</h2>
<p>A child can’t speak up about something they haven’t noticed. And they can’t choose what to do about it until they can say what they saw.</p>
<p>So the order matters. Notice first, then choose, then act. These are three of the seven thinking skills the Dojo teaches, and each has one plain question.</p>

<h2>Early in the week · Notice</h2>
<span class="ask"><small>White Belt · Notice</small>What did you notice today?</span>
<p>Ask it as it stands, then steer gently towards people. Who was on their own at break? Who went quiet? Who wasn’t in the game?</p>
<p>You are asking pupils to describe what they saw. Nobody has to be named and nobody is being accused. A second question helps them look closer:</p>
<span class="ask"><small>White Belt · Notice</small>What might others have missed?</span>

<h2>Midweek · Choose</h2>
<span class="ask"><small>Orange Belt · Choice</small>What might happen if you choose this?</span>
<p>Use a made-up situation, so no real child is the subject. For example: someone in the class is left out of the same game every day.</p>
<p>Take three choices in turn and ask the question about each:</p>
<ul>
<li><strong>Say nothing.</strong></li>
<li><strong>Tell an adult.</strong></li>
<li><strong>Ask them to join in.</strong></li>
</ul>
<p>Let pupils follow each choice through. They will usually work out for themselves that saying nothing is also a choice, and that it has a result.</p>

<h2>End of the week · Act</h2>
<span class="ask"><small>Blue Belt · Act</small>What is one small step?</span>
<p>Small is the point. Sitting next to someone counts. So does asking “Are you all right?”</p>
<p>Telling an adult counts too. For many children it is the hardest step, and it is the one this year’s theme is about.</p>

<h2>The five-minute routine</h2>
<ol>
<li>Put one question on the board.</li>
<li>One minute of silent thinking.</li>
<li>Two minutes in pairs.</li>
<li>Two minutes hearing from three or four pupils.</li>
</ol>
<p>Nothing is written down and nothing is marked.</p>

<h2>At home</h2>
<p>Ask one question at dinner or in the car, then wait. If your child describes something that happened to them or to someone else, listen first. The urge to fix it straight away is strong, and it can end the conversation.</p>
<p>Thank them for telling you. Then, if it sounds like bullying, speak to the school.</p>

<h2>If a child tells you something worrying</h2>
<p>A question like this can bring out more than you expected. In school, follow your safeguarding and anti-bullying procedures and speak to your designated safeguarding lead. These questions support that process. They don’t replace it.</p>

<h2>Print the three cards</h2>
<p>The three questions are on one page, ready to print and cut out: <a href="../../free-cards/anti-bullying-week/">three thinking cards for Anti-Bullying Week</a>.</p>

<h2>After the week</h2>
<p>Noticing, choosing and acting are habits, so they need more than five days. The same questions work on any Monday of the year. There is a full week of them in <a href="../five-minute-thinking-starters-for-the-classroom/">five-minute thinking starters for the classroom</a>.</p>
""",
        "next": ["five-minute-thinking-starters-for-the-classroom", "what-to-ask-instead-of-how-was-school"],
    },
    {
        "slug": "three-questions-for-childrens-mental-health-week",
        "group": "teachers", "belt": 6,
        "date": "2026-11-16", "date_human": "16 November 2026", "rss_date": "Mon, 16 Nov 2026 09:10:00 +0000",
        "title": "Three questions for Children’s Mental Health Week: ask, wait, listen",
        "desc": "Children’s Mental Health Week runs each February. Three questions that help adults step into a child’s world, for ages 7 to 13, with a printable card for each.",
        "lede": "Children’s Mental Health Week runs each February. In 2027 it is 1 to 7 February, and the theme is Step into Our World. You can’t step into a child’s world by guessing what is in it. They have to show you, and a good question is how you ask.",
        "body": """
<h2>What the week is</h2>
<p>Children’s Mental Health Week has been run by the charity Place2Be every February since 2015. The 2027 week runs from Monday 1 to Sunday 7 February.</p>
<p>The 2027 theme, Step into Our World, asks adults to see things from children’s and young people’s point of view, and to be open and curious about what they find there.</p>
<p>Place2Be publishes free resources for schools and families, and those come first. They are on <a href="https://www.childrensmentalhealthweek.org.uk/" rel="noopener">the Children’s Mental Health Week website</a>.</p>
<p>The Thinking Dojo is not part of the campaign and is not a mental health programme. What follows is a short thinking routine that sits beside the week’s own materials.</p>

<h2>Why a question helps</h2>
<p>“How are you feeling?” is a hard question at any age. It asks for a summary of something a child may not have words for yet.</p>
<p>A smaller question works better. It should be about something real, and it should have no right answer. That gives a child a way to show you a piece of their day, and the piece they choose tells you what matters to them.</p>

<h2>First · what they noticed</h2>
<span class="ask"><small>White Belt · Notice</small>What did you notice today?</span>
<p>Anything counts. The supply teacher’s shoes, who sat alone at lunch, the hall smelling of paint. You are not looking for a particular answer. You are finding out what your child looks at.</p>

<h2>Next · what others missed</h2>
<span class="ask"><small>White Belt · Notice</small>What might others have missed?</span>
<p>This is the question that fits the theme best. It invites a child to tell you something the adults haven’t seen.</p>
<p>Take the answer seriously, even when it is about the lunch queue. A child who learns that small things are listened to is more likely to bring you a big one.</p>

<h2>Then · what they think</h2>
<span class="ask"><small>Black Belt · Independent</small>What do you think, and why?</span>
<p>Ask it about something real in their world. A school rule. A falling-out between friends. Something they heard on the news.</p>
<p>Then leave the answer alone. You don’t have to agree with it. You only have to show that you heard it.</p>

<h2>Ask, wait, listen</h2>
<ul>
<li><strong>One question, one moment.</strong> The car, the dinner table or bedtime. Many children talk more easily side by side than face to face.</li>
<li><strong>Ask, then wait.</strong> The silence is the thinking. If you fill it, you have done the thinking for them.</li>
<li><strong>Don’t correct, just listen.</strong> Once you fix an answer, the task changes from thinking to guessing what you want to hear.</li>
</ul>

<h2>In the classroom</h2>
<ol>
<li>Put one question on the board.</li>
<li>One minute of silent thinking.</li>
<li>Two minutes in pairs.</li>
<li>Two minutes hearing from three or four pupils.</li>
</ol>
<p>Nothing is written down and nothing is marked.</p>

<h2>If you are worried about a child</h2>
<p>These questions are for ordinary days. They are not a way to assess a child’s mental health.</p>
<p>If a child says something that worries you, in school follow your safeguarding procedures and speak to your designated safeguarding lead. At home, talk to the school or your GP. If you think a child is in immediate danger, call 999.</p>

<h2>Print the three cards</h2>
<p>The three questions are on one page, ready to print and cut out: <a href="../../free-cards/childrens-mental-health-week/">three thinking cards for Children’s Mental Health Week</a>.</p>

<h2>After the week</h2>
<p>Listening works best as a habit. The same questions work on any ordinary Tuesday, and the first one is the place to start: <a href="../what-to-ask-instead-of-how-was-school/">what to ask instead of “How was school?”</a></p>
""",
        "next": ["what-to-ask-instead-of-how-was-school", "three-questions-for-anti-bullying-week"],
    },
    {
        "slug": "three-questions-for-safer-internet-day",
        "group": "teachers", "belt": 5,
        "date": "2026-11-16", "date_human": "16 November 2026", "rss_date": "Mon, 16 Nov 2026 09:20:00 +0000",
        "title": "Three questions for Safer Internet Day: notice, choose, review",
        "desc": "Safer Internet Day is in February each year. Three five-minute questions that help children aged 7 to 13 reflect on their own screen time, with a printable card for each.",
        "lede": "Safer Internet Day is in February each year. In 2027 it is Tuesday 9 February, and the UK theme asks children to reflect on tech. Reflecting is a thinking skill, and it can be practised with three questions.",
        "body": """
<h2>What the day is</h2>
<p>Safer Internet Day is coordinated in the UK by the UK Safer Internet Centre. The 2027 day is Tuesday 9 February.</p>
<p>The 2027 UK theme is “Reflect on tech: exploring digital well-being and our relationship with technology”. It covers healthy use, how technology affects mood, and how families and young people manage their time online.</p>
<p>The Centre publishes free resources for schools and families, and those come first. They are on <a href="https://saferinternet.org.uk/" rel="noopener">the UK Safer Internet Centre website</a>.</p>
<p>The Thinking Dojo is not part of the campaign and is not an online safety programme. What follows is a short thinking routine that sits beside the day’s own materials.</p>

<h2>Why questions fit this theme</h2>
<p>A rule about screens tells a child what to do. A question asks them to see for themselves what a screen does to their evening.</p>
<p>Both have their place. But a child who has noticed something for themselves is more likely to act on it than a child who has only been told.</p>

<h2>First · notice</h2>
<span class="ask"><small>White Belt · Notice</small>What did you notice today?</span>
<p>Ask it as it stands, then steer towards screens. How did you feel before you picked up the tablet? How did you feel when you put it down? What was happening in the room while you were on it?</p>
<p>You are asking for a description, so there is nothing to tell off.</p>

<h2>Next · choose</h2>
<span class="ask"><small>Orange Belt · Choice</small>What might happen if you choose this?</span>
<p>Use an ordinary evening. It is nearly bedtime and the next episode is about to start. Take three choices in turn and ask the question about each:</p>
<ul>
<li><strong>Watch one more.</strong></li>
<li><strong>Stop now.</strong></li>
<li><strong>Set a timer and stop when it goes.</strong></li>
</ul>
<p>Let them follow each one through to the next morning.</p>

<h2>Then · review</h2>
<span class="ask"><small>Brown Belt · Review</small>What would you do differently next time?</span>
<p>Ask it about one evening this week. One is enough.</p>
<p>Go first. Say what you would do differently about your own phone. Children copy what they hear, and it shows them the question isn’t a trap.</p>

<h2>The five-minute routine</h2>
<ol>
<li>Put one question on the board.</li>
<li>One minute of silent thinking.</li>
<li>Two minutes in pairs.</li>
<li>Two minutes hearing from three or four pupils.</li>
</ol>
<p>Nothing is written down and nothing is marked.</p>

<h2>What this doesn’t cover</h2>
<p>These questions are about a child’s own habits. They don’t cover privacy, reporting, or what to do about harmful content or contact. For those, use the UK Safer Internet Centre’s resources and your school’s online safety policy.</p>
<p>If a child tells you about something online that has frightened or upset them, in school follow your safeguarding procedures and speak to your designated safeguarding lead.</p>

<h2>Print the three cards</h2>
<p>The three questions are on one page, ready to print and cut out: <a href="../../free-cards/safer-internet-day/">three thinking cards for Safer Internet Day</a>.</p>

<h2>After the day</h2>
<p>If your child likes the questions, there are ways to practise the same skills with no screen at all: <a href="../screen-free-thinking-activities-for-children/">screen-free thinking activities for children</a>.</p>
""",
        "next": ["screen-free-thinking-activities-for-children", "three-questions-for-anti-bullying-week"],
    },
    {
        "slug": "how-to-teach-your-child-to-think-for-themselves",
        "group": "parents", "belt": 6,
        "title": "How do I teach my child to think for themselves?",
        "desc": "Thinking for yourself is seven smaller skills that build in order. Here is the order, with one question for each that you can ask at home tonight.",
        "lede": "Most advice on this says “encourage curiosity” and stops there, which is hard to act on at half past six on a Tuesday. It gets easier once you see that thinking for yourself is seven smaller skills, and that they build in order.",
        "body": """
<h2>Why “think about it” doesn’t work</h2>
<p>Telling a child to think harder is like telling them to swim faster before anyone has shown them the stroke. They can’t tell which part to change.</p>
<p>The skills also depend on each other. A child who can’t yet describe what happened can’t spot a pattern in it. A child who can’t see the pattern can’t make a good choice about it. So the order matters more than the effort.</p>

<h2>The seven skills, in order</h2>
<p>The Thinking Dojo gives each skill a belt colour and one plain description. Each has a question you can ask out loud.</p>
{skills}

<h2>How to ask the questions</h2>
<ul>
<li><strong>One question, one moment.</strong> At dinner, in the car, after a hard day. One is enough.</li>
<li><strong>Ask, then wait.</strong> The silence is the thinking. If you fill it, you have done the thinking for them.</li>
<li><strong>Don’t correct, just listen.</strong> Once you fix an answer, the task changes from thinking to guessing what you want to hear.</li>
</ul>

<h2>Where to start</h2>
<p>Most children start at Notice, whatever their age. That doesn’t mean they are behind. A twelve-year-old who is quick at maths may still jump straight to what something means without saying what actually happened.</p>
<p>Ask the first question for a week. When they answer it easily, try the next one.</p>

<h2>When to move on</h2>
<p>There is no test. Move on when you hear your child use a skill without being asked. If they say “this always happens when I leave it until Sunday night”, they have spotted a pattern by themselves, and they are ready for questions about choice.</p>
""",
        "next": ["what-to-ask-instead-of-how-was-school", "screen-free-thinking-activities-for-children"],
    },
    {
        "slug": "what-to-ask-instead-of-how-was-school",
        "group": "parents", "belt": 0,
        "title": "What to ask instead of “How was school?”",
        "desc": "“Fine” is an honest answer to a vague question. Two better questions that get a child describing their day, and how to ask them.",
        "lede": "“How was school?” asks a child to sum up six hours in a word. “Fine” is a fair summary. A smaller question gets a longer answer.",
        "body": """
<h2>Why the usual question fails</h2>
<p>It asks for a verdict before a description. Your child has to decide whether the whole day was good or bad, and most adults couldn’t do that about their own day either. So you get the shortest safe answer.</p>

<h2>Ask for one thing they noticed</h2>
<p>This is a White Belt card. The White Belt trains noticing:</p>
<span class="ask"><small>White Belt · Notice</small>What did you notice today?</span>
<p>It is concrete and it has no wrong answer. The supply teacher’s shoes count. So does who sat alone at lunch, or the hall smelling of paint.</p>

<h2>Then go one step further</h2>
<span class="ask"><small>White Belt · Notice</small>What might others have missed?</span>
<p>This one asks them to look a little closer. Children like knowing something other people don’t, and that makes it a good second question.</p>

<h2>How to ask</h2>
<ul>
<li><strong>Pick the moment.</strong> The school gate is the worst place. Try the car, the dinner table or bedtime. Many children talk more easily side by side than face to face.</li>
<li><strong>Ask once, then wait.</strong> Don’t rephrase it three times.</li>
<li><strong>Don’t turn the answer into a lesson.</strong> If they say a friend was left out, hold back from what they should have done about it. Describing comes first. The Dojo puts it this way: your child describes what actually happened before deciding what it means.</li>
</ul>

<h2>A game that builds noticing</h2>
<p>One evening, move something in the kitchen, such as the toaster. The next morning, ask your child what is different about the kitchen today.</p>
<p>It takes a minute and children enjoy catching you out. Noticing what has changed is the first step towards spotting patterns, and it helps children stay aware of what is around them.</p>

<h2>If the answer is “nothing”</h2>
<p>That is normal for the first few days. Go first. Tell them one thing you noticed today, however small. Children copy what they hear, and a parent who notices things out loud makes it an ordinary thing to do.</p>
<p>Noticing is the first of seven thinking skills. <a href="../how-to-teach-your-child-to-think-for-themselves/">Here is the full order</a>, with a question for each.</p>
""",
        "next": ["how-to-teach-your-child-to-think-for-themselves", "what-to-say-after-a-bad-result"],
    },
    {
        "slug": "my-child-rushes-and-makes-careless-mistakes",
        "group": "parents", "belt": 1,
        "title": "My child rushes and makes careless mistakes. What helps?",
        "desc": "Telling a child to slow down rarely works. Helping them spot their own pattern does. Two questions to try, and when to ask them.",
        "lede": "You have said “slow down” and “check your work” more times than you can count. It doesn’t stick, because it is your observation and not theirs.",
        "body": """
<h2>“Careless” is the wrong word</h2>
<p>Rushing usually follows a pattern. It happens at a certain time of day, on a certain kind of task, or when your child feels a certain way. They can’t see the pattern because they are inside it.</p>
<p>Your job is to help them see it for themselves.</p>

<h2>Let them find the pattern</h2>
<p>This card comes from the Yellow Belt, which trains pattern-spotting:</p>
<span class="ask"><small>Yellow Belt · Pattern</small>What usually happens when you are in a rush?</span>
<p>Ask it at a calm time, never in the middle of the mistake. The Dojo’s own example of this skill at home is a child who spots that mornings go wrong on the days they rush.</p>
<p>Take whatever they give you. “I forget my PE kit” is a real pattern, and they found it.</p>

<h2>Then ask one planning question</h2>
<p>Once they can see the pattern, they need something to do about it. This is a Green Belt card:</p>
<span class="ask"><small>Green Belt · Plan</small>What do you do first?</span>
<p>Use it just before homework or before packing a bag. Let them choose the first step. A step they chose is one they are more likely to take.</p>

<h2>What to avoid</h2>
<ul>
<li><strong>Listing their mistakes.</strong> A list tells them what you think of them. It doesn’t help them see what happens.</li>
<li><strong>Asking straight after a bad mark.</strong> That moment calls for a different question. See <a href="../what-to-say-after-a-bad-result/">what to say after a bad result</a>.</li>
<li><strong>Expecting it to change in a week.</strong> The sign to listen for is your child saying “I’m rushing again” without being told.</li>
</ul>
""",
        "next": ["how-to-help-your-child-make-decisions", "what-to-say-after-a-bad-result"],
    },
    {
        "slug": "how-to-help-your-child-make-decisions",
        "group": "parents", "belt": 2,
        "title": "How to help your child make decisions",
        "desc": "Children get better at deciding by practising on small choices. Two questions that slow a decision down without making it for them.",
        "lede": "Some children freeze in front of a menu. Others choose in a second and regret it by the car park. Both are missing the same thing: nobody has shown them that a decision has steps.",
        "body": """
<h2>Practise on small, real choices</h2>
<p>How to spend pocket money. Which club to try. What to do with a free Saturday morning. These are good practice because being wrong costs very little.</p>

<h2>Step one: name the options</h2>
<p>Many poor choices come from only seeing one option. The Dojo describes this skill at home as a child who names two or three options before picking one.</p>
<p>So before anything else, ask “what else could you do?” until there are at least two.</p>

<h2>Step two: look ahead</h2>
<p>These two cards come from the Orange Belt, which trains choice:</p>
<span class="ask"><small>Orange Belt · Choice</small>What might happen if you choose this?</span>
<span class="ask"><small>Orange Belt · Choice</small>What could go wrong?</span>
<p>Ask them plainly, without a warning tone. You want your child to treat what happens next as part of the choice.</p>

<h2>Step three: let the choice stand</h2>
<p>If it is safe, let them live with what they chose, even when you would have chosen differently. A slightly bad choice they made themselves teaches more than a good one you made for them.</p>
<p>A day or two later, ask what they would do differently next time. That turns the choice into something learned.</p>

<h2>Bigger decisions</h2>
<p>Dropping an activity or choosing school options takes the same steps, with more time between them. You still have the final say on things that matter, and it is fine to tell your child so at the start.</p>
""",
        "next": ["my-child-rushes-and-makes-careless-mistakes", "how-to-teach-your-child-to-think-for-themselves"],
    },
    {
        "slug": "what-to-say-after-a-bad-result",
        "group": "parents", "belt": 5,
        "title": "What to say to your child after a bad result",
        "desc": "After a lost match or a poor test, when you ask matters as much as what you ask. A simple order to follow, and one question that turns it into learning.",
        "lede": "The car journey home after a lost match is a hard one. You want to reassure them or go through what went wrong. Both are too soon.",
        "body": """
<h2>First, say very little</h2>
<p>Reviewing something needs a calm head, and nobody has one in the first hour. “That was a tough one” is enough. Save the conversation for the evening or the next day.</p>

<h2>Then describe before judging</h2>
<p>Start with “what happened?” and ask for a plain account.</p>
<p>“We lost 3–1 and I missed a tackle in the second half” is a description. “I was rubbish” is a verdict. You can learn from the first one. If you get the verdict, ask again for what actually happened.</p>

<h2>Then ask the review question</h2>
<p>This is a Brown Belt card. The Dojo describes the skill as understanding what happened and beginning to learn from outcomes.</p>
<span class="ask"><small>Brown Belt · Review</small>What would you do differently next time?</span>
<p>Ask for one thing. One change is something a child can carry into the next match or the next test.</p>

<h2>What to avoid</h2>
<ul>
<li><strong>Answering for them.</strong> If you supply the lesson, they have learned what you think.</li>
<li><strong>Turning one thing into five.</strong> Stop at the first good answer.</li>
<li><strong>“But you did really well.”</strong> If they know they didn’t, they will stop believing your praise.</li>
</ul>

<h2>Ask after good results too</h2>
<p>If you only review the bad days, your child will hear the question as a telling-off. After a win, ask what worked and what they would keep. Then reviewing becomes something you do after everything.</p>
""",
        "next": ["what-to-ask-instead-of-how-was-school", "my-child-rushes-and-makes-careless-mistakes"],
    },
    {
        "slug": "screen-free-thinking-activities-for-children",
        "group": "parents", "belt": 3,
        "title": "Seven screen-free thinking activities for children aged 7 to 13",
        "desc": "Seven short activities that need no screen, no worksheet and no preparation. One for each thinking skill, from noticing to thinking independently.",
        "lede": "None of these needs a screen, a worksheet or any preparation. Each one practises a single thinking skill and takes a few minutes of a day you were already having.",
        "body": """
<h2>1. The walk-home report <span class="note">· Notice</span></h2>
<p>On any walk, each of you names one thing you noticed that the other might have missed. You take a turn as well.</p>

<h2>2. The Sunday pattern <span class="note">· Pattern</span></h2>
<p>At Sunday dinner, ask what usually happens on the mornings that go well. Then ask what usually happens when everyone is in a rush. Let the children answer before the adults do.</p>

<h2>3. The three-option hour <span class="note">· Choice</span></h2>
<p>Give your child a free hour. Before they start, they name three things they could do with it and what might happen with each. Then they choose.</p>

<h2>4. First-step cooking <span class="note">· Plan</span></h2>
<p>Your child plans a simple meal. Ask two things: what is the goal, and what do you do first? Then cook it their way.</p>

<h2>5. One small step <span class="note">· Act</span></h2>
<p>Pick something they have been putting off, such as a messy desk or a thank-you note. Ask “what is one small step?” and do only that step today.</p>

<h2>6. The replay <span class="note">· Review</span></h2>
<p>After a board game or a match, everyone answers one question: what would you do differently next time? Winners answer too.</p>

<h2>7. The dinner debate <span class="note">· Independent thinking</span></h2>
<p>Choose a small question. Should homework exist? Is it ever right to break a promise? Each child says what they think and why. The adults give their views last, so nobody is guessing the right answer.</p>

<h2>Making it a habit</h2>
<p>The hard part is remembering to ask. That is what the Dojo’s thinking cards are for: a pack for each skill, kept in a kitchen drawer, one card pulled at a time.</p>
""",
        "next": ["how-to-teach-your-child-to-think-for-themselves", "what-to-ask-instead-of-how-was-school"],
    },
    {
        "slug": "five-minute-thinking-starters-for-the-classroom",
        "group": "teachers", "belt": 4,
        "title": "Five-minute thinking starters for the classroom",
        "desc": "A week of five-minute thinking starters for ages 7 to 13, built around planning, doing and reviewing. All you need is one question on the board.",
        "lede": "A week of starters for ages 7 to 13. Each takes five minutes and needs one question on the board. Nothing is written down and nothing is marked.",
        "body": """
<h2>Why spend five minutes on this</h2>
<p>The Education Endowment Foundation’s Teaching and Learning Toolkit puts the average impact of metacognition and self-regulation approaches at eight months of additional progress. It also says that this impact can be difficult to achieve in practice. You can read <a href="https://educationendowmentfoundation.org.uk/education-evidence/teaching-learning-toolkit/metacognition-and-self-regulation" rel="noopener">the EEF’s summary here</a>.</p>
<p>The EEF describes these approaches as teaching pupils specific strategies for planning, monitoring and evaluating their learning. A short daily question is one simple way to make those three steps something pupils say out loud.</p>

<h2>The routine</h2>
<ol>
<li>Put one question on the board.</li>
<li>One minute of silent thinking.</li>
<li>Two minutes in pairs.</li>
<li>Two minutes hearing from three or four pupils.</li>
</ol>

<h2>A week of starters</h2>
<h3>Monday · Notice</h3>
<span class="ask">What did you notice on the way to school that others might have missed?</span>
<h3>Tuesday · Pattern</h3>
<span class="ask">What usually happens when you are in a rush?</span>
<h3>Wednesday · Choice</h3>
<span class="ask">What might happen if you choose this?</span>
<p>Apply it to a character in the class book, or to a real decision the class has to make.</p>
<h3>Thursday · Plan</h3>
<span class="ask">What is your goal, and what do you do first?</span>
<p>Ask it just before a longer piece of work.</p>
<h3>Friday · Review</h3>
<span class="ask">What would you do differently next time?</span>
<p>Ask it about one piece of work from the week.</p>

<h2>Using the same questions inside a lesson</h2>
<ul>
<li><strong>Before a task:</strong> the Thursday question.</li>
<li><strong>Halfway through:</strong> “What is one small step?” for anyone who is stuck.</li>
<li><strong>At the end:</strong> the Friday question, answered to a partner.</li>
</ul>

<h2>Keeping it low-stakes</h2>
<p>Don’t score the answers and don’t correct them. In the first week some pupils will say they noticed nothing. Give an answer of your own and move on. By the second week they will have one ready.</p>
<p>These questions follow the order of the Thinking Dojo’s seven belts. There is more on <a href="../../teachers/">the page for teachers</a>.</p>
""",
        "next": ["thinking-skills-for-home-education", "how-to-teach-your-child-to-think-for-themselves"],
    },
    {
        "slug": "thinking-skills-for-home-education",
        "group": "teachers", "belt": 3,
        "title": "A simple thinking-skills routine for home education",
        "desc": "How to add thinking skills to a home-education week in about ten minutes a day, without another curriculum to manage.",
        "lede": "You already have enough to plan. Thinking skills work better as a habit that sits inside the subjects you teach than as one more subject on the timetable.",
        "body": """
<h2>Attach it to what you already do</h2>
<p>You don’t need a new slot in the day. You need three places to put a question:</p>
<ul>
<li><strong>At breakfast:</strong> one card, one question.</li>
<li><strong>Before a project:</strong> a planning question.</li>
<li><strong>On Friday:</strong> a review question about the week.</li>
</ul>

<h2>A week that works</h2>
<ul>
<li><strong>Monday.</strong> Look at the Thinking Progress Chart and decide which belt fits how your child is thinking now. You are observing, so there is nothing to test.</li>
<li><strong>Every day.</strong> Pull one card from that belt’s pack. Ask it, then listen without correcting.</li>
<li><strong>Midweek.</strong> Read one of the stories together.</li>
<li><strong>Before any project.</strong> Ask “What is your goal?” and “What do you do first?”</li>
<li><strong>Friday.</strong> Ask “What would you do differently next time?” about one thing from the week.</li>
</ul>

<h2>More than one child</h2>
<p>Children of different ages can be on different belts at the same table. Ask each child the question from their own belt. Younger children usually spend longer on the early belts, which is how it is meant to work.</p>

<h2>If you want guided sessions</h2>
<p>The Coach Engine runs a 10–15 minute session of six questions at your child’s belt level. They write their thinking in their own words. It runs in a web browser on iPhone, iPad and desktop.</p>

<h2>Keeping a record</h2>
<p>If you keep a record of learning, the Coach Engine’s session summaries can be exported, and the Starter System includes a Progress Tracker.</p>

<h2>What to start with</h2>
<p>The Starter System has the paper core: the workbook, the story series, the printable thinking cards, the tracker and the chart. If you would rather try the idea first, <a href="../../free-cards/">print the seven free cards</a>.</p>
""",
        "next": ["five-minute-thinking-starters-for-the-classroom", "screen-free-thinking-activities-for-children"],
    },
]


def skills_list():
    items = []
    for i, (belt, name, _cls, skill, q) in enumerate(BELTS):
        items.append('<li><span class="nm">%s%s <span class="note">· %s belt</span></span>%s<span class="q">“%s”</span></li>'
                     % (dot(i), name, belt, skill, q))
    return '<ol class="skill-list">' + "".join(items) + "</ol>"


def build_articles():
    by_slug = {a["slug"]: a for a in ARTICLES}
    urls = []
    for a in ARTICLES:
        up = "../../"
        who = "For parents" if a["group"] == "parents" else "For teachers and home educators"
        body_html = a["body"].replace("{skills}", skills_list())
        nxt = "".join(
            '<a class="row" href="../%s/"><span class="row-t">%s%s</span><span class="row-d">%s</span></a>'
            % (s, dot(by_slug[s]["belt"]), by_slug[s]["title"], by_slug[s]["desc"]) for s in a["next"])
        body = """
<section class="page-head">
  <div class="wrap">
    <p class="crumbs"><a href="../">Articles</a><span aria-hidden="true">/</span><span>{who}</span></p>
    <h1>{title}</h1>
    <p class="lede">{lede}</p>
    <p class="meta">The Thinking Dojo · {date}</p>
  </div>
</section>
<div class="wrap layout">
  <article class="prose">{body}</article>
  <aside class="side no-print" aria-label="From the Thinking Dojo">
    {card}
    <div class="side-box">
      <h3>Seven free cards</h3>
      <p>One question from every belt, ready to print.</p>
      <a class="btn btn-primary" href="{up}free-cards/">Print them</a>
    </div>
  </aside>
</div>
{band}
<section class="more">
  <div class="wrap">
    <h2>Keep reading</h2>
    <div class="rows">{nxt}</div>
  </div>
</section>""".format(who=who, title=a["title"], lede=a["lede"], date=a.get("date_human", PUBLISHED_HUMAN), body=body_html,
                    card=tcard(a["belt"]), up=up, band=band(up), nxt=nxt)
        url = BASE + "articles/" + a["slug"] + "/"
        ld = [{
            "@context": "https://schema.org", "@type": "Article",
            "headline": a["title"], "description": a["desc"],
            "datePublished": a.get("date", PUBLISHED), "dateModified": a.get("date", PUBLISHED),
            "author": {"@type": "Organization", "name": "The Thinking Dojo", "url": BASE},
            "publisher": {"@type": "Organization", "name": "The Thinking Dojo", "url": BASE},
            "image": BASE + "hero-poster.jpg", "mainEntityOfPage": url,
        }]
        urls.append(page("articles/" + a["slug"], a["title"], a["desc"], body, 2, "articles", ld, "article", FEED_LINK))
    return urls


def build_hub():
    def rows(group):
        return "".join(
            '<a class="row" href="%s/"><span class="row-t">%s%s</span><span class="row-d">%s</span></a>'
            % (a["slug"], dot(a["belt"]), a["title"], a["desc"]) for a in ARTICLES if a["group"] == group)
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Articles</p>
    <h1>Practical answers for parents and teachers.</h1>
    <p class="lede">Short articles on helping children aged 7 to 13 think for themselves. Each one answers a single question and gives you something to try today.</p>
  </div>
</section>
<div class="wrap">
  <section class="group">
    <h2>For parents</h2>
    <p>Questions to ask at the table, in the car and after a hard day.</p>
    <div class="rows">{parents}</div>
  </section>
  <section class="group">
    <h2>For teachers and home educators</h2>
    <p>Short routines that fit around the work you already do.</p>
    <div class="rows">{teachers}</div>
  </section>
  <section class="group">
    <h2>Looking for something else?</h2>
    <div class="rows">
      <a class="row" href="../questions/"><span class="row-t">{d0}Questions about the Thinking Dojo</span><span class="row-d">What it is, where a child starts, and which pack to choose.</span></a>
      <a class="row" href="../teachers/"><span class="row-t">{d4}The Thinking Dojo in the classroom</span><span class="row-d">Six places a thinking card fits into a school day.</span></a>
    </div>
  </section>
</div>
{band}""".format(parents=rows("parents"), teachers=rows("teachers"), d0=dot(0), d4=dot(4), band=band("../"))
    return page("articles", "Articles for parents and teachers",
                "Short, practical articles on helping children aged 7 to 13 think for themselves: what to ask, when to ask it, and what to avoid.",
                body, 1, "articles", extra_head=FEED_LINK)


def build_feed():
    items = ""
    for a in ARTICLES:
        url = BASE + "articles/" + a["slug"] + "/"
        items += ("  <item>\n    <title>%s</title>\n    <link>%s</link>\n    <guid>%s</guid>\n"
                  "    <pubDate>%s</pubDate>\n    <description>%s</description>\n  </item>\n"
                  % (esc(a["title"]), url, url, a.get("rss_date", "Sun, 15 Nov 2026 09:00:00 +0000"), esc(a["desc"])))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n'
           '  <title>The Thinking Dojo: articles for parents and teachers</title>\n'
           '  <link>%sarticles/</link>\n'
           '  <description>Short, practical articles on helping children aged 7 to 13 think for themselves.</description>\n'
           '  <language>en-gb</language>\n%s</channel>\n</rss>\n' % (BASE, items))
    open(os.path.join(ROOT, "articles", "feed.xml"), "w", encoding="utf-8").write(xml)


# ---------------------------------------------------------------- questions

QA = [
    ("About the Thinking Dojo", [
        ("What is the Thinking Dojo?",
         "<p>A thinking system for children aged 7–13. There are seven coloured belts, and each one is a real thinking skill. Children move from Notice to Independent Thinker through cards, stories and short guided sessions, at their own pace.</p>"),
        ("What are the seven belts?",
         "<p>" + " ".join("<strong>%s (%s).</strong> %s" % (n, b, s) for b, n, _c, s, _q in BELTS) + "</p>"),
        ("Is it a course or a test?",
         "<p>Neither. There are no scores, no tests, no pass mark and no timeline. Progress is observed, never marked.</p>"),
        ("What age is it for?",
         "<p>The Thinking Dojo is designed for children aged 7–13. Younger children usually spend longer on the early belts, which is exactly how it should work.</p>"),
    ]),
    ("Using it at home", [
        ("Where does my child start?",
         "<p>Most children start at White (Notice). Use the Thinking Progress Chart to observe how your child thinks now and pick the belt that fits best. There is no wrong answer.</p>"),
        ("How much time does it take?",
         "<p>A card takes one moment: you pull one at dinner or in the car, ask the question, and listen. A Coach Engine session is a guided 10–15 minutes.</p>"),
        ("What if my child just says “I don’t know”?",
         "<p>Go back to noticing. Ask what they saw or heard, and wait. If nothing comes, tell them one thing you noticed today. Don’t correct the answer when it does come. There is more in <a href=\"../articles/what-to-ask-instead-of-how-was-school/\">what to ask instead of “How was school?”</a></p>"),
        ("How can I practise noticing at home?",
         "<p>Try the kitchen game. One evening, move something in the kitchen, such as the toaster. The next morning, ask your child what is different about the kitchen today.</p><p>Noticing what has changed is the first step towards spotting patterns. It also helps children stay aware of what is around them.</p>"),
        ("How do I know when to move up a belt?",
         "<p>When your child thinks at the next level on their own, move them up. There is no pass mark and no timeline.</p>"),
        ("Does my child need a screen?",
         "<p>No. The workbook, stories, cards and chart are all used on paper in everyday moments. Only the Coach Engine is on a screen, and it is calm by design with no ads or points.</p>"),
    ]),
    ("Teachers and home educators", [
        ("Can I use it with a whole class?",
         "<p>Yes. You can ask a whole class one question while you read a story, such as “What did you notice?”, and each pupil can write an answer on a printed card. A card also works as a five-minute starter with one question on the board. See <a href=\"../teachers/\">the Thinking Dojo in the classroom</a> and <a href=\"../articles/five-minute-thinking-starters-for-the-classroom/\">a week of starters</a>.</p>"),
        ("Does it fit home education?",
         "<p>Yes. The paper core sits alongside whatever else you teach. <a href=\"../articles/thinking-skills-for-home-education/\">Here is a simple weekly routine</a>.</p>"),
    ]),
    ("Choosing and buying", [
        ("Can I try it before I buy?",
         "<p>Yes. <a href=\"../free-cards/\">Print seven free cards</a>, one from every belt, and try one at dinner tonight.</p>"),
        ("Which pack should I start with?",
         "<p>If you want to try the idea, start with the Workbook. For everyday use at home, the Starter System gives you the stories, cards and chart. The Complete System adds a Parent Guide and premium cards. Add the Coach Engine if your child would enjoy guided sessions on a screen.</p>"),
        ("Are my child’s Coach Engine answers private?",
         "<p>Yes. The Coach Engine runs on your own device and does not send answers to us or to anyone else. At the end of a session you can export a summary if you want to keep it.</p>"),
        ("What devices does the Coach Engine work on?",
         "<p>It runs in the web browser on iPhone, iPad and desktop. There is no app to download.</p>"),
        ("How do I get it after buying?",
         "<p>Checkout is handled securely by Lemon Squeezy. You get instant access to your files straight after purchase.</p>"),
    ]),
]


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def build_questions():
    groups = ""
    entities = []
    for heading, items in QA:
        d = ""
        for q, a in items:
            d += "<details><summary>%s</summary><div>%s</div></details>\n" % (q, a)
            entities.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}})
        groups += '<section class="group"><h2>%s</h2><div class="faq">%s</div></section>\n' % (heading, d)
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Questions</p>
    <h1>Questions parents and teachers ask.</h1>
    <p class="lede">Plain answers about what the Thinking Dojo is, how to use it and where to start.</p>
  </div>
</section>
<div class="wrap">
{groups}
  <section class="group" id="ask">
    <div class="contact">
      <h2>Ask us a question.</h2>
      <p>If your question isn’t answered here, email us. Parents, teachers and home educators are all welcome.</p>
      <p class="addr">{email}</p>
      <p><a href="mailto:{email}?subject=A%20question%20about%20the%20Thinking%20Dojo">Open an email to us</a></p>
      <p>The Thinking Dojo was created by {founder}. You can also find him <a href="{linkedin}" rel="noopener">on LinkedIn</a>.</p>
    </div>
  </section>
</div>
{band}""".format(groups=groups, band=band("../"), email=EMAIL, founder=FOUNDER, linkedin=LINKEDIN)
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}]
    return page("questions", "Questions parents and teachers ask",
                "Plain answers about the Thinking Dojo: what the seven belts are, where a child starts, how long it takes, and which pack to choose.",
                body, 1, "questions", ld)


# ---------------------------------------------------------------- teachers

def build_teachers():
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">For teachers</p>
    <h1>The Thinking Dojo in the classroom.</h1>
    <p class="lede">Seven thinking skills in a fixed order, each with questions pupils can answer out loud. It fits ages 7 to 13 and needs no marking.</p>
  </div>
</section>
<div class="wrap layout">
  <div class="prose">
    <h2 style="margin-top:0">What it gives a class</h2>
    <p>Most pupils are told to “think about it” without being shown the steps. The Dojo names seven steps and puts them in order: Notice, Pattern, Choice, Plan, Act, Review, and thinking independently.</p>
    <p>The Plan, Act and Review steps line up closely with planning, monitoring and evaluating, which is how the Education Endowment Foundation describes metacognitive strategies. The EEF’s Toolkit puts the average impact of those approaches at eight months of additional progress, and notes that this can be difficult to achieve in practice. <a href="https://educationendowmentfoundation.org.uk/education-evidence/teaching-learning-toolkit/metacognition-and-self-regulation" rel="noopener">Read the EEF’s summary</a>.</p>

    <h2>Six places a card fits into the day</h2>
    <ul>
      <li><strong>During a story.</strong> Pause while you read and ask the whole class “What did you notice?” Each pupil writes an answer on a printed card.</li>
      <li><strong>As a starter.</strong> One question on the board, one minute to think, two minutes in pairs. <a href="../articles/five-minute-thinking-starters-for-the-classroom/">Here is a full week of starters</a>.</li>
      <li><strong>After a playground fall-out.</strong> Start with Notice. Each pupil describes what actually happened before anyone says what it means.</li>
      <li><strong>Before a project.</strong> “What is your goal?” and “What do you do first?”</li>
      <li><strong>Halfway through a task.</strong> “What is one small step?” for anyone who is stuck.</li>
      <li><strong>After a test or a piece of work.</strong> “What would you do differently next time?”</li>
    </ul>

    <h2>How it stays low-stakes</h2>
    <p>The Dojo has no scores, no tests and no pass mark. Pupils move up a belt when they use the next skill without prompting. The Thinking Progress Chart describes each belt in one plain sentence, so you can place a pupil by listening to them.</p>

    <h2>Where to start</h2>
    <p><a href="../free-cards/">Print the seven free cards</a> and use one a day for a week. If it works for your class, the Workbook introduces all seven belts step by step, and the Starter System adds the story series, the printable card packs for every belt and the chart.</p>
    <p>You can use your pack with your whole class and print as many cards as your pupils need.</p>

    <h2>Questions about using it in your school</h2>
    <p>Email <a href="mailto:{email}">{email}</a> and we will reply.</p>
  </div>
  <aside class="side no-print" aria-label="From the Thinking Dojo">
    {card}
    <div class="side-box">
      <h3>A week of starters</h3>
      <p>Five questions, five minutes each, Monday to Friday.</p>
      <a class="btn btn-primary" href="../articles/five-minute-thinking-starters-for-the-classroom/">Read it</a>
    </div>
  </aside>
</div>
{band}""".format(card=tcard(5), email=EMAIL, band=band("../", "Try a week of it with seven free cards.", "One question from every belt. Print them for the board or the book corner."))
    return page("teachers", "The Thinking Dojo in the classroom",
                "How teachers of ages 7 to 13 can use the Thinking Dojo’s seven thinking skills as five-minute starters, before projects and after tests.",
                body, 1, "teachers")


# ---------------------------------------------------------------- free cards

def build_free_cards():
    deck = "".join(tcard(i) for i in range(7))
    body = """
<section class="page-head no-print">
  <div class="wrap">
    <p class="eyebrow">Free to print</p>
    <h1>Seven free thinking cards. One from every belt.</h1>
    <p class="lede no-print">Print this page, cut the cards out and keep them in a kitchen drawer. Pull one at dinner or in the car.</p>
    <p class="no-print" style="margin-top:26px"><button class="btn btn-primary" type="button" onclick="window.print()">Print the cards</button></p>
  </div>
</section>
<div class="wrap" style="padding-block:clamp(28px,4vw,48px)">
  <div class="deck">{deck}</div>
</div>
<div class="wrap no-print" style="padding-bottom:clamp(48px,7vw,88px)">
  <h2 style="font-size:clamp(26px,3.2vw,36px);margin-bottom:20px">How to use them</h2>
  <ol class="steps">
    <li><b>One card, one moment</b><span>Start with the White Belt card. Ask it once, in an ordinary moment.</span></li>
    <li><b>Ask, then wait</b><span>Give your child time. The quiet is where the thinking happens.</span></li>
    <li><b>Don’t correct, just listen</b><span>There is no right answer to mark. Move to the next colour when the first comes easily.</span></li>
  </ol>
  <p style="margin-top:28px;color:var(--ink-2);max-width:40em">These seven are a taster. The full system has a card pack for each belt, a workbook, a story series and the Thinking Progress Chart.</p>
  <p style="margin-top:14px;color:var(--ink-2);max-width:40em">One-page sets for dates in the school year: <a href="anti-bullying-week/">Anti-Bullying Week</a>, <a href="childrens-mental-health-week/">Children’s Mental Health Week</a> and <a href="safer-internet-day/">Safer Internet Day</a>.</p>
</div>
<section class="band no-print">
  <div class="wrap band-inner">
    <div>
      <h2>Ready for the whole set?</h2>
      <p>Every belt has its own pack of cards. Choose the pack that suits your family.</p>
    </div>
    <div class="band-actions">
      <a class="btn btn-light" href="../#plans">See the packs</a>
      <a class="btn btn-ghost" href="../articles/">Read the articles</a>
    </div>
  </div>
</section>""".format(deck=deck)
    return page("free-cards", "Seven free thinking cards for children aged 7 to 13",
                "Print seven free thinking cards, one from each belt of the Thinking Dojo. One question each, to ask at dinner or in the car.",
                body, 1, "free-cards")

# One-page card sets for dates in the school year. The address of each never contains a year;
# the dates and theme are refreshed here about six weeks before the event.
EVENT_SHEETS = [
    {
        "path": "free-cards/anti-bullying-week", "crumb": "Anti-Bullying Week",
        "cards": [(0, None), (2, None), (4, None)],
        "h1": "Three thinking cards for Anti-Bullying Week.",
        "lede": "Notice, choose, act. One question for each, to ask in class or at home during the week of 16 to 20 November 2026.",
        "steps": [
            ("Early in the week: notice", "Ask the White Belt card, then steer towards people. Who was on their own? Who went quiet?"),
            ("Midweek: choose", "Use a made-up situation. Ask the Orange Belt card about saying nothing, telling an adult and asking someone to join in."),
            ("End of the week: act", "Ask the Blue Belt card. Telling an adult counts as a step, and it is often the hardest one."),
        ],
        "more": 'The full routine, with what to do if a child tells you something worrying, is in <a href="../../articles/three-questions-for-anti-bullying-week/">Three questions for Anti-Bullying Week</a>.',
        "note": 'Anti-Bullying Week is run by the Anti-Bullying Alliance, which publishes its own school resources at <a href="https://anti-bullyingalliance.org.uk/" rel="noopener">anti-bullyingalliance.org.uk</a>. The Thinking Dojo is not part of the campaign.',
        "band_p": "These three come from a free set of seven. Print the rest and keep going after the week.",
        "title": "Three free thinking cards for Anti-Bullying Week 2026",
        "desc": "Print three free thinking cards for Anti-Bullying Week, 16 to 20 November 2026: notice, choose, act. One question each, for class or home.",
    },
    {
        "path": "free-cards/childrens-mental-health-week", "crumb": "Children’s Mental Health Week",
        "cards": [(0, None), (0, "What might others have missed?"), (6, None)],
        "h1": "Three thinking cards for Children’s Mental Health Week.",
        "lede": "Ask, wait, listen. Three questions that let a child show you their world, for class or home during the week of 1 to 7 February 2027.",
        "steps": [
            ("First: what they noticed", "Ask the first White Belt card. There is no wrong answer, and what a child chooses to mention tells you what matters to them."),
            ("Next: what others missed", "Ask the second White Belt card. It invites a child to tell you something the adults have not seen."),
            ("Then: what they think", "Ask the Black Belt card about something real in their world. Listen to the answer without arguing with it."),
        ],
        "more": 'The full routine, with what to do if you are worried about a child, is in <a href="../../articles/three-questions-for-childrens-mental-health-week/">Three questions for Children’s Mental Health Week</a>.',
        "note": 'Children’s Mental Health Week is run by Place2Be, which publishes its own free resources at <a href="https://www.childrensmentalhealthweek.org.uk/" rel="noopener">childrensmentalhealthweek.org.uk</a>. The Thinking Dojo is not part of the campaign.',
        "band_p": "Two of these come from a free set of seven. Print the rest and keep going after the week.",
        "title": "Three free thinking cards for Children’s Mental Health Week",
        "desc": "Print three free thinking cards for Children’s Mental Health Week, 1 to 7 February 2027. Three questions that help adults listen, for class or home.",
    },
    {
        "path": "free-cards/safer-internet-day", "crumb": "Safer Internet Day",
        "cards": [(0, None), (2, None), (5, None)],
        "h1": "Three thinking cards for Safer Internet Day.",
        "lede": "Notice, choose, review. One question for each, to help children reflect on their own screen time around Tuesday 9 February 2027.",
        "steps": [
            ("First: notice", "Ask the White Belt card, then steer towards screens. How did you feel before you picked it up, and after you put it down?"),
            ("Next: choose", "Ask the Orange Belt card about one more episode, stopping now and setting a timer."),
            ("Then: review", "Ask the Brown Belt card about one evening this week. Go first with an answer about your own phone."),
        ],
        "more": 'The full routine is in <a href="../../articles/three-questions-for-safer-internet-day/">Three questions for Safer Internet Day</a>.',
        "note": 'Safer Internet Day is coordinated in the UK by the UK Safer Internet Centre, which publishes its own free resources at <a href="https://saferinternet.org.uk/" rel="noopener">saferinternet.org.uk</a>. The Thinking Dojo is not part of the campaign.',
        "band_p": "These three come from a free set of seven. Print the rest and keep going after the day.",
        "title": "Three free thinking cards for Safer Internet Day",
        "desc": "Print three free thinking cards for Safer Internet Day, Tuesday 9 February 2027: notice, choose, review. One question each, for class or home.",
    },
]


def build_event_sheets():
    urls = []
    for e in EVENT_SHEETS:
        deck = "".join(tcard(i, q) for i, q in e["cards"])
        steps = "".join("\n    <li><b>%s</b><span>%s</span></li>" % (t, d) for t, d in e["steps"])
        body = """
<section class="page-head no-print">
  <div class="wrap">
    <p class="crumbs"><a href="../">Free cards</a><span aria-hidden="true">/</span><span>{crumb}</span></p>
    <h1>{h1}</h1>
    <p class="lede no-print">{lede}</p>
    <p class="no-print" style="margin-top:26px"><button class="btn btn-primary" type="button" onclick="window.print()">Print the cards</button></p>
  </div>
</section>
<div class="wrap" style="padding-block:clamp(28px,4vw,48px)">
  <div class="deck">{deck}</div>
</div>
<div class="wrap no-print" style="padding-bottom:clamp(48px,7vw,88px)">
  <h2 style="font-size:clamp(26px,3.2vw,36px);margin-bottom:20px">How to use them</h2>
  <ol class="steps">{steps}
  </ol>
  <p style="margin-top:28px;color:var(--ink-2);max-width:40em">{more}</p>
  <p style="margin-top:14px;color:var(--ink-3);font-size:15.5px;max-width:42em">{note}</p>
</div>
<section class="band no-print">
  <div class="wrap band-inner">
    <div>
      <h2>Seven cards, one from every belt.</h2>
      <p>{band_p}</p>
    </div>
    <div class="band-actions">
      <a class="btn btn-light" href="../">Print all seven</a>
      <a class="btn btn-ghost" href="../../articles/">Read the articles</a>
    </div>
  </div>
</section>""".format(deck=deck, steps=steps, crumb=e["crumb"], h1=e["h1"], lede=e["lede"], more=e["more"],
                    note=e["note"], band_p=e["band_p"])
        urls.append(page(e["path"], e["title"], e["desc"], body, 2, "free-cards"))
    return urls


# ---------------------------------------------------------------- privacy and terms

def legal_page(path, title, description, lede, sections):
    inner = "".join("<h2>%s</h2>%s" % (h, b) for h, b in sections)
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">The Thinking Dojo</p>
    <h1>{title}</h1>
    <p class="lede">{lede}</p>
    <p class="meta">Last updated {date}</p>
  </div>
</section>
<div class="wrap"><div class="prose legal">{inner}</div></div>""".format(title=title, lede=lede, date=PUBLISHED_HUMAN, inner=inner)
    return page(path, title, description, body, 1)


def build_privacy():
    mail = '<a href="mailto:%s">%s</a>' % (EMAIL, EMAIL)
    sections = [
        ("Who we are",
         "<p>The Thinking Dojo is run by %s in the United Kingdom. You can reach us at %s.</p>"
         "<p>This policy covers this website and purchases made through it.</p>" % (OPERATOR, mail)),
        ("The short version",
         "<ul><li>This website has no accounts and no sign-up forms.</li>"
         "<li>This website sets no cookies.</li>"
         "<li>There is no advertising and there are no advertising trackers.</li>"
         "<li>We do not knowingly collect information from children through this website.</li>"
         "<li>Your child’s Coach Engine answers stay on your own device.</li></ul>"),
        ("Counting visits",
         "<p>We count page views with GoatCounter, a privacy-focused analytics service. It uses no cookies and stores nothing in your browser. "
         "It records the page viewed, the site you came from, your browser type, your screen size and your approximate location, such as your country. "
         "We use this only to see which pages are read.</p>"),
        ("Fonts",
         "<p>The typefaces on this website load from Google Fonts. To send them, Google’s servers receive your device’s IP address, as any web server does.</p>"),
        ("When you buy",
         "<p>Checkout is run by Lemon Squeezy, which acts as the merchant of record. Lemon Squeezy takes your payment and handles tax and receipts. We never see your card details.</p>"
         "<p>We receive your name, your email address and what you bought, so that we can deliver your purchase and help if something goes wrong. Lemon Squeezy’s own privacy policy applies to the checkout.</p>"),
        ("When you email us",
         "<p>If you email us, we use your address and your message only to reply to you.</p>"),
        ("Children",
         "<p>This website is written for parents, teachers and home educators. The free cards and the printed packs are used on paper and send nothing to us.</p>"),
        ("The Coach Engine",
         "<p>The Coach Engine is a file that runs in the web browser on your own device. It does not send your child’s answers to us or to anyone else, and we cannot see them. It needs no internet connection once it is open.</p>"
         "<p>Answers are held only for the session in progress. At the end of a session you can export a text summary to keep. If you do not, the answers are not kept.</p>"
         "<p>The Coach Engine remembers which belts have been completed in the browser’s storage on that device. It also stores the date it was unlocked and a shortened reference to your access key. Clearing the browser’s data removes all of this.</p>"),
        ("How long we keep information",
         "<p>We keep order details for as long as we need them to support your purchase and to meet our legal duties. We keep emails for as long as we need them to deal with your question.</p>"),
        ("Your rights",
         "<p>Under UK data protection law you can ask for a copy of the information we hold about you, ask us to correct it, or ask us to delete it. Email %s.</p>"
         "<p>If you are unhappy with how we have handled your information, you can complain to the Information Commissioner’s Office at <a href=\"https://ico.org.uk/\" rel=\"noopener\">ico.org.uk</a>.</p>" % mail),
        ("Changes",
         "<p>If we change this policy, we will update this page and the date at the top.</p>"),
    ]
    return legal_page("privacy", "Privacy policy",
                      "What the Thinking Dojo website collects and what it doesn’t: no accounts, no cookies and no advertising trackers.",
                      "What this website collects, and what it doesn’t.", sections)


def build_terms():
    mail = '<a href="mailto:%s">%s</a>' % (EMAIL, EMAIL)
    sections = [
        ("Who we are",
         "<p>The Thinking Dojo is run by %s in the United Kingdom. You can reach us at %s.</p>" % (OPERATOR, mail)),
        ("What you are buying",
         "<p>The Workbook, Starter System and Complete System are digital downloads. You get access to your files straight after purchase. "
         "The Coach Engine is a file that opens in a web browser on iPhone, iPad and desktop.</p>"),
        ("Paying",
         "<p>Checkout is handled by Lemon Squeezy, which acts as the merchant of record for your purchase. Lemon Squeezy’s buyer terms apply to the payment.</p>"),
        ("How you may use it",
         "<ul><li>You may use what you buy with the children in your own household.</li>"
         "<li>If you are a teacher, you may use it with your own class.</li>"
         "<li>You may print as many copies as you need for those uses.</li>"
         "<li>The Coach Engine is sold with a single-user licence.</li>"
         "<li>Please do not resell the files, republish them or share them publicly.</li></ul>"),
        ("The free cards and articles",
         "<p>The free cards and the articles on this website are free to read, print and use at home or in your classroom. Please do not republish them as your own.</p>"),
        ("If something is wrong",
         "<p>If a file will not open, is faulty or is not what this website described, email %s. We will fix it, replace it or arrange a refund.</p>"
         "<p>Nothing in these terms affects your legal rights as a consumer.</p>" % mail),
        ("What the Thinking Dojo is, and is not",
         "<p>The Thinking Dojo is an educational resource for building thinking habits. It is not a medical, psychological or therapeutic service, and we cannot promise a particular result for any child.</p>"),
        ("Ownership",
         "<p>The Thinking Dojo name, the belt system, the cards, the stories and all other materials belong to us. Buying a pack gives you the right to use it as described above.</p>"),
        ("Law",
         "<p>These terms are governed by the law of England and Wales.</p>"),
        ("Changes",
         "<p>If we change these terms, we will update this page and the date at the top.</p>"),
    ]
    return legal_page("terms", "Terms of use",
                      "The terms for buying and using the Thinking Dojo: what you get, how you may use it at home or in class, and what to do if something is wrong.",
                      "Plain terms for buying and using the Thinking Dojo.", sections)


# ---------------------------------------------------------------- homepage and sitemap

HOME_MARK = "<!-- ways-in: links and sharing tags added by _build/build_pages.py -->"


def replace_once(text, old, new, what):
    if text.count(old) != 1:
        sys.exit("index.html: expected exactly one match for %s, found %d" % (what, text.count(old)))
    return text.replace(old, new)


def patch_home():
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf-8").read()
    if HOME_MARK in s:
        return False
    faq = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", s)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                          "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faq]}
    desc = re.search(r'<meta name="description" content="([^"]*)">', s).group(1)
    products = []
    for art in re.findall(r'<article class="plan[^"]*"[\s\S]*?</article>', s):
        products.append({
            "@context": "https://schema.org", "@type": "Product",
            "name": "The Thinking Dojo " + strip_tags(re.search(r"<h3>(.*?)</h3>", art).group(1)),
            "description": strip_tags(re.search(r'<p class="plan-desc">(.*?)</p>', art).group(1)),
            "image": BASE + "hero-poster.jpg",
            "brand": {"@type": "Brand", "name": "The Thinking Dojo"},
            "offers": {"@type": "Offer", "priceCurrency": "GBP",
                       "price": re.search(r"£([\d.]+)", art).group(1),
                       "availability": "https://schema.org/InStock",
                       "url": re.search(r'href="([^"]+)"', art).group(1)},
        })
    if len(products) != 4:
        sys.exit("index.html: expected four packs, found %d" % len(products))
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "The Thinking Dojo", "url": BASE,
           "email": EMAIL, "founder": {"@type": "Person", "name": FOUNDER, "sameAs": LINKEDIN}}
    extra_ld = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(x, ensure_ascii=False)
                       for x in [org] + products)
    head = """{mark}
<link rel="canonical" href="{base}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The Thinking Dojo">
<meta property="og:title" content="The Thinking Dojo: teach children aged 7–13 how to think">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{base}">
<meta property="og:image" content="{base}hero-poster.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
{extra_ld}<style>
  .toplink {{ font-size: 15px; font-weight: 600; color: var(--ink-2); text-decoration: none; padding: 10px 0; }}
  .toplink:hover {{ color: var(--ink); text-decoration: underline; text-underline-offset: 5px; }}
  @media (max-width: 900px) {{ .toplink {{ display: none; }} }}
  .foot-links {{ display: flex; flex-wrap: wrap; gap: 4px 22px; }}
  .foot-links a {{ font-weight: 600; color: var(--ink-2); padding: 8px 0; }}
  .try-free {{ margin-top: 6px; font-size: 17px; color: var(--ink-2); }}
  .try-free a {{ color: var(--navy); font-weight: 700; text-underline-offset: 3px; }}
</style>
</head>""".format(mark=HOME_MARK, base=BASE, desc=desc, ld=json.dumps(ld, ensure_ascii=False), extra_ld=extra_ld)
    s = replace_once(s, "</head>", head, "</head>")
    s = replace_once(s, "<title>The Thinking Dojo</title>",
                     "<title>The Thinking Dojo | Teach children aged 7–13 how to think</title>", "<title>")
    s = replace_once(s, '<span class="topbar-age">Designed for ages 7–13</span>',
                     '<span class="topbar-age">Designed for ages 7–13</span>\n'
                     '      <a class="toplink" href="articles/">Articles</a>\n'
                     '      <a class="toplink" href="teachers/">For teachers</a>\n'
                     '      <a class="toplink" href="free-cards/">Free cards</a>', "top bar")
    s = replace_once(s, '<span>The Thinking Dojo · Part of the Opportunity Intelligence Ecosystem</span>',
                     '<span>The Thinking Dojo · Part of the Opportunity Intelligence Ecosystem</span>\n'
                     '    <span class="foot-links"><a href="articles/">Articles</a><a href="questions/">Questions</a>'
                     '<a href="teachers/">For teachers</a><a href="free-cards/">Free cards</a>'
                     '<a href="questions/#ask">Contact</a><a href="privacy/">Privacy</a><a href="terms/">Terms</a></span>', "footer")
    old_lede = ('<p class="lede">Each pack includes everything in the one before it. The Coach Engine is the digital companion '
                'and works on its own or alongside any pack.</p>')
    s = replace_once(s, old_lede, old_lede +
                     '\n        <p class="try-free">Not ready to choose? <a href="free-cards/">Print seven free cards first</a>.</p>',
                     "plans intro")
    open(p, "w", encoding="utf-8").write(s)
    return True


# Pages added or changed after the first publication date carry their own date here.
LASTMOD = {
    "articles/": "2026-11-16",
    "articles/three-questions-for-anti-bullying-week/": "2026-11-16",
    "free-cards/": "2026-11-16",
    "free-cards/anti-bullying-week/": "2026-11-16",
    "articles/three-questions-for-childrens-mental-health-week/": "2026-11-16",
    "articles/three-questions-for-safer-internet-day/": "2026-11-16",
    "free-cards/childrens-mental-health-week/": "2026-11-16",
    "free-cards/safer-internet-day/": "2026-11-16",
}


def write_sitemap(urls):
    rows = ['  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>' % (BASE, PUBLISHED)]
    rows += ['  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>' % (u, LASTMOD.get(u[len(BASE):], PUBLISHED)) for u in urls]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(xml)


if __name__ == "__main__":
    urls = [build_hub()] + build_articles() + [build_questions(), build_teachers(), build_free_cards(),
                                               build_privacy(), build_terms()] + build_event_sheets()
    build_feed()
    patched = patch_home()
    write_sitemap(urls)
    print("pages written:", len(urls))
    print("index.html patched" if patched else "index.html already patched")
