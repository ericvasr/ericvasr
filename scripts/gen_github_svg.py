#!/usr/bin/env python3
"""Gera cards SVG do perfil a partir de valores REAIS da API do GitHub.
Sem dependência externa (urllib). Roda local (GH_TOKEN=$(gh auth token)) ou no CI (GITHUB_TOKEN).
Saída: assets/stats.svg e assets/langs.svg — assets do próprio repo, imunes a 503 de terceiro.
"""
import json, os, sys, urllib.request, collections, pathlib, html

USER = os.environ.get("GH_USER", "ericvasr")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    sys.exit("faltou GH_TOKEN/GITHUB_TOKEN")

QUERY = """
query($login:String!){
  user(login:$login){
    followers{totalCount} following{totalCount}
    contributionsCollection{ totalCommitContributions restrictedContributionsCount
      totalPullRequestContributions totalIssueContributions }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{ stargazerCount
        languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name color } } } }
    }
  }
}"""

def gql():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json",
                 "User-Agent": USER})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["user"]

def fmt(n):
    return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)

# --- paleta (casada com o README) ---
BG="#0d1117"; CARD="#0d1117"; BORDER="#30363d"; ACCENT="#58a6ff"; HI="#e6edf3"; MID="#8b949e"
FONT="'Segoe UI',Ubuntu,'Helvetica Neue',sans-serif"
CARD_W, CARD_H = 480, 200   # dimensões idênticas nos dois cards → alinham lado a lado no README

def card(w,h,inner,title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{CARD}" stroke="{BORDER}"/>
<text x="26" y="34" font-family="{FONT}" font-size="16" font-weight="600" fill="{ACCENT}">{title}</text>
{inner}
</svg>'''

def stats_svg(u):
    cc=u["contributionsCollection"]
    repos=u["repositories"]
    stars=sum(r["stargazerCount"] for r in repos["nodes"])
    tiles=[
        ("Commits (1 ano)", cc["totalCommitContributions"]),
        ("Pull Requests", cc["totalPullRequestContributions"]),
        ("Issues", cc["totalIssueContributions"]),
        ("Repositórios", repos["totalCount"]),
        ("Seguidores", u["followers"]["totalCount"]),
        ("Stars", stars),
    ]
    w,h=CARD_W,CARD_H; cols=3; cw=(w-52)/cols; y0=76; rh=62; inner=""
    for i,(lab,val) in enumerate(tiles):
        cx=26+(i%cols)*cw; cy=y0+(i//cols)*rh
        inner+=(f'<text x="{cx:.0f}" y="{cy:.0f}" font-family="{FONT}" font-size="26" font-weight="700" fill="{HI}">{fmt(val)}</text>'
                f'<text x="{cx:.0f}" y="{cy+18:.0f}" font-family="{FONT}" font-size="11" fill="{MID}">{html.escape(lab)}</text>')
    return card(w,h,inner,"GitHub · números reais")

def langs_svg(u):
    langs=collections.Counter(); colors={}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]]+=e["size"]; colors[e["node"]["name"]]=e["node"]["color"] or MID
    top=langs.most_common(6); tot=sum(v for _,v in top) or 1
    w,h=CARD_W,CARD_H; bx,by,bw,bh=26,60,w-52,16; inner=""; x=bx
    for n,v in top:
        seg=bw*v/tot
        inner+=f'<rect x="{x:.1f}" y="{by}" width="{seg:.1f}" height="{bh}" fill="{colors[n]}"/>'
        x+=seg
    inner=f'<clipPath id="r"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6"/></clipPath><g clip-path="url(#r)">'+inner+'</g>'
    ly=104
    for i,(n,v) in enumerate(top):
        cx=26+(i%2)*((w-52)/2); cy=ly+(i//2)*28
        pct=100*v/tot
        inner+=(f'<circle cx="{cx+6:.0f}" cy="{cy-4:.0f}" r="6" fill="{colors[n]}"/>'
                f'<text x="{cx+20:.0f}" y="{cy:.0f}" font-family="{FONT}" font-size="13" fill="{HI}">{html.escape(n)}</text>'
                f'<text x="{cx+((w-52)/2)-16:.0f}" y="{cy:.0f}" font-family="{FONT}" font-size="12" fill="{MID}" text-anchor="end">{pct:.1f}%</text>')
    return card(w,h,inner,"Linguagens mais usadas")

def main():
    u=gql()
    out=pathlib.Path(__file__).resolve().parent.parent/"assets"; out.mkdir(exist_ok=True)
    (out/"stats.svg").write_text(stats_svg(u),encoding="utf-8")
    (out/"langs.svg").write_text(langs_svg(u),encoding="utf-8")
    print("gerado: assets/stats.svg, assets/langs.svg")

if __name__=="__main__":
    main()
