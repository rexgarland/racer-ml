const { argMax } = require('./utils')

A = 2.5/100

class Racer {
	constructor(span) {
		this.span = span
		this.init()
	}

	init() {
		this.thrust = 0
		this.x = this.span/2
		this.dx = 0
	}

	sensors(track, frame) {
		// there are 5 sensors, evenly space between -60 to 60 degrees
		// the sensors can only see up to j=80
		// they read 1/j, or 0 if no obstacles sensed
		var s = [0, 0, 0, 0, 0]
		var angles = [-60, -30, 0, 30, 60]
		for (var i = 0; i<80; i++) {
			var val = 1.0/i
			var y = frame + i
			track.obstaclesAt(y).forEach(obstacle=>{
				angles.forEach((angle,j)=>{
					if (s[j]===0) {
						var xf = this.x+i*Math.tan(angle*Math.PI/180)
						if (xf>obstacle[0] && xf<obstacle[1]) {
							s[j] = val
						}
					}
				})
			})
		}
		return s
	}

	iter(track, frame) {
		if (this.brain) {
			this.thrust = this.getThrust(track, frame)
		}
		this.x = this.x + this.dx
		this.dx = this.dx + this.thrust*A
		if (this.x<0) {
			this.x = 0
			this.dx = 0
		} else if (this.x>this.span) {
			this.x = this.span
			this.dx = 0
		}
	}

	getThrust(track, frame) {
		var output = this.brain.evaluate(this.sensors(track, frame))
		var i = argMax(output)
		return [-1,0,1][i]
	}
}

module.exports = Racer