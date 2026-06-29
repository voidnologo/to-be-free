#!/usr/bin/env python3
"""QA pass: detect/strip residual header lines (title/author/role/date/citation) at the
start of article bodies so each starts at the real first sentence."""
import re, sys
from pathlib import Path
SRC=Path("/home/void/Documents/TBF/sources")
WRITE="--write" in sys.argv

PUBS=r'(ensign|new era|improvement era|conference report|liahona|deseret news|church news|gospel ideals|the era|millennial star)'
VENUE=r'(university|fireside|devotional|conference|commencement|institute|forum|symposium|temple|byu|seminary|tabernacle|law society|celebration|summit|lecture|gala|rotunda|marriott center|patriotic service|graduation|address delivered)'
WEEKDAY=r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
ROLE=re.compile(r'^(of the (quorum|council|first presidency|presiding|seventy)|of the twelve|(former )?(president|secretary|governor) of|quorum of the)',re.I)
HONOR=re.compile(r'^(elder|president|bishop|sister|brother|the honorable|by|dr\.|professor)\s+[A-Z]',re.I)
PROV=re.compile(r'^(speaking today|from a talk|from an address|delivered|address given|given at|an address|reprinted|adapted from|excerpt|transcript|this (address|talk|article)|remarks|originally|a (devotional|fireside|forum)|the following|copyright|©)',re.I)
MONTH=r'(january|february|march|april|may|june|july|august|september|october|november|december)'
DATELINE=re.compile(rf'^\s*({WEEKDAY},?\s+)?((\d{{1,2}}\s+)?{MONTH}\.?\s+(\d{{1,2}},?\s+)?(18|19|20)\d\d|{MONTH}\s+(18|19|20)\d\d|(18|19|20)\d\d)\s*$',re.I)

def get(t,k):
    m=re.search(rf'^{k}: "(.*?)"',t,re.M); return m.group(1) if m else ""

PLACE=re.compile(r',\s*(utah|california|idaho|arizona|virginia|massachusetts|new york|texas|washington|d\.?c\.?|ohio|illinois|new jersey|pennsylvania|oregon|colorado|england|provo|ogden|salt lake)\b',re.I)
COUNSEL=re.compile(r'(first|second|third)?\s*counselor in the first presidency|presiding (bishop|patriarch)',re.I)
def residual_kind(s, title, author):
    core=s.strip().lstrip('#').strip().strip('*').strip().strip('“”"').strip()
    if not core: return None
    sl=core.lower()
    if len(core)>140: return None                       # long line = real content
    tl=title.lower().strip()
    # title or a fragment of it (handles titles split across lines / ALL-CAPS)
    if tl:
        tlc=re.sub(r'[^a-z0-9 ]',' ',tl); slc=re.sub(r'[^a-z0-9 ]',' ',sl)
        slc=re.sub(r'\s+',' ',slc).strip()
        if slc and (slc==tlc or slc in tlc or (len(slc)>=10 and tlc in slc)): return "title"
    al=author.lower().strip()
    if al and (sl==al or (al in sl and len(core)<70)): return "author"
    if HONOR.match(core): return "author"
    if ROLE.match(sl) or COUNSEL.search(sl): return "role"
    if DATELINE.match(core): return "date"
    if PROV.match(sl): return "prov"
    if re.match(r'^chapter\s+\d', sl): return "chapter"
    surname=al.split()[-1] if al else ""
    if re.search(PUBS,sl) and ((surname and surname in sl) or re.search(r'\b(18|19|20)\d\d\b',core)): return "cite"
    if re.search(VENUE,sl) and len(core)<80: return "venue"
    if PLACE.search(core) and len(core)<70: return "place"
    if re.fullmatch(r"[A-Z][A-Z0-9 .,'\-]{1,48}", core): return "allcaps"   # THE TEN COMMANDMENTS / AND
    return None

flagged=[]; changed=0; still=[]
for p in sorted(SRC.glob("*/*.md")):
    t=p.read_text(encoding="utf-8")
    m=re.match(r"(---\n.*?\n---\n)(.*)",t,re.S)
    if not m: continue
    fm,body=m.group(1),m.group(2)
    title,author=get(fm,"title"),get(fm,"author")
    lines=body.split("\n")
    def strippable(s):
        core=s.strip().lstrip('#').strip().strip('*').strip().replace('\xa0',' ').strip()
        if not core: return ("blank",core)
        k=residual_kind(s,title,author)
        if k: return (k,core)
        return None
    out=[]; started=False; removed=[]; consumed=0
    for ln in lines:
        if started: out.append(ln); continue
        s=ln.strip()
        if s=="":
            continue   # drop leading blanks
        st = strippable(s) if consumed<12 else None
        if st:
            if st[0]!="blank": removed.append(st); consumed+=1
            continue
        started=True; out.append(ln)
    newbody="\n".join(out).lstrip("\n")
    newbody=re.sub(r'^---\s*\n+','',newbody)
    # second: stray citation/date in first 5 lines
    cl=newbody.split("\n")
    for j in range(min(5,len(cl))):
        s=cl[j].strip()
        if s and (re.search(PUBS,s.lower()) and re.search(r'\b(18|19|20)\d\d\b',s) and len(s)<170) or (s and DATELINE.match(s)):
            removed.append(("stray",s)); del cl[j]; newbody="\n".join(cl).lstrip("\n"); break
    if removed:
        flagged.append((f"{p.parent.name}/{p.name}", removed, newbody[:90]))
        if len(newbody.split())>=40:   # safety
            if WRITE: p.write_text(fm+"\n"+newbody+"\n",encoding="utf-8")
            changed+=1
        else:
            still.append(f"{p.parent.name}/{p.name} (would leave too little)")
    # after potential strip, re-check the new opening for lingering suspicion
    first=next((x for x in newbody.split("\n") if x.strip()),"")
    if residual_kind(first,title,author):
        still.append(f"{p.parent.name}/{p.name}: {first[:70]!r}")

print(f"{'WROTE' if WRITE else 'DRY'} — docs with residual header lines: {len(flagged)} (changed {changed})")
print(f"still-suspicious after pass: {len(still)}\n")
for f,rem,head in flagged[:40]:
    print(f"  {f}\n     removed {[k for k,_ in rem]}: {rem[0][1][:60]!r}\n     now: {head!r}")
if still:
    print("\n--- STILL SUSPICIOUS (manual review) ---")
    for s in still[:30]: print("  ",s)
