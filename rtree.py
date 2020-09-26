from rtreelib import RTree, Rect
from rtreelib.diagram import create_rtree_diagram
import sys
import numpy as np
import rtreelib

class RTreeInstance(RTree):
	"""docstring for RTreeInstance"""
	def __init__(self, max_entries=4, points=None):
		super(RTreeInstance, self).__init__(max_entries)
		self.points = points
		self.nodes_count = 0

	def returnNodesCount(self):
		return self.nodes_count

	def insertDataIntoRTree(self):
		for i, point in enumerate(self.points):
			x = point[0]
			y = point[1]
			self.insert(i, Rect(x, y, x, y))

	def readDataFromFile(self, filename):
		'''
			param: filename - name of the file to take input from.
			processs: constructs the RTreeInstance from given file.
		'''
		self.points = []
		print("Opening file %s and reading data from: " % filename)
		file =  open(filename, 'r')
		for i, line in enumerate(file):
			try:
				tokens = line.strip().split()
				x = float(tokens[0])
				y = float(tokens[1])
				self.points.append(np.array([x,y]))
				# self.insert(i, Rect(x, y, x, y))
			except:
				print("Cannot Insert data at line Number %s Please verify" % i+1)

		print("Task Completed")

	def dfs(self, node):
		if node.is_leaf:
			for entry in node.entries:
				if type(entry.rect) == Rect:
					pass
					# print('yes')
		else:
			for entry in node.entries:
				pass
				# print(entry.child.get_bounding_rect(), entry.rect, entry.is_leaf)

	def returnPoints(self):
		return self.points

	def countNodes(self, node):
		if node.is_leaf:
			self.nodes_count += 1
			for entry in node.entries:
				self.nodes_count += 1
		else:
			self.nodes_count += 1

	def createRTreeDiagram(self):
		create_rtree_diagram(self)

if __name__ == '__main__':
	
	# Create an RTree instance with some sample data
	t = RTreeInstance(max_entries=4)
	print(type(RTree()))
	# reading data from file
	t.readDataFromFile(sys.argv[1])
	t.insertDataIntoRTree()
	# traverse the RTree.....
	print(t.traverse(t.dfs))
	print(type(t.root) == rtreelib.rtree.RTreeNode)
	print(t.root.get_bounding_rect())
	# Create a diagram of the R-tree structure
	create_rtree_diagram(t)