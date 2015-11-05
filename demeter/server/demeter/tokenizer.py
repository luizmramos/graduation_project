import re
import unicodedata

def parse_acronyms(text):
    s = re.search("(\s|^)([A-Z]+)(\s|$)", text)
    while s:
        acronym = s.group(2)
        if len(acronym) > 1:
            text = re.sub(acronym,'{acronym:' + acronym + '}', text)
        else:
            text = re.sub(acronym, acronym.lower(), text)
        s = re.search("(\s|^)([A-Z]+)(\s|$)", text)
    return text


def parse_in_text_tokens(text):
    text = re.sub('((https?://(www\.)?)|(www\.))[^\s]+', '{link}', text)
    text = re.sub('(^|\s)#[^\s]+', ' {hashtag}', text)
    text = re.sub('(^|\s)@[^\s]+', ' {tag}', text)
    text = re.sub('\d+([\.,]\d+)?', '{number}', text)
    text = re.sub('({number}/{number}(/{number})?)|({number}-{number}(-{number})?)', '{date}', text)
    text = re.sub('{number}\%', '{percentage}', text)
    text = re.sub('(r|(us?))?\${number}', '{money}', text)
    return text

def remove_unicode_characters(text):
    unicode = text.decode('utf-8')
    unicode = unicodedata.normalize('NFD', unicode)
    ascii = unicode.encode('ascii', 'ignore') # ignore or substitute by {unicode}
    return ascii

def remove_double_letters(text):
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        text = re.sub(letter + '+', letter, text)
    return text

def remove_non_letters(text):
    text = re.sub("\s+", " ", text)
    text = re.sub("[^\w\s{}:]", " ", text)
    return text

spaces = re.compile(r'[\s\n]')

def split_text(text):
    return filter(lambda l: l!='', spaces.split(text))

def parse_laughter(word):
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

unwanted_words = set([
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
    'como',
    # conjuncoes
    'desde',
    'onde',
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
    'pros',
    'ao',
    'aos',
    'pelo',
    'pelos',
    'pela',
    'pelas'
    #pronomes
    'eu',
    'tu',
    'ele',
    'ela',
    'nos',
    'vos',
    'eles',
    'elas',
    'voce',
    'voces',
    'meu',
    'meus',
    'minha',
    'minhas',
    'seu',
    'seus',
    'sua',
    'suas',
    'dele',
    'deles',
    'dela',
    'delas',
    'nosso',
    'nossos',
    'nossa',
    'nossas'
    #adverbios
    'nao',
    'mais',
    'menos',
    #verbos comuns
    'foi',
    'vai',
    'ir',
    'tem',
    'temos',
    'terei',
    'tera',
    'ha',
    'havia',
    'haveria',
    'havera',
    'ser',
    'esta',
    'estar',
    'estamos',
    'estou',
])

def filter_words(words):
    return filter(lambda w: not w in unwanted_words, words)

def tokenize(words):
    return map(lambda w: w if re.match('^{.+}$', w) else '{w:' + w + '}', words)

def extract_tokens_from_text(text):
    text = remove_unicode_characters(text)
    text = parse_acronyms(text)
    text = text.lower()
    text = parse_in_text_tokens(text)
    text = remove_non_letters(text)
    words = split_text(text)
    words = list(map(parse_laughter, words))
    words = list(map(remove_double_letters, words))
    words = normalize(words)
    words = filter_words(words) 
    tokens = tokenize(words)
    return tokens

def extract_user_token_from_id(id):
    s = re.search("^https://www.facebook.com/(.+?)(/|.php)", id)
    return '{id:' + (s.group(1) if s else 'unknown') + '}'

def get_links_token(links):
    return []

def get_share_type_token(share_type):
    return '{shareType:' + share_type + '}'

def get_has_location_token(has_location):
    if has_location == 'true': 
        return '{hasLoc}'
    return None

def get_has_tagged_friends_token(has_tagged_friends):
    if has_tagged_friends == 'true': 
        return '{hasTaggedFr}'
    return None

def get_is_sponsor(timestamp):
    if timestamp == 'undefined': 
        return '{sponsor}'
    return None

def get_text_size_token(text):
    length = len(text)
    if length < 30:
        return '{size:tiny}'
    if length < 100:
        return '{size:small}'
    if length < 400:
        return '{size:medium}'
    return '{size:large}'

def extract_tokens_from_story(story):
    tokens = extract_tokens_from_text(story.text)
    tokens.append(extract_user_token_from_id(story.id))
    links_token = get_links_token(story.links)
    for link_token in links_token:
        tokens.append(link_token)
    tokens.append(get_share_type_token(story.shareType))
    has_location = get_has_location_token(story.hasLocation)
    if has_location:
        tokens.append(has_location)
    has_tagged_friends = get_has_tagged_friends_token(story.hasTaggedFriends)
    if has_tagged_friends:
        tokens.append(has_tagged_friends)
    is_sponsor = get_is_sponsor(story.timestamp)
    if is_sponsor:
        tokens.append(is_sponsor)
    tokens.append(get_text_size_token(story.text))
    return tokens
