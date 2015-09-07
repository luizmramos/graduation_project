// class StoryClassDom

function StoryClassDom(/* String */ className) {
	this._className = className;
	this._dom = $('<span class="story-class">' + className + "</spam>")
}

StoryClassDom.prototype.getDom = function() {
	return this._dom;
}

StoryClassDom.prototype.onClick = function(/* Function */ callback) {
	this._dom.click(callback.bind(this, this._className));
}

// class StoryClassesListDom

var classesList = [
	"Politica", 
	"Economia", 
	"Esporte", 
	"Pessoal", 
	"Ciencia", 
	"Educacao", 
	"Celebridades", 
	"Filmes", 
	"Curiosidades",
	"Propaganda", 
	"Outros"]

function StoryClassesListDom() {
	this._storyClassesList = classesList.map(function(className) {
		return new StoryClassDom(className);
	}.bind(this));
	var storyClassDoms = this._storyClassesList.map(function(storyClass) {
		return storyClass.getDom();
	});
	this._dom = $('<span></span>');
	storyClassDoms.forEach(function(storyClassDom) {
		this._dom.append(storyClassDom);
	}.bind(this));
}

StoryClassesListDom.prototype.getDom = function() {
	return this._dom;
}

StoryClassesListDom.prototype.onSelect = function(/* Function */ callback) {
	this._storyClassesList.forEach(function(storyClass) {
		storyClass.onClick(callback); 
	}.bind(this));
}

// class StoryClassSelectedChangeButton

function StoryClassSelectedChangeButton() {
	this._dom = $('<img src="' + chrome.extension.getURL("/three-dots.png") + '" class="story-class-selected-change-button"/>');
}

StoryClassSelectedChangeButton.prototype.getDom = function() {
	return this._dom;
}

StoryClassSelectedChangeButton.prototype.onClick = function(/* Function */ callback) {
	this._dom.click(callback);
}

// class Dropdown

function Dropdown(/* Array<String> */ options, /* jQueryElement */ buttonDom) {
	this._positioner = $('<div class="uiContextualLayerPositioner uiLayer hidden_elem"/>');
	this._contextualLayer = $('<div class="uiContextualLayer uiContextualLayerBelowRight dropdown"/>');
	this._items = [];
	options.forEach(function(option) {
		var item = $('<div class="dropdown-item">' + option + '</div>');
		item.click(function(){
			this.hide();
		}.bind(this));
		this._items.push(item);
		this._contextualLayer.append(item);
	}.bind(this));
	this._positioner.append(this._contextualLayer);
	$('#globalContainer').append(this._positioner);
	this._buttonDom = buttonDom;
	this._contextualLayer.click(function(event) {
		event.preventDefault();
		event.stopPropagation();
	});
	this._hidden = true;
}

Dropdown.prototype.toggle = function() {
	if (this._hidden) {
		this.show();
		this._hidden = false;
	} else {
		this.hide();
		this._hidden = true;
	}
}

Dropdown.prototype.show = function() {
	var rect = this._buttonDom.get(0).getBoundingClientRect();
	this._positioner.css({
		width: "200px",
		right: (rect.right - 200) + "px",
		top: (rect.top + $(document).scrollTop()-20) + "px",
	});
	this._positioner.removeClass('hidden_elem');
}

Dropdown.prototype.hide = function() {
	this._positioner.addClass('hidden_elem');	
}

Dropdown.prototype.onSelect= function(/* Number */ i, /* Function */ callback) {
	this._items[i].click(callback.bind(i));
}

// class StoryClassSelectedDom

function StoryClassSelectedDom() {
	this._dom = $('<div><span id="selected-classes"/></div>');
	this._changeButton = new StoryClassSelectedChangeButton();
	this._dom.append(this._changeButton.getDom());
	this._dropdownOptions = ['Mudar assunto', 'Adicionar assunto'];
	this._dropdown = new Dropdown(this._dropdownOptions, this._dom);
	this._changeButton.onClick(function() {
		this._dropdown.toggle();
	}.bind(this));
}

StoryClassSelectedDom.prototype.setSelectedClasses = function(/* Array<String> */ selectedClasses) {
	this._dom.find('#selected-classes').empty();
	this._dom.find('#selected-classes').append(selectedClasses.join(' / '));
}

StoryClassSelectedDom.prototype.getDom = function() {
	return this._dom;
}

StoryClassSelectedDom.prototype.onAddNewClass = function(/* Function */ callback) {
	this._dropdown.onSelect(1, callback);
}

StoryClassSelectedDom.prototype.onRemoveClasses = function(/* Function */ callback) {
	this._dropdown.onSelect(0, callback);
}

// class StoryHeaderDom

function StoryHeaderDom() {
	this._storyClassesList = new StoryClassesListDom();
	this._selectedClasses = [];
	this._dom = $('<div class="story-header"><div id="story-header-content"></div><div class="divisor-line"/></div>');
	this._storyClassesSelectedDom = new StoryClassSelectedDom();
	this._renderStoryClassesList = function() {
		this._dom.find('#story-header-content').children().detach();
		this._dom.find('#story-header-content').append($('<span>Assunto:</span>'));
		this._dom.find('#story-header-content').append(this._storyClassesList.getDom());
	}
	this._renderSelectedStories = function() {
		this._dom.find('#story-header-content').children().detach();
		this._storyClassesSelectedDom.setSelectedClasses(this._selectedClasses);
		this._dom.find('#story-header-content').append(
			this._storyClassesSelectedDom.getDom()
		);
	}
	this._renderStoryClassesList();

	this._storyClassesList.onSelect(function(selectedClass) {
		this._selectedClasses.push(selectedClass);
		this._selectedClasses = $.unique(this._selectedClasses);
		this._renderSelectedStories();
	}.bind(this));
	this._storyClassesSelectedDom.onAddNewClass(function() {
		this._renderStoryClassesList();
	}.bind(this));
	this._storyClassesSelectedDom.onRemoveClasses(function() {
		this._selectedClasses = [];
		this._renderStoryClassesList();
	}.bind(this));
	
}

StoryHeaderDom.prototype.getDom = function() {
	return this._dom;
}