"""Wrap app.html (page content only, as the claude.ai artifact host expects) into index.html for GitHub Pages.

    python -I redesign/site/make_index.py

app.html carries <title>, <meta>, <link>, <style> and <script> tags plus markup, but no <!doctype>, <html>, <head>
or <body>. This script moves the <title> and <meta> tags into a proper <head> and leaves everything else in <body>.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, 'app.html'), encoding='utf-8') as f:
    app = f.read()

head = []
def take(pattern):
    global app
    m = re.search(pattern, app)
    while m:
        head.append(m.group(0)); app = app[:m.start()] + app[m.end():]
        m = re.search(pattern, app)
take(r'<title>.*?</title>\n?')
take(r'<meta name="[^"]*"[^>]*>\n?')

doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       + ''.join(h if h.endswith('\n') else h + '\n' for h in head)
       + '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\'%3E%3Cpath d=\'M2 13l9-2 2-8h2l-1 8 8 2v2l-8 1-1 5h-2l-1-5-8-1z\' fill=\'%231F5FC7\'/%3E%3C/svg%3E">\n'
       '</head>\n<body>\n' + app.lstrip('\n') + '\n</body>\n</html>\n')
with open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(doc)
print('index.html: %d bytes, head tags: %d' % (len(doc), len(head)))
