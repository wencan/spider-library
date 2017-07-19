#!/usr/bin/env python3
# coding: utf-8

import requests
import lxml
import lxml.html
import urllib.parse

home = "http://www.readers365.com/kehuan/"
encoding = "GB18030"


def get(url, encoding='utf-8'):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4"
    })

    print("GET:", url)
    r = session.get(url, allow_redirects=True)
    if r.status_code == 200:
        pass
    elif r.status_code == 404:
        raise LookupError("not found %s" % url)
    else:
        raise IOError('request "%s" got status: %d' % (url, r.status_code))
    return r.content.decode(encoding)


# home
def get_books(home_url, encoding='utf-8'):
    text = get(home_url, encoding)
    doc = lxml.html.fromstring(text)

    body = doc.xpath("/html/body")[0]
    table = body.xpath("//table[@id='table2']")[0]

    links = table.xpath("//tr/td/a/@href")
    links = list(map(lambda l: l.split("=")[0] if "=" in l else l, links))
    links = list(map(lambda l: urllib.parse.urljoin(home_url, l), links))
    imgs = table.xpath("//tr/td/a/img/@src")
    imgs = list(map(lambda i: urllib.parse.urljoin(home_url, i), imgs))
    titles = table.xpath("//tr/td/font")
    titles = list(map(lambda t: t.text, titles))

    books = list(map(lambda idx: (titles[idx], links[idx], imgs[idx]), range(len(titles))))
    return books


# chapter
def get_chapters(book_url, encoding='utf-8'):
    text = get(book_url, encoding)
    doc = lxml.html.fromstring(text)

    body = doc.xpath("/html/body")[0]
    lines = body.xpath("//div[@class=\"content\"]/*")

    chapters = []
    for line in lines:
        title = None
        href = None
        header = False

        if line.tag == "a":
            title = line.text
            href = urllib.parse.urljoin(book_url, line.attrib["href"])
            if not title:
                fonts = line.xpath("font")
                if fonts:
                    title = fonts[0].text
                    if fonts[0].tail:
                        title = "{} {}".format(title, fonts[0].tail)
                    header = True
            if not title:
                continue
        elif line.tag == "font":
            title = line.text
            header = True
            if not title:
                continue
        else:
            continue

        title = title.rstrip()
        title = title.lstrip()
        title = title.replace("\u3000", "", -1)
        chapters.append((title, href, header),)
    return chapters


def get_content(chapter_url, encoding="utf-8"):
    text = get(chapter_url, encoding)
    doc = lxml.html.fromstring(text)

    try:
        body = doc.xpath("/html/body")[0]
        lines = body.xpath("//font[@face=\"宋体\" and @size=\"3\"]/*")

        context = []
        for line in lines:
            if not line.tail:
                continue
            context.append(line.tail)

        return context
    except IndexError:
        print(text)
        raise

books = get_books(home, encoding)
for book in books[80:]:
    chapters = get_chapters(book[1], encoding)
    for chapter in chapters:
        if not chapter[1]:
            continue
        lines = get_content(chapter[1], encoding)
        for line in lines:
            print(line)
