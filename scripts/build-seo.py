"""Refresh static search metadata from the guide catalog. Run with Python 3."""
from pathlib import Path
from html import escape, unescape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
BASE = 'https://indigenouspodcast.org'
BRAND = 'Indigenous Podcast'
LOGO = BASE + '/assets/indigenous-podcast-logo.webp'

# Descriptions summarize the published lessons; no invented authors or credentials.
CATALOG = [
('Who Is the Creator? Free Bible Study', 'Explore what the Bible says about the Creator, your purpose, and knowing God without giving up your Native identity. Read this free Bible study.', [2, 19]),
('Who Is Jesus? Your Creator and Friend', 'Who is Jesus? Explore His life, death, resurrection, and what He reveals about the Creator in this free Bible study for Native and Indigenous readers.', [1, 6]),
('Who Is the Holy Spirit? Free Bible Study', 'Learn what the Bible says about the Holy Spirit, His guidance, and the Creator’s presence in your life. A free guide with Scripture and reflection.', [2, 23]),
('Can You Trust the Bible? Free Study Guide', 'Explore where the Bible came from, how to understand difficult passages, and questions about its misuse against Native people. Read the free guide.', [1, 19]),
('Why Does Evil Exist? A Bible Study', 'If the Creator is good, why does evil exist? Explore the Bible’s account of Lucifer, human freedom, and God’s response to suffering in this free guide.', [13, 14]),
('Salvation and Grace: What Jesus Does for You', 'What does it mean to be saved? Explore grace, forgiveness, the cross, and why you cannot earn the Creator’s love in this free Bible study guide.', [2, 7]),
('Born Again: A New Heart and a New Beginning', 'Can people really change? Explore what it means to be born again, receive a new heart, and grow with the Creator in this free Bible study guide.', [6, 24]),
('Loving God: Grace and the Ten Commandments', 'Explore the relationship between grace, obedience, and the Ten Commandments. Read a free Bible study about loving the Creator with your whole life.', [9, 20]),
('Loving Your Neighbor: A Bible Study', 'Explore how the Ten Commandments protect relationships, human dignity, family, and community. Read this free guide to loving people the Creator’s way.', [8, 25]),
('Faith or Empty Religion? True Worship', 'What is the difference between loving God and empty religion? Explore Jesus’ response to hypocrisy and His teaching about true worship in this free guide.', [19, 30]),
('The Return of Jesus: Hope for Every Nation', 'Explore the Bible’s promise of Jesus’ return, resurrection, and a family from every nation. Read this free study about hope and reunion with the Creator.', [12, 15]),
('Signs of Jesus’ Return: Watch Without Fear', 'What did Jesus teach about the signs of His return? Explore hope, spiritual deception, and how to watch without fear in this free Bible study guide.', [11, 13]),
('Judgment Day: God’s Justice and Hope', 'Can judgment be good news? Explore God’s justice, the book of life, and the hope offered through Jesus in this free Bible study about judgment day.', [5, 14]),
('When Evil Ends: God’s Justice and Peace', 'Will evil last forever? Explore the Bible’s teaching about final judgment, the end of suffering, and the Creator’s promise of justice and peace.', [13, 15]),
('Heaven and the New Earth: Home at Last', 'Is heaven a real place? Explore the Bible’s promises of resurrection, reunion, and life on the new earth in this free guide from Indigenous Podcast.', [11, 16]),
('What Happens When We Die? Bible Study', 'Explore what the Bible says about death, the soul, resurrection, and the hope of seeing loved ones again. Read this free study at your own pace.', [11, 15]),
('Angels and the Spirit World: Bible Study', 'What does the Bible say about angels and evil spirits? Explore spiritual discernment and the Creator’s authority in this free Bible study guide.', [3, 18]),
('Freedom From Spiritual Bondage in Jesus', 'Explore the Bible’s teaching about spiritual bondage, Jesus’ authority, and finding freedom through Him. Read this free guide from Indigenous Podcast.', [17, 23]),
('Can You Follow Jesus and Still Be Native?', 'Explore Native identity, culture, tradition, and following Jesus. A free Bible guide about belonging to your people while considering spiritual truth.', [4, 10]),
('What Is the Sabbath? The Creator’s Day', 'What is the seventh-day Sabbath? Explore its origins in creation, the fourth commandment, and the Creator’s invitation to rest in this free Bible study.', [21, 22]),
('Sabbath and Sunday: Who Changed the Day?', 'Explore Bible passages about Sabbath and Sunday, church tradition, and the question of who changed the Creator’s day. Read this free study guide.', [20, 22]),
('How to Keep the Sabbath: Rest and Worship', 'Explore Sabbath rest, preparation, worship, community, and acts of care. Read this free Bible guide to celebrating the Creator’s seventh-day Sabbath.', [20, 21]),
('How to Pray and Understand God’s Answers', 'Does the Creator hear your prayers? Explore Jesus’ pattern for prayer, the Holy Spirit’s help, and trusting God’s answers in this free Bible study.', [3, 30]),
('What Is Baptism? Water and the Spirit', 'Explore the meaning of baptism, being born again, and choosing to follow Jesus freely. A Bible study about a new beginning without erasing your identity.', [7, 25]),
('Why Join a Church or Faith Community?', 'Why belong to a faith community after religious harm? Explore biblical fellowship, spiritual gifts, and recognizing a caring congregation in this free guide.', [9, 24]),
('Money, Tithing, and Biblical Stewardship', 'Explore what the Bible says about money, tithes, offerings, generosity, and contentment. Read this free guide to the Creator’s teaching about prosperity.', [8, 30]),
('Addiction, Faith, and Finding Support', 'Read a Christian reflection on addiction, dignity, faith, and seeking support. This free Bible guide discusses freedom and hope without defining Native identity by addiction.', [18, 28]),
('Whole-Person Health: A Bible Study', 'Explore a biblical perspective on caring for body, mind, and spirit, including food, rest, and daily habits. Read this free whole-person health guide.', [22, 27]),
('The Bronze Serpent and Faith in Jesus', 'Why did Moses lift up a bronze serpent? Explore the wilderness story, Jesus’ explanation, and the invitation to trust Him in this free Bible study.', [2, 6]),
('Walking With Jesus Every Day: Bible Study', 'Explore everyday faith, prayer, Scripture, and staying connected to Jesus while honoring your Native identity. The final guide in a free 30-part Bible series.', [19, 23]),
]

def plain(value):
    return unescape(re.sub('<[^>]+>', '', value)).strip()

def marked(name, content):
    return f'<!-- {name}:start -->\n{content}\n<!-- {name}:end -->'

def remove_marked(html, name):
    return re.sub(r'<!-- ' + name + r':start -->.*?<!-- ' + name + r':end -->\s*', '', html, flags=re.S)

def meta(html, title, description, path, graph, index=True, article=False):
    head, body = html.split('</head>', 1)
    head = remove_marked(head, 'seo')
    head = re.sub(r'<title>.*?</title>\s*', '', head, flags=re.S)
    head = re.sub(r'<meta\s+(?:name|property)="(?:description|robots|og:[^"]+|twitter:[^"]+)"[^>]*>\s*', '', head)
    head = re.sub(r'<link\s+rel="canonical"[^>]*>\s*', '', head)
    url = BASE + path
    tags = [f'<title>{escape(title)}</title>',
            f'<meta name="description" content="{escape(description, quote=True)}">',
            f'<meta name="robots" content="{"index, follow, max-image-preview:large" if index else "noindex, follow"}">',
            f'<link rel="canonical" href="{url}">']
    values = {'og:type': 'article' if article else 'website', 'og:site_name': BRAND,
              'og:locale': 'en_US', 'og:title': title, 'og:description': description,
              'og:url': url, 'og:image': LOGO, 'og:image:width': '1000',
              'og:image:height': '1000', 'og:image:alt': 'Indigenous Podcast gold microphone and globe logo',
              'twitter:card': 'summary', 'twitter:title': title, 'twitter:description': description,
              'twitter:image': LOGO, 'twitter:image:alt': 'Indigenous Podcast logo'}
    tags += [f'<meta {"property" if k.startswith("og:") else "name"}="{k}" content="{escape(v, quote=True)}">' for k,v in values.items()]
    if graph:
        tags += ['<script type="application/ld+json">' + json.dumps({'@context':'https://schema.org','@graph':graph}, ensure_ascii=False).replace('<','\\u003c') + '</script>']
    return head.rstrip() + '\n' + marked('seo', '\n'.join(tags)) + '\n</head>' + body

org = {'@type':'Organization','@id':BASE+'/#organization','name':BRAND,'url':BASE+'/',
       'logo':{'@type':'ImageObject','url':LOGO,'width':1000,'height':1000},
       'sameAs':['https://www.youtube.com/@IndigenousTalks']}
website = {'@type':'WebSite','@id':BASE+'/#website','name':BRAND,'url':BASE+'/',
           'inLanguage':'en','publisher':{'@id':BASE+'/#organization'}}
titles = [plain(re.search(r'<h1[^>]*>(.*?)</h1>', (DIST/f'guide{i:02}.html').read_text(encoding='utf-8'), re.S)[1]) for i in range(1,31)]

for i, (topic, description, related) in enumerate(CATALOG, 1):
    path = f'/guide{i:02}'
    file = DIST/(path[1:]+'.html')
    html = file.read_text(encoding='utf-8')
    html = remove_marked(remove_marked(html,'breadcrumbs'),'related-guides')
    breadcrumb = '<nav class="small breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/guides">Bible study guides</a> <span aria-hidden="true">/</span> <span aria-current="page">Guide '+f'{i:02}'+'</span></nav>'
    html = html.replace('<div class="guide-heading">', marked('breadcrumbs', breadcrumb)+'\n<div class="guide-heading">', 1)
    related_html = '<aside class="related-guides" aria-labelledby="related-heading"><h2 id="related-heading">Related Bible studies</h2><ul>' + ''.join(f'<li><a href="/guide{n:02}">{escape(titles[n-1])}</a></li>' for n in related) + '</ul><p class="small">From <a href="/#about-us">Indigenous Podcast</a> · <a href="/guides">Explore all 30 free guides</a></p></aside>'
    html = html.replace('</main>',marked('related-guides',related_html)+'\n</main>',1)
    breadcrumbs = {'@type':'BreadcrumbList','@id':BASE+path+'#breadcrumbs','itemListElement':[
        {'@type':'ListItem','position':1,'name':'Home','item':BASE+'/'},
        {'@type':'ListItem','position':2,'name':'Bible study guides','item':BASE+'/guides'},
        {'@type':'ListItem','position':3,'name':titles[i-1],'item':BASE+path}]}
    page = {'@type':'WebPage','@id':BASE+path+'#webpage','url':BASE+path,'name':titles[i-1],
            'description':description,'inLanguage':'en','isPartOf':{'@id':BASE+'/#website'},
            'breadcrumb':{'@id':BASE+path+'#breadcrumbs'},'mainEntity':{'@id':BASE+path+'#article'}}
    article = {'@type':'Article','@id':BASE+path+'#article','headline':titles[i-1],
               'description':description,'url':BASE+path,'mainEntityOfPage':{'@id':BASE+path+'#webpage'},
               'inLanguage':'en','isAccessibleForFree':True,'publisher':org,
               'isPartOf':{'@type':'CollectionPage','@id':BASE+'/guides#webpage','url':BASE+'/guides'},
               'educationalUse':'Bible study','learningResourceType':'Study guide'}
    file.write_text(meta(html, topic+' | '+BRAND, description, path, [page,article,breadcrumbs],article=True),encoding='utf-8')

file = DIST/'index.html'
html = file.read_text(encoding='utf-8')
html = html.replace('<a href="#get-guides">The Guides</a>','<a href="/guides">Read the Guides</a>')
html = html.replace('Free online Bible guides created with Native readers in mind. Get to know', 'Free online Bible study guides for Native American and Indigenous readers. Get to know')
html = html.replace('href="#get-guides">Take a moment to explore','href="/guides">Browse all 30 free Bible study guides')
questions = [('Who is the Creator, and can I know Him personally?',1),('Who is Jesus, and what did He really teach?',2),('Does God hear my prayers?',23),('Where is God when people suffer?',5),('Can faith bring peace, healing, and purpose?',6),('Can I follow Jesus and remain connected to my people?',19)]
for question, number in questions:
    html = html.replace(f'</span><p>{question}</p></li>',f'</span><p><a href="/guide{number:02}">{question}</a></p></li>')
html = html.replace('<h3 id="form-heading">Send Me My Free Bible Guides</h3>','<h2 id="form-heading">Send Me My Free Bible Guides</h2>')
html = html.replace('alt="Original Indigenous Podcast gold microphone and globe logo" fetchpriority="high"','alt="Original Indigenous Podcast gold microphone and globe logo" loading="lazy" decoding="async"')
html = html.replace('<div class="form-wrapper" aria-label=', '<div class="form-wrapper" data-nosnippet aria-label=')
html = html.replace('<p>Indigenous Podcast</p>\n      <p>©','<p><a href="/guides">Free Bible study guides</a></p>\n      <p>©')
description = 'Explore 30 free Bible study guides for Native American and Indigenous readers. Discover the Creator, Jesus, prayer, and faith while honoring your Native identity.'
page = {'@type':'WebPage','@id':BASE+'/#webpage','url':BASE+'/','name':'Free Bible Study Guides for Native Readers',
        'description':description,'inLanguage':'en','isPartOf':{'@id':BASE+'/#website'},'about':{'@id':BASE+'/#organization'}}
file.write_text(meta(html,'Free Bible Study Guides for Native Readers | '+BRAND,description,'/',[org,website,page]),encoding='utf-8')

file = DIST/'guides.html'
html = file.read_text(encoding='utf-8')
html = html.replace('<h1>A quiet place to explore.</h1>','<h1>30 Free Bible Study Guides</h1>')
html = html.replace('Get to know the Creator through the Bible, one guide at a time. Begin with Guide 01 or choose a topic that matters to you.', 'Explore the Creator, Jesus, prayer, the Sabbath, and everyday faith through Bible study guides created with Native American and Indigenous readers in mind. Begin with Guide 01 or choose a question that matters to you. Read Scripture, reflect, and move at your own pace.')
description = 'Browse 30 free Bible study guides for Native American and Indigenous readers. Explore Jesus, prayer, identity, the Sabbath, and hope. No account needed to read.'
items = {'@type':'ItemList','@id':BASE+'/guides#list','numberOfItems':30,'itemListElement':[
    {'@type':'ListItem','position':i,'name':title,'url':BASE+f'/guide{i:02}'} for i,title in enumerate(titles,1)]}
page = {'@type':'CollectionPage','@id':BASE+'/guides#webpage','url':BASE+'/guides','name':'30 Free Bible Study Guides',
        'description':description,'inLanguage':'en','isPartOf':{'@id':BASE+'/#website'},'mainEntity':items,'publisher':org}
file.write_text(meta(html,'30 Free Bible Study Guides | '+BRAND,description,'/guides',[page]),encoding='utf-8')

file = DIST/'welcome.html'
html = file.read_text(encoding='utf-8')
file.write_text(meta(html,'Welcome — Your Bible Guides Are Ready | '+BRAND,
    'Your free Bible guides are ready. Start your first guide, return to a lesson, or explore Indigenous Podcast conversations on YouTube.', '/welcome',[],index=False),encoding='utf-8')

# The welcome page is a signup destination, and the 404 page is an error response.
urls = ['/','/guides'] + [f'/guide{i:02}' for i in range(1,31)]
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{BASE}{path}</loc></url>\n' for path in urls) + '</urlset>\n',encoding='utf-8')
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n',encoding='utf-8')
print('Updated metadata for 33 pages and sitemap for 32 indexable URLs.')
