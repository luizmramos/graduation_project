import re
import unicodedata

def parseAcronyms(text):
    s = re.search("(\s|^)([A-Z]+)(\s|$)", text)
    while s:
        acronym = s.group(2)
        if len(acronym) > 1:
            text = re.sub(acronym,'{acronym:' + acronym + '}', text)
        else:
            text = re.sub(acronym, acronym.lower(), text)
        s = re.search("(\s|^)([A-Z]+)(\s|$)", text)
    return text


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
    return ascii

def removeDoubleLetters(text):
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        text = re.sub(letter + '+', letter, text)
    return text

def removeNonLetters(text):
    text = re.sub("\s+", " ", text)
    text = re.sub("[^\w\s{}:]", " ", text)
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

def filterWords(words):
    return filter(lambda w: not w in unwantedWords, words)

def tokenize(words):
    return map(lambda w: w if re.match('^{.+}$', w) else '{w:' + w + '}', words)

def extractTokensFromText(text):
    text = removeUnicodeCharacters(text)
    text = parseAcronyms(text)
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


class Document:
    def __init__(self, tokens, classification):
        self.tokens = tokens
        self.classification = classification

from collections import defaultdict
import math

class NaiveBayes:
    def __init__(self):
        self.nWordsPerClassificationPerToken = defaultdict(lambda: defaultdict(lambda: 0))
        self.nDocumentsPerClassification = defaultdict(lambda: 0)
        self.nwordsPerClassification = defaultdict(lambda: 0)
        self.classifications = set()
        self.vocabulary = set()

    def increment(self, document):
        self.classifications.add(document.classification)
        self.nDocumentsPerClassification[document.classification] += 1
        for token in document.tokens:
            self.nWordsPerClassificationPerToken[document.classification][token] += 1
            self.nwordsPerClassification[document.classification] += 1
            self.vocabulary.add(token)


    def train(self, documents):
        for document in documents:
            self.increment(document) 

    def load(self, nWordsPerClassificationPerToken, nDocumentsPerClassification, classifications, vocabulary):
        self.nWordsPerClassificationPerToken = nWordsPerClassificationPerToken
        self.nDocumentsPerClassification = nDocumentsPerClassification
        self.classifications = classifications
        self.vocabulary = vocabulary

    def write(self):
        naiveBayesJson = {
            'nWordsPerClassificationPerToken': self.nWordsPerClassificationPerToken,
            'nDocumentsPerClassification': self.nDocumentsPerClassification,
            'classifications': self.classifications,
            'vocabulary': self.vocabulary
        }
        #print(json.dumps(naiveBayesJson))

    def getWeight(self, token):
        return 1
        if not token in self.vocabulary:
            return 0.01
        w = 0
        ndocs = sum(self.nDocumentsPerClassification.values())
        L = len(self.classifications)
        for classification in self.classifications:
            pcGivenT = (self.nWordsPerClassificationPerToken[classification][token] + 1) * 1.0 / (sum([self.nWordsPerClassificationPerToken[c][token] for c in self.classifications]) + L)
            pc = float(self.nDocumentsPerClassification[classification] + 1) / (ndocs + L)
            w += pcGivenT * math.log(pcGivenT / pc)
        pToken = (sum([self.nWordsPerClassificationPerToken[c][token] for c in self.classifications]) + 1) * 1.0 / (sum([self.nwordsPerClassification[c] for c in self.classifications]) + L)
        return -w/(pToken * math.log(pToken))

    def classify(self, tokens):
        maxClassification = (-float('inf'), None)
        ndocs = sum(self.nDocumentsPerClassification.values())
        V = len(self.vocabulary)
        alpha = 1
        for classification in self.classifications:
            #print '-------------------------------'
            #print classification
            logpPrior = math.log(float(self.nDocumentsPerClassification[classification]) / ndocs)
            logpLikelihood = 0
            for token in tokens:
                n = self.nWordsPerClassificationPerToken[classification][token]
                w = self.getWeight(token)
                logp = w * math.log(float(n + alpha*1) / (self.nwordsPerClassification[classification] + alpha*V + alpha*1))
                logpLikelihood += logp
                #print token + ': '  + str(n) + ' / ' + str(self.nwordsPerClassification[classification]) + ' peso ' + str(w)

            logpClassifiation = logpPrior + logpLikelihood
            #print classification + " -> " + str(logpClassifiation)
            maxClassification = max(maxClassification, (logpClassifiation, classification))
        logpClassifiation, classification = maxClassification
        
        return classification

    def classifyMulti(self, tokens):
        classes =[]
        ndocs = sum(self.nDocumentsPerClassification.values())
        nwords = sum(self.nwordsPerClassification.values())
        V = len(self.vocabulary)
        alpha = 1
        for classification in self.classifications:
            logpPrior = math.log(float(self.nDocumentsPerClassification[classification]) / ndocs)
            logpPriorOther = math.log(float(ndocs - self.nDocumentsPerClassification[classification]) / ndocs)
            logpLikelihood = 0
            logpLikelihoodOther = 0
            for token in tokens:
                n = self.nWordsPerClassificationPerToken[classification][token]
                nOther = sum([self.nWordsPerClassificationPerToken[c][token] if c != classification else 0 for c in self.classifications])
                w = self.getWeight(token)
                logp = w * math.log(float(n + alpha*1) / (self.nwordsPerClassification[classification] + alpha*V + alpha*1))
                logpOther = w * math.log(float(nOther + alpha*1) / (nwords - self.nwordsPerClassification[classification] + alpha*V + alpha*1))
                logpLikelihood += logp
                logpLikelihoodOther += logpOther
                
            logpClassifiation = logpPrior + logpLikelihood
            logpClassifiationOther = logpPriorOther + logpLikelihoodOther
            if logpClassifiation > logpClassifiationOther:
                classes.append(classification)
        
        return classes


import json
from random import shuffle

data = raw_input()

globalPrecision = defaultdict(lambda: 0)
globalRecall = defaultdict(lambda: 0)
globalAccuracy = defaultdict(lambda: 0)
globalF1 = defaultdict(lambda: 0)
globalCount = 0
globalExactMatch = 0

for xxx in range(0,1):
    confusionMatrix = defaultdict(lambda: defaultdict(lambda: 0))

    stories = mockStories(json.loads(data))

    shuffle(stories)

    documents = []
    testData = []
    for story in stories:
        storyTokens = extractTokensFromStory(story)
        if len(storyTokens) < 5:
            continue
        bestCount = max(story.classification.values())
        classification = max(story.classification, key=story.classification.get)

        if len(documents) < len(stories)*2.0/4:
            documents.append(Document(storyTokens, classification))
        else:
            testData.append(Document(storyTokens, classification))
            testData[len(testData)-1].textoCompleto = story.text

    naiveBayes = NaiveBayes()
    naiveBayes.train(documents)

    truePositives = defaultdict(lambda: 0)
    trueNegatives = defaultdict(lambda: 0)
    falsePositives = defaultdict(lambda: 0)
    falseNegatives = defaultdict(lambda: 0)
    exactMatch = 0

    for document in testData:
        chosen = [naiveBayes.classify(document.tokens)]
        confusionMatrix[document.classification][chosen[0]] += 1
        print '<divisor>'
        print chosen
        print document.textoCompleto
        print '</divisor>'
        if document.classification in chosen:
            exactMatch += 1
        else:
            print '[WRONG] Deveria ser ' +  document.classification + ' mas foi ' + str(chosen)
        for classification in naiveBayes.classifications:
            if document.classification == classification and classification in chosen:
                truePositives[classification] += 1
            elif document.classification == classification and not classification in chosen:
                falseNegatives[classification] += 1
            elif document.classification != classification and not classification in chosen:
                trueNegatives[classification] += 1
            elif document.classification != classification and classification in chosen:
                falsePositives[classification] += 1
        
    exactMatch /= 1.0*len(testData)
    globalExactMatch += exactMatch
    globalCount += 1
    for classification in naiveBayes.classifications:
        if truePositives[classification] + falsePositives[classification] == 0:
            precision = 1
        else:
            precision = (truePositives[classification]) * 1.0 / (truePositives[classification] + falsePositives[classification])
        if truePositives[classification] + falseNegatives[classification] == 0:
            recall = 1
        else:
            recall = (truePositives[classification]) * 1.0 / (truePositives[classification] + falseNegatives[classification])
        if precision + recall != 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0

        accuracy = (truePositives[classification] + trueNegatives[classification]) * 1.0 / (truePositives[classification] + trueNegatives[classification] + falsePositives[classification] + falseNegatives[classification])
        globalPrecision[classification] += precision
        globalRecall[classification] += recall
        globalF1[classification] += f1
        globalAccuracy[classification] += accuracy
        #print classification + ' TP: ' + str(truePositives[classification]) + ' / ' + str(total[classification]) + ' TN: ' + str(trueNegatives[classification]) + ' / '  + str(nDocs - total[classification]) 
        #print classification + ': Precision: ' + str(precision),
        #print ' # Recall: ' + str(recall),   
        #print ' # F1: ' + str(2 * precision * recall / (precision + recall)) 
    for classification in naiveBayes.classifications:
        print classification
    for classification in naiveBayes.classifications:
        for predicted in naiveBayes.classifications:
            print "%5d" % confusionMatrix[classification][predicted],
        print


    """
    temasErrados = defaultdict(lambda: 0)
    temasTotal = defaultdict(lambda: 0)

    for document in testData:
        temasTotal[document.classification] += 1
        print '-----------------------'
        chosenClassification = naiveBayes.classify(document.tokens)
        if document.classification != chosenClassification:
            print '[WRONG]',
            temasErrados[document.classification] += 1
        print('Deveria ser ' + str(document.classification) + ' e foi ' + str(chosenClassification))
        if document.classification == 'Minorias':
            for token in document.tokens:
                print str(token) + ': ' + str(chosenClassification) + '(' + str(naiveBayes.nDocsPerClassificationPerToken[str(chosenClassification)][str(token)]) + ') vs ' + str(document.classification) + '(' + str(naiveBayes.nDocsPerClassificationPerToken[str(document.classification)][str(token)]) + ')'

    acertosPercentuais = 0

    for tema in temasTotal:
        print(tema + ': ' + str(temasTotal[tema] - temasErrados[tema]) + '/' + str(temasTotal[tema])) + ' ',
        print str((temasTotal[tema] - temasErrados[tema])*1.0/temasTotal[tema]*100) + '%'
        acertosPercentuais += (temasTotal[tema] - temasErrados[tema])*1.0
    print str(acertosPercentuais*1.0/sum(temasTotal.values()))
    """

for classification in naiveBayes.classifications:
    print classification + ' ' + str(globalPrecision[classification]*1.0/globalCount),
    print ' / ' + str(globalRecall[classification]*1.0/globalCount),
    print ' / ' + str(globalF1[classification]*1.0/globalCount),
    print ' / ' + str(globalAccuracy[classification]*1.0/globalCount)
print 'Exact match: ' + str(globalExactMatch * 1.0 / globalCount)

