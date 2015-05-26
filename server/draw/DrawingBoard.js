window.DrawingBoard = typeof DrawingBoard !== "undefined" ? DrawingBoard : {};

/**
 * pass the id of the html element to put the drawing board into
 * and some options : {
 *	controls: array of controls to initialize with the drawingboard. 'Colors', 'Size', and 'Navigation' by default
 *		instead of simple strings, you can pass an object to define a control opts
 *		ie ['Color', { Navigation: { reset: false }}]
 *	controlsPosition: "top left" by default. Define where to put the controls: at the "top" or "bottom" of the canvas, aligned to "left"/"right"/"center"
 *	background: background of the drawing board. Give a hex color or an image url "#ffffff" (white) by default
 *	color: pencil color ("#000000" by default)
 *	size: pencil size (3 by default)
 *	webStorage: 'session', 'local' or false ('session' by default). store the current drawing in session or local storage and restore it when you come back
 *	droppable: true or false (false by default). If true, dropping an image on the canvas will include it and allow you to draw on it,
 *	errorMessage: html string to put in the board's element on browsers that don't support canvas.
 *	stretchImg: default behavior of image setting on the canvas: set to the canvas width/height or not? false by default
 * }
 */
DrawingBoard.Board = function(id, opts) {
	this.opts = this.mergeOptions(opts);

	this.id = id;
	this.$el = $(document.getElementById(id));
	if (!this.$el.length)
		return false;

	this.dom = {
		$canvas: this.$el.find('.drawing-board-canvas'),
		$stickerHover: $('.drawing-board-sticker-hover')
	};

	this.dom.$stickerHover.css({
		position: "absolute",
		zIndex: 1000,
		width: "100px",
		height: "200px",
		top: "-200px",
		left: "-200px",
		"background-repeat": "no-repeat"
	});

	this.canvas = this.dom.$canvas.get(0);
	this.ctx = this.canvas && this.canvas.getContext && this.canvas.getContext('2d') ? this.canvas.getContext('2d') : null;

	this.initHistory();
	//set board's size after the controls div is added
	this.resize();
	//reset the board to take all resized space
	this.reset({ history: true, background: true });

	this.initDrawEvents();
};



DrawingBoard.Board.defaultOpts = {
	color: "#fff",
	outerColor: "#ff00ff",
	size: 4,
	outerSize: 4,
	background: "rgba(0,0,0,0)",
	stickerFile: "javascript:void(0);",
	stickerSize: [200,200],
	stickerRotate: 0,
	rollerSize: 100,

	enlargeYourContainer: false,
	stretchImg: false //when setting the canvas img, strech the image at the whole canvas size when this opt is true
};



DrawingBoard.Board.prototype = {

	mergeOptions: function(opts) {
		opts = $.extend({}, DrawingBoard.Board.defaultOpts, opts);
		if (!opts.background && opts.eraserColor === "background")
			opts.eraserColor = "transparent";
		return opts;
	},

	/**
	 * Canvas reset/resize methods: put back the canvas to its default values
	 *
	 * depending on options, can set color, size, background back to default values
	 * and store the reseted canvas in webstorage and history queue
	 *
	 * resize values depend on the `enlargeYourContainer` option
	 */

	reset: function(opts) {
		opts = $.extend({
			color: this.opts.color,
			size: this.opts.size,
			history: true,
			background: false
		}, opts);

		this.setMode('pencil');

		if (opts.size) this.ctx.lineWidth = opts.size;

		this.ctx.lineCap = "round";
		this.ctx.lineJoin = "round";
		// this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.width);

		if (opts.history) this.saveHistory();

		this.blankCanvas = this.getImg();

	},

	resize: function() {
		var canvasWidth, canvasHeight;
		var that = this;
		var sum = function(values, multiplier) { //make the sum of all array values
			multiplier = multiplier || 1;
			var res = values[0];
			for (var i = 1; i < values.length; i++) {
				res = res + (values[i]*multiplier);
			}
			return res;
		};
		var sub = function(values) { return sum(values, -1); }; //substract all array values from the first one

		canvasWidth = 552;
		canvasHeight = 736;

		this.dom.$canvas.css('width', canvasWidth + 'px');
		this.dom.$canvas.css('height', canvasHeight + 'px');

		this.canvas.width = canvasWidth;
		this.canvas.height = canvasHeight;
	},




	/**
	 * History methods: undo and redo drawed lines
	 */

	initHistory: function() {
		this.history = {
			values: [],
			position: 0
		};
	},

	saveHistory: function () {
		while (this.history.values.length > 5) {
			this.history.values.shift();
			this.history.position--;
		}
		if (this.history.position !== 0 && this.history.position < this.history.values.length) {
			this.history.values = this.history.values.slice(0, this.history.position);
			this.history.position++;
		} else {
			this.history.position = this.history.values.length+1;
		}
		this.history.values.push(this.getImg());
	},

	_goThroughHistory: function(goForth) {
		if ((goForth && this.history.position == this.history.values.length) ||
			(!goForth && this.history.position == 1))
			return;
		var pos = goForth ? this.history.position+1 : this.history.position-1;
		if (this.history.values.length && this.history.values[pos-1] !== undefined) {
			this.history.position = pos;
			this.setImg(this.history.values[pos-1]);
		}
	},

	goBackInHistory: function() {
		this._goThroughHistory(false);
	},

	goForthInHistory: function() {
		this._goThroughHistory(true);
	},

	rollerImages: [],

	updateRollers: function(files){
		this.rollerImages = [];
		for(var i =0; i<files.length; i++){
			var image = new Image();
			image.src = files[i];
			this.rollerImages.push(image);
		}
	},

	/**
	 * Image methods: you can directly put an image on the canvas, get it in base64 data url or start a download
	 */

	setImg: function(src, opts) {
		opts = $.extend({
			stretch: this.opts.stretchImg
		}, opts);
		var ctx = this.ctx;
		var img = new Image();
		var oldGCO = ctx.globalCompositeOperation;
		img.onload = function() {
			ctx.globalCompositeOperation = "source-over";
			ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

			if (opts.stretch) {
				ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
			} else {
				ctx.drawImage(img, 0, 0);
			}

			ctx.globalCompositeOperation = oldGCO;
		};
		img.src = src;
	},

	getImg: function() {
		return this.canvas.toDataURL("image/png");
	},

	downloadImg: function() {
		var img = this.getImg();
		img = img.replace("image/png", "image/octet-stream");
		window.location.href = img;
	},


	/**
	 * set and get current drawing mode
	 *
	 * possible modes are "pencil" (draw normally), "eraser" (draw transparent, like, erase, you know), "filler" (paint can)
	 */

	setMode: function(newMode) {
		newMode = newMode || 'pencil';
		this.ctx.globalCompositeOperation = newMode === "eraser" ? "destination-out" : "source-over";
		this.mode = newMode;
	},

	getMode: function() {
		return this.mode || "pencil";
	},

	/**
	 * Drawing handling, with mouse or touch
	 */

	initDrawEvents: function() {
		this.isDrawing = false;
		this.coords = {};
		this.coords.old = this.coords.current = this.coords.oldMid = { x: 0, y: 0 };
		this.coords.path = [];

		this.dom.$canvas.on('mousedown touchstart', $.proxy(function(e) {
			this._onInputStart(e, this._getInputCoords(e) );
		}, this));

		this.dom.$canvas.on('mousemove touchmove', $.proxy(function(e) {
			this._onInputMove(e, this._getInputCoords(e) );
		}, this));

		this.dom.$stickerHover.on('mousemove touchmove', $.proxy(function(e) {
			this._onInputMove(e, this._getInputCoords(e) );
		}, this));	

		this.dom.$canvas.on('mouseup touchend', $.proxy(function(e) {
			this._onInputStop(e, this._getInputCoords(e) );
		}, this));

		this.dom.$stickerHover.on('mouseup touchend', $.proxy(function(e) {
			this._onInputStop(e, this._getInputCoords(e) );
		}, this));


		this.dom.$canvas.on('mouseover', $.proxy(function(e) {
			this._onMouseOver(e, this._getInputCoords(e) );
		}, this));

		this.dom.$canvas.on('mouseout', $.proxy(function(e) {
			this._onMouseOut(e, this._getInputCoords(e) );
		}, this));

		$('body').on('mouseup touchend', $.proxy(function(e) {
			this.isDrawing = false;
		}, this));

		if (window.requestAnimationFrame) requestAnimationFrame( $.proxy(this.draw, this) );
	},

	draw: function() {
		if (this.isDrawing){
			if (this.mode == "pencil" || this.mode=="eraser") {
				this.drawLine();
			} else if (this.mode == "sticker") {
				this.drawSticker();
			} else if (this.mode == "roller") {
				this.drawRoller();
			}
		}
		if (window.requestAnimationFrame) requestAnimationFrame( $.proxy(function() { this.draw(); }, this) );
	},

	drawSticker: function() {
		var left = this.coords.mouse.x - Math.floor(this.opts.stickerSize[0]/2);
		var top = this.coords.mouse.y - Math.floor(this.opts.stickerSize[1]/2);
		this.dom.$stickerHover.css({
			top: top + "px",
			left: left + "px"
		});

	},

	drawLine: function() {
		if(this.mode == 'pencil') {
			// Border
			this.ctx.strokeStyle = this.opts.outerColor;
			this.ctx.lineWidth = this.opts.size + (2 * this.opts.outerSize);
			this.ctx.beginPath();
			this.coords.old = this.coords.path[0];
			this.coords.oldMid = this._getMidInputCoords(this.coords.path[0]);
			for (var i=1; i<this.coords.path.length; i++) {
				var mid = this._getMidInputCoords(this.coords.path[i]);
				this.ctx.moveTo(mid.x, mid.y);
				this.ctx.quadraticCurveTo(this.coords.old.x, this.coords.old.y, this.coords.oldMid.x, this.coords.oldMid.y);
				this.coords.oldMid = mid;
				this.coords.old = this.coords.path[i];
			}
			
			this.ctx.stroke();
			this.ctx.strokeStyle = this.opts.color;
		}

		this.ctx.lineWidth = this.opts.size;
		this.ctx.beginPath();
		this.coords.old = this.coords.path[0];
		this.coords.oldMid = this._getMidInputCoords(this.coords.path[0]);
		for (var i=1; i<this.coords.path.length; i++) {
			var mid = this._getMidInputCoords(this.coords.path[i]);
			this.ctx.moveTo(mid.x, mid.y);
			this.ctx.quadraticCurveTo(this.coords.old.x, this.coords.old.y, this.coords.oldMid.x, this.coords.oldMid.y);
			this.coords.oldMid = mid;
			this.coords.old = this.coords.path[i];
		}
		
		this.ctx.stroke();
	},



	drawRoller: function() {
		var minDistance = this.opts.rollerSize * .8;
		var currentCoords = this.coords.path.slice(-1)[0];
		if (this.coords.lastRoller === false) {
			this.drawRollerImage(currentCoords);
			this.coords.lastRoller = currentCoords;
		} else if (this._distanceBetween(this.coords.lastRoller, currentCoords) > minDistance) {
			this.drawRollerImage(currentCoords);
			this.coords.lastRoller = currentCoords;
		}
	},
	rollerCounter: 0,
	drawRollerImage: function(coords) {
		if (this.rollerCounter == this.rollerImages.length) {
			this.rollerCounter = 0;
		}
		var image = this.rollerImages[this.rollerCounter];
		this.ctx.drawImage(image, coords.x, coords.y, this.opts.rollerSize, this.opts.rollerSize);

		this.rollerCounter++;

	},

	_distanceBetween: function (point1, point2) {
	  return Math.sqrt(Math.pow(point2.x - point1.x, 2) + Math.pow(point2.y - point1.y, 2));
	},

	_angleBetween: function(point1, point2) {
  		return Math.atan2( point2.x - point1.x, point2.y - point1.y );
	},

	hoverSticker: function(){
		var css = {
			"width": this.opts.stickerSize[0]+"px",
			"height": this.opts.stickerSize[1]+"px",
			"background-image": "url('"+this.opts.stickerFile+"')",
			"background-size": this.opts.stickerSize[0]+"px "+this.opts.stickerSize[1]+"px",
			'transform': "rotate("+this.opts.stickerRotate+"deg)"
		}
		this.dom.$stickerHover.css(css);
		this.drawSticker();
	},

	pasteSticker: function() {
		// get coords from path
		var upperLeftCoords = this.coords.path.slice(-1)[0];
		var middleCoords = {x: upperLeftCoords.x, y: upperLeftCoords.y};

		upperLeftCoords.x -= Math.floor(parseInt(this.opts.stickerSize[0],10)/2);
		upperLeftCoords.y -= Math.floor(parseInt(this.opts.stickerSize[1],10)/2);

		this.dom.$stickerHover.css({
			top: "-1000px",
			left: "-1000px"
		});

		var img = new Image();
		img.onload = $.proxy(function(){
			if (this.opts.stickerRotate == 0) {
				this.ctx.drawImage(img, upperLeftCoords.x, upperLeftCoords.y, 
					this.opts.stickerSize[0], this.opts.stickerSize[1]);

			} else {
				// Rotate that shit
				this.ctx.save();

				this.ctx.translate(middleCoords.x, middleCoords.y);

				var TO_RADIANS = Math.PI/180;
				var angle = this.opts.stickerRotate;
				var radAngle = parseInt(angle, 10) * TO_RADIANS;
				this.ctx.rotate(radAngle);
				this.ctx.drawImage(img, -(this.opts.stickerSize[0]/2), -(this.opts.stickerSize[0]/2),
					this.opts.stickerSize[0], this.opts.stickerSize[1]);

				this.ctx.restore();
			}





			this.saveHistory();
		}, this);
		img.src = this.opts.stickerFile;
	},

	_onInputStart: function(e, coords) {
		this.coords.mouse = this._getEventCoords(e);
		this.coords.path = [coords];
		this.coords.lastRoller = false;
		this.isDrawing = true;

		if (this.mode == 'sticker'){
			this.hoverSticker();
		}

		if (!window.requestAnimationFrame) this.draw();

		e.stopPropagation();
		e.preventDefault();
	},

	_onInputMove: function(e, coords) {
		this.coords.path.push(coords);
		this.coords.mouse = this._getEventCoords(e);
		if (this.isDrawing && this.mode == 'sticker') {
			//this.drawSticker();
		}

		if (!window.requestAnimationFrame) this.draw();

		e.stopPropagation();
		e.preventDefault();
	},

	_onInputStop: function(e, coords) {
		if (this.isDrawing && (!e.touches || e.touches.length === 0)) {
			this.isDrawing = false;

			if (this.mode == 'sticker') {
				this.pasteSticker();
			}

			this.saveHistory();

			e.stopPropagation();
			e.preventDefault();
		}
	},

	_onMouseOver: function(e, coords) {
		this.coords.mouse = {x: e.pageX, y: e.pageY};
	},

	_onMouseOut: function(e, coords) {
	},

	_getEventCoords: function(e){
		e = e.originalEvent ? e.originalEvent : e;
		if (e.touches && e.touches.length == 1) {
			x = e.touches[0].pageX;
			y = e.touches[0].pageY;
		} else {
			x = e.pageX;
			y = e.pageY;
		}
		return {x: x, y: y};
	},

	_getInputCoords: function(e) {
		var xy = this._getEventCoords(e);
		return {
			x: xy.x - this.dom.$canvas.offset().left,
			y: xy.y - this.dom.$canvas.offset().top
		};
	},

	_getMidInputCoords: function(coords) {
		return {
			x: this.coords.old.x + coords.x>>1,
			y: this.coords.old.y + coords.y>>1
		};
	}
};