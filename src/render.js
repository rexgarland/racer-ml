var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");

var sensors = document.getElementById("sensors");

function initSensors() {
	sensors.innerHTML = Array(5).fill().map((v,i)=>{
		return `<div id="sensor${i}" class="sensor"></div>`
	}).join('')
}

initSensors()

function drawSensors(racer, field) {
	var vals = racer.sensors(field)
	vals.forEach((v,i)=>{
		document.getElementById(`sensor${i}`).style.opacity = v
	})
}

var nnDisplay = document.getElementById("nn");

function drawNN(racer, field) {
	var nn = racer.brain.nn
	nnDisplay.innerHTML = nn.summarize()
}

function render(racer, field) {
	

	field.forEach(([j, obstacles])=>{
		draw(j, obstacles);
	});

	drawRacer(racer);

	drawSensors(racer, field);

	if (racer.brain) {
		drawNN(racer, field);
	} else {
		nnDisplay.innerHTML = ''
	}

}

module.exports = Render