// onload

function onLoad() {
	var facebookPage = new FacebookPage(onLoad);
	facebookPage.getMainContainer().getStreamPagelet().getNewsFeed().forEachStory(function(story) {
		var previousSelectedClasses = [];
		story.prependToStoryCard((new StoryHeaderDom(function(selectedClasses) {
			var content = story.getJSONContent();
			// mandar request com content e selected classes
			$.ajax('https://demeter-1075.appspot.com/stories/add', 
				{
				    'type': 'POST',
				    'async': true,
				    'data': {
				       	'remove-classifications': previousSelectedClasses.join(','),
						'classifications': selectedClasses.join(','),
						'content': JSON.stringify(content),
						'id': content.id
			    	},
			    	'dataType': 'json'
			    }
		  	);

			console.log(content);
			console.log(selectedClasses);
			previousSelectedClasses = selectedClasses.slice();
		})).getDom());
	});
}

window.onload = onLoad;