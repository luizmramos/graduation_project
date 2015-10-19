function inherits(child, parent) {
	child.prototype = Object.create(parent.prototype);
	child.prototype.super = parent;
	child.prototype.constructor = child;
}
