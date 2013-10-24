//Yay Javascript!
Number.prototype.mod = function(n) {
	return ((this%n)+n)%n;
};

//Experiment stuff
var experimentName = "grid";
var creatureWidth = 800;
var creatureHeight = 600;
var thumbWidth = 152; // +2 to include the border
var thumbHeight = 114; // +2 to include the border
var thumbPadding = 10;

// Generate stuff
var CONCURRENCY = 5;
var cols = 5;
var rows = 5;

var debug = false;

$(document).ready(init);


function Thumb(td) {

	var self = this; // O Javascript Joy!

	this.name = null;
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
		self.td.append(self.thumb);
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
		$(self.thumb).click(self.openDialog);
		// Change the class.
		$(self.thumb).removeClass("qm").addClass("thumb");
	};


	this.onFail = function() {
		self.thumb.src = "broken.jpg";
		self.on_arrive_src = "broken.jpg";
	};

	
	this.openDialog = function() {

        $("#creature").attr("src", self.img.src);
        $("#creature").show();
        $("#dialog").dialog({
            title: "Creature " + self.name,
            height: "auto",
            width: "auto",
            position: "center",
            modal: true,
            resizable: false,
            buttons: { 
                "More Info": function() { window.open(self.page_url); },
                "Add To Gallery": function() { window.open(self.gallery_url); },
                "Close": function() { $("#dialog").dialog("close"); }
            }
        });

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

	// Get the dims of the table
	cols = Math.floor($(window).width() / (thumbWidth + thumbPadding));
    rows = Math.floor($(window).height() / (thumbHeight + thumbPadding));

	// Init the creatures.
	initCreatures();

}


function initConfig(data) {

	if (data == null) {
		// The AJAX call failed.  Use the defaults instead.
		return;
	}

	creatureWidth = data.img_width;
	creatureHeight = data.img_height
	debug = data.debug;

}


function initCreatures(data) {
    for (var i = 0; i < rows; i++) {
        var tr = $("<tr>");
        tr.attr("id", "tr_" + i);
        $("#grid").append(tr);
    }
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
    var thumb = new Thumb(td);
    thumb.generate();
}
