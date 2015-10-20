// onload

window.onload = function() {
	var facebookPage = new FacebookPage();
	facebookPage.getMainContainer().getStreamPagelet().getNewsFeed().forEachStory(function(story) {
		var previousSelectedClasses = [];
		story.prependToStoryCard((new StoryHeaderDom(function(selectedClasses) {
			var content = story.getJSONContent();
			// mandar request com content e selected classes
			$.get('https://demeter-1075.appspot.com/stories/add', {
				'remove-classifications': previousSelectedClasses.join(','),
				'classifications': selectedClasses.join(','),
				'content': JSON.stringify(content),
				'id': content.id
			});
			console.log(content);
			console.log(selectedClasses);
			previousSelectedClasses = selectedClasses.slice();
		})).getDom());
	});
};