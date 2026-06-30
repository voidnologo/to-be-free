#!/usr/bin/env python3
"""Build the 'To Be Free' static site (GitHub Pages) from sources/*/*.md.
Reusable: rerun after editing any markdown. Output -> docs/ ."""
import re, json, html, subprocess, shutil
from pathlib import Path

PROJ = Path(__file__).resolve().parent
SRC  = PROJ/"sources"
OUT  = PROJ/"docs"
ASSETS = OUT/"assets"

SECTION_TITLES = {
 "01-ezra-taft-benson":"Ezra Taft Benson","02-d-todd-christofferson":"D. Todd Christofferson",
 "03-quentin-l-cook":"Quentin L. Cook","04-robert-d-hales":"Robert D. Hales",
 "05-jeffrey-r-holland":"Jeffrey R. Holland","06-david-o-mckay":"David O. McKay",
 "07-dallin-h-oaks":"Dallin H. Oaks","08-ronald-a-rasband":"Ronald A. Rasband",
 "09-historical-statements":"Historical Statements & First Presidency Letters",
 "10-j-reuben-clark":"J. Reuben Clark Jr.","11-resource-hubs":"Resource Hubs",
 "12-l-tom-perry":"L. Tom Perry",
 "13-w-cleon-skousen":"W. Cleon Skousen","14-marion-g-romney":"Marion G. Romney",
 "15-h-verlan-andersen":"H. Verlan Andersen","16-gordon-b-hinckley":"Gordon B. Hinckley",
 "17-howard-w-hunter":"Howard W. Hunter","18-john-taylor":"John Taylor",
 "19-joseph-smith":"Joseph Smith","20-spencer-w-kimball":"Spencer W. Kimball",
 "21-additional-church-leaders":"Additional Church Leaders",
 "22-supporting-authors":"Supporting Authors & Commentators",
 "23-topical-and-founding-documents":"Topical & Founding Documents",
}
SECTION_GROUPS = [
 ("Prophets & Apostles", ["01-ezra-taft-benson","07-dallin-h-oaks","06-david-o-mckay",
   "02-d-todd-christofferson","05-jeffrey-r-holland","04-robert-d-hales","03-quentin-l-cook",
   "08-ronald-a-rasband","16-gordon-b-hinckley","17-howard-w-hunter","20-spencer-w-kimball",
   "12-l-tom-perry","14-marion-g-romney","19-joseph-smith","18-john-taylor","21-additional-church-leaders"]),
 ("Statements & Scholars", ["09-historical-statements","10-j-reuben-clark",
   "13-w-cleon-skousen","15-h-verlan-andersen","22-supporting-authors"]),
 ("Topical & Reference", ["23-topical-and-founding-documents","11-resource-hubs"]),
]

CSS = r"""
:root{
  --paper:#fbfaf6; --panel:#f4f1ea; --ink:#23262c; --soft-ink:#3a3f47;
  --muted:#71757c; --accent:#1f4e79; --accent-2:#7a2e2e; --rule:#e4ded2;
  --rule-2:#d8d2c4; --shadow:0 1px 2px rgba(30,30,30,.05),0 8px 24px rgba(30,30,30,.06);
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);
  font-size:18px;line-height:1.65;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

/* top bar */
.topbar{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:14px;
  height:56px;padding:0 18px;background:rgba(251,250,246,.92);backdrop-filter:saturate(1.2) blur(8px);
  border-bottom:1px solid var(--rule);font-family:var(--sans)}
.brand{font-family:var(--serif);font-weight:700;font-size:1.2rem;color:var(--ink);letter-spacing:.2px}
.brand:hover{text-decoration:none}
.hamb{display:none;border:0;background:none;font-size:1.4rem;cursor:pointer;color:var(--soft-ink);padding:4px 6px}
.topnav{margin-left:auto;font-size:.95rem}
.topnav a{color:var(--soft-ink)}
.search{position:relative;margin-left:auto;width:min(420px,40vw)}
.search input{width:100%;font:inherit;font-size:.95rem;padding:8px 12px;border:1px solid var(--rule-2);
  border-radius:9px;background:#fff;color:var(--ink)}
.search input:focus{outline:2px solid var(--accent);outline-offset:0;border-color:var(--accent)}
.topnav{margin-left:14px}
.results{position:absolute;top:42px;left:0;right:0;background:#fff;border:1px solid var(--rule-2);
  border-radius:10px;box-shadow:var(--shadow);max-height:60vh;overflow:auto;display:none}
.results.on{display:block}
.results a{display:block;padding:9px 12px;border-bottom:1px solid var(--rule);color:var(--ink);font-size:.92rem}
.results a:hover{background:var(--panel);text-decoration:none}
.results .r-a{color:var(--muted);font-size:.82rem}
.results .r-s{color:var(--accent);font-size:.76rem;text-transform:uppercase;letter-spacing:.4px}
.results .none{padding:11px 12px;color:var(--muted);font-size:.9rem}

/* layout */
.layout{display:flex;align-items:flex-start;max-width:1180px;margin:0 auto}
.side{flex:0 0 286px;position:sticky;top:56px;height:calc(100vh - 56px);overflow:auto;
  border-right:1px solid var(--rule);background:var(--paper);font-family:var(--sans)}
.side-inner{padding:18px 14px 60px}
.side-home{display:block;font-weight:600;color:var(--soft-ink);padding:5px 8px;border-radius:7px;font-size:.95rem}
.side-home:hover{background:var(--panel);text-decoration:none}
.side-group{margin:18px 8px 6px;font-size:.72rem;font-weight:700;letter-spacing:.9px;
  text-transform:uppercase;color:var(--muted)}
.side-sec{border-radius:7px}
.side-sec>summary{list-style:none;cursor:pointer;padding:6px 8px;border-radius:7px;font-size:.92rem;
  font-weight:600;color:var(--ink);display:flex;align-items:center;gap:8px}
.side-sec>summary::-webkit-details-marker{display:none}
.side-sec>summary:before{content:"▸";color:var(--muted);font-size:.8em;transition:transform .15s}
.side-sec[open]>summary:before{transform:rotate(90deg)}
.side-sec>summary:hover{background:var(--panel)}
.side-sec .cnt{margin-left:auto;font-size:.74rem;color:var(--muted);font-weight:600}
.side-sec ul{list-style:none;margin:2px 0 8px;padding:0 4px 0 22px}
.side-sec li a{display:block;padding:4px 8px;border-radius:6px;font-size:.86rem;color:var(--soft-ink);
  line-height:1.35;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.side-sec li a:hover{background:var(--panel);text-decoration:none;color:var(--ink)}

.main{flex:1 1 auto;min-width:0;padding:30px 40px 90px}

/* reading column */
.reading .main{max-width:760px;margin:0 auto}
.crumbs{font-family:var(--sans);font-size:.82rem;color:var(--muted);margin-bottom:14px}
.doc-head{border-bottom:1px solid var(--rule);padding-bottom:18px;margin-bottom:26px}
.doc-head h1{font-size:2rem;line-height:1.2;margin:.1em 0 .35em;font-weight:700;letter-spacing:-.01em}
.byline{font-family:var(--sans);color:var(--soft-ink);font-size:.96rem;display:flex;gap:10px;
  align-items:center;flex-wrap:wrap}
.badge{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;
  padding:2px 7px;border-radius:20px;font-family:var(--sans)}
.badge.c{background:#e7eef6;color:var(--accent)}
.badge.r{background:#efeadf;color:#7a6320}
.badge.b{background:#eee2e2;color:var(--accent-2)}
.tags{margin:12px 0 8px;display:flex;flex-wrap:wrap;gap:7px}
.tag{font-family:var(--sans);font-size:.78rem;background:var(--panel);color:var(--soft-ink);
  padding:3px 10px;border-radius:20px;border:1px solid var(--rule-2)}
.tag:hover{background:#fff;text-decoration:none;border-color:var(--accent);color:var(--accent)}
.src{font-family:var(--sans);font-size:.84rem;color:var(--muted);margin-top:4px}
.src-orig{margin-top:14px}
.src-link{display:inline-flex;align-items:center;gap:7px;font-family:var(--sans);font-size:.85rem;
  font-weight:600;color:var(--accent);text-decoration:none;border:1px solid var(--rule);
  border-radius:8px;padding:7px 13px;background:var(--panel);transition:border-color .15s}
.src-link:hover{border-color:var(--accent);text-decoration:none}
.doc-toc{font-family:var(--sans);background:var(--panel);border:1px solid var(--rule);
  border-radius:10px;padding:12px 18px;margin:0 0 30px}
.doc-toc>summary{font-weight:700;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;
  color:var(--muted);cursor:pointer;list-style-position:inside}
.doc-toc ul{list-style:none;padding:.6em 0 0;margin:0;columns:2;column-gap:30px;font-size:.92rem}
.doc-toc li{margin:.28em 0;break-inside:avoid}
.doc-toc .toc-sub{padding-left:1.1em;font-size:.86rem}
.doc-toc a{color:var(--soft-ink);text-decoration:none}
.doc-toc a:hover{color:var(--accent)}
.prose h2,.prose h3{scroll-margin-top:72px}
@media(max-width:640px){.doc-toc ul{columns:1}}
.src-note{font-family:var(--sans);font-size:.86rem;color:var(--soft-ink);background:var(--panel);
  border-left:3px solid var(--rule-2);padding:9px 13px;border-radius:0 8px 8px 0;margin-top:12px;line-height:1.5}

/* prose */
.prose{font-size:1.12rem;line-height:1.72;text-align:justify;
  -webkit-hyphens:auto;hyphens:auto;hyphenate-limit-chars:6 3 3}
.prose p{margin:0 0 1.15em}
.prose blockquote,.prose h1,.prose h2,.prose h3{text-align:left;hyphens:none}
.prose h1,.prose h2,.prose h3{font-weight:700;line-height:1.25;margin:1.7em 0 .5em}
.prose h2{font-size:1.5rem} .prose h3{font-size:1.22rem}
.prose blockquote{margin:1.3em 0;padding:.2em 0 .2em 1.1em;border-left:3px solid var(--rule-2);
  color:var(--soft-ink);font-style:italic}
.prose ol,.prose ul{padding-left:1.5em;margin:0 0 1.15em}
.prose li{margin:.3em 0}
.prose hr{border:0;border-top:1px solid var(--rule);margin:2em 0}
.prose pre{white-space:pre-wrap;word-wrap:break-word;overflow-x:auto;background:var(--panel);
  padding:10px 13px;border-radius:8px;font-size:.92em;text-align:left;hyphens:none}
.prose code{word-break:break-word}
/* quote-compilation pages: justified quotes, each with a cited source + separator */
.prose.quotes blockquote{text-align:justify;-webkit-hyphens:auto;hyphens:auto;
  margin:0;padding:0;border-left:none;color:var(--soft-ink);font-style:normal}
.prose.quotes blockquote p{margin:0 0 .7em}
.prose.quotes blockquote p:last-child{margin-bottom:0}
.prose.quotes>p{text-align:right;font-family:var(--sans);font-size:.84rem;color:var(--muted);
  margin:.55em 0 2.1em;padding-bottom:1.7em;border-bottom:1px solid var(--rule-2)}
.prose.quotes>p:last-child{border-bottom:none;padding-bottom:0}
.prose.quotes>p em{font-style:normal}
.prose a{color:var(--accent);text-decoration:underline;text-underline-offset:2px}
.prose em{font-style:italic}

.prevnext{display:flex;justify-content:space-between;gap:16px;margin-top:46px;padding-top:20px;
  border-top:1px solid var(--rule);font-family:var(--sans);font-size:.9rem}
.pn{max-width:46%;color:var(--soft-ink)}
.pn.next{text-align:right;margin-left:auto}
.pn:hover{color:var(--accent)}

/* landing */
.hero{text-align:center;padding:46px 16px 6px}
.hero h1{font-size:3.1rem;letter-spacing:-.02em;margin:0;font-weight:700}
.tagline{font-size:1.22rem;color:var(--soft-ink);margin:.5em auto 0;max-width:34ch}
.intro{max-width:680px;margin:30px auto 0;font-size:1.12rem;line-height:1.72;
  text-align:justify;-webkit-hyphens:auto;hyphens:auto}
.intro blockquote{text-align:left;hyphens:none}
.intro blockquote{margin:1.4em 0;padding:.6em 0 .6em 1.2em;border-left:4px solid var(--accent);
  font-style:italic;color:var(--soft-ink)}
.about h2{font-family:var(--sans);font-size:1.18rem;font-weight:700;margin:1.9em 0 .4em;text-align:left}
.about .callout{background:var(--panel);border:1px solid var(--rule);border-radius:10px;
  padding:15px 18px;margin:1.6em 0;font-size:.99rem;text-align:left}
.about ul{text-align:left;padding-left:1.3em} .about li{margin:.35em 0}
.intro blockquote cite{display:block;margin-top:.5em;font-style:normal;font-family:var(--sans);
  font-size:.86rem;color:var(--muted)}
.stats{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;max-width:680px;margin:40px auto;
  padding:22px;background:var(--panel);border-radius:14px}
.stats div{display:flex;flex-direction:column;align-items:center;min-width:90px}
.stats b{font-size:1.9rem;color:var(--accent);font-weight:700}
.stats span{font-family:var(--sans);font-size:.78rem;text-transform:uppercase;letter-spacing:.6px;color:var(--muted)}
.explore{text-align:center;margin:50px 0 4px;font-size:1.6rem}
.explore-sub{text-align:center;color:var(--muted);font-family:var(--sans);font-size:.92rem;max-width:560px;margin:0 auto 24px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;max-width:900px;margin:0 auto}
.card{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:13px 16px;
  background:#fff;border:1px solid var(--rule-2);border-radius:11px;box-shadow:var(--shadow)}
.card:hover{text-decoration:none;border-color:var(--accent);transform:translateY(-1px)}
.card-t{font-weight:600;color:var(--ink);font-size:.98rem}
.card-n{font-family:var(--sans);font-size:.76rem;color:var(--muted);white-space:nowrap}

/* browse */
.browse{max-width:840px;margin:0 auto}
.browse h1{font-size:2.2rem;margin:.2em 0 .2em}
.lead{color:var(--soft-ink)}
.filter{width:100%;font:inherit;font-size:1rem;padding:11px 14px;border:1px solid var(--rule-2);
  border-radius:10px;margin:14px 0 26px;background:#fff}
.filter:focus{outline:2px solid var(--accent);border-color:var(--accent)}
.grp{font-family:var(--sans);font-size:.8rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  color:var(--muted);margin:34px 0 6px;border-bottom:1px solid var(--rule);padding-bottom:6px}
.bsec{margin:22px 0}
.bsec h3{font-size:1.3rem;margin:.4em 0 .3em;scroll-margin-top:70px}
.bsec h3 .cnt{font-family:var(--sans);font-size:.78rem;color:var(--muted);font-weight:600}
.blist{list-style:none;padding:0;margin:0;border-top:1px solid var(--rule)}
.blist li{display:flex;justify-content:space-between;gap:14px;align-items:baseline;
  padding:8px 4px;border-bottom:1px solid var(--rule)}
.blist li a{font-size:1.02rem}
.bmeta{font-family:var(--sans);font-size:.82rem;color:var(--muted);white-space:nowrap;text-align:right}
.filter-empty{color:var(--muted)}

/* off-canvas + scrim (mobile) */
.scrim{position:fixed;inset:0;background:rgba(20,20,20,.4);z-index:30;display:none}
.scrim.on{display:block}

@media (max-width:900px){
  body{font-size:17px}
  .hamb{display:block}
  .search{width:auto;flex:1}
  .topnav{display:none}
  .side{position:fixed;top:56px;left:0;z-index:35;width:300px;height:calc(100vh - 56px);
    transform:translateX(-100%);transition:transform .22s ease;box-shadow:var(--shadow)}
  .side.open{transform:none}
  .main{padding:24px 20px 80px}
  .reading .main{max-width:100%}
  .doc-head h1{font-size:1.7rem}
  .hero h1{font-size:2.4rem}
  .prose{font-size:1.08rem}
}
@media (max-width:520px){
  .main{padding:20px 16px 70px}
  .bmeta{display:none}
  .stats{gap:6px;padding:16px 10px}
  .stats b{font-size:1.5rem}
}
"""

JS = r"""
(function(){
  var R = window.SITE_ROOT || "./";
  // mobile sidebar
  var side=document.getElementById('side'), scrim=document.getElementById('scrim'),
      hamb=document.getElementById('hamb');
  function close(){side&&side.classList.remove('open');scrim&&scrim.classList.remove('on');}
  hamb&&hamb.addEventListener('click',function(){var o=side.classList.toggle('open');
    scrim.classList.toggle('on',o);});
  scrim&&scrim.addEventListener('click',close);
  // ensure current sidebar item visible
  var cur=document.querySelector('.side-sec[open] li a[href$="'+location.pathname.split('/').pop()+'"]');

  // live search
  var q=document.getElementById('q'), box=document.getElementById('results'), idx=null;
  function load(cb){ if(idx){cb();return;}
    fetch(R+'search-index.json').then(function(r){return r.json();}).then(function(d){idx=d;cb();}); }
  function esc(s){return (s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function run(){
    var v=q.value.trim().toLowerCase();
    if(!v){box.classList.remove('on');box.innerHTML='';return;}
    load(function(){
      var terms=v.split(/\s+/), out=[];
      for(var i=0;i<idx.length && out.length<14;i++){
        var d=idx[i], hay=(d.t+' '+d.a+' '+d.s+' '+(d.g||[]).join(' ')).toLowerCase();
        if(terms.every(function(t){return hay.indexOf(t)>-1;})) out.push(d);
      }
      if(!out.length){box.innerHTML='<div class="none">No documents match.</div>';box.classList.add('on');return;}
      box.innerHTML=out.map(function(d){return '<a href="'+R+d.u+'"><span class="r-s">'+esc(d.s)+
        '</span><br>'+esc(d.t)+'<br><span class="r-a">'+esc(d.a)+'</span></a>';}).join('');
      box.classList.add('on');
    });
  }
  if(q){
    q.addEventListener('input',run);
    q.addEventListener('focus',run);
    document.addEventListener('click',function(e){ if(!e.target.closest('.search')) box.classList.remove('on'); });
    document.addEventListener('keydown',function(e){ if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus();}
      if(e.key==='Escape')box.classList.remove('on'); });
  }

  // browse filter (+ ?q= prefill from tag links / global search)
  var filter=document.getElementById('filter');
  if(filter){
    var params=new URLSearchParams(location.search), pre=params.get('q');
    function apply(){
      var v=(filter.value||'').trim().toLowerCase(), any=false;
      document.querySelectorAll('.blist li').forEach(function(li){
        var hit=!v||li.getAttribute('data-text').indexOf(v)>-1;
        li.style.display=hit?'':'none'; if(hit)any=true;
      });
      document.querySelectorAll('.bsec').forEach(function(s){
        var vis=s.querySelector('.blist li:not([style*="none"])');
        s.style.display=vis?'':'none';
      });
      document.querySelectorAll('.grp').forEach(function(g){
        var n=g.nextElementSibling, show=false;
        while(n&&!n.classList.contains('grp')){ if(n.classList.contains('bsec')&&n.style.display!=='none')show=true; n=n.nextElementSibling;}
        g.style.display=show?'':'none';
      });
      var fe=document.getElementById('fempty'); if(fe)fe.hidden=any;
    }
    filter.addEventListener('input',apply);
    if(pre){filter.value=pre;apply();}
  }
})();
"""

def esc(s): return html.escape(str(s or ""), quote=True)

def parse(p):
    t = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    if not m: return None
    raw, post = m.group(1), m.group(2)
    d = {}
    for line in raw.splitlines():
        mm = re.match(r'(\w+):\s*(.*)$', line)
        if not mm: continue
        k, v = mm.group(1), mm.group(2).strip()
        if k == "tags":
            d["tags"] = re.findall(r'"(.*?)"', v)
        else:
            d[k] = v.strip('"').split("   #")[0].strip().strip('"')
    # extract body: strip the preamble (# Title / *Author* / note / hr)
    body = post
    idx = post.find("\n---\n")
    if 0 <= idx < 700:
        body = post[idx+5:]
    else:
        # fall back: drop a leading "# ..." line and a following "*...*" byline
        body = re.sub(r'^\s*#\s+.*\n+(\*.*\*\s*\n+)?', '', post, count=1)
    return d, clean_body(body.strip(), d.get("title",""), d.get("author",""))

def _is_byline(line, title, author):
    s = line.strip().strip("*").strip()
    if not s or len(s) > 260: return False
    sl = s.lower()
    th = re.split(r"[—-]", title.lower())[0].strip()
    starts_title = len(th) >= 6 and sl.startswith(th[:14])
    full_author = bool(author) and author.lower() in sl
    surname = author.split()[-1].lower() if author else ""
    has_year = bool(re.search(r"\b(1[789]\d\d|20\d\d)\b", s))
    return starts_title or full_author or (len(surname) > 2 and surname in sl and has_year)

def clean_body(body, title, author):
    """Strip a leading duplicate H1 and a byline line that just repeat the header fields."""
    b = body.lstrip("\n")
    b = re.sub(r"^\s*#\s+.*\n+", "", b, count=1)        # leading dup H1 (title or author)
    lines = b.split("\n")
    j = 0
    while j < len(lines) and lines[j].strip() == "": j += 1
    if j < len(lines) and _is_byline(lines[j], title, author):
        del lines[j]
    return "\n".join(lines).lstrip("\n")

def fmt_date(d):
    d=(d or "").strip()
    MO=["","January","February","March","April","May","June","July","August","September","October","November","December"]
    m=re.match(r'^(\d{4})-(\d{2})-(\d{2})$', d)
    if m: return f"{MO[int(m.group(2))]} {int(m.group(3))}, {m.group(1)}"
    m=re.match(r'^(\d{4})-(\d{2})$', d)
    if m: return f"{MO[int(m.group(2))]} {m.group(1)}"
    return d  # bare year or anything else passes through

PUB_NAME={"general-conference":"General Conference","ensign":"Ensign","new-era":"New Era",
 "liahona":"Liahona","friend":"Friend"}
def cite_text(d):
    """Short citation for the meta line (venue/date). The fuller source_note is
    rendered separately in its own box, so we do NOT repeat it here."""
    u=d.get("source_url") or ""; dt=d.get("date") or ""; fd=fmt_date(dt) if dt else ""
    m=re.search(r'/(general-conference|ensign|new-era|liahona|friend)/(\d{4})/(\d{2})\b',u)
    if m: return f"{PUB_NAME[m.group(1)]}, {fmt_date(m.group(2)+'-'+m.group(3))}"
    if "scriptures/dc-testament" in u: return "Doctrine and Covenants"
    if "speeches.byu.edu" in u: return "BYU Speeches"+(f", {fd}" if fd else "")
    if "newsroom.churchofjesuschrist.org" in u: return "Church Newsroom"+(f", {fd}" if fd else "")
    if "/study/manual/" in u: return "Church curriculum"+(f", {fd}" if fd else "")
    return fd  # otherwise show the date if we have one

def reading_time(words):
    m=max(1,round(words/220))
    if m<60: return f"{m} min read"
    h,mm=divmod(m,60)
    return f"{h} hr {mm} min read" if mm else f"{h} hr read"

_SRC_LABELS=[("newsroom","Church Newsroom"),("mormonnewsroom","Church Newsroom"),
  ("churchofjesuschrist.org","ChurchofJesusChrist.org"),("lds.org","ChurchofJesusChrist.org"),
  ("speeches.byu.edu","BYU Speeches"),
  ("rsc.byu.edu","BYU Religious Studies Center"),("digitalcommons.law.byu.edu","BYU Law Digital Commons"),
  ("archive.org","the Internet Archive"),("gutenberg","Project Gutenberg"),
  ("latterdayconservative.com","Latter-day Conservative")]
def source_link(d):
    u=(d.get("source_url") or "").strip()
    if not u: return ""
    for k,v in _SRC_LABELS:
        if k in u:
            return (f'<a class="src-link" href="{esc(u)}" target="_blank" rel="noopener noreferrer">'
                    f'Read the original on {v} <span aria-hidden="true">↗</span></a>')
    return (f'<a class="src-link" href="{esc(u)}" target="_blank" rel="noopener noreferrer">'
            f'Read the original source <span aria-hidden="true">↗</span></a>')

def build_toc(body_html):
    items=re.findall(r'<(h[23]) id="([^"]+)">(.*?)</\1>', body_html, re.S)
    if len(items) < 4: return ""
    li=[]
    for tag,hid,txt in items:
        txt=re.sub(r'<[^>]+>','',txt).strip()
        if not txt: continue
        cls="toc-sub" if tag=="h3" else "toc-top"
        li.append(f'<li class="{cls}"><a href="#{hid}">{esc(txt)}</a></li>')
    return ('<details class="doc-toc" open><summary>Contents</summary><ul>'
            + ''.join(li) + '</ul></details>')

def md2html(md):
    # strip leading indentation so extracted text isn't misread as code blocks (monospace/overflow)
    md = re.sub(r'(?m)^[ \t]+', '', md)
    r = subprocess.run(["pandoc","-f","markdown+smart-raw_html","-t","html5","--no-highlight","--wrap=none"],
                       input=md, capture_output=True, text=True)
    return r.stdout

# ---------- clean output dir so stale/renamed pages don't linger ----------
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)

# ---------- load all docs ----------
docs = []   # dict: section, slug, title, author, date, tags, words, status, collection, src, body_html, url
for secdir in sorted(SRC.glob("*/")):
    sec = secdir.name
    if sec not in SECTION_TITLES: continue
    for f in sorted(secdir.glob("*.md")):
        pr = parse(f)
        if not pr: continue
        d, body = pr
        slug = f.stem
        url = f"c/{sec}/{slug}.html"
        docs.append(dict(
            section=sec, slug=slug, url=url,
            title=d.get("title","Untitled"), author=d.get("author",""),
            date=d.get("date",""), tags=d.get("tags",[]),
            words=int(d.get("word_count","0") or 0), status=d.get("status",""),
            collection=d.get("collection",""), source_url=d.get("source_url",""),
            source_file=d.get("source_file",""), source_note=d.get("source_note",""),
            body_md=body))
# ---------- author-based grouping into thematic buckets ----------
def author_slug(a): return re.sub(r'[^a-z0-9]+','-',a.lower()).strip('-') or "other"
def sort_key(a):  # alphabetical by FIRST name as displayed
    return a.lower()

EARLY={"Joseph Smith","Brigham Young","John Taylor","Wilford Woodruff","Lorenzo Snow","Parley P. Pratt"}
SCHOLARS={"W. Cleon Skousen","H. Verlan Andersen","Mark Skousen","Arnold K. Garr","Darren Andrews",
 "Henry Grady Weaver","Carson","Laurence M. Vance","Embassy of Heaven","R. Quinn Gardner"}
STATEMENTS={"First Presidency","George Washington","Founding Documents & Compilations",
 "Reference & Resource Hubs","The Church of Jesus Christ of Latter-day Saints"}
BUCKETS=["Modern Prophets & Apostles","Early Church Leaders","Scholars & Commentators","Statements & Founding Documents"]

def group_author(d):
    a=d["author"].strip()
    if a.startswith("First Presidency") or ";" in a: return "First Presidency"  # multi-signer FP statements
    if a: return a
    if d["section"]=="23-topical-and-founding-documents": return "Founding Documents & Compilations"
    if d["section"]=="11-resource-hubs": return "Reference & Resource Hubs"
    if d["section"]=="09-historical-statements": return "First Presidency"
    return "Founding Documents & Compilations"

def bucket_of(a):
    if a in EARLY: return "Early Church Leaders"
    if a in SCHOLARS: return "Scholars & Commentators"
    if a in STATEMENTS: return "Statements & Founding Documents"
    return "Modern Prophets & Apostles"

docs_by_author={}
for d in docs:
    d["gauthor"]=group_author(d)
    docs_by_author.setdefault(d["gauthor"], []).append(d)
for a in docs_by_author:
    docs_by_author[a].sort(key=lambda x:(x["title"].lower()))
# bucket -> ordered authors
bucket_authors={b:[] for b in BUCKETS}
for a in docs_by_author: bucket_authors[bucket_of(a)].append(a)
for b in bucket_authors: bucket_authors[b].sort(key=sort_key)

docs_by_section = {}
for d in docs: docs_by_section.setdefault(d["section"], []).append(d)
ALL_TAGS = sorted({t for d in docs for t in d["tags"]})
N_DOCS=len(docs); N_WORDS=sum(d["words"] for d in docs); N_AUTH=len(docs_by_author)

# ---------- shared chrome ----------
def sidebar_html(root, cur_author=None):
    out=['<nav class="side" id="side"><div class="side-inner">']
    out.append(f'<a class="side-home" href="{root}index.html">Home</a>'
               f'<a class="side-home" href="{root}browse.html">Browse all</a>')
    for b in BUCKETS:
        if not bucket_authors[b]: continue
        out.append(f'<div class="side-group">{esc(b)}</div>')
        for a in bucket_authors[b]:
            items=docs_by_author[a]
            opn=" open" if a==cur_author else ""
            out.append(f'<details class="side-sec"{opn}><summary>{esc(a)}'
                       f'<span class="cnt">{len(items)}</span></summary><ul>')
            for it in items:
                out.append(f'<li><a href="{root}{it["url"]}">{esc(it["title"])}</a></li>')
            out.append('</ul></details>')
    out.append('</div></nav>')
    return "".join(out)

def page(root, title, body, cur_author=None, extra_class=""):
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · To Be Free</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">
<script>window.SITE_ROOT="{root}";</script>
</head><body class="{extra_class}">
<header class="topbar">
  <button class="hamb" id="hamb" aria-label="Menu">☰</button>
  <a class="brand" href="{root}index.html">To&nbsp;Be&nbsp;Free</a>
  <div class="search"><input id="q" type="search" placeholder="Search documents…" autocomplete="off" spellcheck="false">
    <div class="results" id="results"></div></div>
  <nav class="topnav"><a href="{root}browse.html">Browse</a> <a href="{root}about.html">About</a></nav>
</header>
<div class="layout">
{sidebar_html(root, cur_author)}
<main class="main">{body}</main>
</div>
<div class="scrim" id="scrim"></div>
<script src="{root}assets/app.js"></script>
</body></html>"""

# ---------- document pages ----------
def badge(d):
    b=[]
    if d["collection"]=="research-extended": b.append('<span class="badge r">from raw</span>')
    elif d["collection"]=="tbf-book": b.append('<span class="badge b">from book</span>')
    else: b.append('<span class="badge c">core</span>')
    return "".join(b)

for ga, items in docs_by_author.items():
    bkt=bucket_of(ga)
    for i, d in enumerate(items):
        sec=d["section"]
        root="../../"
        d["body_html"]=md2html(d["body_md"])
        meta=[]
        if d["author"]: meta.append(esc(d["author"]))
        if d["date"]: meta.append(esc(fmt_date(d["date"])))
        metaline=" · ".join(meta)
        tags="".join(f'<a class="tag" href="{root}browse.html?q={esc(t)}">{esc(t)}</a>' for t in d["tags"])
        cite=cite_text(d)
        src=f'<span class="cite">{esc(cite)}</span>' if cite else ''
        note=f'<p class="src-note">{esc(d["source_note"])}</p>' if d["source_note"] else ""
        srclink=source_link(d)
        origin=f'<div class="src-orig">{srclink}</div>' if srclink else ''
        rt=reading_time(d["words"])
        toc=build_toc(d["body_html"])
        quotes_cls=" quotes" if (d["title"].lower().startswith("quotes on freedom") or "quotes-on-freedom" in d["slug"]) else ""
        prev=items[i-1] if i>0 else None
        nxt=items[i+1] if i<len(items)-1 else None
        pn='<nav class="prevnext">'
        pn+=(f'<a class="pn prev" href="{root}{prev["url"]}">‹ {esc(prev["title"])}</a>' if prev else '<span></span>')
        pn+=(f'<a class="pn next" href="{root}{nxt["url"]}">{esc(nxt["title"])} ›</a>' if nxt else '<span></span>')
        pn+='</nav>'
        body=f"""
<article class="doc">
  <div class="crumbs"><a href="{root}index.html">Home</a> › {esc(bkt)} › <a href="{root}browse.html#a-{author_slug(ga)}">{esc(ga)}</a></div>
  <header class="doc-head">
    <h1>{esc(d["title"])}</h1>
    <div class="byline">{metaline}</div>
    <div class="tags">{tags}</div>
    <div class="src">{src}{' · ' if src else ''}<span class="wc">{d["words"]:,} words · {rt}</span></div>
    {note}
    {origin}
  </header>
  {toc}
  <div class="prose{quotes_cls}">{d["body_html"]}</div>
  {pn}
</article>"""
        outp=OUT/f"c/{sec}/{d['slug']}.html"
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(page(root, d["title"], body, cur_author=ga, extra_class="reading"), encoding="utf-8")

# ---------- browse page ----------
root="./"
rows=[]
def bucket_slug(b): return re.sub(r'[^a-z0-9]+','-',b.lower()).strip('-')
for b in BUCKETS:
    if not bucket_authors[b]: continue
    rows.append(f'<h2 class="grp" id="{bucket_slug(b)}">{esc(b)}</h2>')
    for a in bucket_authors[b]:
        items=docs_by_author[a]
        rows.append(f'<section class="bsec" id="a-{author_slug(a)}"><h3>{esc(a)} '
                    f'<span class="cnt">{len(items)}</span></h3><ul class="blist">')
        for d in items:
            meta=" · ".join([x for x in [esc(d["author"]), esc(fmt_date(d["date"]))] if x])
            tg=" ".join(d["tags"])
            rows.append(f'<li data-text="{esc((d["title"]+" "+a+" "+tg+" "+b).lower())}">'
                        f'<a href="{d["url"]}">{esc(d["title"])}</a>'
                        f'<span class="bmeta">{meta}</span></li>')
        rows.append('</ul></section>')
browse=f"""
<div class="browse">
  <h1>Browse the collection</h1>
  <p class="lead">{N_DOCS} documents by {N_AUTH} authors. Type to filter by title, author, theme, or tag.</p>
  <input id="filter" class="filter" type="search" placeholder="Filter documents…" autocomplete="off">
  <p class="filter-empty" id="fempty" hidden>No documents match.</p>
  {''.join(rows)}
</div>"""
(OUT/"browse.html").write_text(page(root,"Browse",browse), encoding="utf-8")

# ---------- landing ----------
def bucket_card(b):
    nauth=len(bucket_authors[b]); ndoc=sum(len(docs_by_author[a]) for a in bucket_authors[b])
    return (f'<a class="card" href="browse.html#{bucket_slug(b)}">'
            f'<span class="card-t">{esc(b)}</span>'
            f'<span class="card-n">{nauth} authors · {ndoc} docs</span></a>')
cards="".join(bucket_card(b) for b in BUCKETS if bucket_authors[b])
landing=f"""
<div class="hero">
  <h1>To Be Free</h1>
  <p class="tagline">Latter-day Saint teachings on liberty, agency, and the divine purpose of freedom.</p>
</div>
<div class="intro">
  <p>This is a curated archive of addresses, scriptures, and writings by prophets, apostles,
  and thoughtful Latter-day Saints on <strong>freedom, agency, the Constitution, and religious
  liberty</strong>. It was gathered for a single purpose: to help readers understand and weigh the
  political and social questions of our day against <em>revealed principles</em> rather than the
  shifting opinions of the moment.</p>

  <p>Why does this matter? Because the freedom to choose lies at the very center of the plan of
  salvation, and the conditions that protect that freedom are not accidental. Scripture frames
  liberty as a sacred trust:</p>

  <blockquote>“We believe that no government can exist in peace, except such laws are framed and
  held inviolate as will secure to each individual the free exercise of conscience, the right and
  control of property, and the protection of life.”
  <cite>— Doctrine &amp; Covenants 134:2</cite></blockquote>

  <p>Modern prophets and apostles have taught that defending these freedoms is not a partisan
  errand but a matter of discipleship. President Dallin H. Oaks has reminded the Church of its
  stewardship over the founding charter of liberty:</p>

  <blockquote>“Our belief in divine inspiration gives Latter-day Saints a unique responsibility to
  uphold and defend the United States Constitution and principles of constitutionalism.”
  <cite>— President Dallin H. Oaks, “Defending Our Divinely Inspired Constitution” (2021)</cite></blockquote>

  <p>Religious freedom, in particular, is the soil in which conscience and community grow. Elder
  D. Todd Christofferson described it as the foundation on which a peaceful, pluralistic society
  rests:</p>

  <blockquote>“Religious freedom is the cornerstone of peace in a world with many competing
  philosophies. It gives us all space to determine for ourselves what we think and believe—to
  follow the truth that God speaks to our hearts.”
  <cite>— Elder D. Todd Christofferson, “A Celebration of Religious Freedom” (2015)</cite></blockquote>

  <p>And the prophets have been equally clear that liberty cannot be separated from virtue—that a
  free people remain free only as they remain good. President Ezra Taft Benson, who spent five
  decades teaching on these themes, put it plainly:</p>

  <blockquote>“Their righteousness was the indispensable ingredient to liberty … They would counsel
  us to preserve this liberty by alert righteousness.”
  <cite>— President Ezra Taft Benson</cite></blockquote>

  <p>The documents collected here span nearly two centuries—from Joseph Smith and the early
  First Presidency to the living prophets—and they are presented in a single, consistent format so
  that the collection reads as one continuous conversation about what it means, and what it costs,
  to be free.</p>
</div>

<h2 class="explore">Explore the collection</h2>
<p class="explore-sub">Jump to an author or theme, use <a href="browse.html">Browse all</a> for the full
table of contents, or search from the bar above.</p>
<div class="cards">{cards}</div>
"""
(OUT/"index.html").write_text(page("./","Home",landing), encoding="utf-8")

# ---------- about / sources & methodology ----------
_yrs=sorted(int(d["date"][:4]) for d in docs if d["date"][:4].isdigit())
_ndate=sum(1 for d in docs if d["date"])
_nlink=sum(1 for d in docs if (d.get("source_url") or "").strip())
about=f"""
<div class="hero"><h1>About &amp; Sources</h1>
<p class="tagline">How this collection was built — and how to use it for your own research.</p></div>
<div class="intro about">
<p><em>To Be Free</em> is a curated, searchable collection of Latter-day Saint teaching on liberty,
moral agency, the Constitution, and religious freedom. It gathers <strong>{N_DOCS} documents</strong>
(~{N_WORDS:,} words) from <strong>{N_AUTH} authors</strong>, spanning roughly
<strong>{_yrs[0]}–{_yrs[-1]}</strong>, into one consistent format so the whole reads as a single
continuous conversation about what it means — and what it costs — to be free.</p>

<h2>How it is organized</h2>
<p>Documents are grouped into four thematic collections (Modern Prophets &amp; Apostles, Early Church
Leaders, Scholars &amp; Commentators, and Statements &amp; Founding Documents), then by author. Every
document carries standardized metadata — title, author, date, source, word count, and topical tags —
and you can reach any of it through <a href="browse.html">Browse all</a> or the search bar.</p>

<h2>Sourcing &amp; provenance</h2>
<p>Wherever a document has a known online home, its page links straight to it — look for the
<strong>“Read the original”</strong> button beneath the title. {_nlink} of the {N_DOCS} documents
currently link to an original source, and that coverage is steadily being upgraded toward authoritative
archives — the Church’s <a href="https://www.churchofjesuschrist.org/study/general-conference"
target="_blank" rel="noopener">General Conference archive</a>,
<a href="https://speeches.byu.edu" target="_blank" rel="noopener">BYU Speeches</a>, and the
<a href="https://archive.org" target="_blank" rel="noopener">Internet Archive</a> — rather than
secondary aggregators.</p>

<h2>Dates &amp; accuracy</h2>
<p>{_ndate} of {N_DOCS} documents carry a date, each verified against a source citation rather than a
web-scrape default. A document deliberately left undated — for example a “Quotes on Freedom” page — is
a <em>compilation</em> drawn from many sources across a lifetime; its individual quotations are sourced
line by line instead. Bodies have been cleaned to begin at the author’s first words, with bibliographic
detail moved into the metadata.</p>

<h2>Using this for personal research</h2>
<ul>
<li>Open any document and click <strong>“Read the original”</strong> to go to the source.</li>
<li>On the “Quotes on Freedom” pages, each quotation shows its own citation.</li>
<li>Search by phrase, or browse by author or topical tag.</li>
<li>When citing, cite the <em>original</em> source — treat this site as a finding aid that points you to it.</li>
</ul>

<div class="callout">
<strong>Disclaimer.</strong> This is an independent, non-commercial collection made for personal study,
scholarship, and commentary. It is not affiliated with, endorsed by, or an official publication of The
Church of Jesus Christ of Latter-day Saints; views expressed within the documents are those of their
original authors. Copyright in each work remains with its rights-holder; copyrighted material is offered
under fair-use principles for nonprofit educational purposes — please consult the original source before
reusing a text.</div>

<h2>Corrections</h2>
<p>Spotted a wrong date, a broken link, or a mis-attribution? The project is open source — corrections
are welcome at <a href="https://github.com/voidnologo/to-be-free" target="_blank" rel="noopener">github.com/voidnologo/to-be-free</a>.</p>
</div>
"""
(OUT/"about.html").write_text(page("./","About & Sources",about), encoding="utf-8")

# ---------- search index ----------
index=[dict(t=d["title"], a=d["author"] or d["gauthor"], s=bucket_of(d["gauthor"]),
            g=d["tags"], u=d["url"]) for d in docs]
(OUT/"search-index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

# ---------- assets ----------
ASSETS.mkdir(parents=True, exist_ok=True)
(OUT/".nojekyll").write_text("", encoding="utf-8")
(ASSETS/"style.css").write_text(CSS, encoding="utf-8")
(ASSETS/"app.js").write_text(JS, encoding="utf-8")
print(f"Built {N_DOCS} document pages + index/browse into {OUT}")
print(f"Buckets: {len([b for b in BUCKETS if bucket_authors[b]])} · authors: {N_AUTH} · words: {N_WORDS:,}")
