import webapp2
import json
import tokenizer
from naive_bayes import NaiveBayes
from collections import defaultdict
from google.appengine.ext import ndb

class Story(ndb.Model):
    id = ndb.StringProperty(indexed=True)
    classification = ndb.JsonProperty(indexed=False)
    text = ndb.TextProperty(indexed=False)
    links = ndb.TextProperty(indexed=False)
    shareType = ndb.StringProperty(indexed=False)
    hasTaggedFriends = ndb.StringProperty(indexed=False)
    hasLocation = ndb.StringProperty(indexed=False)
    timestamp = ndb.StringProperty(indexed=False)

class CountPerToken(ndb.Model):
    token = ndb.StringProperty(indexed=True)
    perTag = ndb.JsonProperty(indexed=False)

class DocumentsPerTag(ndb.Model):
    tag = ndb.StringProperty(indexed=True)
    count = ndb.IntegerProperty(indexed=False)

class WordsPerTag(ndb.Model):
    tag = ndb.StringProperty(indexed=True)
    count = ndb.IntegerProperty(indexed=False)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


def updateCounts(story, previousBestTag, self):
    bestTag =  max(story.classification, key=story.classification.get)
    if bestTag != previousBestTag: 
        tokens = tokenizer.extract_tokens_from_story(story, None)
        for token in tokens:
            token_query = CountPerToken.query(CountPerToken.token == token).fetch(1)
            if  len(token_query) == 0:
                token_count = CountPerToken(token=token, perTag={})
            else:
                token_count = token_query[0]

            if previousBestTag:
                if previousBestTag in token_count.perTag:
                    token_count.perTag[previousBestTag] -= 1
            if not bestTag in token_count.perTag:
                token_count.perTag[bestTag] = 0
            token_count.perTag[bestTag] += 1 
            token_count.put()

        if previousBestTag:
            prevDocumentsPerTagQuery = DocumentsPerTag.query(DocumentsPerTag.tag == previousBestTag).fetch(1)
            if len(prevDocumentsPerTagQuery) != 0:
                prevDocumentsPerTagQuery[0].count -= 1
                prevDocumentsPerTagQuery[0].put()
        documentsPerTagQuery = DocumentsPerTag.query(DocumentsPerTag.tag == bestTag).fetch(1)
        
        if len(documentsPerTagQuery) != 0:
            documentsPerTag = documentsPerTagQuery[0]
        else:
            documentsPerTag = DocumentsPerTag(tag=bestTag,count=0)
        #self.response.write(documentsPerTag.tag)
        #self.response.write(documentsPerTag.count)
        documentsPerTag.count += 1
        documentsPerTag.put()

        wordsPerTagQuery = WordsPerTag.query(WordsPerTag.tag == bestTag).fetch(1)
    
        if len(wordsPerTagQuery) != 0:
            wordsPerTag = wordsPerTagQuery[0]
        else:
            wordsPerTag = WordsPerTag(tag=bestTag,count=0)
        
        wordsPerTag.count += len(tokens)
        wordsPerTag.put()

class AddStoryHandler(webapp2.RequestHandler):
    def post(self):
        id = self.request.get('id')
        classifications = self.request.get('classifications')
        remove_classifications = self.request.get('remove-classifications')
        hasLocation = self.request.get('has-location')
        hasTaggedFriends = self.request.get('has-tagged-friends')
        timestamp = self.request.get('timestamp')
        shareType = self.request.get('share-type')
        links = self.request.get('links')
        text = self.request.get('text')

        if not links:
            links = ''
        if not hasLocation:
            hasLocation = "false"
        if not timestamp:
            timestamp = "undefined"
        if not hasTaggedFriends:
            hasTaggedFriends = "false"
        if not shareType:
            shareType = "update"

        if not id or not text:
        	self.response.write('invalid')
        	return

        query = Story.query(Story.id == id).fetch(1)
        previousClassification = {}
        story = None
        previousBestTag = None
        if len(query) != 0:
            previousClassification = query[0].classification
            story = query[0]
            previousBestTag =  max(previousClassification, key=previousClassification.get)


        if remove_classifications:
            for classification in remove_classifications.split(','):
                if not classification in previousClassification:
                    continue
                if previousClassification[classification] > 0:
                    previousClassification[classification] = previousClassification[classification] - 1
                    
        if classifications:
            for classification in classifications.split(','):
                if not classification in previousClassification:
                    previousClassification[classification] = 0
                previousClassification[classification] = previousClassification[classification] + 1
        
        story = story or Story(id=id, classification=previousClassification, text=text, links=links, shareType=shareType, hasTaggedFriends=hasTaggedFriends, hasLocation=hasLocation, timestamp=timestamp)
        story.put()

        # update naive bayes
        #return
        #self.response.write(previousBestTag)
        updateCounts(story,previousBestTag, self)


class AllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        all = Story.query()
        jsonAll = []
        for story in all:
            js = {
                'id': story.id,
                'classification': story.classification,
                'text': story.text,
                'links': story.links,
                'shareType':  story.shareType,
                'hasTaggedFriends': story.hasTaggedFriends,
                'hasLocation': story.hasLocation,
                'timestamp': story.timestamp
            }
            jsonAll.append(js)
    	self.response.write(json.dumps(jsonAll))
    	self.response.write('<br>')


class AddAllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        return
        all = Story.query()
        i = 0
        start = False
        for story in all.fetch(offset=int(self.request.get('from')), limit=int(self.request.get('to'))-int(self.request.get('from'))):
            updateCounts(story, None, self)

class AddCountsHandler(webapp2.RequestHandler):
    def get(self):
        return
        tag = self.request.get('tag')
        count = self.request.get('count')
        if not tag:
            self.response.write('invalid')
        query = WordsPerTag.query(WordsPerTag.tag == tag).fetch(1)
        if len(query) == 0:
            wordsPerTag = WordsPerTag(tag=tag, count=0)
        else:
            wordsPerTag = query[0]
        wordsPerTag.count = int(count)
        wordsPerTag.put()
        self.response.write(wordsPerTag.tag)
        self.response.write(wordsPerTag.count)


class TestAllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('teste')
        all = DocumentsPerTag.query()
        for document in all:
            self.response.write(document.tag)
            self.response.write(document.count)
            self.response.write('<br>')

        all = CountPerToken.query()

        for count_token in all:
            self.response.write('<br>')
            self.response.write(count_token.token)
            self.response.write(count_token.perTag)
            self.response.write('<br>')

        all = WordsPerTag.query()

        for wPerTag in all:
            self.response.write('<br>')
            self.response.write(wPerTag.tag)
            self.response.write(wPerTag.count)
            self.response.write('<br>')

class ClearAllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        return
        self.response.write('teste')
        all = DocumentsPerTag.query()
        for document in all:
            document.key.delete()

        all = CountPerToken.query()

        for count_token in all:
            count_token.key.delete()

        all = WordsPerTag.query()

        for wPerTag in all:
            wPerTag.key.delete()


class ClassifyStoryHandler(webapp2.RequestHandler):
    def post(self):
        
        id = self.request.get('id')
        hasLocation = self.request.get('has-location')
        hasTaggedFriends = self.request.get('has-tagged-friends')
        timestamp = self.request.get('timestamp')
        shareType = self.request.get('share-type')
        links = self.request.get('links')
        text = self.request.get('text')

        if not links:
            links = ''
        if not hasLocation:
            hasLocation = "false"
        if not timestamp:
            timestamp = "undefined"
        if not hasTaggedFriends:
            hasTaggedFriends = "false"
        if not shareType:
            shareType = "update"

        if not id or not text:
            self.response.write('invalid')
            return

        query = Story.query(Story.id == id).fetch(1)
        story = None
        bestTag = None
        if len(query) != 0:
            story = query[0]
            bestTag =  max(story.classification, key=story.classification.get)

        if bestTag:
            self.response.write(bestTag)
            return

        story = story or Story(id=id, classification={}, text=text, links=links, shareType=shareType, hasTaggedFriends=hasTaggedFriends, hasLocation=hasLocation, timestamp=timestamp)
        tokens = tokenizer.extract_tokens_from_story(story, None)
        
        n_words_per_tag_per_token = defaultdict(lambda: defaultdict(lambda: 0))
        n_documents_per_tag = defaultdict(lambda: 0)
        n_words_per_tag = defaultdict(lambda: 0) #TODO ver esse n_words_per_tag
        tags = set()
        vocabulary = set()
        for token in tokens:
            count_per_token = CountPerToken.query(CountPerToken.token==token).fetch(1)
            if len(count_per_token) != 0:
                vocabulary.add(count_per_token[0].token)
                for tag in count_per_token[0].perTag:
                    n_words_per_tag_per_token[tag][token] = count_per_token[0].perTag[tag]

        allDocCounts = DocumentsPerTag.query()
        for docCount in allDocCounts:
            n_documents_per_tag[docCount.tag] = docCount.count
            tags.add(docCount.tag)

        allWordsCount = DocumentsPerTag.query()
        for wCount in allWordsCount:
            n_words_per_tag[wCount.tag] = wCount.count

        naiveBayes = NaiveBayes()
        naiveBayes.load(n_words_per_tag_per_token, n_documents_per_tag, tags, vocabulary, n_words_per_tag)
        self.response.write(naiveBayes.classify(tokens))

                    


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/stories/add', AddStoryHandler),
    ('/stories/all', AllStoriesHandler),
    ('/stories/add-all', AddAllStoriesHandler),
    ('/stories/test', TestAllStoriesHandler),
    ('/stories/clear', ClearAllStoriesHandler),
    ('/stories/classify', ClassifyStoryHandler),
    ('/stories/add-count', AddCountsHandler)
], debug=True)
