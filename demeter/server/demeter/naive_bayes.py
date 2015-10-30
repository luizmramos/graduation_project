import re
import unicodedata

def parseInTextTokens(text):
    text = re.sub('((https?://(www\.)?)|(www\.))[^\s]+', '{link}', text)
    text = re.sub('(^|\s)#[^\s]+', ' {hashtag}', text)
    text = re.sub('(^|\s)@[^\s]+', ' {tag}', text)
    text = re.sub('\d+([\.,]\d+)?', '{number}', text)
    text = re.sub('({number}/{number}(/{number})?)|({number}-{number}(-{number})?)', '{date}', text)
    text = re.sub('{number}\%', '{percentage}', text)
    text = re.sub('(r|(us?))?\${number}', '{money}', text)
    return text

def removeUnicodeCharacters(text):
    unicode = text.decode('utf-8')
    unicode = unicodedata.normalize('NFD', unicode)
    ascii = unicode.encode('ascii', 'ignore') # ignore or substitute by {unicode}
    ascii = ascii.lower()
    return ascii

def removeDoubleLetters(text):
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        text = re.sub(letter + '+', letter, text)
    return text

def removeNonLetters(text):
    text = re.sub("\s+", " ", text)
    text = re.sub("[^\w\s{}]", " ", text)
    return text

spaces = re.compile(r'[\s\n]')

def splitText(text):
    return filter(lambda l: l!='', spaces.split(text))

def parseLaughter(word):
    countH = 0
    countA = 0
    countS = 0
    countU = 0
    for l in word:
        if l == 'a':
            countA = countA + 1
        if l == 'h':
            countH = countH + 1
        if l == 's':
            countS = countS + 1
        if l == 'u':
            countU = countU + 1

    laughter = '{laughter}'

    length = len(word)
    if countH + countS + countU + countA == length and countH > 1 and countS > 1:
        return laughter
    if countH + countA == length and countA + countH > 4 and countH > 1:
        return laughter
    if all([l == 'r' or l == 's' for l in word]) or all ([l == 'k' for l in word]):
        return laughter

    return word


acronyms = {
    'aew': 'ai',
    'aki': 'aqui',
    'blz': 'beleza',
    'bjo': 'beijo' ,
    'brinks': 'brincadeira',
    'cmg': 'comigo',
    'ctg': 'contigo',
    'd': 'de',
    'd+': 'demais',
    'eh': 'e',
    'gnt': 'gente',
    'hj': 'hoje',
    'n': 'nao',
    'neh': 'ne',
    'ngm': 'ninguem',
    'p': 'para',
    'q': 'que',
    'qnd': 'quando',
    'qndo': 'quando',
    'qq': 'qualquer',
    'soh': 'so',
    'tb': 'tambem',
    'td': 'tudo',
    'vc': 'voce'
}

def normalize(words):
    return map(lambda w: acronyms[w] if w in acronyms else w, words)

unwantedWords = set([
    # preposicoes
    'por',
    'para',
    'perante',
    'a',
    'ante',
    'ate',
    'apos',
    'de',
    'em',
    'entre',
    'com',
    'sem',
    'sob',
    'sobre',
    # conjuncoes
    'desde',
    'quando',
    'e',
    'mas',
    'porem',
    'senao',
    'ja',
    'ou',
    'que',
    'por',
    'mesmo',
    # artigos
    'a',
    'as',
    'o',
    'os',
    'um',
    'uns',
    'uma',
    'umas',
    # contracoes
    'do',
    'dos',
    'da',
    'das',
    'no',
    'nos',
    'na',
    'nas',
    'num',
    'nuns',
    'numa',
    'numas',
    'pra',
    'pras',
    'pro',
    'pros'
])

def filterWords(words):
    return filter(lambda w: not w in unwantedWords, words)

def tokenize(words):
    return map(lambda w: w if re.match('^{.+}$', w) else '{w:' + w + '}', words)

def extractTokensFromText(text):
    text = removeUnicodeCharacters(text)
    text = text.lower()
    text = parseInTextTokens(text)
    text = removeNonLetters(text)
    words = splitText(text)
    words = list(map(parseLaughter, words))
    words = list(map(removeDoubleLetters, words))
    words = normalize(words)
    words = filterWords(words) 
    tokens = tokenize(words)
    return tokens

def extractUserTokenFromId(id):
    s = re.search("^https://www.facebook.com/(.+?)(/|.php)", id)
    return '{id:' + (s.group(1) if s else 'unknown') + '}'

def getLinksToken(links):
    return []

def getShareTypeToken(shareType):
    return '{shareType:' + shareType + '}'

def getHasLocationToken(hasLocation):
    if hasLocation == 'true': 
        return '{hasLoc}'
    return None

def getHasTaggedFriendsToken(hasTaggedFriends):
    if hasTaggedFriends == 'true': 
        return '{hasTaggedFr}'
    return None

def getIsSponsor(timestamp):
    if timestamp == 'undefined': 
        return '{sponsor}'
    return None

def getTextSizeToken(text):
    length = len(text)
    if length < 30:
        return '{size:tiny}'
    if length < 100:
        return '{size:small}'
    if length < 400:
        return '{size:medium}'
    return '{size:large}'

def extractTokensFromStory(story):
    tokens = extractTokensFromText(story.text)
    tokens.append(extractUserTokenFromId(story.id))
    linksToken = getLinksToken(story.links)
    for linkToken in linksToken:
        tokens.append(linkToken)
    tokens.append(getShareTypeToken(story.shareType))
    hasLocation = getHasLocationToken(story.hasLocation)
    if hasLocation:
        tokens.append(hasLocation)
    hasTaggedFriends = getHasTaggedFriendsToken(story.hasTaggedFriends)
    if hasTaggedFriends:
        tokens.append(hasTaggedFriends)
    isSponsor = getIsSponsor(story.timestamp)
    if isSponsor:
        tokens.append(isSponsor)
    tokens.append(getTextSizeToken(story.text))
    return tokens


class Story:
    pass

def mockStories(data):
    stories = []
    for d in data:
        st = Story()
        st.id = d['id']
        st.classification = d['classification']
        st.text = d['text']
        st.links = d['links']
        st.shareType = d['shareType']
        st.hasTaggedFriends = d['hasTaggedFriends']
        st.hasLocation = d['hasLocation']
        st.timestamp = d['timestamp']
        st.text = st.text.encode('utf-8')
        stories.append(st)
    return stories

import json

data = raw_input()
stories = mockStories(json.loads(data))

tokensPerClassification = {}
for story in stories:
    print extractTokensFromStory(story)