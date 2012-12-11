from types import DictType
from .lazy_import import LazyImport

class Series(object):
    '''An abstract class that represents a series of x & y points.'''

    # Trend orders
    LINEAR = 1
    QUADRATIC = 2
    CUBIC = 3
    QUARTIC = 4

    # Moving average methods
    SIMPLE = 0

    def __init__(self, points):
        '''Initialise the series. `points` is expected to be either a list of
        tuples where each tuple represents a point (x, y), or a dict where keys
        represent the x points and values represent the y points.'''
        if type(points) == DictType:
            points = points.items()
        self.points = points

    @property
    def x(self):
        '''Get all x points from the series.'''
        return [ point[0] for point in self.points ]

    @property
    def y(self):
        '''Get all y points from the series.'''
        return [ point[1] for point in self.points ]

    def trend(self, order=LINEAR, positive=True, rounded=True):
        '''Calculate a trend of the specified order and return as
        a new series.'''
        coefficients = self.trend_coefficients(order)
        x = self.x
        trend_y = LazyImport.numpy().polyval(coefficients, x)
        if positive:
            trend_y = map(lambda y: max(y, 0), trend_y)
        if rounded:
            trend_y = map(int, trend_y)
        return Series(zip(x, trend_y))

    def moving_average(self, window, method=SIMPLE, rounded=True):
        '''Calculate a moving average using the specified method and window'''
        if len(self.points) < window:
            raise ArithmeticError('Not enough points for moving average')
        numpy = LazyImport.numpy()
        if method == Series.SIMPLE:
            weights = numpy.ones(window) / float(window)
        ma_x = self.x[window-1:]
        ma_y = numpy.convolve(self.y, weights)[window-1:-(window-1)].tolist()
        if rounded:
            ma_y = map(lambda y: int(round(y)), ma_y)
        return Series(zip(ma_x, ma_y))

    def trend_coefficients(self, order=LINEAR):
        '''Calculate trend coefficients for the specified order.'''
        if not len(self.points):
            raise ArithmeticError('Cannot calculate the trend of an empty series')
        return LazyImport.numpy().polyfit(self.x, self.y, order)

    def __add__(self, operand):
        lookup = dict(operand.points)
        return Series([ ( x, y + lookup[x] ) for x, y in self.points if x in lookup ])

    def __iadd__(self, operand):
        lookup = dict(operand.points)
        self.points = [ ( x, y + lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __sub__(self, operand):
        lookup = dict(operand.points)
        return Series([ ( x, y - lookup[x] ) for x, y in self.points if x in lookup ])

    def __isub__(self, operand):
        lookup = dict(operand.points)
        self.points = [ ( x, y - lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __getitem__(self, items):
        return self.points.__getitem__(items)

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    def __repr__(self):
        return 'Series(%s)' % repr(self.points)

