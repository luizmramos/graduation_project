// onload

window.onload = function() {
	var facebookPage = new FacebookPage();
	facebookPage.getMainContainer().getStreamPagelet().getNewsFeed().forEachStory(function(story) {
		story.prependToStoryCard((new StoryHeaderDom()).getDom());
	});
};