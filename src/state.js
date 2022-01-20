const Racer = require('./racer')
const UI = require('./ui')
const Track = require('./track')
const NeuralNet = require('./nn')
const GeneticAlgorithm = require('./alg')
const { randomlyChoose, randn } = require('./utils')

class State {
	constructor() {
		this.frame = 0
		this.ui = new UI()
		this.racer = new Racer(this.ui.canvas.width)
		this.isPlaying = false
		this.mode = 'user'
		this.track = Track.gradualSine
		this.breeding = null
		this.parameters = {
			rate: 0.1,
			variance: 0.1,
			num: 10
		}

		this.alg = this.createAlg()
		
		this.leftKeyDown = false
		this.rightKeyDown = false

		// plumbing
		this.ui.playPause.onclick = (e) => {this.onPlayPause(e)}
		this.ui.modeSelect.onchange = (e) => {this.onModeChange(e)}
		this.ui.breed.onclick = (e) => {this.onBreed(e)}
		Object.keys(this.parameters).forEach(parameter=>{
			this.ui.parameterInput[parameter].oninput = (e) => {this.onParameterInput(parameter)(e)}
			this.ui.parameterInput[parameter].onchange = (e) => {this.onParameterChange(parameter)(e)}
		})
		window.onkeydown = (e) => {this.onKeyDown(e)}
		window.onkeyup = (e) => {this.onKeyUp(e)}

		// graphics
		this.updateCanvas()
	}

	onParameterInput(parameter) {
		return (e) => {
			document.querySelector(`label[for="${parameter}"] span`).style.opacity = 0.5;
			this.updateParameter(parameter)(e)
		}
	}

	onParameterChange(parameter) {
		return (e) => {
			document.querySelector(`label[for="${parameter}"] span`).style.opacity = 1;
			this.updateParameter(parameter)(e)
		}
	}

	updateParameter(parameter) {
		return (e) => {
			var val
			if (parameter==='rate' || parameter==='variance') {
				val = Math.pow(10,e.target.value/100)
				if (e.target.value>=1) {
					val = Math.round(val)
				} else {
					val = Math.round(val*1000)/1000
				}
			} else {
				val = Math.round(e.target.value)
			}
			this.parameters[parameter] = val
			if (val>1000) {
				this.ui.update(parameter, Math.round(this.parameters[parameter]/1000)+"e3");
			} else {
				this.ui.update(parameter, this.parameters[parameter]);
			}
			// update for alg
			this.alg.num = this.parameters.num
		}
	}

	iterFrame() {
		if (this.isPlaying) {
			this.stepTime()
			this.updateCanvas()
			if (this.track.hit(this.racer.x,this.frame)) {
				this.isPlaying = false
				this.ui.playPause.innerHTML = 'Restart'
				this.ui.playPause.onclick = (e) => {this.onRestart(e)}
			}
		}
	}

	stepTime() {
		this.racer.iter(this.track, this.frame)
		this.frame++
	}

	updateCanvas() {
		this.ui.clearCanvas()
		this.ui.drawRacerAt(this.racer.x)
		this.ui.drawTrack(this.track,this.frame)
	}

	onPlayPause() {
		this.isPlaying = this.isPlaying ? false : true;
		this.ui.playPause.innerHTML = this.isPlaying ? 'Pause' : 'Play';
	}

	onRestart(e) {
		this.racer.init()
		this.frame = 0
		this.isPlaying = true
		this.ui.playPause.innerHTML = 'Pause'
		this.ui.playPause.onclick = (e) => {this.onPlayPause(e)}
	}

	onKeyDown(e) {
		if (e.key==='ArrowLeft') {
			this.leftKeyDown = true
		} else if (e.key==="ArrowRight") {
			this.rightKeyDown = true
		}
		if (this.mode==='user') {
			this.updateThrust()
		}
	}

	onKeyUp(e) {
		if (e.key==='ArrowLeft') {
			this.leftKeyDown = false
		} else if (e.key==="ArrowRight") {
			this.rightKeyDown = false
		}
		if (this.mode==='user') {
			this.updateThrust()
		}
	}

	updateThrust() {
		if (this.leftKeyDown && !this.rightKeyDown) {
			this.racer.thrust = -1
		} else if (this.rightKeyDown && !this.leftKeyDown) {
			this.racer.thrust = 1
		} else {
			this.racer.thrust = 0
		}
	}

	onModeChange() {
		this.mode = this.ui.modeSelect.value
		if (this.mode==='robot') {
			this.breedingIter = 0
			this.ui.mlControls.style.opacity = 1;
			this.racer.brain = NeuralNet.random()
			this.createAlg()
		} else {
			this.ui.mlControls.style.opacity = 0;
			delete this.racer.brain
		}
	}

	createAlg() {
		this.alg = new GeneticAlgorithm(()=>{
			var racer = new Racer(this.ui.canvas.width)
			racer.brain = NeuralNet.random()
			return racer
		})
	}

	iterAlg() {
		this.alg.iter(fitness(this.track), breed, mutate(this.parameters.rate, this.parameters.variance))
	}

	onBreed(e) {
		if (this.breeding===null) {
			this.breeding = setInterval(() => {
				this.iterAlg()
				this.racer = this.alg.top
				this.breedingIter++
				this.ui.update('breed-iteration', this.breedingIter)
				this.ui.update('breed-score', this.alg.score)
			},1)
		} else {
			clearInterval(this.breeding)
			this.breeding = null
		}
	}
}


function breed(r1, r2) {
	// randomly choose parameters between the two parents
	var n1 = r1.brain
	var n2 = r2.brain
	var newWeights = []
	for (var i = 0; i<n1.weights.length; i++) {
		var a = []
		for (var j = 0; j<n1.weights[i].length; j++) {
			var b = []
			for (var k = 0; k<n1.weights[i][j].length; k++) {
				var c = randomlyChoose([n1.weights[i][j][k],n2.weights[i][j][k]]);
				b.push(c)
			}
			a.push(b)
		}
		newWeights.push(a)
	}
	var newRacer = new Racer(r1.span)
	newRacer.brain = new NeuralNet(newWeights)
	return newRacer
}

function mutate(rate=0.1, weight=1) {
	return (racer) => {
		// the rate is chance of a weight mutating
		// the variance is the variance a normal variable added to a mutated weight
		var nn = racer.brain
		var newWeights = []
		for (var i = 0; i<nn.weights.length; i++) {
			var a = []
			for (var j = 0; j<nn.weights[i].length; j++) {
				var b = []
				var variance = 1.0/Math.sqrt(nn.weights[i][j].length)
				for (var k = 0; k<nn.weights[i][j].length; k++) {
					var w = nn.weights[i][j][k]
					if (Math.random()<rate) {
						w = w + randn()*variance*weight
					}
					b.push(w)
				}
				a.push(b)
			}
			newWeights.push(a)
		}
		var newRacer = new Racer(racer.span)
		newRacer.brain = new NeuralNet(newWeights)
		return newRacer
	}
}

function fitness(track, maxIter=10000) {
	return (racer) => {
		racer.init()
		var frame = 0;
		while (!track.hit(racer.x,frame) && frame<maxIter) {
			racer.iter(track, frame)
			frame++
		}
		return frame
	}
}


module.exports = State