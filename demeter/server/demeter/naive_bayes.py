from collections import defaultdict
import math
import os
import re


class Document:
    def __init__(self, tokens, tag):
        self.tokens = tokens
        self.tag = tag

class NaiveBayes:

    TAG_COUNT = defaultdict(lambda: 0)

    def __init__(self):
        self.n_words_per_tag_per_token = defaultdict(lambda: defaultdict(lambda: 0))
        self.n_documents_per_tag = defaultdict(lambda: 0)
        self.n_words_per_tag = defaultdict(lambda: 0)
        self.tags = set()
        self.vocabulary = set()
        self._link_stats = {'documents_with_link': 0, 'total_documents': 0}

    def increment(self, document):
        tag = document.tag
        self.TAG_COUNT[tag] += 1
        self.tags.add(tag)
        self.n_documents_per_tag[tag] += 1
        has_link = False
        for token in document.tokens:
            self.n_words_per_tag_per_token[tag][token] += 1
            self.n_words_per_tag[tag] += 1
            self.vocabulary.add(token)
            if self._is_link(token):
                has_link = True

        if has_link:
            self._link_stats['documents_with_link'] += 1
        self._link_stats['total_documents'] += 1


    def _is_link(self, token):
        return re.match('^\{link.*?\}$', token)

    def train(self, documents):
        for document in documents:
            self.increment(document)
        self.weights = self._compute_weights()

        with open('__stats.dat', 'w') as f:
            f.write('documents with link = {}'.format(self._link_stats['documents_with_link']))
            f.write(os.linesep)
            f.write('total documents = {}'.format(self._link_stats['total_documents']))
            f.write(os.linesep)
            f.write('1 / 2 = {:.2f}'.format(float(self._link_stats['documents_with_link']) / self._link_stats['total_documents']))
            f.write(os.linesep)

        for tag in self.tags:
            stag = re.sub('[/\s]+', "_", tag.lower())
            with open('_{}.dat'.format(stag), 'w') as f:
                tokens = dict((t, 1) for t in self.vocabulary)
                total = sum(n for t, n in tokens.iteritems())
                links = sum(n for t, n in tokens.iteritems() if self._is_link(t))

                f.write('number of links = {}'.format(links))
                f.write(os.linesep)
                f.write('total of tokens = {}'.format(total))
                f.write(os.linesep)
                f.write(os.linesep)

                for token, n in sorted(tokens.iteritems(), key=lambda (t, n): self.get_weight(t, 0), reverse=True):
                    # if not self._is_link(token):
                    #     continue
                    # if n <= 0:
                    #     continue
                    stoken = re.sub('\{w:(.*)\}', '\\1', token)
                    stoken = stoken.encode('ascii', 'ignore')
                    f.write('{:<25} {:<5} {:<5.2f} {:<5.2f}'.format(stoken, n, self.get_weight(token, 0), float(n) / total))
                    f.write(os.linesep)

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

    def get_weight(self, token, sum_weights):
        if not token in self.vocabulary:
            return 0.01
        w = self.weights[token]
        if re.search('\{link:(.*)\}', token):
            return w
        #     print 'get_weight(): {}'.format(token)
        return w

    def classify(self, tokens):
        max_tag = (-float('inf'), None)
        ndocs = sum(self.n_documents_per_tag.values())
        V = len(self.vocabulary)
        alpha = 1
        token_weights = {}
        sum_weights = 0
        #for token in tokens:
         #   w = self.get_weight(token, 0)
          #  sum_weights += w

        for token in tokens:
            w = self.get_weight(token, sum_weights)
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


    def debug_state(self, dir):
        pass
        # TODO


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
                w = self.get_weight(token, 0)
                logp = w * math.log(float(n + alpha*1) / (self.n_words_per_tag[tag] + alpha*V + alpha*1))
                logp_other = w * math.log(float(n_other + alpha*1) / (nwords - self.n_words_per_tag[tag] + alpha*V + alpha*1))
                logp_likelihood += logp
                logp_likelihood_other += logp_other
                
            logp_classifiation = logp_prior + logp_likelihood
            logp_classifiation_other = logp_prior_other + logp_likelihood_other
            if logp_classifiation > logp_classifiation_other:
                classes.append(tag)
        
        return classes