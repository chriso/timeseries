from .lazy_import import LazyImport
from .series import Series
from .utilities import table_output, to_datetime
from .data_frame import DataFrame

class TimeSeries(Series):
    '''A representation of a time series with a fixed interval.'''

    # Forecast methods
    ETS = 'ets'
    ARIMA = 'arima'

    def __init__(self, points):
        '''Initialise the time series. `points` is expected to be either a list of
        tuples where each tuple represents a point (timestamp, value), or a dict where
        the keys are timestamps. Timestamps are expected to be in milliseconds.'''
        Series.__init__(self, points)

    @property
    def timestamps(self):
        '''Get all timestamps from the series.'''
        return self.x

    @property
    def dates(self):
        '''Get all dates from the time series as `datetime` instances.'''
        return map(to_datetime, self.x)

    @property
    def values(self):
        '''Get all values from the time series.'''
        return self.y

    @property
    def interval(self):
        if len(self.points) <= 1:
            return None
        return self.points[1][0] - self.points[0][0]

    def map(self, fn):
        '''Run a map function across all y points in the series.'''
        return TimeSeries(Series.map(self, fn).points)

    def trend(self, **kwargs):
        '''Override Series.trend() to return a TimeSeries instance.'''
        series = Series.trend(self, **kwargs)
        return TimeSeries(series.points)

    def forecast(self, horizon, method=ARIMA, frequency=None):
        '''Forecast points beyond the time series range using the specified
        forecasting method. `horizon` is the number of points to forecast.'''
        if len(self.points) <= 1:
            raise ArithmeticError('Cannot run forecast when len(series) <= 1')
        R = LazyImport.rpy2()
        series = LazyImport.numpy().array(self.y)
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
        timestamps = self.x
        series = LazyImport.numpy().array(self.y)
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
        pylab.plot(self.dates, self.y, '%s%s' % (colour, style), label=label)
        if label is not None:
            pylab.legend()
        pylab.show()

    def __add__(self, operand):
        return TimeSeries(Series.__add__(self, operand))

    def __sub__(self, operand):
        return TimeSeries(Series.__sub__(self, operand))

    def __mul__(self, operand):
        return TimeSeries(Series.__mul__(self, operand))

    def __div__(self, operand):
        return TimeSeries(Series.__div__(self, operand))

    def __pow__(self, operand):
        return TimeSeries(Series.__pow__(self, operand))

    def __abs__(self):
        '''Apply abs() to all series values'''
        return TimeSeries(Series.__abs__(self))

    def __round__(self, n=0):
        '''Apply round() to all series values'''
        return TimeSeries(Series.__round__(self, n))

    def __str__(self): # pragma: no cover
        data = {}
        data['Date'] = map(lambda date: date.isoformat(' '), self.dates)
        data['Value'] = self.values
        return table_output(data)

    def __repr__(self):
        return 'TimeSeries(%s)' % repr(self.points)

