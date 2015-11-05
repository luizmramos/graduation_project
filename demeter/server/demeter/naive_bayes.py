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


class Story:
    pass

def mock_stories(data):
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
    def __init__(self, tokens, tag):
        self.tokens = tokens
        self.tag = tag

from collections import defaultdict
import math

class NaiveBayes:
    def __init__(self):
        self.n_words_per_tag_per_token = defaultdict(lambda: defaultdict(lambda: 0))
        self.n_documents_per_tag = defaultdict(lambda: 0)
        self.n_words_per_tag = defaultdict(lambda: 0)
        self.tags = set()
        self.vocabulary = set()

    def increment(self, document):
        self.tags.add(document.tag)
        self.n_documents_per_tag[document.tag] += 1
        for token in document.tokens:
            self.n_words_per_tag_per_token[document.tag][token] += 1
            self.n_words_per_tag[document.tag] += 1
            self.vocabulary.add(token)


    def train(self, documents):
        for document in documents:
            self.increment(document) 

    def load(self, n_words_per_tag_per_token, n_documents_per_tag, tags, vocabulary):
        self.n_words_per_tag_per_token = n_words_per_tag_per_token
        self.n_documents_per_tag = n_documents_per_tag
        self.tags = tags
        self.vocabulary = vocabulary

    def write(self):
        naive_bayes_json = {
            'nWordsPerTagPerToken': self.n_words_per_tag_per_token,
            'nDocumentsPerTag': self.n_documents_per_tag,
            'tags': self.tags,
            'vocabulary': self.vocabulary
        }
        #print(json.dumps(naive_bayes_json))

    def get_weight(self, token): 
        if not token in self.vocabulary:
            return 0.01
        w = 0
        ndocs = sum(self.n_documents_per_tag.values())
        L = len(self.tags)
        for tag in self.tags:
            pc_given_t = (self.n_words_per_tag_per_token[tag][token] + 1) * 1.0 / (sum([self.n_words_per_tag_per_token[c][token] for c in self.tags]) + L)
            pc = float(self.n_documents_per_tag[tag] + 1) / (ndocs + L)
            w += pc_given_t * math.log(pc_given_t / pc)
        p_token = (sum([self.n_words_per_tag_per_token[c][token] for c in self.tags]) + 1) * 1.0 / (sum([self.n_words_per_tag[c] for c in self.tags]) + L)
        return -w/(p_token * math.log(p_token))

    def classify(self, tokens):
        max_tag = (-float('inf'), None)
        ndocs = sum(self.n_documents_per_tag.values())
        V = len(self.vocabulary)
        alpha = 1
        for tag in self.tags:
            #print '-------------------------------'
            #print tag
            logp_prior = math.log(float(self.n_documents_per_tag[tag]) / ndocs)
            logp_likelihood = 0
            for token in tokens:
                n = self.n_words_per_tag_per_token[tag][token]
                w = self.get_weight(token)
                logp = w * math.log(float(n + alpha*1) / (self.n_words_per_tag[tag] + alpha*V + alpha*1))
                logp_likelihood += logp
                #print token + ': '  + str(n) + ' / ' + str(self.n_words_per_tag[tag]) + ' peso ' + str(w)

            logp_classifiation = logp_prior + logp_likelihood
            #print tag + " -> " + str(logp_classifiation)
            max_tag = max(max_tag, (logp_classifiation, tag))
        logp_classifiation, tag = max_tag
        
        return tag

    def classifyMulti(self, tokens):
        classes =[]
        ndocs = sum(self.n_documents_per_tag.values())
        nwords = sum(self.n_words_per_tag.values())
        V = len(self.vocabulary)
        alpha = 1
        for tag in self.tags:
            logp_prior = math.log(float(self.n_documents_per_tag[tag]) / ndocs)
            logp_prior_other = math.log(float(ndocs - self.n_documents_per_tag[tag]) / ndocs)
            logp_likelihood = 0
            logp_likelihood_other = 0
            for token in tokens:
                n = self.n_words_per_tag_per_token[tag][token]
                n_other = sum([self.n_words_per_tag_per_token[c][token] if c != tag else 0 for c in self.tags])
                w = self.get_weight(token)
                logp = w * math.log(float(n + alpha*1) / (self.n_words_per_tag[tag] + alpha*V + alpha*1))
                logp_other = w * math.log(float(n_other + alpha*1) / (nwords - self.n_words_per_tag[tag] + alpha*V + alpha*1))
                logp_likelihood += logp
                logp_likelihood_other += logp_other
                
            logp_classifiation = logp_prior + logp_likelihood
            logp_classifiation_other = logp_prior_other + logp_likelihood_other
            if logp_classifiation > logp_classifiation_other:
                classes.append(tag)
        
        return classes


import json
from random import shuffle

data = raw_input()

stories = mock_stories(json.loads(data))
for n_stories in range(20,len(stories), 20):
    global_precision = defaultdict(lambda: 0)
    global_recall = defaultdict(lambda: 0)
    global_accuracy = defaultdict(lambda: 0)
    global_f1 = defaultdict(lambda: 0)
    global_count = 0
    global_exact_match = 0
    global_kappa = 0
    for tries in range(0,25):
        confusion_matrix = defaultdict(lambda: defaultdict(lambda: 0))
        exact_match = 0
        done=0

        shuffle(stories)

        documents = []
        test_data = []
        count_links = 0
        count_total = 0
        i = 0
        for story in stories:
            if i > n_stories:
                break
            i += 1
            story_tokens = extract_tokens_from_story(story)
            if len(story_tokens) < 5:
                continue
            best_count = max(story.classification.values())
            tag = max(story.classification, key=story.classification.get)
            count_total += 1
            if len(story.links):
                count_links += 1
            if len(documents) < n_stories*2.0/4:
                documents.append(Document(story_tokens, tag))
            else:
                test_data.append(Document(story_tokens, tag))
                test_data[len(test_data)-1].texto_completo = story.text

        naive_bayes = NaiveBayes()
        naive_bayes.train(documents)

        true_positives = defaultdict(lambda: 0)
        true_negatives = defaultdict(lambda: 0)
        false_positives = defaultdict(lambda: 0)
        false_negatives = defaultdict(lambda: 0)

        for document in test_data:
            chosen = [naive_bayes.classify(document.tokens)]
            confusion_matrix[document.tag][chosen[0]] += 1
            #print '<divisor>'
            #print chosen
            #print document.textoCompleto
            #print '</divisor>'
            if document.tag in chosen:
                exact_match += 1
            #else:
                #print '[WRONG] Deveria ser ' +  document.tag + ' mas foi ' + str(chosen)
            for tag in naive_bayes.tags:
                if document.tag == tag and tag in chosen:
                    true_positives[tag] += 1
                elif document.tag == tag and not tag in chosen:
                    false_negatives[tag] += 1
                elif document.tag != tag and not tag in chosen:
                    true_negatives[tag] += 1
                elif document.tag != tag and tag in chosen:
                    false_positives[tag] += 1
            
        done += 1.0*len(test_data)
        global_count += 1
        for tag in naive_bayes.tags:
            if true_positives[tag] + false_positives[tag] == 0:
                precision = 1
            else:
                precision = (true_positives[tag]) * 1.0 / (true_positives[tag] + false_positives[tag])
            if true_positives[tag] + false_negatives[tag] == 0:
                recall = 1
            else:
                recall = (true_positives[tag]) * 1.0 / (true_positives[tag] + false_negatives[tag])
            if precision + recall != 0:
                f1 = 2 * precision * recall / (precision + recall)
            else:
                f1 = 0

            accuracy = (true_positives[tag] + true_negatives[tag]) * 1.0 / (true_positives[tag] + true_negatives[tag] + false_positives[tag] + false_negatives[tag])
            global_precision[tag] += precision
            global_recall[tag] += recall
            global_f1[tag] += f1
            global_accuracy[tag] += accuracy
            
            ##print tag + ' TP: ' + str(truePositives[tag]) + ' / ' + str(total[tag]) + ' TN: ' + str(trueNegatives[tag]) + ' / '  + str(nDocs - total[tag]) 
            ##print tag + ': Precision: ' + str(precision),
            ##print ' # Recall: ' + str(recall),   
            ##print ' # F1: ' + str(2 * precision * recall / (precision + recall)) 
    
        exact_match = exact_match * 1.0/ done
        global_exact_match += exact_match
        #print str(exactMatch * 100)
        #print str(n_stories) + ' - Exact match: ' + str(exactMatch*100)
        #for tag in naiveBayes.tags:
            #print tag
        #for tag in naiveBayes.tags:
         #   for predicted in naiveBayes.tags:
                #print "%5d" % confusionMatrix[tag][predicted],
            #print
        expected_accuracy = 0
        total = 0
        for line in confusion_matrix:
            #for column in confusionMatrix:
            #    print '%5d' % confusionMatrix[line][column],
            #print
            sum_column = sum([confusion_matrix[l][line] for l in confusion_matrix])
            sum_line = sum(confusion_matrix[line].values())
            expected_accuracy += sum_column*sum_line
            total += sum_line
        
        expected_accuracy = expected_accuracy * 1.0 / (total ** 2)
        #print str(expectedAccuracy * 100)

        kappa = (exact_match - expected_accuracy) / (1 - expected_accuracy)
        global_kappa += kappa
        #print kappa
    
    #print str(globalExactMatch * 1.0 / globalCount)
    print str(global_kappa * 1.0 / global_count)


    """
    temasErrados = defaultdict(lambda: 0)
    temasTotal = defaultdict(lambda: 0)

    for document in testData:
        temasTotal[document.tag] += 1
        #print '-----------------------'
        chosentag = naiveBayes.classify(document.tokens)
        if document.tag != chosentag:
            #print '[WRONG]',
            temasErrados[document.tag] += 1
        #print('Deveria ser ' + str(document.tag) + ' e foi ' + str(chosentag))
        if document.tag == 'Minorias':
            for token in document.tokens:
                #print str(token) + ': ' + str(chosentag) + '(' + str(naiveBayes.nWordsPertagPerToken[str(chosentag)][str(token)]) + ') vs ' + str(document.tag) + '(' + str(naiveBayes.nWordsPertagPerToken[str(document.tag)][str(token)]) + ')'

    acertosPercentuais = 0

    for tema in temasTotal:
        #print(tema + ': ' + str(temasTotal[tema] - temasErrados[tema]) + '/' + str(temasTotal[tema])) + ' ',
        #print str((temasTotal[tema] - temasErrados[tema])*1.0/temasTotal[tema]*100) + '%'
        acertosPercentuais += (temasTotal[tema] - temasErrados[tema])*1.0
    #print str(acertosPercentuais*1.0/sum(temasTotal.values()))
    """

#for tag in naiveBayes.tags:
    #print tag + ' ' + str(globalPrecision[tag]*1.0/globalCount),
    #print ' / ' + str(globalRecall[tag]*1.0/globalCount),
    #print ' / ' + str(globalF1[tag]*1.0/globalCount),
    #print ' / ' + str(globalAccuracy[tag]*1.0/globalCount)
