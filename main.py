import datetime
import re

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Template
import pywikibot


def getvalue(t: Template, p: str):
    try:
        return t.get(p).value.strip()
    except ValueError:
        return ''


def format_date(date: str) -> str:
    match1 = re.match(r'\d{4}年\d\d?月\d\d?日', date)
    match2 = re.match(r'\d{4}/\d\d?/\d\d?', date)
    match3 = re.match(r'\d{4}-\d\d?-\d\d?', date)

    if match1:
        dt = datetime.datetime.strptime(date, '%Y年%m月%d日')
    elif match2:
        dt = datetime.datetime.strptime(date, '%Y/%m/%d')
    elif match3:
        dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    elif not date:
        return None
    else:
        dt = datetime.datetime.strptime(input(date), '%Y-%m-%d')

    return f'{dt.year}年{dt.month}月{dt.day}日'


def from_citeweb(wikicode: Wikicode) -> Wikicode:
    count = 0
    for t in wikicode.filter_templates():
        if t.name == 'Cite web' and not t.has(format) and not t.has('author'):
            title = getvalue(t, 'title')
            url = getvalue(t, 'url')
            date = format_date(getvalue(t, 'date'))
            website = getvalue(t, 'website')
            publisher = getvalue(t, 'publisher')
            last = getvalue(t, 'last')
            accessdate = format_date(getvalue(t, 'accessdate')) if getvalue(t, 'accessdate') else format_date(getvalue(t, 'access-date'))

            if (title, url, accessdate):
                new = f'“[{url} {title}]”'

                publisher = '日本放送協会' if not publisher and last == '日本放送協会' else publisher

                if publisher and website:
                    new += f'. \'\'{website}\'\'. {publisher} ({date}). ' if date else f'. \'\'{website}\'\'. {publisher}. '
                elif publisher and not website:
                    new += f'. {publisher} ({date}). ' if date else f'. {publisher}. '
                elif not publisher and website:
                    new += f'. \'\'{website}\'\' ({date}). ' if date else f'. \'\'{website}\'\'. '
                else:
                    new += f' ({date}) .' if date else f'. '
                new += f'{accessdate}閲覧。'

                wikicode.replace(t, new)
                count += 1

    pywikibot.output(f'{{{{Cite web}}}} を {count} 回置換しました')
    return wikicode


def main():
    title = pywikibot.input('元の記事名を入力: ')
    site = pywikibot.Site()
    page = pywikibot.Page(site, title)

    output_file = pywikibot.input('出力先ファイル名を入力', default='new.txt')

    if page.exists():
        wikicode = mwparserfromhell.parse(page.text)
        wikicode = from_citeweb(wikicode)

        with open(output_file, mode='w', encoding='utf_8') as f:
            f.write(str(wikicode))

        pywikibot.output('処理完了')
        pywikibot.output(f'{output_file} に出力しました')

    else:
        pywikibot.output(f'{page.title(as_link=True)} は存在しません')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Ctrl+C が押されました')
        input('Enter で終了')
