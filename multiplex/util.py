"""
A set of utility functions that are common to all types of visualizations.
"""

def get_bb(figure, axis, component, transform=None):
	"""
	Get the bounding box of the given component.

	:param figure: The figure that the component occupies.
				   This is used to get the figure renderer.
	:type figure: :class:`matplotlib.figure.Figure`
	:param axis: The axis (or subplot) where the component is plotted.
	:type axis: :class:`matplotlib.axis.Axis`
	:param component: The component whose bounding box will be fetched.
	:type component: object
	:param transform: The bounding box transformation.
					  If `None` is given, the data transformation is used.
	:type transform: None or :class:`matplotlib.transforms.TransformNode`

	:return: The bounding box of the text object.
	:rtype: :class:`matplotlib.transforms.Bbox`
	"""

	transform = axis.transData if transform is None else transform

	renderer = figure.canvas.get_renderer()
	bb = component.get_window_extent(renderer).inverse_transformed(transform)
	return bb

def overlapping(figure, axis, c1, c2, *args, **kwargs):
	"""
	Check whether the given components overlap.
	The overlap considers the bounding box, and is therefore not perfectly precise.

	:param figure: The figure that the component occupies.
				   This is used to get the figure renderer.
	:type figure: :class:`matplotlib.figure.Figure`
	:param axis: The axis (or subplot) where the component is plotted.
	:type axis: :class:`matplotlib.axis.Axis`
	:param c1: The first component.
			   Its bounding box will be compared to the second component.
	:type c1: object
	:param c2: The second component.
			   Its bounding box will be compared to the first component.
	:type c2: object

	:return: A boolean indicating whether the two components overlap.
	:rtype: bool
	"""

	bb1, bb2 = get_bb(figure, axis, c1, *args, **kwargs), get_bb(figure, axis, c2, *args, **kwargs)

	return (
		(bb2.x0 < bb1.x0 < bb2.x1 or bb2.x0 < bb1.x1 < bb2.x1) and
		(bb2.y0 < bb1.y0 < bb2.y1 or bb2.y0 < bb1.y1 < bb2.y1) or
		(bb1.x0 < bb2.x0 < bb1.x1 or bb1.x0 < bb2.x1 < bb1.x1) and
		(bb1.y0 < bb2.y0 < bb1.y1 or bb1.y0 < bb2.y1 < bb1.y1)
	)

def get_linespacing(figure, axis, wordspacing=0, *args, **kwargs):
	"""
	Calculate the line spacing of text tokens.
	The line spacing is calculated by creating a token and getting its height.
	The token is immediately removed.
	The token's styling have to be provided as keyword arguments.

	:param figure: The figure that the component occupies.
				   This is used to get the figure renderer.
	:type figure: :class:`matplotlib.figure.Figure`
	:param axis: The axis (or subplot) where the component is plotted.
	:type axis: :class:`matplotlib.axis.Axis`
	:param wordspacing: The spacing between tokens.
						This is used to be able to create the padding around words.
	:type wordspacing: float

	:return: The line spacing.
	:rtype: float
	"""

	"""
	Draw a dummy token first.
	Some styling are set specifically for the bbox.
	"""
	bbox_kwargs = { 'facecolor': 'None', 'edgecolor': 'None' }
	for arg in bbox_kwargs:
		if arg in kwargs:
			bbox_kwargs[arg] = kwargs.get(arg)
			del kwargs[arg]

	"""
	The bbox's padding is calculated in pixels.
	Therefore it is transformed from the provided axis coordinates to pixels.
	"""
	wordspacing_px = (axis.transData.transform((wordspacing, 0))[0] -
					  axis.transData.transform((0, 0))[0])
	token = axis.text(0, 0, 'None', bbox=dict(pad=wordspacing_px / 2., **bbox_kwargs),
					  *args, **kwargs)

	"""
	Get the height from the bbox.
	"""
	bb = get_bb(figure, axis, token)
	height = bb.height
	token.remove()
	return height
