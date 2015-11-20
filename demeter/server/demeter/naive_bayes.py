from collections import defaultdict
import math
import os
import re


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
        self.weights = self._compute_weights()

    def load(self, n_words_per_tag_per_token, n_documents_per_tag, tags, vocabulary):
        self.n_words_per_tag_per_token = n_words_per_tag_per_token
        self.n_documents_per_tag = n_documents_per_tag
        self.tags = tags
        self.vocabulary = vocabulary
        self.weights = self._compute_weights()

    def write(self):
        naive_bayes_json = {
            'nWordsPerTagPerToken': self.n_words_per_tag_per_token,
            'nDocumentsPerTag': self.n_documents_per_tag,
            'tags': self.tags,
            'vocabulary': self.vocabulary
        }
        #print(json.dumps(naive_bayes_json))

    def _compute_weights(self):
        weights = {}
        grs = {}

        n_tokens = sum(sum(self.n_words_per_tag_per_token[tag].values()) for tag in self.tags)
        n_tokens_per_tag = {}
        for tag in self.tags:
            n_tokens_per_tag[tag] = sum(self.n_words_per_tag_per_token[tag].values())
        for token in self.vocabulary:
            N = 0
            n_t = sum(self.n_words_per_tag_per_token[tag][token] for tag in self.tags)
            for tag in self.tags:
                n_tc = self.n_words_per_tag_per_token[tag].get(token, 0)
                n_c_tokens = n_tokens_per_tag[tag]
                p_tc = float(n_tc) / n_tokens
                if n_tc > 0:
                    N += p_tc * math.log(float(n_tc) * n_tokens / n_c_tokens / n_t, 2)
            p_t = float(n_t) / n_tokens
            D = - p_t * math.log(p_t, 2)
            grs[token] = N / D

        gr_avg = sum(grs.values()) / len(grs)
        for token in self.vocabulary:
            weights[token] = grs[token] / gr_avg

        return weights

    def get_weight(self, token):
        if not token in self.vocabulary:
            return 0.01
        return self.weights[token]

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