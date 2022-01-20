const State = require('./state')

var state = new State()

function loop() {
	state.iterFrame()
	window.requestAnimationFrame(loop);
}
loop()