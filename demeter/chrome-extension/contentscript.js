// onload

function onLoad() {
	var facebookPage = new FacebookPage(onLoad);
	facebookPage.getMainContainer().getStreamPagelet().getNewsFeed().forEachStory(function(story) {
		var previousSelectedClasses = [];
		var storyHeader = (new StoryHeaderDom(function(selectedClasses) {
			var content = story.getJSONContent();
			
			if(selectedClasses.some(function(el){return el === 'Classificar';})){
				console.log('fazendo o ajax')
				$.ajax('https://demeter-1075.appspot.com/stories/classify',
					{
					    type: 'POST',
					    async: true,
					    data: {
							'text': content.text,
							'id': content.id,
							'links': content.links.join(','),
							'share-type': content.shareType,
							'timestamp': content.timestamp,
							'has-tagged-friends': content.hasTaggedFriends,
							'has-location': content.hasLocation
				    	},
				    	dataType: 'json',
				    	success: function(response){
				    		classification = response.responseText;
					  		console.log(classification);
					    	if(classification.length < 30){
					    		storyHeader.setClassification(classification);	
					    	} else {
					    		storyHeader.setClassification('invalid');	
					    	}
					    },
					    error: function(response){
					    	classification = response.responseText;
					    	console.log(classification);
					    	if(classification.length < 30){
					    		storyHeader.setClassification(classification);	
					    	} else {
					    		storyHeader.setClassification('invalid');	
					    	}
					    }
				    }
			  	);
			    return
			}

			$.ajax('https://demeter-1075.appspot.com/stories/add', 
				{
				    'type': 'POST',
				    'async': true,
				    'data': {
				       	'remove-classifications': previousSelectedClasses.join(','),
						'classifications': selectedClasses.join(','),
						'text': content.text,
						'id': content.id,
						'links': content.links.join(','),
						'share-type': content.shareType,
						'timestamp': content.timestamp,
						'has-tagged-friends': content.hasTaggedFriends,
						'has-location': content.hasLocation
			    	},
			    	'dataType': 'json'
			    }
		  	);

			console.log(content);
			console.log(selectedClasses);
			previousSelectedClasses = selectedClasses.slice();
		}));
		story.prependToStoryCard(storyHeader.getDom());
	});
}

window.onload = onLoad;