// onload

window.onload = function() {
	var facebookPage = new FacebookPage();
	function print() {
		console.log(facebookPage._mainContainer._streamPagelet._newsFeed._stories);
		setTimeout(print, 20000);	
	}
	print();
};