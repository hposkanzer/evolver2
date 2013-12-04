//Yay Javascript!
Number.prototype.mod = function(n) {
	return ((this%n)+n)%n;
};

//Experiment stuff
var experimentName = null;
var creatureWidth = 800;
var creatureHeight = 600;
var thumbWidth = 152; // +2 to include the border
var thumbHeight = 114; // +2 to include the border
var thumbPadding = 10;
var tileMode = false;
var reflectMode = false;

// Generate stuff
var CONCURRENCY = 5;
var cols = 5;
var rows = 5;

// Dialog stuff
var byIndex = [];
var currentCreature = null;

var debug = false;

$(document).ready(init);


function Thumb(index, td) {

	var self = this; // O Javascript Joy!

	this.name = null;
	this.index = index;
	this.td = td;
	this.img = new Image(); // The full-size image.
	this.img.src = null;
	this.thumb = new Image(); // The thumbnail.
	this.thumb.src = "loading.gif"; // Initialize it with the "loading" image.
	this.thumb.className = "qm";
	this.on_arrive_src = "loading.gif"; // The thumb src to use when we arrive at our destination.
	this.page_url = null;
	this.gallery_url = null;

	this.initialize = function() {
	    byIndex[self.index] = self;
		self.td.append(self.thumb);
		if (tileMode || reflectMode) {
		    $(self.thumb).hover(
		            function() {
		                $(document.body).css({"background-image": "url(" + self.img.src + ")"});
		            },
		            function() {
		                $(document.body).css({"background-image": "none"});
		            }
		    );
		}
	};


	this.generate = function(tr) {
	    console.log("Generating...");
		var data = {"e": experimentName, "rnd": Math.random()};
		var req = $.ajax({
			type: "GET",
			url: "/cgi-bin/new_creature.py", 
			data: data,
			dataType: "json",
			async: true,
		});
		req.fail(self.onFail);
        req.fail(initCreatureInner);
		req.done(self.onLoad);
		req.done(initCreatureInner);
	};


	this.onLoad = function(data) {
		// Set the returned attributes.
	    console.log("Generated " + data.name + ".");
		self.name = data.name;
		self.img.src = data.image_url;
		self.thumb.src = data.thumb_url;
		self.on_arrive_src = data.thumb_url;
		self.page_url = data.page_url;
		self.gallery_url = data.gallery_url;
		// Add the dialog handler.
		$(self.thumb).click(function() {
		    currentCreature = self;
		    openDialog();
		});
		// Change the class.
		$(self.thumb).removeClass("qm").addClass("thumb");
	};


	this.onFail = function() {
		self.thumb.src = "broken.jpg";
		self.on_arrive_src = "broken.jpg";
	};

	
	// Call the initialization method.
	this.initialize();

}


function openDialog() {
    
    $("#creature").attr("src", currentCreature.img.src);

    // Show & zoom the zoomer.  We start it off at the same location & size as the thumb,
    // then animate it to where we think the dialog will display it.
    $("#zoomer").show();
    $("#zoomer").css(
            {
                width: currentCreature.thumb.width, 
                height: currentCreature.thumb.height,
                opacity: 1
            });
    $("#zoomer").offset($(currentCreature.thumb).offset());
    $("#zoomer").animate(
            {
                // Dialog position is always relative to the window, not the container.
                top: window.innerHeight/2 - currentCreature.img.height/2,
                left: window.innerWidth/2 - currentCreature.img.width/2, 
                width: currentCreature.img.width, 
                height: currentCreature.img.height,
                opacity: 0
            }, 
            {
                easing : "quadEaseOut",
                complete : function() {
                    
                    $("#dialog").dialog({
                        title: "Creature " + currentCreature.name,
                        height: "auto",
                        width: "auto",
                        position: "center",
                        modal: true,
                        resizable: false,
                        buttons: { 
                            "More Info": function() { window.open(currentCreature.page_url); },
                            "Add To Gallery": function() { window.open(currentCreature.gallery_url); },
                            "Close": closeDialog
                        }
                    });
                    $("#zoomer").hide();
                    
                }
            });
};


function closeDialog() {
    if (currentCreature != null) {
        
        $("#dialog").dialog("close");
        
        $("#zoomer").show();
        $("#zoomer").css(
                {
                    width: currentCreature.img.width, 
                    height: currentCreature.img.height,
                    opacity: 0
                });
        $("#zoomer").offset($(currentCreature.img).offset());
        $("#zoomer").animate(
                {
                    // Dialog position is always relative to the window, not the container.
                    top: $(currentCreature.thumb).offset().top+1, // +1 to account for the border
                    left: $(currentCreature.thumb).offset().left+1, // +1 to account for the border 
                    width: currentCreature.thumb.width, 
                    height: currentCreature.thumb.height,
                    opacity: 1
                }, 
                {
                    easing : "quadEaseOut",
                    complete : function() {
                        $("#zoomer").hide();
                    }
                });

        currentCreature = null; 

    }
}


function setDialog() {
    $("#creature").attr("src", currentCreature.img.src);
    $("#dialog").dialog("option", {
        title: "Creature " + currentCreature.name,
        modal: true,
        resizable: false,
        buttons: { 
            "More Info": function() { window.open(currentCreature.page_url); },
            "Add To Gallery": function() { window.open(currentCreature.gallery_url); },
            "Close": closeDialog
        }
    });
}


function getPreviousCreature(index) {
    var i = index;
    while (true) {
        i = (i - 1).mod(byIndex.length)
        var creature = byIndex[i];
        if (creature != null && creature.name != null) {
            return creature;
        }
    }
}

function getNextCreature(index) {
    var i = index;
    while (true) {
        i = (i + 1).mod(byIndex.length);
        var creature = byIndex[i];
        if (creature != null && creature.name != null) {
            return creature;
        }
    }
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

	// Get the dims of the table
	cols = Math.floor($(window).width() / (thumbWidth + thumbPadding));
    rows = Math.floor($(window).height() / (thumbHeight + thumbPadding));

    // Set up the left/right handlers
    $("#left_img").parent().click(dialogPrevious);
    $("#right_img").parent().click(dialogNext);
    $(document).keydown(function(e) {
        switch ( e.keyCode ) {
            // Escape
            case 27:
                closeDialog();
                break;
            // Left arrow.
            case 37:  
                dialogPrevious(); 
                break;
            // Right arrow.
            case 39: 
                dialogNext(); 
                break;
        }
    });

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


function dialogPrevious() {
    if (currentCreature != null) {
        currentCreature = getPreviousCreature(currentCreature.index);
        setDialog();
    };
}

function dialogNext() {
    if (currentCreature != null) {
        currentCreature = getNextCreature(currentCreature.index);
        setDialog();
    };
}


function initConfig(data) {

	if (data == null) {
		// The AJAX call failed.  Use the defaults instead.
		return;
	}

    experimentName = data.name;
	creatureWidth = data.img_width;
	creatureHeight = data.img_height;
	tileMode = data.tile_mode;
	reflectMode = data.reflect_mode;
	debug = data.debug;

}


function initCreatures(data) {

    if (data == null || data.length == 0) {
        newCreatures();
    } else {
        restoreCreatures(data);
    }

}


function newCreatures() {
    makeRows(rows);
    for (var i = 0; i < CONCURRENCY; i++) {
        initCreatureInner();
    }
}


var generatedCount = 0;
function initCreatureInner() {
    var i = generatedCount++;
    if (i > (rows * cols)) {
        return;
    }
    console.log("Init " + i + "...");
    var tr = $("#tr_" + Math.floor(i/cols));
    var td = $("<td>");
    tr.append(td);
    var thumb = new Thumb(i, td);
    thumb.generate();
}


function restoreCreatures(thumbInfos) {
    makeRows(Math.ceil(thumbInfos.length/cols));
    for (var i = 0; i < thumbInfos.length; i++) {
        var tr = $("#tr_" + Math.floor(i/cols));
        var td = $("<td>");
        tr.append(td);
        var thumb = new Thumb(i, td);
        thumb.onLoad(thumbInfos[i]);
    }
}


function makeRows(count) {
    // Make all the rows we'll need.
    for (var i = 0; i < count; i++) {
        var tr = $("<tr>");
        tr.attr("id", "tr_" + i);
        $("#grid").append(tr);
    }
}
