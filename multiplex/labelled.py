"""
A labelled visualization is one that allows labels.
These labels are normal :class:`~text.text.TextAnnotation`.
However, a labelled visualization has functionality to ensure that the labels do not overlap.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import util

from visualization import Visualization
from text.text import Annotation

class LabelledVisualization(Visualization):
	"""
	The labelled visualization adds functionality to visualizations that use labels.
	Labels are normal :class:`~text.text.TextAnnotation`.
	This class adds functionality to distribute overlapping labels.

	:ivar labels: The labels in the time series.
				  This list is used to ensure that labels do not overlap.
	:vartype labels: list of :class:`~text.text.TextAnnotation`
	"""

	def __init__(self, *args, **kwargs):
		"""
		Create the labelled visualization by initializing the list of annotations that make up the labels.
		"""

		super(LabelledVisualization, self).__init__(*args, **kwargs)
		self.labels = [ ]

	def draw_label(self, label, x, y, *args, **kwargs):
		"""
		Draw a label at the end of the line.

		:param label: The label to draw.
		:type label: str
		:param x: The x-position of the last point on the line.
		:type x: float
		:param y: The y-position of the last point on the line.
		:type y: float
		"""

		label = self.drawable.axis.text(x * 1.01, y, label, va='center', *args, **kwargs)
		self.labels.append(label)
		self._arrange_labels()

	def _arrange_labels(self):
		"""
		Go through the labels and ensure that none overlap.
		If any do overlap, move the labels.
		The function keeps repeating until no labels overlap.

		.. image:: ../examples/exports/3-overlapping-labels.png
		   :class: example
		"""

		overlapping = self._get_overlapping_labels()
		while overlapping:
			for group in overlapping:
				self._distribute_labels(group)
			overlapping = self._get_overlapping_labels()

	def _get_overlapping_labels(self):
		"""
		Get groups of overlapping labels.
		The function returns a list of lists.
		Each inner list contains the labels that overlap.
		The function automatically excludes labels that do not overlap with other labels.

		:return: A list of lists.
				 Each inner list represents overlapping labels.
		:rtype: list of lists of :class:`matplotlib.text.Text`
		"""

		figure = self.drawable.figure
		axis = self.drawable.axis

		labels = sorted(self.labels, key=lambda x: util.get_bb(figure, axis, x).y0)

		overlapping_labels = []
		for label in labels:
			assigned = False

			"""
			Go through each label and visit each group of overlapping labels.
			If the label overlaps with any label in that group, add it to that group.
			That group would have to be distributed entirely.
			"""
			for group in overlapping_labels:
				if (any([ util.overlapping(figure, axis, label, other) for other in group ])):
					group.append(label)
					assigned = True
					break

			"""
			If the label does not overlap with any other label, add it to its own group.
			Groups with a single label overlap with no other group and require no distribution.
			"""
			if not assigned:
				overlapping_labels.append([ label])

		return [ group for group in overlapping_labels if len(group) > 1 ]

	def _distribute_labels(self, labels):
		"""
		Distribute the given labels so that they do not overlap.

		:param labels: The list of overlapping labels.
		:type labels: list of :class:`matplotlib.text.Text`
		"""

		figure = self.drawable.figure
		axis = self.drawable.axis

		"""
		Calculate the total height that the labels should occupy.
		Then, get the mean y-coordinate of the labels to find the middle.
		"""
		total_height = self._get_total_height(labels)
		middle = self._get_middle(labels)

		"""
		Sort the labels in ascending order of position (y-coordinate).
		Then, move the labels one by one.
		The initial offset is calculated as the distance that the first label needs to move.
		Subsequently, the offset is calculated by adding the height of each label.
		"""
		labels = sorted(labels, key=lambda x: util.get_bb(figure, axis, x).y0)
		y0 = middle - total_height / 2.
		for label in labels:
			position = label.get_position()
			bb = util.get_bb(figure, axis, label)
			label.set_position((position[0], y0 + bb.height / 2.))
			y0 += bb.height

	def _get_total_height(self, labels):
		"""
		Get the total height of the given labels.

		:param labels: The list of labels.
		:type labels: list of :class:`matplotlib.text.Text`

		:return: The total height of the labels.
		:rtype: float
		"""

		figure = self.drawable.figure
		axis = self.drawable.axis

		return sum([ util.get_bb(figure, axis, label).height for label in labels ])

	def _get_middle(self, labels):
		"""
		Get the middle y-coordinate of the given labels.
		The middle is calculated as the mid-point between the label that is highest and lowest.

		:param labels: The list of labels.
		:type labels: list of :class:`matplotlib.text.Text`

		:return: The middle y-coordinate of the labels.
		:rtype: float
		"""

		figure = self.drawable.figure
		axis = self.drawable.axis

		labels = sorted(labels, key=lambda x: util.get_bb(figure, axis, x).y0)
		bb0, bb1 = util.get_bb(figure, axis, labels[0]), util.get_bb(figure, axis, labels[-1])

		return (bb0.y0 + bb1.y1) / 2.
