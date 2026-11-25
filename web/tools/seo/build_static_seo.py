# -*- coding: utf-8 -*-
"""Generate the static SEO content of the app into web/index.html.

The catalogue and the alloy encyclopedia are empty shells in the HTML and are filled by
JavaScript. Search engines that do not execute JS (Bing's first pass, social previews and
AI crawlers such as GPTBot/PerplexityBot) therefore see an app with no aluminium content at
all. This script writes the real tables into the HTML between two markers.

At runtime app.js overwrites both containers (`renderCatalog`, `renderAlloys`), so visitors
never see this copy twice: it exists for crawlers and for the no-script case.

Re-run it whenever web/alloys.json or web/catalog.json changes:
    python -X utf8 tools/seo/build_static_seo.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.abspath(os.path.join(HERE, '..', '..'))
INDEX = os.path.join(WEB, 'index.html')

CATALOG_START = '<!--seo:catalog:start-->'
CATALOG_END = '<!--seo:catalog:end-->'
ALLOY_START = '<!--seo:alloys:start-->'
ALLOY_END = '<!--seo:alloys:end-->'


def esc(value):
    return (str(value if value is not None else '')
            .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def catalog_html(data):
    parts = ['<h2 class="seo-heading">کاتالوگ محصولات آلوم متال</h2>',
             '<p class="seo-lead">جدول‌های زیر آلیاژها، تمپر، ابعاد و ضخامت قابل تأمین را نشان می‌دهند.</p>']
    for sheet in data.get('catalogs', []):
        # A sheet is either one flat table or a list of inner tables (`sections`), e.g. the
        # pipe sheet holds the wall-thickness table and the inner-diameter table.
        sections = sheet.get('sections') or [sheet]
        tables = []
        for section in sections:
            headers = section.get('headers') or []
            rows = section.get('rows') or []
            head = ''.join(f'<th>{esc(h)}</th>' for h in headers)
            body = ''.join(
                '<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in row) + '</tr>'
                for row in rows
            )
            title = section.get('title')
            tables.append(
                (f'<h4 class="seo-subheading">{esc(title)}</h4>' if title and len(sections) > 1 else '')
                + f'<div class="seo-scroll"><table class="seo-table"><thead><tr>{head}</tr></thead>'
                f'<tbody>{body}</tbody></table></div>'
            )
        parts.append(
            f'<section class="seo-sheet"><h3>{esc(sheet.get("name"))}</h3>'
            f'<p>{esc(sheet.get("subtitle"))}</p>'
            f'{"".join(tables)}</section>'
        )
    return ''.join(parts)


def alloys_html(data):
    rows = []
    for alloy in data.get('alloys', []):
        rows.append(
            '<tr>'
            f'<td class="seo-code">{esc(alloy.get("code"))}</td>'
            f'<td>{esc(alloy.get("family"))}</td>'
            f'<td>{esc(alloy.get("title"))}</td>'
            f'<td class="seo-num">{esc(alloy.get("density"))}</td>'
            f'<td>{esc(alloy.get("elements"))}</td>'
            f'<td>{esc(alloy.get("mechanical"))}</td>'
            f'<td>{esc(alloy.get("physical"))}</td>'
            f'<td>{esc(alloy.get("use"))}</td>'
            f'<td>{esc(alloy.get("heatTreatment"))}</td>'
            f'<td>{esc(alloy.get("corrosion"))}</td>'
            f'<td>{esc(alloy.get("standard"))}</td>'
            '</tr>'
        )
    head = ('<th>کد آلیاژ</th><th>خانواده</th><th>ویژگی اصلی</th><th>چگالی (g/cm³)</th>'
            '<th>عناصر اصلی</th><th>خواص مکانیکی</th><th>خواص فیزیکی</th><th>کاربرد رایج</th>'
            '<th>عملیات حرارتی</th><th>مقاومت خوردگی</th><th>استاندارد</th>')
    return (
        '<h2 class="seo-heading">جدول کامل آلیاژهای آلومینیوم</h2>'
        f'<p class="seo-lead">مشخصات فنی {len(rows)} گرید آلومینیوم کارپذیر و ریختگی: '
        'چگالی، ترکیب شیمیایی، خواص مکانیکی، کاربرد، عملیات حرارتی، مقاومت خوردگی و استاندارد.</p>'
        f'<div class="seo-scroll"><table class="seo-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def fill(html, start, end, content):
    pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.S)
    if not pattern.search(html):
        raise SystemExit(f'markers not found: {start} … {end}')
    return pattern.sub(start + content + end, html, count=1)


def main():
    with open(INDEX, encoding='utf-8') as handle:
        html = handle.read()
    with open(os.path.join(WEB, 'catalog.json'), encoding='utf-8') as handle:
        catalog = json.load(handle)
    with open(os.path.join(WEB, 'alloys.json'), encoding='utf-8') as handle:
        alloys = json.load(handle)

    cat = catalog_html(catalog)
    al = alloys_html(alloys)
    html = fill(html, CATALOG_START, CATALOG_END, cat)
    html = fill(html, ALLOY_START, ALLOY_END, al)

    with open(INDEX, 'w', encoding='utf-8', newline='') as handle:
        handle.write(html)
    print(f'catalog block {len(cat)/1024:.1f} KB | alloy block {len(al)/1024:.1f} KB')


if __name__ == '__main__':
    main()
