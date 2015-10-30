#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

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
        if len(query) != 0:
        	previousClassification = query[0].classification
        	story = query[0]

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


class AllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        all = Story.query()
        jsonAll = []
        for story in all:
            json = {
                'id': story.id,
                'classification': story.classification,
                'text': story.text,
                'links': story.links,
                'shareType':  story.shareType,
                'hasTaggedFriends': story.hasTaggedFriends,
                'hasLocation': story.hasLocation,
                'timestamp': story.timestamp
            }
            jsonAll.append(json)
    	self.response.write(jsonAll)
    	self.response.write('<br>')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/stories/add', AddStoryHandler),
    ('/stories/all', AllStoriesHandler)
], debug=True)
