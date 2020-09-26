import numpy as np
import scipy.spatial #import ConvexHull, convex_hull_plot_2d
import matplotlib.pyplot as plt
from rtreelib import Rect

class ConvexHull(object):
	"""docstring for ConvexHull"""
	def __init__(self, x_list, y_list):
		super(ConvexHull, self).__init__()
		self.xpoints = x_list
		self.ypoints = y_list
		self.convexHullPoints = None

	def __init__(self, query_points):
		super(ConvexHull, self).__init__()
		self.points = query_points
		self.convexHullPoints = None

	def convertToPoints(self):
		self.xpoints = np.array(self.xpoints)
		self.ypoints = np.array(self.ypoints)
		self.points = np.array([self.xpoints, self.ypoints])
		self.points = np.transpose(self.points)

	def convertPointsToIndividualCoordinates(self):
		self.xpoints = []
		self.ypoints = []
		for point in self.points:
			self.xpoints.append(point[0])
			self.ypoints.append(point[1])

	def returnPoints(self):
		return self.points

	def findConvexHull(self):
		try:
			if len(self.points) > 2:
				self.convexHull = scipy.spatial.ConvexHull(self.points)
				self.convertToHullPoints()
			else:
				self.convexHullPoints = self.points
		except Exception as e:
			print(e)

	def plotConvexHull(self):
		if self.convexHullPoints:
			plt.plot(self.points[self.convexHull.vertices, 0], self.points[self.convexHull.vertices, 1], 'r--')
			plt.plot(self.xpoints, self.ypoints, 'o')
			plt.show()
		else:
			print("Points yet to be calculated\n Use below to calculate convex hull points.....\n\tobject.findConvexHull()")

	def printConvexHullPoints(self):
		if self.convexHullPoints:
			for vertex in self.convexHullPoints:
				print(vertex)
		else:
			print("Points yet to be calculated\n Use below to calculate convex hull points.....\n\tobject.findConvexHull()")

	def convertToHullPoints(self):
		self.convexHullPoints = []
		for vertex in self.convexHull.vertices:
			self.convexHullPoints.append(self.points[vertex])

	def convexHullPointsCount(self):
		if self.convexHullPoints:
			return len(self.convexHullPoints)
		else:
			return None

	def returnConvexHullPoints(self):
		if self.convexHullPoints:
			return np.array(self.convexHullPoints)
		else:
			print("Points yet to be calculated\n Use below to calculate convex hull points.....\n\tobject.findConvexHull()")
			return None

	def returnAngle(self, p, p1, p2):
		'''
			Given points p, p1 and p2
			function return angle between lines p-p1 and p-p2.
		'''
		pp1 = p1 - p
		pp2 = p2 - p
		angle = None
		if np.dot(pp1, pp2) == 0.0:
			angle = 1.0
		else:
			cos_angle = np.dot(pp1, pp2) / (np.linalg.norm(pp1) * np.linalg.norm(pp2))
			angle = np.arccos(cos_angle)
		return np.degrees(angle)

	def isPointInsideConvexHull(self, point):
		point = np.array(point)
		if self.convexHullPoints:
			angleSum = 0
			totalPoints = self.convexHullPointsCount()
			for i in range(totalPoints):
				if point[0] == self.convexHullPoints[i][0] and point[1] == self.convexHullPoints[i][1]:
					return True
				point1 = np.array(self.convexHullPoints[i%totalPoints])
				point2 = np.array(self.convexHullPoints[(i+1)%totalPoints])
				angleSum += self.returnAngle(point, point1, point2)
			if abs(angleSum - 360) < 0.00001:
				return True
			else:
				return False
		else:
			print("Points yet to be calculated\n Use below to calculate convex hull points.....\n\tobject.findConvexHull()")
			return False

	def isRectangleInsideConvexHull(self, rect):
		'''
			input: rect - Rect object
			process: to check if all points of rect inside convex hull or not
		'''
		if self.convexHullPoints:
			point1 = (rect.min_x, rect.min_y)
			point2 = (rect.min_x, rect.max_y)
			point3 = (rect.max_x, rect.min_y)
			point4 = (rect.max_x, rect.max_y)
			if self.isPointInsideConvexHull(point1) and \
					self.isPointInsideConvexHull(point2) and \
					self.isPointInsideConvexHull(point3) and \
					self.isPointInsideConvexHull(point4):
				return True
			else:
				return False
		else:
			print("Points yet to be calculated\n Use below to calculate convex hull points.....\n\tobject.findConvexHull()")
			return False


if __name__ == '__main__':
	points = np.array([[1,1], [2,0], [2,3], [1,5], [2.5,4], [3,1]])
	ch = ConvexHull(points)
	# ch.convertToPoints()
	ch.findConvexHull()
	ch.convertPointsToIndividualCoordinates()
	points = ch.returnConvexHullPoints()
	print(points)
	print("point: ", ch.isPointInsideConvexHull((1.5,0.5)))
	# print(ch.isPointInsideConvexHull((3,2)))
	# print(ch.isPointInsideConvexHull((3,0)))
	# print(ch.isPointInsideConvexHull((5,5)))
	# print(ch.isRectangleInsideConvexHull([(1,1), (2,2)]))
	# print(ch.isRectangleInsideConvexHull(Rect(1.5,1.5,2,2)))
	ch.plotConvexHull()