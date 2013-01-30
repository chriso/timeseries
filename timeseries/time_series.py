from types import DictType
from .lazy_import import LazyImport
from .utilities import table_output, to_datetime
from .data_frame import DataFrame

class TimeSeries(object):
    '''A representation of a time series with a fixed interval.'''

    # Trend orders
    LINEAR = 1
    QUADRATIC = 2
    CUBIC = 3
    QUARTIC = 4

    # Moving average methods
    SIMPLE = 0

    # Forecast methods
    ETS = 'ets'
    ARIMA = 'arima'

    def __init__(self, points):
        '''Initialise the time series. `points` is expected to be either a list of
        tuples where each tuple represents a point (timestamp, value), or a dict where
        the keys are timestamps. Timestamps are expected to be in milliseconds.'''
        if type(points) == DictType:
            points = points.items()
        self.points = sorted(points)

    @property
    def timestamps(self):
        '''Get all timestamps from the series.'''
        return [ point[0] for point in self.points ]

    @property
    def dates(self):
        '''Get all dates from the time series as `datetime` instances.'''
        return [ to_datetime(timestamp) for timestamp, _ in self.points ]

    @property
    def values(self):
        '''Get all values from the time series.'''
        return [ point[1] for point in self.points ]

    @property
    def interval(self):
        if len(self.points) <= 1:
            return None
        return self.points[1][0] - self.points[0][0]

    def map(self, fn):
        '''Run a map function across all y points in the series.'''
        return TimeSeries([ (x, fn(y)) for x, y in self.points ])

    def trend(self, order=LINEAR):
        '''Override Series.trend() to return a TimeSeries instance.'''
        coefficients = self.trend_coefficients(order)
        x = self.timestamps
        trend_y = LazyImport.numpy().polyval(coefficients, x)
        return TimeSeries(zip(x, trend_y))

    def trend_coefficients(self, order=LINEAR):
        '''Calculate trend coefficients for the specified order.'''
        if not len(self.points):
            raise ArithmeticError('Cannot calculate the trend of an empty series')
        return LazyImport.numpy().polyfit(self.timestamps, self.values, order)

    def moving_average(self, window, method=SIMPLE):
        '''Calculate a moving average using the specified method and window'''
        if len(self.points) < window:
            raise ArithmeticError('Not enough points for moving average')
        numpy = LazyImport.numpy()
        if method == TimeSeries.SIMPLE:
            weights = numpy.ones(window) / float(window)
        ma_x = self.timestamps[window-1:]
        ma_y = numpy.convolve(self.values, weights)[window-1:-(window-1)].tolist()
        return TimeSeries(zip(ma_x, ma_y))

    def forecast(self, horizon, method=ARIMA, frequency=None):
        '''Forecast points beyond the time series range using the specified
        forecasting method. `horizon` is the number of points to forecast.'''
        if len(self.points) <= 1:
            raise ArithmeticError('Cannot run forecast when len(series) <= 1')
        R = LazyImport.rpy2()
        series = LazyImport.numpy().array(self.values)
        if frequency is not None:
            series = R.ts(series, frequency=frequency)
        if method == TimeSeries.ARIMA:
            fit = R.forecast.auto_arima(series)
        elif method == TimeSeries.ETS:
            fit = R.forecast.ets(series)
        else:
            raise ValueError('Unknown forecast() method')
        forecasted = R.forecast.forecast(fit, h=horizon)
        forecast_y = list(forecasted.rx2('mean'))
        interval = self.interval
        last_x = self.points[-1][0]
        forecast_x = [ last_x + x * interval for x in xrange(1, horizon+1) ]
        return TimeSeries(zip(forecast_x, forecast_y))

    def decompose(self, frequency, window=None, periodic=False):
        '''Use STL to decompose the time series into seasonal, trend, and
        residual components.'''
        R = LazyImport.rpy2()
        if periodic:
            window = 'periodic'
        elif window is None:
            window = frequency
        timestamps = self.timestamps
        series = LazyImport.numpy().array(self.values)
        length = len(series)
        series = R.ts(series, frequency=frequency)
        kwargs = { 's.window': window }
        decomposed = R.robjects.r['stl'](series, **kwargs).rx2('time.series')
        decomposed = [ row for row in decomposed ]
        seasonal = decomposed[0:length]
        trend = decomposed[length:2*length]
        residual = decomposed[2*length:3*length]
        seasonal = TimeSeries(zip(timestamps, seasonal))
        trend = TimeSeries(zip(timestamps, trend))
        residual = TimeSeries(zip(timestamps, residual))
        return DataFrame(seasonal=seasonal, trend=trend, residual=residual)

    def plot(self, label=None, colour='g', style='-'): # pragma: no cover
        '''Plot the time series.'''
        pylab = LazyImport.pylab()
        pylab.plot(self.dates, self.values, '%s%s' % (colour, style), label=label)
        if label is not None:
            pylab.legend()
        pylab.show()

    def __abs__(self):
        return TimeSeries([ (x, abs(y)) for x, y in self.points ])

    def __round__(self, n=0):
        return TimeSeries([ (x, round(y, n)) for x, y in self.points ])

    def round(self, n=0):
        # Manual delegation for v2.x
        return self.__round__(n)

    def __add__(self, operand):
        if not isinstance(operand, TimeSeries):
            return TimeSeries([ ( x, y + operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return TimeSeries([ ( x, y + lookup[x] ) for x, y in self.points if x in lookup ])

    def __iadd__(self, operand):
        if not isinstance(operand, TimeSeries):
            self.points = [ ( x, y + operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, y + lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __sub__(self, operand):
        if not isinstance(operand, TimeSeries):
            return TimeSeries([ ( x, y - operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return TimeSeries([ ( x, y - lookup[x] ) for x, y in self.points if x in lookup ])

    def __isub__(self, operand):
        if not isinstance(operand, TimeSeries):
            self.points = [ ( x, y - operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, y - lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __mul__(self, operand):
        if not isinstance(operand, TimeSeries):
            return TimeSeries([ ( x, y * operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return TimeSeries([ ( x, y * lookup[x] ) for x, y in self.points if x in lookup ])

    def __imul__(self, operand):
        if not isinstance(operand, TimeSeries):
            self.points = [ ( x, y * operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, y * lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __div__(self, operand):
        if not isinstance(operand, TimeSeries):
            return TimeSeries([ ( x, float(y) / operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return TimeSeries([ ( x, float(y) / lookup[x] ) for x, y in self.points if x in lookup ])

    def __idiv__(self, operand):
        if not isinstance(operand, TimeSeries):
            self.points = [ ( x, float(y) / operand ) for x, y in self.points ]
        else:
            lookup = dict(operand.points)
            self.points = [ ( x, float(y) / lookup[x] ) for x, y in self.points if x in lookup ]
        return self

    def __pow__(self, operand):
        if not isinstance(operand, TimeSeries):
            return TimeSeries([ ( x, y ** operand ) for x, y in self.points ])
        lookup = dict(operand.points)
        return TimeSeries([ ( x, y ** lookup[x] ) for x, y in self.points if x in lookup ])

    def __ipow__(self, operand):
        if not isinstance(operand, TimeSeries):
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

    def __str__(self): # pragma: no cover
        data = {}
        data['Date'] = [ date.isoformat(' ') for date in self.dates ]
        data['Value'] = self.values
        return table_output(data)

    def __repr__(self):
        return 'TimeSeries(%s)' % repr(self.points)

