import numpy as np
import pdb

def sigmoid(x):
	return np.exp(x)/(np.exp(x)+1)

def flatten_layers(weights):
	if not any([type(a)==list or type(a)==np.ndarray for a in weights]):
		return weights
	else:
		flat = []
		for i in range(len(weights)):
			flat.extend(flatten_layers(weights[i]))
		return flat

def shape_layers(flat_weights, layers):
	assert len(flat_weights)==sum([layers[i]*layers[i+1] for i in range(len(layers)-1)]), "Data does not fit shape of layers."
	weights = []
	i = 0
	for level in range(len(layers)-1):
		num_current = layers[level]
		num_next = layers[level+1]
		l1 = []
		for k in range(num_next):
			l2 = []
			for j in range(num_current):
				l2.append(flat_weights[i])
				i += 1
			l1.append(l2)
		weights.append(l1)
	return weights


class NeuralNet(object):
	def __init__(self, layers, variance=0.1, data=None):
		self.weights = []
		self.layers = layers
		if data:
			self.weights = data
		else:
			for i in range(len(layers)-1):
				num_current = layers[i]
				num_next = layers[i+1]
				self.weights.append([[variance*np.random.randn() for j in range(num_current)] for k in range(num_next)])

	def forward(self, input_vect):
		next_input = np.array([np.dot(input_vect, self.weights[0][j]) for j in range(self.layers[1])])
		for i in range(1,len(self.layers)-1):
			input_vect = sigmoid(next_input)
			next_input = np.array([np.dot(input_vect, self.weights[i][j]) for j in range(self.layers[i+1])])
		return next_input

	def mutate(self, rate, variance):
		flat = np.array(flatten_layers(self.weights))
		num_weights = len(flat)
		num_mutations = int(rate*num_weights)
		assert num_mutations>0, "Mutation rate must be larger to affect single weight."
		flat[np.random.choice(range(num_weights),size=num_mutations,replace=False)] += variance*np.random.randn(num_mutations)
		new_weights = shape_layers(flat, self.layers)
		return NeuralNet(self.layers, data=new_weights)

	def breed(self, other_nn):
		assert type(other_nn)==NeuralNet, "Attempted breed with unknown class."
		assert other_nn.layers==self.layers, "Attempted breed of neural nets of different size."
		flat = np.array(flatten_layers(self.weights))
		other_flat = np.array(flatten_layers(other_nn.weights))
		stacked = np.vstack([flat, other_flat])
		choice = np.random.randint(2, size=len(flat))
		child_flat = [stacked[choice[i],i] for i in range(len(flat))]
		child_weights = shape_layers(child_flat, self.layers)
		child = NeuralNet(self.layers, data=child_weights)
		return child

if __name__=='__main__':
	n1 = NeuralNet([3,4,2])
	n2 = NeuralNet([3,4,2])
	child = n1.breed(n2)
	pdb.set_trace()











