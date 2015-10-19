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
    content = ndb.TextProperty(indexed=False)
    

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class AddStoryHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.get('id')
      	content = self.request.get('content')
        classification = self.request.get('classification')
        if not id or not content or not classification:
        	self.response.write('invalid')
        	return

        query = Story.query(Story.id == id).fetch(1)
        previousClassification = {}
        story = None
        if len(query) != 0:
        	previousClassification = query[0].classification
        	story = query[0]

        if not classification in previousClassification:
        	previousClassification[classification] = 0
        previousClassification[classification] = previousClassification[classification] + 1	
        story = story or Story(id=id, classification=previousClassification, content=content)
        story.put()


class AllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        all = Story.query()
        for story in all:
        	self.response.write(story.id)
        	self.response.write(' / ')
        	self.response.write(story.content)
        	self.response.write(' / ')
        	self.response.write(story.classification)
        	self.response.write('<br>')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/stories/add', AddStoryHandler),
    ('/stories/all', AllStoriesHandler)
], debug=True)
