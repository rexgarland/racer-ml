function straightawayTrack(i) {
	if (i%10==0) {
		return [[10,30], [70,90]]
	}
}

function gentleSineTrack(i) {
	if (i%30==0) {
		var shift = 10*Math.sin(2*Math.PI*i/300)
		return [[10+shift,30+shift], [70+shift,90+shift]]
	}
}

function bigSineTrack(i) {
	if (i%10==0) {
		var shift = 24*Math.sin(2*Math.PI*(i-20)/300);
		return [[10+shift,30+shift], [70+shift,90+shift]]
	}
}

function gradualSineTrack(i) {
	if (i%10==0) {
		var amp = Math.min(30, i*100/1000)
		var shift = amp*Math.sin(2*Math.PI*i/300);
		return [[10+shift,30+shift], [70+shift,90+shift]]
	}
}

class Track {
	constructor(generator) {
		// a function: (trackIndex) -> list of obstacles
		this.generator = generator
	}

	hit(x,y) {
		var obstacles = this.obstaclesAt(y)
		for (var i=0; i<obstacles.length; i++) {
			var [x0, x1] = obstacles[i];
			if (x>x0 && x<x1) {
				return true
			}
		}
		return false
	}

	obstaclesAt(y) {
		var obstacles = this.generator(y)
		if (obstacles) {
			return obstacles
		}
		return []
	}

	toListInRange(y0,y1) {
		var list = []
		for (var y=y0; y<y1; y++) {
			var obstacles = this.generator(y)
			if (obstacles) {
				list.push([y,obstacles])
			}
		}
		return list
	}

	static straight = new Track(straightawayTrack)
	static gradualSine = new Track(gradualSineTrack)
	static sine = new Track(bigSineTrack)
}

module.exports = Track