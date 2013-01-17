from types import DictType, FloatType
from .lazy_import import LazyImport
from .utilities import table_output

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
        self.points = sorted(points)

    @property
    def x(self):
        '''Get all x points from the series.'''
        return [ point[0] for point in self.points ]

    @property
    def y(self):
        '''Get all y points from the series.'''
        return [ point[1] for point in self.points ]

    def map(self, fn):
        '''Run a map function across all y points in the series.'''
        return Series([ (x, fn(y)) for x, y in self.points ])

    def trend(self, order=LINEAR, positive=True):
        '''Calculate a trend of the specified order and return as
        a new series.'''
        coefficients = self.trend_coefficients(order)
        x = self.x
        trend_y = LazyImport.numpy().polyval(coefficients, x)
        return Series(zip(x, trend_y))

    def moving_average(self, window, method=SIMPLE):
        '''Calculate a moving average using the specified method and window'''
        if len(self.points) < window:
            raise ArithmeticError('Not enough points for moving average')
        numpy = LazyImport.numpy()
        if method == Series.SIMPLE:
            weights = numpy.ones(window) / float(window)
        ma_x = self.x[window-1:]
        ma_y = numpy.convolve(self.y, weights)[window-1:-(window-1)].tolist()
        return Series(zip(ma_x, ma_y))

    def trend_coefficients(self, order=LINEAR):
        '''Calculate trend coefficients for the specified order.'''
        if not len(self.points):
            raise ArithmeticError('Cannot calculate the trend of an empty series')
        return LazyImport.numpy().polyfit(self.x, self.y, order)

    def __abs__(self):
        self.points = [ (x, abs(y)) for x, y in self.points ]

    def __round__(self, n):
        self.points = [ (x, round(y, n)) for x, y in self.points ]

    def round(self):
        # Manual delegation for v2.x
        self.__round__(0)
        return self

    def __add__(self, operand):
        if not isinstance(operand, Series):
            return Series([ ( x, y + operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return Series([ ( x, y + lookup[x] ) for x, y in self.points if x in lookup ])

    def __iadd__(self, operand):
        if not isinstance(operand, Series):
            self.points = [ ( x, y + operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, y + lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __sub__(self, operand):
        if not isinstance(operand, Series):
            return Series([ ( x, y - operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return Series([ ( x, y - lookup[x] ) for x, y in self.points if x in lookup ])

    def __isub__(self, operand):
        if not isinstance(operand, Series):
            self.points = [ ( x, y - operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, y - lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __mul__(self, operand):
        if not isinstance(operand, Series):
            return Series([ ( x, y * operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return Series([ ( x, y * lookup[x] ) for x, y in self.points if x in lookup ])

    def __imul__(self, operand):
        if not isinstance(operand, Series):
            self.points = [ ( x, y * operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, y * lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __div__(self, operand):
        if not isinstance(operand, Series):
            return Series([ ( x, float(y) / operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return Series([ ( x, float(y) / lookup[x] ) for x, y in self.points if x in lookup ])

    def __idiv__(self, operand):
        if not isinstance(operand, Series):
            self.points = [ ( x, float(y) / operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, float(y) / lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __pow__(self, operand):
        if not isinstance(operand, Series):
            return Series([ ( x, y ** operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return Series([ ( x, y ** lookup[x] ) for x, y in self.points if x in lookup ])

    def __ipow__(self, operand):
        if not isinstance(operand, Series):
            self.points = [ ( x, y ** operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, y ** lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __getitem__(self, x):
        return dict(self.points)[x]

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    def __str__(self):
        return table_output([ ('X', self.x), ('Y', self.y) ])

    def __repr__(self):
        return 'Series(%s)' % repr(self.points)

