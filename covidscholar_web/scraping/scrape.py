from bs4 import BeautifulSoup
import requests
import re
import datefinder
import pickle


def parseAbstract(abstract, sessionCode):
    timeRE = re.compile('[0-9]{1,2}:[0-9]{1,2} [A,P]M')
    sessionRE = re.compile('%s\.[0-9]{1,2}\.[0-9]{1,2}' % (sessionCode))

    parsedAbstract = dict()
    parsedAbstract['sessionCode'] = sessionCode
    for i, tag in enumerate(abstract.children):
        if i == 0:
            time = timeRE.findall(tag.get_text())[0]
            parsedAbstract['time'] = time
            try:
                session = sessionRE.findall(tag.get_text())[0]
                parsedAbstract['session'] = session
            except:
                return None
        elif i == 1:
            title = tag.get_text()
            parsedAbstract['title'] = title
        elif i == 3:
            for j, t in enumerate(tag.children):
                if j == 0:
                    authors = re.sub('[0-9]', '', t.get_text())
                    parsedAbstract['authors'] = authors
                if j == 2:
                    affiliations = re.sub('[0-9]', '', t.get_text())
                    parsedAbstract['affiliations'] = affiliations
                if j == 5:
                    abstract = t.get_text()
                    parsedAbstract['abstract'] = abstract
    return parsedAbstract


prefixes = ['BI', 'EL', 'EN', 'FF', 'MQ', 'MT', 'MS', 'SB']
abstracts = []
sessionStrings = []
for prefix in prefixes:
    for i in ["%02d" % i for i in range(20)]:
        sessionCode = "%s%s" % (prefix, i)
        url = "https://www.mrs.org/fall2019/symposium-sessions/symposium-sessions-detail?code=%s" % (
            sessionCode)
        html = requests.get(url).content

        soup = BeautifulSoup(html, 'html.parser')

        sessionName = ''
        for e in soup.find_all('html'):
            for tag in e.find_all('div'):
                try:
                    tag["class"]
                    if tag["class"] == ["abstract"]:
                        parsed = parseAbstract(tag, sessionCode)
                        if parsed is not None:
                            abstracts.append(parsed)
                    else:
                        for j, s in enumerate(re.compile(
                                '%s\.[0-9]{1,2}:.*\n' % (sessionCode)).findall(tag.get_text())):
                            sessionStrings.append(s[:250])
                            for j, s in enumerate(re.compile(
                                    '%s\.[0-9]{1,2}\/[A-Z]{2}[0-9]{2}\.[0-9]{1,2}.*\n' % (sessionCode)).findall(tag.get_text())):
                                sessionStrings.append(s[:250])
                except (KeyError, TypeError):
                    pass

pickle.dump(abstracts, open('abstractdict.pkl', 'wb'))
with open("sessionStrings.xt", 'w') as f:
    for l in sessionStrings:
        f.write(l + "\n")
