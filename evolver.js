//Yay Javascript!
Number.prototype.mod = function(n) {
	return ((this%n)+n)%n;
};

//Experiment stuff
var experimentName = null;
var creatureWidth = 800;
var creatureHeight = 600;

//Canvas stuff
var tabletop = null;
var ctx = null;
var WIDTH;
var HEIGHT;
var animStepCount = 0;
var animStepModulo = 10;
var moreWidth = 16;
var moreHeight = 16;

//Ring stuff
var rings = new Array();
var ringInitialRadius = 80;
var ringInitialRadiusIncrement = 120;
var ringRadiusDecrement = 1.0;
var ringWidth = 10;
var ringColor = "150,150,255";
var ringOpacityDecrement = 0.8;
var ringOpacityIncrement = 0.05;

//Line stuff
var lineWidth = 1.5;
var lineColor = "255,127,0";

//Thumbnail stuff
var thumbInitialCount = 5; // Default value
var thumbCountIncrement = 5; // Default value
//Creatures are all in landscape orientation for now.
var thumbWidth = 72; // +2 to include the border
var thumbHeight = 54; // +2 to include the border

//Dialog stuff
var zoomerInitialOpacity = 0.7;
var tileMode = false;
var reflectMode = false;

//FBA stuff
var spreadSpringConstant = 0.2;
var wanderSpringConstant = 0.1;
var fbaIterations = 20;
var idealSpacing = 80;
var fbaSleepBetweenRings = 500;

var debug = false;
var TWOPI = Math.PI * 2;

$(document).ready(init);


function Ring(index) {

	var self = this; // O Javascript Joy!

	this.index = index;
	this.radius = ringInitialRadius + (ringInitialRadiusIncrement * index * Math.pow(ringRadiusDecrement, index-1));
	this.opacity = 0;
	this.targetOpacity = Math.pow(ringOpacityDecrement, index);
	this.broods = new Array();

	this.addThumb = function(index, thumb) {self.thumbs.splice(index, 0, thumb);};


	this.incrementOpacity = function() {
		if (self.opacity < self.targetOpacity) {
			self.opacity += ringOpacityIncrement;
		}
	};


	this.newThumbs = function(thumbCount, parentThumb) {
		var brood = self.getBrood(parentThumb);
		if (parentThumb != null) {
			parentThumb.childBrood = brood;
		}
		for (var i = 0; i < thumbCount; i++) {
			var thumb = new Thumb(self, parentThumb);
			brood.addThumb(thumb);
			thumb.generate();
		}
		self.distributeThumbs(true);
	};

	
	// Get the brood for a particular parent.
	this.getBrood = function(parentThumb) {
		var newBrood = new Brood(parentThumb);
		if (parentThumb == null) {
			// Ring 0.  Always one brood.
			if (self.broods.length == 0) {
				self.addBrood(0, newBrood);
			}
			return self.broods[0];
		} else {
			// Look for the right brood.
			for (var i=0; i<self.broods.length; i++) {
				var brood = self.broods[i];
				if (parentThumb == brood.parentThumb) {
					// That's our brood!
					newBrood = brood;
					return newBrood;
				} else if (brood.parentThumb.angle > parentThumb.angle) {
					// We've gone past it!
					self.addBrood(i, newBrood);
					return newBrood;
				}
			}
			// Couldn't find the right place. Push it on to the end.
			self.addBrood(self.broods.length, newBrood);
			return newBrood;
		}
	};
	
	
	this.addBrood = function(index, brood) {
		// Get our neighbors.
		var prev;
		var next;
		if (self.broods.length == 0) {
			prev = brood;
			next = brood;
		} else {
			prev = self.broods[(index-1).mod(self.broods.length)];
			next = self.broods[index.mod(self.broods.length)];
			// Figure out the starting extents of the new brood.
			// We want to make sure the extents are not within another brood.
			if (prev.contains(brood.parentThumb.angle)) {
				brood.minExtentAngle = prev.maxExtentAngle;
				brood.maxExtentAngle = brood.minExtentAngle;
			} else if (next.contains(brood.parentThumb.angle)) {
				brood.minExtentAngle = next.minExtentAngle;
				brood.maxExtentAngle = brood.minExtentAngle;
			} // else {leave them at the default: parentThumb.angle}
		}
		// Insert the brood.
		self.broods.splice(index, 0, brood);
		// Set the neighbors.
		prev.nextBrood = brood;
		brood.prevBrood = prev;
		brood.nextBrood = next;
		next.prevBrood = brood;
	};
	

	this.removeBrood = function(brood) {
		brood.nextBrood.prevBrood = brood.prevBrood;
		brood.prevBrood.nextBrood = brood.nextBrood;
		self.broods.splice(self.broods.indexOf(brood), 1);
	};
	

	// Figure out where in the thumb array to insert the new thumb.
	this.getNewThumbIndex = function(parentThumb) {
		if (parentThumb == null) {
			// Ring 0.
			return 0;
		} else if (self.thumbs.length == 0) {
			// Brand new ring.
			return 0;
		} else {
			// Find the correct location by iterating over all thumbs in the ring.
			var i = 0;
			for (i = 0; i < self.thumbs.length; i++) {
				var thumb = self.thumbs[i];
				if (parentThumb.angle < thumb.parentThumb.angle) {
					// This will group thumbs by their parents, so the connecting lines won't cross.
					break;
				} else if (parentThumb.angle == thumb.parentThumb.angle) {
					// We're adding more children to a parent that already has some.
					// Stick the new children in closest to the parent.
					if (parentThumb.angle < thumb.angle) {
						break;
					}
				}
			}			
			return i;
		}
	};


	this.distributeThumbsInSection = function(section) {
		var thumbSet = new Array();
		for (var i = 0; i < self.thumbs.length; i++) {
			var thumb = self.thumbs[i];
			if (thumb.section == section) {
				thumbSet.push(thumb);
			}
		}
		var spread = TWOPI/thumbInitialCount; // angle size of the section
		var spacing = spread/thumbSet.length; // angle between thumbs in this section
		var minAngle = (section/thumbInitialCount * TWOPI) - spread/2 + spacing/2;
		var maxAngle = (section/thumbInitialCount * TWOPI) + spread/2 + spacing/2;
		for (var i = 0; i < thumbSet.length; i++) {
			var thumb = thumbSet[i];
			var angle = minAngle + (i/thumbSet.length * (maxAngle-minAngle));
			thumb.slideTo(angle);
		}
	};


	this.distributeThumbs = function(recurseOut) {
		if (self.index == 0) {
			// Ring 0
			self.distributeInitialThumbs(recurseOut);
		} else {
			self.distributeBroods(recurseOut);
		}
	};
	
	
	this.distributeInitialThumbs = function(recurseOut) {
		var brood = self.broods[0];  // Ring 0 should only have one brood.
		for (var i = 0; i < brood.thumbs.length; i++) {
			var thumb = brood.thumbs[i];
			var angle = i/brood.thumbs.length * TWOPI;
			thumb.slideTo(angle);
		}
		// Do it for the next ring out, too?
		if (recurseOut && (rings.length > self.index+1)) {
			// Do it a little bit in the future.  It looks better that way.
			window.setTimeout(rings[self.index+1].distributeThumbs, fbaSleepBetweenRings, true);
		}
	};
	
	
	this.distributeBroods = function(recurseOut) {
		// Figure out how all the broods fit together.
		for (var i=0; i<fbaIterations; i++) {
			for (var j=0; j<self.broods.length; j++) {
				self.broods[j].calculateExtents();
			}
		}
		// Now place all the thumbs.
		for (var j=0; j<self.broods.length; j++) {
			self.broods[j].distributeThumbs();
		}
		// Do it for the next ring out, too?
		if (recurseOut && (rings.length > self.index+1)) {
			// Do it a little bit in the future.  It looks better that way.
			window.setTimeout(rings[self.index+1].distributeThumbs, fbaSleepBetweenRings, true);
		}
	};

}


function Brood(parentThumb) {

	var self = this; // O Javascript Joy!

	this.parentThumb = parentThumb;
	this.thumbs = new Array();
	this.minExtentAngle = (parentThumb == null) ? 0 : parentThumb.angle;
	this.maxExtentAngle = (parentThumb == null) ? 0 : parentThumb.angle;
	this.prevBrood = null;
	this.nextBrood = null;

	this.addThumb = function(thumb) {
		self.thumbs.push(thumb);
		thumb.brood = self;
		if (self.parentThumb != null) {
			$(self.parentThumb.thumb).addClass("mutated");
		}
		self.idealSpread = self.thumbs.length * Math.asin(idealSpacing/thumb.ring.radius);
	};

	
	this.removeThumb = function(thumb) {
		self.thumbs.splice(self.thumbs.indexOf(thumb), 1);
		self.idealSpread = self.thumbs.length * Math.asin(idealSpacing/thumb.ring.radius);
	}
	
	
	this.hideThumbs = function() {
		for (var i = 0; i < self.thumbs.length; i++) {
			self.thumbs[i].hide();
		}
	}

	
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
		var wander = parentThumb.angle - self.minExtentAngle;
		netForce += wanderSpringConstant * wander;
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
		wander = self.maxExtentAngle - parentThumb.angle;
		netForce += wanderSpringConstant * wander;
		self.maxExtentAngle -= netForce;

		// Handle collisions with the next brood.
		if (self.nextBrood.contains(self.maxExtentAngle)) {
			self.maxExtentAngle -= Math.abs(netForce/2);
			self.nextBrood.minExtentAngle += Math.abs(netForce/2);
		}

	};


	this.distributeThumbs = function() {
		var spread = (self.maxExtentAngle-self.minExtentAngle);
		for (var i=0; i<self.thumbs.length; i++) {
			var angle = self.minExtentAngle + (i/self.thumbs.length * spread) + (spread/self.thumbs.length/2);
			self.thumbs[i].slideTo(angle);
		}
	};

}


function Thumb(ring, parentThumb) {

	var self = this; // O Javascript Joy!

	this.name = null;
	this.div = null;
	this.img = new Image(); // The full-size image.
	this.img.src = null;
	this.thumb = new Image(); // The thumbnail.
	this.thumb.src = "loading.gif"; // Initialize it with the "loading" image.
	this.thumb.className = "qm";
	this.on_arrive_src = "loading.gif"; // The thumb src to use when we arrive at our destination.
	this.del = new Image();
	this.del.src = "empty.gif";
	this.page_url = null;
	this.gallery_url = null;
	this.ring = ring;
	this.brood = null;  // What I'm part of.
	this.childBrood = null;  // What my children are part of.
	this.angle = null;
	this.smallCornerCoords = null;  // These two are for convenience, and so that
	this.largeCornerCoords = null;  // we always know where the img should be, even while it's animating.
	this.parentThumb = parentThumb;
	this.hidden = false;

	this.initialize = function() {

	    self.div = $("<div/>").addClass("tdiv");
	    
		// Add the hover handler.
		$(self.div).hover(
				function() {
					$(self.div).css("z-index", 1);
			        $(self.del).show();
			        $("#canvas").css({"background-image": "url(" + self.img.src + ")"});
			        if (!tileMode && !reflectMode) {
	                    $("#canvas").css({
	                        "background-repeat": "no-repeat",
	                        "background-position": "center center"
	                    });
			        }
				},
				function() {
			        $(self.del).hide();
					$(self.div).css("z-index", 0);
                    $("#canvas").css({"background-image": "none"});
				}
		);

		// Insert it in the document.
		$(self.thumb).css({
			width: thumbWidth, 
			height: thumbHeight
		});
		self.div.append(self.thumb);
        self.div.append(self.del);
        $(self.del).addClass("delete");
        $(self.del).hide();
		if (debug) {
			self.debugText = $("<div class='debugText'></div>");
			self.div.append(self.debugText);
		}
        $("#tabletop").append(self.div);

		// Set the location.
		if (self.parentThumb == null) {
			// Initial image.  Place it at the origin.
			self.placeAt(new Array(0, 0));
		} else {
			// Child image.  Place it at the parent's location.
			self.angle = self.parentThumb.angle;
			var coords = toCenterFromThumb(self.parentThumb);
			self.placeAt(coords);
		}

	};


	this.generate = function() {
		var data = {"e": experimentName, "rnd": Math.random()};
		if (self.parentThumb != null) {
			data["p"] = self.parentThumb.name;
		}
		$.ajax({
			type: "GET",
			url: "/cgi-bin/new_creature.py", 
			data: data,
			dataType: "json",
			async: true,
			success: self.onLoad,
			error: self.onFail // Doesn't get called when we're using jsonp.
		});
	};


	this.placeAt = function(coords) {
		self.smallCornerCoords = toCorner(coords);
		self.largeCornerCoords = toDoubleSizeCorner(coords);
		self.div.css({
			left: self.smallCornerCoords[0] + "px",
			top: self.smallCornerCoords[1] + "px"
		});
	};


	this.slideTo = function(angle) {
		self.angle = angle;
		var x = Math.sin(self.angle) * self.ring.radius;
		var y = Math.cos(self.angle) * self.ring.radius;
		var center = new Array(x, y);
		self.smallCornerCoords = toCorner(center);
		self.largeCornerCoords = toDoubleSizeCorner(center);
		self.div.animate({
			left: self.smallCornerCoords[0] + "px",
			top: self.smallCornerCoords[1] + "px"
		}, {
			easing: "sineEaseInOut",
			duration: 1000,
			step: function(value, animEvent) {
				handleAnimation(animEvent);
			},
			complete: function() {
				  self.thumb.src = self.on_arrive_src;
				  drawCanvas();
				  }
		});
		if (debug) {
			self.debugText.html(angle.toFixed(2) + "\u00B0");
		}
	};


	this.onLoad = function(data) {
		// Hide the loading message.
		$("#msg").css({display: "none"});
		// Set the returned attributes.
		self.name = data.name;
		self.img.src = data.image_url;
		self.thumb.src = data.thumb_url;
		self.on_arrive_src = data.thumb_url;
		self.page_url = data.page_url;
		self.gallery_url = data.gallery_url;
		self.del.src = "delete.gif";
		// Add the mutation handler.
		$(self.thumb).click(self.openDialog);
		// Change the class.
		$(self.thumb).removeClass("qm").addClass("thumb");
		// Add the delete handler.
		$(self.del).click(self.doHide);
	};


	this.onFail = function() {
		self.thumb.src = "broken.jpg";
		self.on_arrive_src = "broken.jpg";
	};

	
	this.doHide = function() {
        var data = {"e": experimentName, "c": self.name};
        $.ajax({
            type: "GET",
            url: "/cgi-bin/hide_creature.py", 
            data: data,
            dataType: "json",
            async: true,
            error: self.onFail // Doesn't get called when we're using jsonp.
        });
		hideThumb(self);
	};
	
	
	this.hide = function() {
		self.hidden = true;
		$(self.thumb).animate(
				{
					opacity: 0
				}, 
				{
					easing : "quadEaseOut",
					complete: function() {
						$(self.thumb).hide();
					}
				});
        $(self.del).hide();
		if (debug) {
			self.debugText.hide();
		}
	};
	
	
	this.mutate = function() {
		newThumbs(thumbCountIncrement, self);
	};


	this.openDialog = function() {

	    // Unset the background.
        $("#canvas").css({"background-image": "none"});

		// Show & zoom the zoomer.  We start it off at the same location & size as the thumb,
		// then animate it to where we think the dialog will display it.
		$("#zoomer").attr("src", self.img.src);
		$("#creature").attr("src", self.img.src);  // The dialog seems to work better if we set this up here.
		$("#zoomer").css(
				{
					display: "block", 
					width: self.thumb.width, 
					height: self.thumb.height,
					opacity: zoomerInitialOpacity
				});
		$("#zoomer").offset($(self.thumb).offset());
		$("#zoomer").animate(
				{
					// Dialog position is always relative to the window, not the container.
					top: window.innerHeight/2 - self.img.height/2 - 20, // Bump up to account for dialog buttons.
					left: window.innerWidth/2 - self.img.width/2, 
					width: self.img.width, 
					height: self.img.height,
					opacity: 1
				}, 
				{
					easing : "quadEaseOut",
					complete : function() {self.openDialog2();}
				});
	    
	};

	this.openDialog2 = function() {

		// Open the dialog.
		$("#creature").css({display: "block"}); // It's hidden before the first dialog opens.
		$("#dialog").dialog({
			title: "Creature " + self.name,
			height: "auto",
			width: "auto",
			position: "center",
			modal: true,
			resizable: false,
			buttons: { 
				"Mutate!": function() { self.closeDialog(); self.mutate(); },
				"More Info": function() { window.open(self.page_url); },
				"Add To Gallery": function() { window.open(self.gallery_url); },
                "Delete": function() { self.closeDialog(); self.doHide(); },
				"Close": function() { self.closeDialog(); }
			}
		});
		// Change the close-icon handler.  Little hacky, I know.
		$(".ui-dialog-titlebar-close").unbind();
		$(".ui-dialog-titlebar-close").click(self.closeDialog);

		// Hide the zoomer.
		$("#zoomer").css({display: "none"});
		
	};


	this.closeDialog = function() {

		// Place & show the zoomer.  We start at the current location of the creature.
		$("#zoomer").css(
				{
					display: "block",
					top: $("#creature").offset().top,
					left: $("#creature").offset().left
				}
		);

		// Close the dialog.
		$("#dialog").dialog("close");

		// Un-zoom the zoomer.  We zoom to the location and size of the thumbnail.
		$("#zoomer").animate(
				{
					top: $(self.thumb).offset().top+1, // +1 to account for the border
					left: $(self.thumb).offset().left+1, // +1 to account for the border 
					width: self.thumb.width, 
					height: self.thumb.height,
					opacity: zoomerInitialOpacity
				}, 
				{
					easing : "quadEaseOut",
					duration : "slow",
					complete : function() {self.closeDialog2();}
				});

	};

	this.closeDialog2 = function() {
		// Hide the zoomer.
		$("#zoomer").css({display: "none"});
	};

	// Call the initialization method.
	this.initialize();

}


function init() {

	// Initialize the configuration.
	$.ajax({
		type: "GET",
		url: "./config.json", 
		dataType: "json",
		async: false,  // Make sure we get it before we move on.
		success: function(data) {initConfig(data);}
	});

	// The frame, with scrollbars.  This is a relative size to the browser window.
	// The div inside the frame.  This is a fixed size, usually larger than the frame.
	tabletop = document.getElementById("tabletop");

	// Get the dims of the frame & center the scrollbars.
	WIDTH = tabletop.clientWidth - 2; // -2 so we fit inside.
	HEIGHT = tabletop.clientHeight - 2; // -2 so we fit inside.
	var jframe = $("#frame");
	jframe.scrollTop(HEIGHT/2 - jframe.innerHeight()/2);
	jframe.scrollLeft(WIDTH/2 - jframe.innerWidth()/2);

	// Make the canvas the same size as the tabletop.
	var canvas = document.getElementById("canvas");
	canvas.width = WIDTH;
	canvas.height = HEIGHT;

	// Get the 2D context.
	ctx = null;
	if (canvas.getContext) {
		ctx = canvas.getContext("2d");
		// Translate the origin to the center so the math is easier.
		ctx.translate(WIDTH / 2, HEIGHT / 2);
	} else {
		msg("<h2>Doh! Your browser does not support the &lt;canvas&gt; element!</h2>Perhaps you should switch to a modern browser such as <a href='http://www.rockmelt.com/'>Rockmelt</a>.");
	}

	// Place the + button.
	initMore();

	// Init the creatures.
	$.ajax({
		type: "GET",
		url: "/cgi-bin/get_creatures.py", 
		data: {"e": experimentName},
		dataType: "json",
		async: false,  // Make sure we get it before we move on.
		success: function(data) {initCreatures(data);}
	});

}


function initConfig(data) {

	if (data == null) {
		// The AJAX call failed.  Use the defaults instead.
		return;
	}

	experimentName = data.name;
	creatureWidth = data.img_width;
	creatureHeight = data.img_height
	thumbInitialCount = data.start;
	thumbCountIncrement = data.progeny;
	tileMode = data.tile_mode;
	reflectMode = data.reflect_mode;
	debug = data.debug;

}


function initMore() {
	var corner = new Array(2);
	corner[0] = 0 - moreWidth/2 + WIDTH/2;
	corner[1] = 0 - moreHeight/2 + HEIGHT/2;
	$("#more").css({
		width: moreWidth, 
		height: moreHeight,
		left: corner[0] + "px",
		top: corner[1] + "px"
	});
	$("#more").click(function() {
		rings[0].newThumbs(1, null);
	});
}


function initCreatures(data) {

	if (data == null || data.length == 0) {
		// Create the initial thumbs.
		newThumbs(thumbInitialCount, null);
	} else {
		// Restore the existing thumbs.
		restoreThumbs(data);
	}

}


function restoreThumbs(thumbInfos) {

	// Organize them all by name so we can find them quickly.
	var thumbsByName = {}; // { thumb_name : thumbInfo }
	for (var i=0; i<thumbInfos.length; i++) {
		var thumbInfo = thumbInfos[i];
		thumbsByName[thumbInfo.name] = thumbInfo;
	}

	// Organize them all by ring so we can paint each ring.
	// We set thumbInfo.ringIndex so we can determine the parent's ring.
	var thumbsByRing = new Array();
	while (thumbInfos.length) {
		var thumbInfo = thumbInfos.shift();
        if (thumbInfo.hidden) {
            continue;
        } else if (thumbInfo.parent == null) {
			// Ring 0.  We can place it now.
			thumbInfo.ringIndex = 0;
		} else {
			if (thumbInfo.parent in thumbsByName) {
				var parentThumbInfo = thumbsByName[thumbInfo.parent];
				if (parentThumbInfo.hidden) {
					thumbInfo.hidden = true;
		            continue;
				} else if ("ringIndex" in parentThumbInfo) {
					// The parent's been placed, we can place the child now.
					thumbInfo.ringIndex = parentThumbInfo.ringIndex + 1;
				} else {
					// We'll have to place it later.  Push it back on the stack.
					thumbInfos.push(thumbInfo);
					continue;
				}
			} else {
				// Parent doesn't exist.  Toss the child.
				continue;
			}
		}
		// Do we need a new ring?
		if (thumbInfo.ringIndex >= thumbsByRing.length) {
			thumbsByRing.push(new Array());
		}
		// Add the thumbInfo to the ring.
		thumbsByRing[thumbInfo.ringIndex].push(thumbInfo);
	}

	// Create each Ring and populate it with Thumbs.
	for (var i=0; i<thumbsByRing.length; i++) {
		
		// Create the Ring.
		var ring = new Ring(i);
		rings.push(ring);
		
		// Walk through each thumbInfo for this ring.
		for (var j=0; j<thumbsByRing[i].length; j++) {
			
			var thumbInfo = thumbsByRing[i][j];
			
			// Set the parent & section.
			var parent = null;
			if (thumbInfo.parent != null) {
				var parentThumbInfo = thumbsByName[thumbInfo.parent];
				parent = parentThumbInfo.thumb; // Could be null.
			}
			
			// Create the Thumb object & set a bunch of known properties.
			var thumb = new Thumb(ring, null); // A little hack to get them all to appear at the origin.
			thumb.parentThumb = parent;
			thumb.onLoad(thumbInfo);
			thumb.thumb.src = "loading.gif"; // We need something opaque until it arrives at its destination.
			
			// Insert the Thumb in the Ring in the correct location.
			var brood = ring.getBrood(parent);
			if (parent != null) {
				parent.childBrood = brood;
			}
			brood.addThumb(thumb);
			
			// Add the Thumb to the thumbInfo so we can access it during later rings.
			thumbInfo.thumb = thumb;
			
		}
		
		// Now distribute the thumbs around the ring.
		// We have to do this before moving on to the next ring
		// because the positions in the next ring depend on the positions in this ring.
		ring.distributeThumbs(false);
		
	}

}


function newThumbs(thumbCount, parentThumb) {

	// What ring is this for?
	if (parentThumb == null) {
		ringIndex = 0;
		msg("Hang on, it takes a little while to create the first generation...");
	} else {
		ringIndex = parentThumb.ring.index + 1;
	}

	// Do we need a new ring?
	if (ringIndex >= rings.length) {
		rings.push(new Ring(ringIndex));
	}

	// Create the images.
	var ring = rings[ringIndex];
	ring.newThumbs(thumbCount, parentThumb);

}


function hideThumb(thumb) {
	thumb.hide();
	thumb.brood.removeThumb(thumb);
	if (thumb.brood.thumbs.length == 0) {
		thumb.ring.removeBrood(thumb.brood);
	}
	if (thumb.childBrood != null) {
		thumb.ring.distributeThumbs(false);
		window.setTimeout(hideBroods, fbaSleepBetweenRings, [thumb.childBrood]);
	} else {
		thumb.ring.distributeThumbs(true);
	}
}


function hideBroods(broods) {
	var childBroods = [];
	var ring;
	for (var i = 0; i < broods.length; i++) {
		var brood = broods[i];
		for (var j = 0; j < brood.thumbs.length; j++) {
			var thumb = brood.thumbs[j];
			ring = thumb.ring;
			if (thumb.childBrood != null) {
				childBroods.push(thumb.childBrood);
			}
		}
		brood.hideThumbs();
		ring.removeBrood(brood);
	}
	if (childBroods.length > 0) {
		ring.distributeThumbs(false);
		window.setTimeout(hideBroods, fbaSleepBetweenRings, childBroods);
	} else {
		ring.distributeThumbs(true);
	}
}


function handleAnimation(animEvent) {

	// This gets called for each value change of each property being animated.
	// To cut down on redraws, we'll proceed only occasionally.
	if (animStepCount++ % animStepModulo != 0) {
		return;
	}

	drawCanvas();

	// Increase the opactiy of the rings if necessary.
	for (var i = 0; i < rings.length; i++) {
		rings[i].incrementOpacity();
	}

}


function drawCanvas() {

	if (ctx == null) {
		return;
	}

	// Clean slate!
	ctx.clearRect(-ctx.canvas.width/2, -ctx.canvas.height/2, ctx.canvas.width, ctx.canvas.height);

	if (debug) {
		// Draw radial lines.
		ctx.lineWidth = 0.5;
		ctx.strokeStyle = "rgb(255,0,0)";
		ctx.font = "20pt Arial";
		ctx.textAlign = "center";
		ctx.beginPath();
		for (var i = 0; i < thumbInitialCount; i++) {
			ctx.moveTo(0, 0);
			var angle = (i+0.5)/thumbInitialCount * TWOPI;
			var x = Math.sin(angle) * (ringInitialRadius + 5 * ringInitialRadiusIncrement);
			var y = Math.cos(angle) * (ringInitialRadius + 5 * ringInitialRadiusIncrement);
			ctx.lineTo(x, y);
			if (ctx.strokeText) {
				x = Math.sin(angle) * (ringInitialRadius + 3 * ringInitialRadiusIncrement);
				y = Math.cos(angle) * (ringInitialRadius + 3 * ringInitialRadiusIncrement);
				ctx.strokeText(angle.toFixed(2) + "\u00B0", x, y);
			}
		}
		ctx.stroke();
	}

	// Iterate over the rings.
	for (var i = 0; i < rings.length; i++) {

		var ring = rings[i];

		// Draw the ring.
		ctx.lineWidth = ringWidth;
		ctx.strokeStyle = "rgba(" + ringColor + "," + ring.opacity + ")";
		ctx.beginPath();
		ctx.arc(0, 0, ring.radius, 0, Math.PI * 2, true);
		ctx.stroke();

		// If this isn't Ring 0.
		if (i > 0) {
			
			if (debug) {
				// Draw the broods.
				if (i > 0) {
					for (var j = 0; j < ring.broods.length; j++) {
						var brood = ring.broods[j];
						if (brood.parentThumb.hidden) {
							continue;
						}
						ctx.fillStyle = "rgb(200,255,200)";
						ctx.beginPath();
						var coords = toCenterFromThumb(brood.parentThumb);
						ctx.moveTo(coords[0], coords[1]);
						for (var k = 0; k < brood.thumbs.length; k++) {
							coords = toCenterFromThumb(brood.thumbs[k]);
							ctx.lineTo(coords[0], coords[1]);
						}
						ctx.closePath();
						ctx.fill();
					}
				}
			}

			// Draw the lines between thumbs.
			ctx.lineWidth = lineWidth;
			ctx.strokeStyle = "rgb(" + lineColor + ")";
			ctx.beginPath();
			for (var j = 0; j < ring.broods.length; j++) {
				var brood = ring.broods[j];
				for (var k=0; k<brood.thumbs.length; k++) {
					var thumb = brood.thumbs[k];
					if (thumb.parentThumb.hidden) {
						continue;
					}
					var startCoords = toCenterFromThumb(thumb.parentThumb);
					ctx.moveTo(startCoords[0], startCoords[1]);
					var endCoords = toCenterFromThumb(thumb);
					ctx.lineTo(endCoords[0], endCoords[1]);
				}
			}
			ctx.stroke();
			
		}

		if (debug) {
			if (ctx.strokeText) {
				// Draw the radius.
				ctx.lineWidth = 0.5;
				ctx.strokeStyle = "rgb(255,0,0)";
				ctx.font = "20pt Arial";
				ctx.textAlign = "center";
				ctx.beginPath();
				ctx.strokeText(""+Math.round(ring.radius), 0, ring.radius);
				ctx.stroke();
			}
		}
	}

}


function msg(str) {
	var jdiv = $('#msg');
	jdiv.html("<center><font>" + str + "</font></center>");
	var left = $("body").width()/2 - jdiv.outerWidth()/2;
	var top = $("body").height()/2 - jdiv.outerHeight()/2 - ringInitialRadius - thumbHeight;
	jdiv.css({
		"left": left + "px",
		"top": top + "px",
		"z-index": 2
	});
}


//This converts the center of an image relative to the center of the canvas
//into coordinates for stylesheet placement:
//the top left corner relative to the origin.
function toCorner(center) {
	var corner = new Array(2);
	corner[0] = center[0] - thumbWidth/2 + WIDTH/2;
	corner[1] = center[1] - thumbHeight/2 + HEIGHT/2;
	return corner;
}

function toDoubleSizeCorner(center) {
	var corner = new Array(2);
	corner[0] = center[0] - thumbWidth + WIDTH/2;
	corner[1] = center[1] - thumbHeight + HEIGHT/2;
	return corner;
}


//This converts the top left corner of an image relative to the origin
//into coordinates for calculations:
//the center of the image relative to the center of the canvas.
function toCenter(corner) {
	var center = new Array(2);
	center[0] = corner[0] + thumbWidth/2 - WIDTH/2;
	center[1] = corner[1] + thumbHeight/2 - HEIGHT/2;
	return center;
}

function toDoubleSizeCenter(corner) {
	var center = new Array(2);
	center[0] = corner[0] + thumbWidth - WIDTH/2;
	center[1] = corner[1] + thumbHeight - HEIGHT/2;
	return center;
}

//Convenience.
function toCenterFromThumb(thumb) {
	return toCenter(new Array(thumb.div[0].offsetLeft, thumb.div[0].offsetTop));
}

function toCenterFromDoubleSizeThumb(thumb) {
	return toDoubleSizeCenter(new Array(thumb.div[0].offsetLeft, thumb.div[0].offsetTop));
}
