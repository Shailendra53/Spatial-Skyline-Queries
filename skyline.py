import numpy as np
from rtreelib import Rect

class SkylinePoint(object):
	"""docstring for SkylinePoint"""

	def __init__(self, point):
		super(SkylinePoint, self).__init__()
		self.point = point
		
	def findDistanceBetweenPoints(self, point1, point2):
		if point1 is not None and point2 is not None:
			return np.sqrt(np.square(point1[0] - point2[0]) + np.square(point1[1] - point2[1]))
		else:
			return None

	def isValueLiesBetweenGivenLimits(self, val, limit):
		limit = sorted(limit)
		return val >= limit[0] and val <= limit[-1]

	def convertTwoPointsToLine(self, point1, point2):
		'''
			input:-
				point1 = (x1,y1)
				point2 = (x2,y2)
			
			output:-
				(a,b,c) :- line constants of line ax + by + c = 0
		'''
		if (point2[0] - point1[0]) == 0:
			return (1, 0, -point1[0])

		slope = (point2[1] - point1[1])/(point2[0] - point1[0])
		a = slope
		b = -1
		c = point1[1] - slope*point1[0]

		return (a,b,c)

	def convertSlopeAndPointToLine(self, slope, point):
		'''
			input:-
				slope = slope of line
				point = (x,y)
			
			output:-
				(a,b,c) :- line constants of line ax + by + c = 0
		'''
		if slope == None:
			return (1, 0, -point[0])

		a = slope
		b = -1
		c = point[1] - slope*point[0]

		return (a,b,c)

	def findDistanceBetweenLineAndPoint(self, line, point):
		'''
			input:-
			line = (a,b,c) -> line constants of line ax + by + c = 0

			output:-
			shortest distance between line and point
		'''
		a, b, c = line
		numerator = np.abs(a*point[0] + b*point[1] + c)
		denominator = np.sqrt(a*a + b*b)
		return numerator/denominator

	def findIntersectionPointOfLines(self, line1, line2):
		'''
			input:-
			line1 = (a1,b1,c1) -> line constants of line a1x + b1y + c1 = 0
			line2 = (a2,b2,c2) -> line constants of line a2x + b2y + c2 = 0

			output:-
			intersection point = (x,y)
		'''
		a1, b1, c1 = line1
		a2, b2, c2 = line2
		x, y = (None, None)

		if (a1 == 0 and a2 == 0) or (b1 == 0 and b2 == 0):
			x, y = (None, None)
		elif b1 == 0 and b2 != 0:
			x = -c1
			y = (-a2*x - c2)/b2
		elif b1 != 0 and b2 == 0:
			x = -c2
			y = (-a1*x - c1)/b1
		elif b1 !=0 and b2 != 0:
			x = ((b2*c1)/b1 - c2)/(a2 - (a1*b2)/b1)
			y = (-c1 - a1*x)/b1

		return (x,y)


	def calculateMBR(self, query_points):
		self.circle = []
		for qp in query_points:
			self.circle.append((qp, self.findDistanceBetweenPoints(self.point, qp)))
		xmin = ymin = np.inf
		xmax = ymax = -np.inf
		for qp in self.circle:
			if (qp[0][0] - qp[1]) < xmin:
				xmin = (qp[0][0] - qp[1])

			if (qp[0][0] + qp[1]) > xmax:
				xmax = (qp[0][0] + qp[1])

			if (qp[0][1] - qp[1]) < ymin:
				ymin = (qp[0][1] - qp[1])

			if (qp[0][1] + qp[1]) > ymax:
				ymax = (qp[0][1] + qp[1])

		# print(xmin, ymin, xmax, ymax)
		self.mbr = Rect(xmin, ymin, xmax, ymax)

	def returnMBR(self):
		return self.mbr

	def isPointInsideCircle(self, point, circle):
		return (np.square(point[0] - circle[0][0]) + np.square(point[1] - circle[0][1])) < np.square(circle[1])

	def isPointDominated(self, point):
		if self.circle:
			for circle in self.circle:
				if self.isPointInsideCircle(point, circle):
					return False
			return True
		else:
			print("MBR is not calculated yet...PLease use below to do so..\n\tobject.calculateMBR(query_points)")
			return None

	def isRectangleDominated(self, rect):
		if self.circle:
			point1 = (rect.min_x, rect.min_y)
			point2 = (rect.min_x, rect.max_y)
			point3 = (rect.max_x, rect.min_y)
			point4 = (rect.max_x, rect.max_y)
			if not self.isPointDominated(point1) or \
				not self.isPointDominated(point2) or \
				not self.isPointDominated(point3) or \
				not self.isPointDominated(point4):
				return False

			distance_dict = {}
			distance_dict[self.findDistanceBetweenPoints(self.point, point1)] = point1
			distance_dict[self.findDistanceBetweenPoints(self.point, point2)] = point2
			distance_dict[self.findDistanceBetweenPoints(self.point, point3)] = point3
			distance_dict[self.findDistanceBetweenPoints(self.point, point4)] = point4

			sorted_keys = sorted(distance_dict.keys())
			closest_point1 = distance_dict[sorted_keys[0]]
			closest_point2 = distance_dict[sorted_keys[1]]

			line_from_points = self.convertTwoPointsToLine(closest_point1, closest_point2)
			for circle in self.circle:
				center = circle[0]
				radius = circle[1]
				if line_from_points[0] == 0:
					center_line = self.convertSlopeAndPointToLine(None, center)
				else:
					center_line = self.convertSlopeAndPointToLine(line_from_points[1]/line_from_points[0], center)
				x, y = self.findIntersectionPointOfLines(line_from_points, center_line)
				if not x and not y:
					continue
				sd = self.findDistanceBetweenLineAndPoint(line_from_points, center)
				if sd <= radius and \
					self.isValueLiesBetweenGivenLimits(x, [closest_point1[0], closest_point2[0]]) and \
					self.isValueLiesBetweenGivenLimits(y, [closest_point1[1] ,closest_point2[1]]):
					return False

			return True
		else:
			print("MBR is not calculated yet...Please use below to do so..\n\tobject.calculateMBR(query_points)")
			return None


if __name__ == '__main__':
	points = np.array([[1,1], [2,0], [1,5], [2.5,4], [3,1]])
	sp = SkylinePoint((2,3))
	sp.calculateMBR(points)
	print(sp.isPointDominated((2,7.23)))
	print(sp.isRectangleDominated(Rect(0,-3, 2,-3.1)))