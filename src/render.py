"""일간 뉴스레터 HTML과 아카이브 index를 GitHub Pages 폴더에 생성한다."""
from __future__ import annotations

import html
import os

import config
from src.models import Article

_CSS = """
:root{--bg:#f7f8f6;--card:#fff;--ink:#1f2a24;--sub:#5c6b63;
--accent:#2f7d5b;--line:#e4e8e5;--link:#1a6b47}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo",
"Malgun Gothic",sans-serif;line-height:1.65}
.wrap{max-width:720px;margin:0 auto;padding:24px 18px 64px}
header.top{padding:14px 0 8px;border-bottom:2px solid var(--accent);margin-bottom:22px}
.brand{font-size:1.55rem;font-weight:800;color:var(--accent);letter-spacing:-.5px}
.date{color:var(--sub);font-size:.92rem;margin-top:2px}
.intro{background:#eef5f0;border-radius:12px;padding:14px 16px;margin-bottom:22px;
font-size:.95rem;color:#2c4a3b}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:20px 20px 16px;margin-bottom:18px}
.tag{display:inline-block;font-size:.72rem;font-weight:700;padding:2px 9px;
border-radius:999px;margin-bottom:9px}
.tag.dom{background:#e5f0ff;color:#1c5bbd}
.tag.glob{background:#fff0e6;color:#c05a12}
h2.head{font-size:1.18rem;margin:2px 0 6px;line-height:1.4}
h2.head a{color:var(--ink);text-decoration:none}
h2.head a:hover{text-decoration:underline}
.src{color:var(--sub);font-size:.82rem;margin-bottom:12px}
ul.sum{margin:8px 0 12px;padding-left:19px}
ul.sum li{margin-bottom:5px}
.why{background:#f3f7f4;border-left:3px solid var(--accent);padding:8px 12px;
border-radius:6px;font-size:.92rem;margin:10px 0}
.cont{background:#fff8e6;border-left:3px solid #e0a516;padding:8px 12px;
border-radius:6px;font-size:.9rem;margin:10px 0;color:#6b520a}
.links{margin-top:12px;border-top:1px dashed var(--line);padding-top:10px}
.links a{display:inline-block;font-size:.85rem;color:var(--link);
text-decoration:none;margin:3px 10px 3px 0}
.links a:hover{text-decoration:underline}
.orig{font-size:.85rem}.orig a{color:var(--link)}
footer{color:var(--sub);font-size:.82rem;text-align:center;margin-top:34px}
.archive-list{list-style:none;padding:0}
.archive-list li{padding:10px 0;border-bottom:1px solid var(--line)}
.archive-list a{color:var(--ink);text-decoration:none;font-weight:600}
.archive-list a:hover{color:var(--accent)}
.archive-list .meta{color:var(--sub);font-size:.85rem}
.special-term{font-size:1.9rem;font-weight:800;color:var(--accent);margin:6px 0}
"""


def _e(s: str) -> str:
    return html.escape(s or "")


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(title)}</title><style>{_CSS}</style></head>
<body><div class="wrap">{body}</div></body></html>"""


def _article_card(a: Article) -> str:
    tag_cls = "dom" if a.region == "domestic" else "glob"
    tag_txt = "국내" if a.region == "domestic" else "해외"
    sums = "".join(f"<li>{_e(s)}</li>" for s in a.summary)
    cont = f'<div class="cont">🔗 {_e(a.continuity)}</div>' if a.continuity else ""
    why = f'<div class="why">💡 {_e(a.why_important)}</div>' if a.why_important else ""
    extra = "".join(
        f'<a href="{_e(l["url"])}" target="_blank" rel="noopener">{_e(l["label"])}</a>'
        for l in a.extra_links
    )
    extra_block = f'<div class="links">{extra}</div>' if extra else ""
    return f"""<article class="card">
  <span class="tag {tag_cls}">{tag_txt}</span>
  <h2 class="head"><a href="{_e(a.url)}" target="_blank" rel="noopener">{_e(a.headline_ko or a.title)}</a></h2>
  <div class="src">{_e(a.source)}</div>
  <ul class="sum">{sums}</ul>
  {why}
  {cont}
  <div class="orig">📰 <a href="{_e(a.url)}" target="_blank" rel="noopener">원문 기사 보기</a></div>
  {extra_block}
</article>"""


def render_daily(day: str, intro: str, articles: list[Article]) -> str:
    cards = "".join(_article_card(a) for a in articles)
    body = f"""<header class="top">
  <div class="brand">🌱 {_e(config.NEWSLETTER_TITLE)}</div>
  <div class="date">{_e(day)} · 오늘의 ESG 뉴스 {len(articles)}건</div>
</header>
<div class="intro">{_e(intro)}</div>
{cards}
<footer>이 뉴스레터는 매 평일 아침 자동 생성됩니다 · <a href="index.html">지난 호 보기</a></footer>"""
    path = os.path.join(config.DOCS_DIR, f"{day}.html")
    _write(path, _page(f"{config.NEWSLETTER_TITLE} {day}", body))
    return path


def render_special(day: str, special: dict) -> str:
    related = "".join(
        f'<a href="https://ko.wikipedia.org/w/index.php?search={_e(t)}" '
        f'target="_blank" rel="noopener">📖 {_e(t)}</a>'
        for t in special.get("related_terms", [])
    )
    related_block = f'<div class="links">{related}</div>' if related else ""
    body = f"""<header class="top">
  <div class="brand">🌱 {_e(config.NEWSLETTER_TITLE)}</div>
  <div class="date">{_e(day)} · ESG 용어 특별편</div>
</header>
<div class="intro">오늘은 주요 뉴스가 조용해, ESG 용어 하나를 정리해 드립니다. 📚</div>
<article class="card">
  <span class="tag glob">용어 특별편</span>
  <div class="special-term">{_e(special.get("term",""))}</div>
  <div class="why">💡 {_e(special.get("one_liner",""))}</div>
  <p>{_e(special.get("definition",""))}</p>
  <div class="cont">왜 중요할까? {_e(special.get("why_matters",""))}</div>
  <p><b>예시</b> — {_e(special.get("example",""))}</p>
  {related_block}
</article>
<footer>이 뉴스레터는 매 평일 아침 자동 생성됩니다 · <a href="index.html">지난 호 보기</a></footer>"""
    path = os.path.join(config.DOCS_DIR, f"{day}.html")
    _write(path, _page(f"{config.NEWSLETTER_TITLE} {day} 특별편", body))
    return path


def render_index(archive_data: dict) -> None:
    items = []
    for ed in sorted(archive_data.get("editions", []),
                     key=lambda e: e.get("date", ""), reverse=True):
        day = ed.get("date", "")
        if ed.get("type") == "special":
            label = f'용어 특별편 — {ed.get("term","")}'
        else:
            titles = [a.get("title", "") for a in ed.get("articles", [])]
            label = titles[0] + (f" 외 {len(titles)-1}건" if len(titles) > 1 else "")
        items.append(
            f'<li><a href="{_e(day)}.html">{_e(label)}</a>'
            f'<div class="meta">{_e(day)}</div></li>'
        )
    body = f"""<header class="top">
  <div class="brand">🌱 {_e(config.NEWSLETTER_TITLE)}</div>
  <div class="date">지난 호 아카이브</div>
</header>
<ul class="archive-list">{''.join(items) or '<li>아직 발행된 호가 없습니다.</li>'}</ul>
<footer>매 평일 아침 자동 발행</footer>"""
    _write(os.path.join(config.DOCS_DIR, "index.html"),
           _page(f"{config.NEWSLETTER_TITLE} 아카이브", body))


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
