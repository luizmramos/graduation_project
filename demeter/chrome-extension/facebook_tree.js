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

StreamPagelet.prototype.getNewsFeed = function() {
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
	/* Map<String, jQueryObject> */ substreams,
	/* Array<Function> */ storyMutators
) {
	var allSubstreams = feedStreamDom.find('> div').get();
	allSubstreams.forEach(function(substream) {
		if (substreams[substream.id] === undefined) {
			substreams[substream.id] = $(substream);
			// The substream gets rendered before its hyperfeed_story's, which means that
			// we might lose some stories. This timeout reduces this problem
			setTimeout(function() {
				$(substream).find('div[data-ft]').get().forEach(function(hyperfeed_story) {
					var stories = [];
					if ($(hyperfeed_story).find('.uiCollapsedList').length > 0) { // several stories inside an hyperfeed story
						stories = $(hyperfeed_story).find('.uiCollapsedList > li').get();	
						for (var i = 0; i < stories.length; i++) {
							stories[i].id = hyperfeed_story.id + '##' + i;
						}
					} else { // only one story in the hyperfeed (most cases)
						stories.push(hyperfeed_story);
					}
					for (var i = 0; i < stories.length; i++) {
						var story = stories[i];
						if (storiesMap[story.id] === undefined) {
							storiesMap[story.id] = $(story);
							var newsFeedStory = new NewsFeedStory($(story));
							stories.push(newsFeedStory);	
							storyMutators.forEach(function(mutator) {
								mutator(newsFeedStory);
							});
						}
					}
				});
			}, 500);
		}
	});
}

function NewsFeed(/* jQueryObject */ newsFeedDom) {
	this.super(newsFeedDom);
	this._feedStreamDom = newsFeedDom.find('div[id*="feed_stream"]');
	this._stories = [];
	this._storiesMap = {};
	this._substreams = {};
	this._storyMutators = [];
	this._documentHeight = $(document).height();
	updateNewsFeedStories(
		this._feedStreamDom, 
		this._stories, 
		this._storiesMap, 
		this._substreams, 
		this._storyMutators
	);
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
			updateNewsFeedStories(
				this._feedStreamDom, 
				this._stories, 
				this._storiesMap, 
				this._substreams, 
				this._storyMutators
			);
		}.bind(this), WINDOW_SCROLL_DEBOUNCE);

	}.bind(this));
}

inherits(NewsFeed, DomElement);

NewsFeed.prototype.getStories = function() {
	return this._stories;
}

NewsFeed.prototype.forEachStory = function(/* Function */ mutator) {
	this._stories.forEach(function(story) {
		mutator(story);
	});
	this._storyMutators.push(mutator);
}

// class NewsFeedStory

function NewsFeedStory(/* jQueryObject */ newsFeedStoryDom) {
	this.super(newsFeedStoryDom);
	var currentDom = newsFeedStoryDom;
	var contentDom = currentDom.find('.userContentWrapper:not(.userContentWrapper .userContentWrapper)');
	this._contentWrapper = new NewsFeedStoryContentWrapper(contentDom);
}

inherits(NewsFeedStory, DomElement);

NewsFeedStory.prototype.getContentWrapper = function() {
	return this._contentWrapper;
}

NewsFeedStory.prototype.prependToStoryCard = function(/* jQueryObject */ dom) {
	var storyCard = this._dom.find('.userContentWrapper:not(.userContentWrapper .userContentWrapper)');
	storyCard.prepend(dom);
}

NewsFeedStory.prototype.getJSONContent = function() {
	var jsonContent = {};
	jsonContent.text = this._contentWrapper.getContent();
	jsonContent.links = this._contentWrapper.getLinks();
	var idAndTimestamp = this._contentWrapper.getIdAndTimestamp();
	jsonContent.id = idAndTimestamp.id;
	jsonContent.timestamp = idAndTimestamp.timestamp;
	return jsonContent;
}

// class NewsFeedStoryContentWrapper

function NewsFeedStoryContentWrapper(/* jQueryObject */ newsFeedStoryContentWrapperDom) {
	this.super(newsFeedStoryContentWrapperDom);
}

inherits(NewsFeedStoryContentWrapper, DomElement);

NewsFeedStoryContentWrapper.prototype.getContent = function() {
	var ps = this.getDomNode().find('p');
	var ans = '';
	for (var i = 0; i < ps.length; i++) {
		if (ps[i].textContent) {
			ans = ans + ps[i].textContent + ' ';
		}
	}
	return ans;
}

NewsFeedStoryContentWrapper.prototype.getLinks = function() {
	var as = this.getDomNode().find('a');
	var ans = [];
	var outros = [];
	for (var i = 0; i < as.length; i++) {
		var href = as[i].href;
		if (href && href.startsWith('http')) {
			if (href.indexOf('.facebook.com') == -1) {
				ans.push(href);	
			} else if (href.indexOf('l.php?u=') !== -1) {
				var args = href.substr(href.indexOf('l.php?u=') + 8);
				var link = args.split('&')[0];
				var decoded = decodeURIComponent(link);
				outros.push(decoded);
			}
			
		}
	}
	if (ans.length === 0) {
		ans = outros;
	}
	// Remove repetition
	return ans.filter(function (e, i, ans) { 
	    return ans.lastIndexOf(e) === i;
	});
}

NewsFeedStoryContentWrapper.prototype.getIdAndTimestamp = function() {
	var as = this.getDomNode().find('a');
	for (var i = 0; i < as.length; i++) {
		if (as[i].classList.contains('uiStreamSponsoredLink')) {
			return {
				'id': as[i].href
			};
		}
		else if ($(as[i]).find('span.timestampContent').length > 0) {
			var timestamp = $(as[i]).find('abbr')[0].getAttribute('data-utime');
			return {
				'id': as[i].href,
				'timestamp': timestamp
			};
		}
	}
	return undefined;
}

// TODO: create NewsFeedStoryContent -> .userContent