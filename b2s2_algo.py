import numpy as np
import rtreelib
from rtreelib import Rect
from skyline import SkylinePoint
from rtree import RTreeInstance
from convex_hull import ConvexHull
import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import argparse
import time
import os

class B2S2Algo(object):
	"""docstring for B2S2Algo"""
	def __init__(self, data_points=None, query_points=None, data_points_file=None, query_points_file=None, output_file=None):
		'''
			Constructor:
			Input: data_points/data_points_file
				   query_points/query_points_file
				   output_file
		'''
		super(B2S2Algo, self).__init__()
		if data_points:
			self.data_points = data_points
		else:
			self.data_points = self.readDataFromFile(data_points_file)

		if query_points:
			self.data_points = data_points
		else:
			self.query_points = self.readDataFromFile(query_points_file)

		if output_file:
			self.output_file = output_file
			open(self.output_file, 'w').close()
		else:
			self.output_file = 'output.log'
			open(self.output_file, 'w').close()
		self.box = None
		self.skyline_points = set()
		self.minheap = []
		self.min_heap_ele_count = 0
		self.count_rtree_nodes_accessed = 0
		self.dominance_check = 0

	def writeToOutputFile(self, data_dict):
		'''
			function to write stat file of the algo results
			input: data_dict, eg.: {'query size' : 2, 'algo time': '100s'}
		'''
		with open(self.output_file, 'a') as file:
			for key, value in data_dict.items():
				file.write(str(key) + "\t\t\t= " + str(value) + "\n")

	def writingRemainingStatsofAlgo(self, algo_time):
		'''
			Writing final remaining stats of algo 
			full algo time.
			dominance check.
			no. of rtree nodes accessed.
		'''
		data = {}
		data['Algorithm run time    '] = str(algo_time) + "s"
		data['No, of Dominance Check'] = str(self.dominance_check)
		data['R-tree Nodes accessed '] = str(self.returnRtreeNodesAccessCount())
		self.writeToOutputFile(data)

	def returnQueryPointsArea(self):
		'''
			Function to return Q MBR
			i.e. total area covered by query points.
		'''
		qp = np.array(self.query_points)
		min_x = min(qp[:,0])
		max_x = max(qp[:,0])
		min_y = min(qp[:,1])
		max_y = max(qp[:,1])
		qp_rect = [(min_x, min_y), (max_x, max_y)]

		return abs(max_x - min_x) * abs(max_y - min_y), qp_rect

	def returnDataPoints(self):
		return self.data_points

	def returnQueryPoints(self):
		return self.query_points

	def returnRtreeNodesAccessCount(self):
		return self.count_rtree_nodes_accessed

	def returnTotalNodesInRTree(self):
		return self.RTree.returnNodesCount()

	def readDataFromFile(self, filename):
		'''
			input:-
			filename: name of the file containing row wise space separated points
			output:-
			set_of_points = [(x,y),....]
		'''
		set_of_points = []
		try:
			file = open(filename, 'r')
			for line in file:
				tokens = line.strip().split()
				set_of_points.append((float(tokens[0]), float(tokens[1])))
		except Exception as e:
			print(e)
			exit()

		return set_of_points

	def plotPointsOnGraph(self):
		'''
			For visualizing the algo resutls
		'''
		if self.data_points and self.query_points and self.skyline_points:
			red_patch = mpatches.Patch(color='red', label='data points')
			green_patch = mpatches.Patch(color='green', label='query points')
			blue_patch = mpatches.Patch(color='blue', label='skyline points')
			plt.legend(handles=[red_patch])
			for pt in self.data_points:
				plt.plot(pt[0], pt[1], 'ro')
			for pt in self.query_points:
				plt.plot(pt[0], pt[1], 'go')
			for pt in self.skyline_points:
				plt.plot(pt.point[0], pt.point[1], 'bo')
			plt.legend(handles=[red_patch, green_patch, blue_patch])
			plt.show()
		else:
			print('data not available')

	def findDistanceBetweenPoints(self, point1, point2):
		if point1 is not None and point2 is not None:
			return np.sqrt(np.square(point1[0] - point2[0]) + np.square(point1[1] - point2[1]))
		else:
			return None

	def findDistanceBetweenPointAndRect(self, point, rect):
		'''
			input:-
			point - (x,y)
			rect - Rect instance
		'''
		if (point[0] >= rect.min_x) and (point[0] <= rect.max_x) and (point[1] >= rect.min_y) and (point[1] <= rect.max_y):
			return 0
		elif (point[0] >= rect.min_x) and (point[0] <= rect.max_x):
			return min(abs(point[1] - rect.min_y), abs(point[1] - rect.max_y))
		elif (point[1] >= rect.min_y) and (point[1] <= rect.max_y):
			return min(abs(point[0] - rect.min_x), abs(point[0] - rect.max_x))
		elif (point[0] < rect.min_x) and (point[1] < rect.min_y):
			return self.findDistanceBetweenPoints(point, (rect.min_x, rect.min_y))
		elif (point[0] > rect.max_x) and (point[1] > rect.max_y):
			return self.findDistanceBetweenPoints(point, (rect.max_x, rect.max_y))
		elif (point[0] < rect.min_x) and (point[1] > rect.max_y):
			return self.findDistanceBetweenPoints(point, (rect.min_x, rect.max_y))
		elif (point[0] > rect.max_x) and (point[1] < rect.min_y):
			return self.findDistanceBetweenPoints(point, (rect.max_x, rect.min_y))
		else:
			return None

	def mindistPointandSet(self, point, set_of_points):
		'''
			input:-
			point - (x,y)
			set_of_points - set of (x,y)'s
		'''
		total_dist = 0
		for pt in set_of_points:
			dist = self.findDistanceBetweenPoints(pt, point)
			if dist:
				total_dist += dist

		return total_dist

	def mindistRectAndSet(self, rect, set_of_points):
		'''
			input:-
			rect - Rect instance
			set_of_points - set of (x,y)'s
		'''
		total_dist = 0
		# print(set_of_points)
		for pt in set_of_points:
			# print(pt)
			dist = self.findDistanceBetweenPointAndRect(pt, rect)
			if dist:
				total_dist += dist

		return total_dist

	def isRectIntersectsBoxB(self, rect):
		'''
			Assumes that your self.box is not None
		'''
		if (self.box.min_x > rect.max_x) or (rect.min_x > self.box.max_x):
			return False
		if (self.box.min_y > rect.max_y) or (rect.min_y > self.box.max_y):
			return False

		return True

	def newBoxB(self, rect):
		'''
			For finding new box B of mentioned in algo line no. 12.
		'''
		if self.box:
			min_x = max(self.box.min_x, rect.min_x)
			min_y = max(self.box.min_y, rect.min_y)
			max_x = min(self.box.max_x, rect.max_x)
			max_y = min(self.box.max_y, rect.max_y)
			return Rect(min_x, min_y, max_x, max_y)

		else:
			return rect

	def isEntryDominated(self, entry_rect):
		self.dominance_check += 1
		for sp in self.skyline_points:
			if entry_rect.min_x == entry_rect.max_x and entry_rect.min_y == entry_rect.max_y:
				if sp.isPointDominated((entry_rect.min_x, entry_rect.min_y)):
					return True
			else:
				if sp.isRectangleDominated(entry_rect):
					return True
		return False

	def addToSkyline(self, entry_rect):
		x = entry_rect.min_x
		y = entry_rect.min_y
		sp = SkylinePoint((x,y))
		sp.calculateMBR(self.convexHullPoints)
		self.skyline_points.add(sp)
		return sp.returnMBR()

	def insertIntoHeap(self, priority, entry):
		key = self.mindistRectAndSet(priority, self.convexHullPoints)
		heapq.heappush(self.minheap, (key, self.min_heap_ele_count , entry))
		self.min_heap_ele_count += 1

	def initializeB2S2Algo(self, m_value=4):
		'''
			Initialize algo elements
			1. Convex Hull.
			2. Heap.
			3. writing available stats of algo to output file.
		'''
		self.dominance_check = 0
		#### Conveh Hull calculation and points retrival
		convex_hull_start_time = time.time()
		self.ch = ConvexHull(self.query_points)
		self.ch.findConvexHull()
		convex_hull_end_time = time.time()
		self.ch.convertPointsToIndividualCoordinates()
		self.convexHullPoints = self.ch.returnConvexHullPoints()

		#### RTree Initialization and heap initialization
		self.RTree = RTreeInstance(points=self.data_points, max_entries=m_value)
		self.RTree.insertDataIntoRTree()
		rtree_root = self.RTree.root
		dp_root_bb = self.RTree.root.get_bounding_rect()
		self.insertIntoHeap(dp_root_bb, rtree_root)
		self.box = dp_root_bb
		self.RTree.traverse(self.RTree.countNodes)
		# file = open('out.txt', 'w')
		# file.write(str(self.RTree.returnNodesCount()))
		# file.close()

		#### Writing pre-stats to supplied output file
		dp_l1 = abs(dp_root_bb.min_x - dp_root_bb.max_x)
		dp_l2 = abs(dp_root_bb.min_y - dp_root_bb.max_y)

		qp_area, qp_rect = self.returnQueryPointsArea()

		data = {}
		data['No. Of Data Points   ']  = len(self.returnDataPoints())
		data['No. Of Query Points  '] = len(self.returnQueryPoints())
		data['Value of M in R-tree '] = m_value
		data['Total Convex Hull pts'] = len(self.convexHullPoints)
		data['Convex Hull exec time'] = str(abs(convex_hull_end_time - convex_hull_start_time)) + 's'
		data['Total Nodes in RTree '] = self.RTree.returnNodesCount()
		data['Data points MBR area '] = str(dp_l1 * dp_l2) + "units"
		data['Query points MBR area'] = str(qp_area) + "units"
		data['Data Points Rect     '] = str([(dp_root_bb.min_x, dp_root_bb.min_y), (dp_root_bb.max_x, dp_root_bb.max_y)])
		data['Query Points Rect    '] = str(qp_rect)
		data['Query Points MBR %age'] = str(qp_area/(dp_l1 * dp_l2))

		self.writeToOutputFile(data)

	def runB2S2Algo(self):
		'''
			**IMPORATANT : call this method after you have called object.initializeB2S2Algo()
			i.e. Algorithm other parts are initialized
			B2S2 Full algo steps.
		'''
		self.count_rtree_nodes_accessed = 0
		while self.minheap:
			entry = heapq.heappop(self.minheap)[2]
			bounding_box = None
			if type(entry) == Rect:
				bounding_box = entry
			else:
				bounding_box = entry.get_bounding_rect()
			if not self.isRectIntersectsBoxB(bounding_box):
				continue
			if self.ch.isRectangleInsideConvexHull(bounding_box) or \
				not self.isEntryDominated(bounding_box):
				self.count_rtree_nodes_accessed += 1
				if type(entry) == Rect:
					mbr_of_entry = self.addToSkyline(entry)
					self.box = self.newBoxB(mbr_of_entry)
				else:
					for entry_dash in entry.entries:
						if not self.isRectIntersectsBoxB(entry_dash.rect):
							continue
						if self.ch.isRectangleInsideConvexHull(entry_dash.rect) or \
							not self.isEntryDominated(entry_dash.rect):
							# print(self.mindistRectAndSet(entry_dash.rect, self.convexHullPoints), )
							key = self.mindistRectAndSet(entry_dash.rect, self.convexHullPoints)
							if entry_dash.child:
								# heapq.heappush(self.minheap, (key, entry_dash.child))
								self.insertIntoHeap(entry_dash.rect, entry_dash.child)
							else:
								# heapq.heappush(self.minheap, (key, entry_dash.rect))
								self.insertIntoHeap(entry_dash.rect, entry_dash.rect)

		return self.skyline_points


if __name__ == '__main__':


	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--data", help = "file containing data points. each point separated by space.") 
	parser.add_argument("-q", "--query", help = "query points. same format") 
	parser.add_argument("-M", "--m-value", help = "interger value for M value of R-tree")
	parser.add_argument("-O", "--output", help = "name of the output file")

	args = parser.parse_args()
	# print(args)
	if not args.query or not args.data:
		raise Exception("Please Supply Proper arguments\nuse --help/-h to see options")

	script_start = time.time()
	b2s2 = B2S2Algo(data_points_file=args.data, query_points_file=args.query, output_file=args.output)
	if args.m_value:
		b2s2.initializeB2S2Algo(int(args.m_value))
	else:
		b2s2.initializeB2S2Algo()
	# print("Data initialized")
	start = time.time()
	# print("Runnning Algorithm")
	skyline_points = b2s2.runB2S2Algo()
	# print("Execution completed")
	end = time.time()
	b2s2.writingRemainingStatsofAlgo(abs(end - start))
	# data = {}
	# data['Algorithm run time    '] = str(abs(end - start)) + "s"
	# data['No, of Dominance Check'] = str(b2s2.dominance_check)
	# data['R-tree Nodes accessed '] = str(b2s2.returnRtreeNodesAccessCount())
	# b2s2.writeToOutputFile(data)
	print("Script Time: ", end - script_start)