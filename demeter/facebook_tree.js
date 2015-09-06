// class DomElement

function DomElement(/* jQueryObject */ dom) {
	this._dom = dom;
}

DomElement.prototype.getDomNode = function() {
	return this._dom;
}

// class FacebookPage

function FacebookPage() {
	this._mainContainer = new MainContainer($('#mainContainer'));
}

FacebookPage.prototype.getMainContainer = function() {
	return this._mainContainer;
}

// class MainContainer

function MainContainer(/* jQueryObject */ mainContainerDom) {
	this.super(mainContainerDom);
	this._streamPagelet = new StreamPagelet(mainContainerDom.find('#stream_pagelet'));
}

inherits(MainContainer, DomElement);

MainContainer.prototype.getStreamPagelet = function() {
	return this._streamPagelet;
}

// class StreamPagelet

function StreamPagelet(/* jQueryObject */ streamPageletDom) {
	this.super(streamPageletDom);
	this._pageletComposer = new PageletComposer(streamPageletDom.find('#pagelet_composer'));
	this._newsFeed = new NewsFeed(streamPageletDom.find('div[id*="topnews_main_stream"]'));
}

inherits(StreamPagelet, DomElement);

StreamPagelet.prototype.getPageletComposer= function() {
	return this._pageletComposer;
}

StreamPagelet.getNewsFeed = function() {
	return this._newsFeed;
}

// class PageletComposer

function PageletComposer(/* jQueryObject */ pageletComposerDom) {
	this.super(pageletComposerDom);
}

inherits(PageletComposer, DomElement);

// class NewsFeed

/**
 * Newsfeed is composed of several substreams. Each substream has several stories
 * when the user scrolls down, a new substream is added with the new stories.
 * So in order to get the new stories, we must keep looking for new substreams
 */
function updateNewsFeedStories(
	/*jQueryObject */ feedStreamDom, 
	/* Array<NewsFeedStory> */ stories, 
	/* Map<String, NewsFeedStory> */ storiesMap, 
	/* Map<String, jQueryObject> */ substreams
) {
	var allSubstreams = feedStreamDom.find('div[id*="substream"]').get();
	allSubstreams.forEach(function(substream) {
		if (substreams[substream.id] === undefined) {
			substreams[substream.id] = $(substream);
			$(substream).find('div[id*="hyperfeed_story_id"]').get().forEach(function(story) {
				if (storiesMap[story.id] === undefined) {
					storiesMap[story.id] = $(story);
					stories.push(new NewsFeedStory($(story)));	
				}
			});
		}
	});
}

function NewsFeed(/* jQueryObject */ newsFeedDom) {
	this.super(newsFeedDom);
	this._feedStreamDom = newsFeedDom.find('div[id*="feed_stream"]');
	this._stories = [];
	this._storiesMap = {};
	this._substreams = {};
	this._documentHeight = $(document).height();
	updateNewsFeedStories(this._feedStreamDom, this._stories, this._storiesMap, this._substreams);
	var WINDOW_SCROLL_DEBOUNCE = 100;
	$(window).scroll(function() {
		var documentHeight = $(document).height();
		if (documentHeight <= this._documentHeight) { return; }
		this._documentHeight = documentHeight;

		if (this._windowScrollTimeout !== undefined) {
			clearTimeout(this._windowScrollTimeout);
			this._windowScrollTimeout = undefined;
		}

		this._windowScrollTimeout = setTimeout(function() {
			updateNewsFeedStories(this._feedStreamDom, this._stories, this._storiesMap, this._substreams);
		}.bind(this), WINDOW_SCROLL_DEBOUNCE);

	}.bind(this));
}

inherits(NewsFeed, DomElement);

NewsFeed.prototype.getStories = function() {
	return this._stories;
}

// class NewsFeedStory

function NewsFeedStory(/* jQueryObject */ newsFeedStoryDom) {
	this.super(newsFeedStoryDom);
}

inherits(NewsFeedStory, DomElement);

// TODO: create NewsFeedStoryContent -> .userContentWrapper:not(.userContentWrapper .userContentWrapper)