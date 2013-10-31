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
            "Close": function() { 
                currentCreature = null; 
                $("#dialog").dialog("close"); 
            }
        }
    });
};


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

    // Set up the left/right click handlers
    $("#left_img").parent().click(function() {
        currentCreature = getPreviousCreature(currentCreature.index);
        openDialog();
    });
    $("#right_img").parent().click(function() {
        currentCreature = getNextCreature(currentCreature.index);
        openDialog();
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
