const { argMax, randomlyChoose, randn, cloneDeep, dot, sigmoid } = require('./utils')

class NeuralNet {
	// a fully-connected neural network with sigmoid activation

	constructor(weights) {
		this.weights = weights
	}

	evaluate(inputs) {
		var output = dot(inputs,this.weights[0])
		for (var i=1; i<this.weights.length; i++) {
			output = output.map(sigmoid)
			output = dot(output, this.weights[i])
		}
		output = output.map(sigmoid)
		return output
	}

	clone() {
		return new NeuralNet(null, cloneDeep(this.weights))
	}

	static random(layers=[5,9,4,3]) {
		// randomly initialize weights for a given network shape
		var weights = []
		for (var i = 0; i<layers.length-1; i++) {
			var thisNum = layers[i];
			var nextNum = layers[i+1];
			var variance = 1.0/Math.sqrt(nextNum) // to keep the output near -1 to 1
			var w = Array(thisNum).fill().map(()=>{
				return Array(nextNum).fill().map(()=>randn()*variance)
			})
			weights.push(w);
		}
		return new NeuralNet(weights)
	}

	static zeros(layers=[5,9,4,3]) {
		// randomly initialize weights for a given network shape
		var weights = []
		for (var i = 0; i<layers.length-1; i++) {
			var thisNum = layers[i];
			var nextNum = layers[i+1];
			var w = Array(thisNum).fill().map(()=>Array(nextNum).fill(0))
			weights.push(w);
		}
		return new NeuralNet(weights)
	}
}

// run racer for each

module.exports = NeuralNet