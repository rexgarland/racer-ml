const { argMax } = require('./utils')

class GeneticAlgorithm {
	constructor(generator, num=10) {
		// creates a population
		this.num = num
		this.population = Array(num).fill().map(generator)
		this.score = 0
		this.top = this.population[0]
	}

	iter(fitness, breed, mutate) {
		// generates the next population
		var scores = this.population.map(fitness)
		var i = argMax(scores);
		if (scores[i]>this.score) {
			this.top = this.population.splice(i,1)[0]
			this.score = scores.splice(i,1)
		}
		var i = argMax(scores);
		var parent = this.population.splice(i,1)[0]
		var child = breed(this.top, parent)
		this.population = Array(this.num).fill(child).map(mutate)
	}
}

module.exports = GeneticAlgorithm