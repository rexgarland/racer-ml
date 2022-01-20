from tkinter import *
import numpy as np
import time, pickle, pdb

from neural_net import NeuralNet

def ray_intersection(p1, d1, p2, d2):
	# all inputs are row vectors
	D = np.vstack([d1, -d2])
	try:
		Dinv = np.linalg.inv(D)
	except np.linalg.linalg.LinAlgError:
		return None
	c1, c2 = np.dot(p2-p1, Dinv)
	if c1>=0 and c1<=1 and c2>=0 and c2<=1:
		return c1
	else:
		return None

class RaceGraphics(object):
	def __init__(self):
		# initialize graphics data
		self.root = Tk()
		self.dt = 0.01
		self.delta_y = 10
		self.track_width = 400
		self.visible_height = 600
		self.block_size = 40
		self.canvas = Canvas(self.root, width=self.track_width, height=self.visible_height)
		self.canvas.pack()
		self.track_data = None

	def initialize_racers(self, neural_nets):
		self.racers = [Racer(neural_net, self.track_width, self.visible_height, self.canvas) for neural_net in neural_nets]
		self.num_racers = len(neural_nets)

	def start(self):
		self.travel = 0
		self.display_counter = 0
		self.initialize_blocks()
		self.initialize_buffer_blocks()
		self.root.after(0, self.draw)
		self.root.mainloop()

	def initialize_blocks(self):
		# initialize blocks
		self.blocks = []
		self.block_size = 40
		self.blocks_per_length = 4
		# load with data
		if self.track_data:
			initial_blocks = self.track_data[0]
			for i in range(len(initial_blocks)):
				x1, y1, x2, y2 = initial_blocks[i]
				self.blocks.append(self.canvas.create_rectangle(x1, y1, x2, y2, fill="black"))
		else:
			min_x = -self.block_size/2; max_x = self.track_width+self.block_size/2
			min_y = 0; max_y = self.visible_height/2
			num_blocks = int(self.blocks_per_length*0.5)
			xs = min_x+(max_x-min_x)*np.random.rand(num_blocks)
			ys = min_y+(max_y-min_y)*np.random.rand(num_blocks)
			for i in range(len(xs)):
				x, y = xs[i], ys[i]
				self.blocks.append(self.canvas.create_rectangle(x-self.block_size/2, y-self.block_size/2, x+self.block_size/2, y+self.block_size/2, fill="black"))
		

	def initialize_buffer_blocks(self):
		self.buffer_blocks = []
		if self.track_data:
			buffer_blocks = self.track_data[1]
			for i in range(len(buffer_blocks)):
				x1, y1, x2, y2 = buffer_blocks[i]
				self.buffer_blocks.append(self.canvas.create_rectangle(x1, y1, x2, y2, fill="black"))
		else:
			min_x = -self.block_size/2; max_x = self.track_width+self.block_size/2
			min_y = -self.visible_height; max_y = 0
			num_blocks = self.blocks_per_length
			xs = min_x+(max_x-min_x)*np.random.rand(num_blocks)
			ys = min_y+(max_y-min_y)*np.random.rand(num_blocks)
			for i in range(len(xs)):
				x, y = xs[i], ys[i]
				self.buffer_blocks.append(self.canvas.create_rectangle(x-self.block_size/2, y-self.block_size/2, x+self.block_size/2, y+self.block_size/2, fill="black"))

	def initialize_vision_rays(self):
		self.vision_rays = []
		self.direction_rays = []
		self.vision_angles = [-30, -15, 0, 15, 30]
		self.vision_distance = 300
		for i in range(self.num_racers):
			self.vision_rays.append([self.canvas.create_line(self.reported_xs[i], \
									self.visible_height, \
									self.reported_xs[i]+np.sin(np.pi*angle/180)*self.vision_distance, \
									self.visible_height-np.cos(np.pi*angle/180)*self.vision_distance) for angle in self.vision_angles])
			self.direction_rays.append([np.array([np.sin(np.pi*angle/180)*self.vision_distance, -np.cos(np.pi*angle/180)*self.vision_distance]) for angle in self.vision_angles])

	def draw(self):
		while any([r.alive for r in self.racers]):
			# ipy.embed()
			time.sleep(self.dt)
			# update blocks
			for block in self.blocks:
				self.canvas.move(block, 0, self.delta_y)
			for block in self.buffer_blocks:
				self.canvas.move(block, 0, self.delta_y)
			[r.update(self.blocks, self.travel) for r in self.racers]
			# update canvas
			self.canvas.update()
			# store new travel
			self.travel += self.delta_y
			# periodically update stored blocks
			if self.travel-self.visible_height*self.display_counter>self.visible_height:
				self.display_counter += 1
				self.update_block_memory()
		self.fitnesses = [r.travel for r in self.racers]
		self.quit()

	def update_block_memory(self):
		if self.track_data:
			[self.canvas.delete(block) for block in self.blocks]
			self.blocks = self.buffer_blocks
			self.buffer_blocks = []
			buffer_blocks = self.track_data[self.display_counter+1]
			for i in range(len(buffer_blocks)):
				x1, y1, x2, y2 = buffer_blocks[i]
				self.buffer_blocks.append(self.canvas.create_rectangle(x1, y1, x2, y2, fill="black"))
		else:
			[self.canvas.delete(block) for block in self.blocks]
			self.blocks = self.buffer_blocks
			self.buffer_blocks = []
			min_x = -self.block_size/2; max_x = self.track_width+self.block_size/2
			min_y = -self.visible_height; max_y = 0
			num_blocks = self.blocks_per_length
			xs = min_x+(max_x-min_x)*np.random.rand(num_blocks)
			ys = min_y+(max_y-min_y)*np.random.rand(num_blocks)
			for i in range(len(xs)):
				x, y = xs[i], ys[i]
				self.buffer_blocks.append(self.canvas.create_rectangle(x-self.block_size/2, y-self.block_size/2, x+self.block_size/2, y+self.block_size/2, fill="black"))

	def quit(self):
		[self.canvas.delete(block) for block in self.blocks]
		[self.canvas.delete(block) for block in self.buffer_blocks]
		self.canvas.quit()

	def static_track_data(self):
		# Initialize track data.
		self.blocks_per_length = 4
		self.block_size = 40
		self.track_data = []
		blocks = []
		min_x = -self.block_size/2; max_x = self.track_width+self.block_size/2
		min_y = 0; max_y = self.visible_height/2
		num_blocks = int(self.blocks_per_length*0.5)
		xs = min_x+(max_x-min_x)*np.random.rand(num_blocks)
		ys = min_y+(max_y-min_y)*np.random.rand(num_blocks)
		for i in range(len(xs)):
			x, y = xs[i], ys[i]
			blocks.append((x-self.block_size/2, y-self.block_size/2, x+self.block_size/2, y+self.block_size/2))
		self.track_data.append(blocks)
		for _ in range(1000):
			blocks = []
			min_x = -self.block_size/2; max_x = self.track_width+self.block_size/2
			min_y = -self.visible_height; max_y = 0
			num_blocks = self.blocks_per_length
			xs = min_x+(max_x-min_x)*np.random.rand(num_blocks)
			ys = min_y+(max_y-min_y)*np.random.rand(num_blocks)
			for i in range(len(xs)):
				x, y = xs[i], ys[i]
				blocks.append((x-self.block_size/2, y-self.block_size/2, x+self.block_size/2, y+self.block_size/2))
			self.track_data.append(blocks)

class Racer():
	def __init__(self, neural_net, track_width, visible_height, canvas):
		self.neural_net = neural_net
		self.track_width = track_width
		self.visible_height = visible_height
		self.alive = True
		self.width = 20
		self.velocity = 0
		self.acceleration = 0
		self.x = self.track_width/2
		self.reported_x = int(self.x)
		self.acceleration_choices = [-0.2, 0, 0.2]
		self.canvas = canvas
		self.id = self.canvas.create_polygon(self.reported_x-self.width/2,\
														self.visible_height,\
														self.reported_x,\
														self.visible_height-self.width,\
														self.reported_x+self.width/2,\
														self.visible_height, fill='black')
		self.vision_angles = [-30, -15, 0, 15, 30]
		self.vision_distance = 300
		self.enable_rays = False
		if self.enable_rays:
			self.vision_rays = [self.canvas.create_line(self.reported_x, \
								self.visible_height, \
								self.reported_x+np.sin(np.pi*angle/180)*self.vision_distance, \
								self.visible_height-np.cos(np.pi*angle/180)*self.vision_distance) for angle in self.vision_angles]
		self.direction_rays = [np.array([np.sin(np.pi*angle/180)*self.vision_distance, -np.cos(np.pi*angle/180)*self.vision_distance]) for angle in self.vision_angles]

	def sense(self, blocks):
		# distance_data = []
		# for i in range(len(self.vision_angles)):
		# 	p1 = np.array([self.x, self.visible_height])
		# 	d1 = self.direction_rays[i]
		# 	closest = np.float('+inf')
		# 	# check for line-of-sight blocks
		# 	for block in blocks:
		# 		x1, y1, x2, y2 = self.canvas.coords(block)
		# 		p2 = np.array([x1, y2])
		# 		d2 = np.array([x2-x1,0])
		# 		r = ray_intersection(p1, d1, p2, d2)
		# 		if not r==None:
		# 			distance = r*self.vision_distance
		# 			if distance<closest:
		# 				closest = distance
		# 	# check for line-of-sight walls
		# 	p2 = np.array([-1,0])
		# 	d2 = np.array([0,self.visible_height*1.5])
		# 	r = ray_intersection(p1, d1, p2, d2)
		# 	if not r==None:
		# 		distance = r*self.vision_distance
		# 		if distance<closest:
		# 			closest = distance
		# 	p2 = np.array([self.track_width+1,0])
		# 	d2 = np.array([0,self.visible_height*1.5])
		# 	r = ray_intersection(p1, d1, p2, d2)
		# 	if not r==None:
		# 		distance = r*self.vision_distance
		# 		if distance<closest:
		# 			closest = distance
		# 	if closest==np.float('+inf'):
		# 		closest = self.vision_distance
		# 	distance_data.append((self.vision_distance-closest)/float(self.vision_distance))
		# return np.array(distance_data+[self.velocity, 1])
		vision_resolution = self.track_width/5
		vision = [0]*5
		vision[0] = self.x; vision[4] = self.track_width-self.x
		for block in blocks:
			x1, y1, x2, y2 = self.canvas.coords(block)
			if y2>self.visible_height-self.vision_distance:
				diff_x = (x1+x2)/2-self.x
				if abs(diff_x)<vision_resolution*1.5:
					diff_y = self.visible_height-y2
					if diff_x>vision_resolution/2:
						vision[3] = max(vision[3], 1-diff_y/float(self.vision_distance))
					elif diff_x>-vision_resolution/2:
						vision[2] = max(vision[2], 1-diff_y/float(self.vision_distance))
					else:
						vision[1] = max(vision[1], 1-diff_y/float(self.vision_distance))
		return np.array(vision+[self.velocity, 1])

	def update(self, blocks, travel):
		if self.alive:
			self.travel = travel
			input_data = self.sense(blocks)
			self.acceleration = self.acceleration_choices[np.argmax(self.neural_net.forward(input_data))]
			# self.acceleration = self.neural_net.forward(input_data)[0]
			self.velocity += self.acceleration
			self.x += self.velocity
			diff = int(self.x)-self.reported_x
			if diff:
				self.reported_x += diff
				self.canvas.move(self.id, diff, 0)
				if self.enable_rays:
					[self.canvas.move(ray, diff, 0) for ray in self.vision_rays]
			self.check_hit(blocks)
	
	def check_hit(self, blocks):
		for block in blocks:
			x1, y1, x2, y2 = self.canvas.coords(block)
			block_size = x2-x1
			if y2>self.visible_height-self.width and y2<self.visible_height+block_size:
				if self.x>x1-self.width/2 and self.x<x2+self.width/2:
					self.end()
		if self.reported_x>=self.track_width-self.width/2 or self.x<=self.width/2:
			self.end()

	def end(self):
		self.canvas.delete(self.id)
		if self.enable_rays:
			[self.canvas.delete(ray) for ray in self.vision_rays]
		self.alive = False

def unique(l):
	new_l = []
	for element in l:
		if element not in new_l:
			new_l.append(element)
	return new_l

def best_two(fitness):
	# u = unique(fitness)
	# if len(u)==1:
	# 	return u[0], 0, u[0], 1
	# else:
	# 	dad_fitness, mom_fitness = sorted(u)[-2:]
	# 	return dad_fitness, fitness.index(dad_fitness), mom_fitness, fitness.index(mom_fitness)
	dad_fitness, mom_fitness = sorted(fitness)[-2:]
	if dad_fitness==mom_fitness:
		indices = []
		for i in range(len(fitness)):
			if fitness[i]==mom_fitness:
				indices.append(i)
			if len(indices)==2:
				break
		mom_index, dad_index = indices
	else:
		mom_index = fitness.index(mom_fitness)
		dad_index = fitness.index(dad_fitness)
	return dad_fitness, dad_index, mom_fitness, mom_index

def clean_save_file():
	with open('data.dat','w') as f:
		pickle.dump([],f)

def save_fitness_data(v1, v2, m3, v3, data):
	with open('data.dat','r') as f:
		previous_save = pickle.load(f)
	with open('data.dat','w') as f:
		pickle.dump(previous_save+[(v1, v2, m3, v3, data)],f)


def train(rg, v1, v2, m3, v3):
	num_children = 40
	mom = NeuralNet([7,9,4,3], variance=v1)
	dad = NeuralNet([7,9,4,3], variance=v2)
	generation = 0
	best_fitness = 0
	best_neural_net = None
	for _ in range(20):
		first_born = mom.breed(dad)
		children = [first_born.mutate(m3, v3) for _ in range(num_children)]
		rg.initialize_racers(children)
		rg.start()
		# ipy.embed()
		dad_fitness, dad_index, mom_fitness, mom_index = best_two(rg.fitnesses)
		mom = children[mom_index]
		dad = children[dad_index]
		if mom_fitness>best_fitness:
			best_neural_net = children[mom_index]
			best_fitness = mom_fitness
		generation += 1
		print("Generation {}:".format(generation))
		print("Mom fitness: {}\tDad fitness {}".format(mom_fitness, dad_fitness))
	return best_neural_net


def block_locations_to_lists(locations, block_size, visible_height):
	track_data = []
	offset = np.array([block_size, block_size])
	highest_y = sorted(locations, key=lambda item: item[1])[-1][1]
	num_screens = np.ceil(highest_y/float(visible_height))
	for num in range(int(num_screens)):
		visible_locations = [location for location in locations if (location[1]>num*visible_height and location[1]<=(num+1)*visible_height)]
		current_block_locations = [location-np.array([0,num*visible_height]) for location in visible_locations]
		blocks = [(location[0], -location[1], location[0]+offset[0], -location[1]-offset[1]) for location in current_block_locations]
		track_data.append(blocks)
	return track_data

def path_to_block_locations(points, block_size):
	locations = []
	offset = np.array([-block_size/2, -block_size/2])
	for i in range(len(points)-1):
		diff = np.array(points[i+1])-np.array(points[i])
		# ipy.embed()
		num_blocks = int(np.linalg.norm(diff)/block_size)
		for j in range(num_blocks):
			locations.append(np.array(points[i])+j*block_size*diff/np.linalg.norm(diff)+offset)
	return locations

def training_track(track_width, visible_height, block_size):
	t = track_width; v = visible_height
	left = [(t/4, 0), (0, v), (t/2, 3*v), (0, 3.5*v), (t/2, 4*v), (0, 4.5*v), (t/2, 5*v)]
	right = [(3*t/4, 0), (t/2, v), (t, 3*v), (t/2, 3.5*v), (t, 4*v), (t/2, 4.5*v), (t, 5*v)]
	locations = path_to_block_locations(left, block_size)+path_to_block_locations(right, block_size)
	track_data = block_locations_to_lists(locations, block_size, visible_height)
	# ipy.embed()
	return track_data

def search_hyperparameter_space():
	clean_save_file()
	rg = RaceGraphics()
	rg.static_track_data()
	v1s, m3s, v3s = np.logspace(-1,2,4), np.logspace(-1.5,-0.5,4), np.logspace(-1,-0.5,4)
	choices = zip(*[np.random.choice(range(4),size=4,replace=False) for _ in range(3)])
	for (i, k, m) in choices:
		v1, m3, v3 = v1s[i], m3s[k], v3s[m]
		data = train(rg, v1, v1, m3, v3)
		save_fitness_data(v1, v2, m3, v3, data)

if __name__=='__main__':
	v1 = 1; v2 = 1; m3 = .5; v3 = 0.5
	rg = RaceGraphics()
	rg.track_data = training_track(rg.track_width, rg.visible_height, rg.block_size)
	best_nn = train(rg, v1, v1, m3, v3)
	rg = RaceGraphics()
	raw_input()
	for _ in range(10):
		rg.initialize_racers([best_nn])
		rg.start()





