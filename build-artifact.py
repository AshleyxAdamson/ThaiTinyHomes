#!/usr/bin/env python3
"""Flatten the prototype into one HTML fragment with inlined CSS/JS and data-URI assets, for the Artifact viewer.
Usage: python3 build-artifact.py OUT.html
"""
import re, sys, base64, mimetypes, os
out = sys.argv[1]
html = open('index.html', encoding='utf-8').read()
css = open('styles.css', encoding='utf-8').read()
js = open('main.js', encoding='utf-8').read()

body = re.search(r'<body[^>]*>(.*)</body>', html, re.S).group(1)
m = re.search(r'<link href="https://fonts.googleapis.com[^>]*>', html); fonts = m.group(0) if m else ''
title = re.search(r'<title>(.*?)</title>', html).group(1)

def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()

# drop srcset/sizes so each image is embedded once, then inline every asset path
body = re.sub(r'\s(srcset|sizes)="[^"]*"', '', body)
def repl(m):
    attr, path = m.group(1), m.group(2)
    return f'{attr}="{data_uri(path)}"'
body = re.sub(r'\b(src|poster|data-src)="(assets/[^"]+)"', repl, body)
body = body.replace('<script src="main.js" defer></script>', '<script>\n' + js + '\n</script>')

css = re.sub(r'url\("(assets/[^"]+)"\)', lambda m: 'url("' + data_uri(m.group(1)) + '")', css)
page = f'<title>{title}</title>\n{fonts}\n<style>\n{css}\n</style>\n{body}'
open(out, 'w', encoding='utf-8').write(page)
print(out, round(os.path.getsize(out) / 1e6, 2), 'MB')
