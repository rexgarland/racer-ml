

function draw(j, obstacles) {
	ctx.save();
	obstacles.forEach(obstacle => {
		ctx.beginPath();
		ctx.moveTo(obstacle[0],canvas.height-j)
		ctx.lineTo(obstacle[1],canvas.height-j)
		ctx.stroke()
	})
	ctx.restore()
}


class UI {
	constructor() {
		this.canvas = document.getElementById('canvas')
		this.ctx = this.canvas.getContext("2d");
		this.playPause = document.getElementById('playPause')
		this.modeSelect = document.getElementById('mode')
		this.mlControls = document.getElementById('controls-ml')
		this.breed = document.getElementById('breed')
		this.parameterInput = {
			num: document.getElementById('num'),
			rate: document.getElementById('rate'),
			variance: document.getElementById('variance'),
			varianceZero: document.getElementById('variance-zero')
		}
		this.outputs = {
			'variance': document.getElementById('variance-display'),
			'num': document.getElementById('num-display'),
			'rate': document.getElementById('rate-display'),
			'breed-iteration': document.getElementById('breed-iteration'),
			'breed-score': document.getElementById('breed-score'),
		}
	}

	update(id, value) {
		this.outputs[id].innerHTML = value
	}

	clearCanvas() {
		this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
	}

	drawRacerAt(x) {
		var ctx = this.ctx
		ctx.save()
		ctx.beginPath();
		var width = 10
		var height = 6
		ctx.moveTo(x-width/2,canvas.height)
		ctx.lineTo(x+width/2,canvas.height)
		ctx.lineTo(x,canvas.height-height)
		ctx.fill()
		ctx.restore()
	}

	drawTrack(track, frame) {
		var ctx = this.ctx
		ctx.save();
		for (var i=0; i<this.canvas.height; i++) {
			var obstacles = track.obstaclesAt(i+frame)
			if (obstacles) {
			obstacles.forEach(obstacle=>{
					ctx.beginPath();
					ctx.moveTo(obstacle[0],this.canvas.height-i)
					ctx.lineTo(obstacle[1],this.canvas.height-i)
					ctx.stroke()
				})
			}
		}
		ctx.restore()
	}
}

module.exports = UI