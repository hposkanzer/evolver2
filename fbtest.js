//Yay Javascript!
Number.prototype.mod = function(n) {
	return ((this%n)+n)%n;
};

var TWOPI = Math.PI * 2;
var colors = new Array(
		"255,0,0",
		"0,255,0",
		"255,165,0",
		"0,0,255",
		"255,255,0"
);

//Canvas stuff
var ctx = null;
var WIDTH;
var HEIGHT;

//Ring stuff
var ringInitialRadius = 100;
var ringWidth = 10;
var ringColor = "150,150,255";
var ringOpacityDecrement = 0.8;

//Thumbnail stuff
var parentCount = 5;
var parents = new Array(parentCount);
var thumbRadius = 20;
var thumbColors = new Array(colors.length);
for (var i=0; i<colors.length; i++) {
	thumbColors[i] = "rgb(" + colors[i] + ")";
}

//Line stuff
var lineWidth = 1.5;
var lineColor = "255,127,0";

//FBA stuff
var spreadSpringConstant = 0.2;
var parentSpringConstant = 0.1;
var fbaIterations = 20;
var fbaSleep = 1;
var maxSpread = TWOPI/3;
var idealSpacing = thumbRadius * 3;
var maxSpreadColors = new Array(colors.length);
for (var i=0; i<colors.length; i++) {
	maxSpreadColors[i] = "rgba(" + colors[i] + ",0.5)";
}

$(document).ready(init);

function init() {

	var jframe = document.getElementById("frame");
	WIDTH = jframe.clientWidth - 2; // -2 so we fit inside.
	HEIGHT = jframe.clientHeight - 2; // -2 so we fit inside.

	// Make the canvas the same size as the tabletop.
	var canvas = document.getElementById("canvas");
	canvas.width = WIDTH;
	canvas.height = HEIGHT;

	// Get the 2D context.
	if (canvas.getContext) {
		ctx = canvas.getContext("2d");
		// Translate the origin to the center so the math is easier.
		ctx.translate(WIDTH / 2, HEIGHT / 2);
	}

	drawCanvas();

}


function drawCanvas() {

	if (ctx == null) {
		return;
	}

	var broods = new Array();
	for (var i = 0; i < parentCount; i++) {
		parents[i] = i/parentCount * TWOPI; 
	}

	redraw(broods);

	broods.push(new Brood(0, 5));
	broods.push(new Brood(1, 5));
	//broods.push(new Brood(3, 7));
	setBroodNeighbors(broods);
	
	drawLoop(broods, 0);

}


function setBroodNeighbors(broods) {
	for (var i=0; i<broods.length; i++) {
		var j = (i+1) % broods.length;
		broods[j].prevBrood = broods[i];
		broods[i].nextBrood = broods[j];
	}
}

function drawLoop(broods, i) {
	$("#iter").text("Iteration " + i);
	redraw(broods);
	if (i < fbaIterations) {
		for (var j=0; j<broods.length; j++) {
			broods[j].calculateExtents();
		}
		window.setTimeout(drawLoop, fbaSleep, broods, i+1);
	} else {
		window.setTimeout(tweak, 5000, broods);
	}

}


function tweak(broods) {
	if (broods.length == 2) {
		// Insert a new brood in the open.
		var brood = new Brood(3, 7);
		insertBrood(broods, brood, 0);
//		brood.minExtentAngle = (broods[1].maxExtentAngle.mod(TWOPI) + broods[0].minExtentAngle.mod(TWOPI)) / 2;
//		brood.maxExtentAngle = brood.minExtentAngle;
//		broods.push(brood);
//		setBroodNeighbors(broods);
		drawLoop(broods, 0);
	} else if (broods[2].size == 5) {
		// Add more to a brood.
		broods[2].setSize(12);
		drawLoop(broods, 0);
	} else if (parents[1] < (1/parentCount * TWOPI) + 0.1) {
		// Shift a parent.
		parents[1] += 0.5;
		drawLoop(broods, 0);
	} else if (broods.length == 3) {
		// Insert a new brood where there's no room.
		var brood = new Brood(2, 5);
		insertBrood(broods, brood, 3);
//		brood.minExtentAngle = (broods[1].maxExtentAngle.mod(TWOPI) + broods[2].minExtentAngle.mod(TWOPI)) / 2;
//		brood.maxExtentAngle = brood.minExtentAngle;
//		broods.splice(2, 0, brood);
//		setBroodNeighbors(broods);
		drawLoop(broods, 0);
	}
}


// i = The index before which to insert the new brood.
function insertBrood(broods, newBrood, i) {
	i = i % broods.length;
	var prevBrood = broods[(i-1).mod(broods.length)];
	var nextBrood = broods[i];
	// Shift the extents so they're not within another brood.
	if (prevBrood.contains(parents[newBrood.parent])) {
		newBrood.minExtentAngle = prevBrood.maxExtentAngle;
		newBrood.maxExtentAngle = newBrood.minExtentAngle;
	} else if (nextBrood.contains(parents[newBrood.parent])) {
		newBrood.minExtentAngle = nextBrood.minExtentAngle;
		newBrood.maxExtentAngle = newBrood.minExtentAngle;
	} // else {leave them at the parent's angle}
	broods.splice(i, 0, newBrood);
	setBroodNeighbors(broods);
}


function redraw(broods) {
	ctx.clearRect(-ctx.canvas.width/2, -ctx.canvas.height/2, ctx.canvas.width, ctx.canvas.height);
	drawRings(3);
	drawParents();
	for (var i=0; i<broods.length; i++) {
		broods[i].draw();
	}
}


function Brood(parent, size) {

	var self = this; // O Javascript Joy!

	this.parent = parent;
	this.minExtentAngle = parents[parent];
	this.maxExtentAngle = parents[parent];
	this.prevBrood = null;
	this.nextBrood = null;

	this.setSize = function(size) {
		this.size = size;
		this.idealSpread = this.size * Math.asin(idealSpacing/(ringInitialRadius*2));
	};
	this.setSize(size);

	
	this.contains = function(angle) {
		var otherAngle = angle.mod(TWOPI);
		var myMin = self.minExtentAngle.mod(TWOPI);
		var myMax = self.maxExtentAngle.mod(TWOPI);
		if (myMin > myMax) {
			return (myMin < otherAngle) || (myMax > otherAngle);
		} else {
			return (myMin < otherAngle) && (myMax > otherAngle);
		}
	};

	
	this.calculateExtents = function() {

		// First the min extent.
		var netForce = 0.0;
		// Adjust for the distance to the max extent.
		var spread = self.maxExtentAngle - self.minExtentAngle;
		netForce += spreadSpringConstant * (spread - self.idealSpread);
		// Adjust for the distance to the parent.
		var wander = parents[self.parent] - self.minExtentAngle;
		netForce += parentSpringConstant * wander;
		self.minExtentAngle += netForce;
		
		// Handle collisions with the previous brood.
		if (self.prevBrood.contains(self.minExtentAngle)) {
			self.minExtentAngle += Math.abs(netForce/2);
			self.prevBrood.maxExtentAngle -= Math.abs(netForce/2);
		}

		// Now the max extent.
		netForce = 0.0;
		// Adjust for the distance to the min extent.
		spread = self.maxExtentAngle - self.minExtentAngle;
		netForce += spreadSpringConstant * (spread - self.idealSpread);
		// Adjust for the distance to the parent.
		wander = self.maxExtentAngle - parents[self.parent];
		netForce += parentSpringConstant * wander;
		self.maxExtentAngle -= netForce;

		// Handle collisions with the next brood.
		if (self.nextBrood.contains(self.maxExtentAngle)) {
			self.maxExtentAngle -= Math.abs(netForce/2);
			self.nextBrood.minExtentAngle += Math.abs(netForce/2);
		}

	};


	this.draw = function() {

		drawRadius(parents[self.parent]-self.idealSpread/2, thumbColors[self.parent]);
		drawRadius(parents[self.parent]+self.idealSpread/2, thumbColors[self.parent]);

		drawRadius(self.minExtentAngle, maxSpreadColors[self.parent]);
		drawRadius(self.maxExtentAngle, maxSpreadColors[self.parent]);

		if (ctx.strokeText) {
			ctx.lineWidth = 0.5;
			ctx.font = "10pt Arial";
			ctx.textAlign = "center";
			ctx.beginPath();
			ctx.strokeStyle = thumbColors[self.parent];
			var x = Math.sin(self.minExtentAngle) * ringInitialRadius*3;
			var y = Math.cos(self.minExtentAngle) * ringInitialRadius*3;
			ctx.strokeText("<" + self.minExtentAngle.toFixed(2) + "\u00B0", x, y);
			x = Math.sin(self.maxExtentAngle) * ringInitialRadius*3;
			y = Math.cos(self.maxExtentAngle) * ringInitialRadius*3;
			ctx.strokeText(">" + self.maxExtentAngle.toFixed(2) + "\u00B0", x, y);
			ctx.stroke();
		}


		var spread = (self.maxExtentAngle-self.minExtentAngle);
		for (var i = 0; i < self.size; i++) {
			var angle = self.minExtentAngle + (i/self.size * spread) + (spread/self.size/2);
			drawThumb(angle, ringInitialRadius*2, thumbColors[self.parent]);
		}

	};

}


function drawParents() {
	for (var i = 0; i < parents.length; i++) {
		var angle = i/parentCount * TWOPI;
		drawRadius(parents[i], "gray");
		drawThumb(parents[i], ringInitialRadius, thumbColors[i]);
	}
}


function drawRings(count) {

	var radius = ringInitialRadius;
	var opacity = 1.0;
	for (var i = 0; i < count; i++) {
		ctx.lineWidth = ringWidth;
		ctx.strokeStyle = "rgba(" + ringColor + "," + opacity + ")";
		ctx.beginPath();
		ctx.arc(0, 0, radius, 0, Math.PI * 2, true);
		ctx.stroke();
		radius += ringInitialRadius;
		opacity *= ringOpacityDecrement;
	}

}


function drawThumb(angle, radius, color) {

	ctx.lineWidth = 0;
	ctx.fillStyle = color;
	ctx.beginPath();
	var x = Math.sin(angle) * radius;
	var y = Math.cos(angle) * radius;
	ctx.arc(x, y, thumbRadius, 0, Math.PI * 2, true);
	ctx.fill();

}


function drawRadius(angle, color) {

	ctx.lineWidth = 1.0;
	ctx.strokeStyle = color;
	ctx.beginPath();
	ctx.moveTo(0, 0);
	x = Math.sin(angle) * WIDTH/2;
	y = Math.cos(angle) * WIDTH/2;
	ctx.lineTo(x, y);
	ctx.stroke();

}