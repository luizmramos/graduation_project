// onload

window.onload = function() {
	var facebookPage = new FacebookPage();
	facebookPage.getMainContainer().getStreamPagelet().getNewsFeed().forEachStory(function(story) {
		var previousSelectedClasses = [];
		story.prependToStoryCard((new StoryHeaderDom(function(selectedClasses) {
			var content = story.getJSONContent();
			// mandar request com content e selected classes
			console.log(content);
			console.log(selectedClasses);
			previousSelectedClasses = selectedClasses;
		})).getDom());
	});
};