from collections import defaultdict
import math

class Document:
    def __init__(self, tokens, tag):
        self.tokens = tokens
        self.tag = tag

class NaiveBayes:

    TAG_MAP = {
        'Curiosidades': 'Curiosidades / Humor',
        'Humor': 'Curiosidades / Humor',
        'Celebridade': 'Celebridade / Filme',
        'Filme': 'Celebridade / Filme',
        'Noticias': 'Noticias',
        'Turismo': 'Noticias',
        'Medicina': 'Outros',
        'Propaganda': 'Outros',
        'Esportes': 'Outros',
    }
    TAG_COUNT = defaultdict(lambda: 0)

    def __init__(self):
        self.n_words_per_tag_per_token = defaultdict(lambda: defaultdict(lambda: 0))
        self.n_documents_per_tag = defaultdict(lambda: 0)
        self.n_words_per_tag = defaultdict(lambda: 0)
        self.tags = set()
        self.vocabulary = set()

    def increment(self, document):
        tag = self.TAG_MAP[document.tag] if document.tag in self.TAG_MAP else document.tag
        self.TAG_COUNT[tag] += 1
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
        #return 1
        if not token in self.vocabulary:
            return 0.01

        w = 0
        ndocs = sum(self.n_documents_per_tag.values())
        L = len(self.tags)
        nwords = sum(self.n_words_per_tag.values())
        
        for tag in self.tags:
            pc_given_t = (self.n_words_per_tag_per_token[tag][token] + 1) * 1.0 / (sum([self.n_words_per_tag_per_token[c][token] for c in self.tags]) + L)
            pc = float(self.n_documents_per_tag[tag] + 1) / (ndocs + L)
            w += pc_given_t * math.log(pc_given_t / pc)*(self.n_words_per_tag_per_token[tag][token] + 1)*1.0/nwords
            w += (1-pc_given_t) * math.log((1-pc_given_t) / (1-pc))*(nwords-self.n_words_per_tag_per_token[tag][token] - 1)*1.0/nwords
        p_token = (sum([self.n_words_per_tag_per_token[c][token] for c in self.tags]) + 1) * 1.0 / (sum([self.n_words_per_tag[c] for c in self.tags]) + L)

        return -w/((p_token * math.log(p_token))+((1-p_token) * math.log(1-p_token)))

    def classify(self, tokens):
        max_tag = (-float('inf'), None)
        ndocs = sum(self.n_documents_per_tag.values())
        V = len(self.vocabulary)
        alpha = 1
        token_weights = {}
        for token in tokens:
                w = self.get_weight(token)
                token_weights[token] = w

        for tag in self.tags:
            #print '-------------------------------'
            #print tag
            logp_prior = math.log(float(self.n_documents_per_tag[tag]) / ndocs)
            logp_likelihood = 0
            for token in tokens:
                n = self.n_words_per_tag_per_token[tag][token]
                w = token_weights[token]
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