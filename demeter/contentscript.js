// onload

window.onload = function() {
	var facebookPage = new FacebookPage();
	function print() {
		facebookPage._mainContainer._streamPagelet._newsFeed._stories.forEach(function(story){
			console.log(story._contentWrapper._dom.find('.userContent').html());
		});
		setTimeout(print, 20000);	
	}
	print();
};