from collections import MutableMapping
from types import IntType, LongType
from datetime import datetime
from .lazy_import import LazyImport
from .series import Series

class TimeSeries(Series):
    '''A representation of a time series with a fixed interval.'''

    # Forecast methods
    ETS = 'ets'
    ARIMA = 'arima'

    def __init__(self, points, frequency=None):
        '''Initialise the time series. `points` is expected to be either a list of
        tuples where each tuple represents a point (timestamp, value), or a dict where
        the keys are timestamps. Timestamps are expected to be in milliseconds.
        `frequency` is optional and is used for additional analysis.'''
        Series.__init__(self, points)
        self.frequency = frequency

    @property
    def timestamps(self):
        '''Get all timestamps from the series.'''
        return self.x

    @property
    def dates(self):
        '''Get all dates from the time series as `datetime` instances.'''
        return map(self._to_datetime, self.x)

    @property
    def values(self):
        '''Get all values from the time series.'''
        return self.y

    @property
    def interval(self):
        if len(self.points) <= 1:
            return None
        return self.points[1][0] - self.points[0][0]

    def trend(self, **kwargs):
        '''Override Series.trend() to return a TimeSeries instance.'''
        series = Series.trend(self, **kwargs)
        return TimeSeries(series.points)

    def forecast(self, horizon, method=ARIMA, positive=True, rounded=True):
        '''Forecast points beyond the time series range using the specifie
        forecasting method. `horizon` is the number of points to forecast.'''
        if len(self.points) <= 1:
            raise ArithmeticError('Cannot run forecast when len(series) <= 1')
        R = LazyImport.rpy2()
        series = LazyImport.numpy().array(self.y)
        if self.frequency is not None:
            series = R.ts(series, frequency=self.frequency)
        if method == TimeSeries.ARIMA:
            fit = R.forecast.auto_arima(series)
        elif method == TimeSeries.ETS:
            fit = R.forecast.ets(series)
        else:
            raise ValueError('Unknown forecast() method')
        forecasted = R.forecast.forecast(fit, h=horizon)
        forecast_y = list(forecasted.rx2('mean'))
        if positive:
            forecast_y = map(lambda y: max(y, 0), forecast_y)
        if rounded:
            forecast_y = map(int, forecast_y)
        interval = self.interval
        last_x = self.points[-1][0]
        forecast_x = [ last_x + x * interval for x in xrange(1, horizon+1) ]
        return TimeSeries(zip(forecast_x, forecast_y))

    def decompose(self, window=None, periodic=False, rounded=True):
        '''Use STL to decompose the time series into seasonal, trend, and
        residual components.'''
        if not self.frequency:
            raise ValueError('Cannot decompose without a time series frequency')
        R = LazyImport.rpy2()
        if periodic:
            window = 'periodic'
        elif window is None:
            window = self.frequency
        timestamps = self.x
        series = LazyImport.numpy().array(self.y)
        length = len(series)
        series = R.ts(series, frequency=self.frequency)
        kwargs = { 's.window': window }
        decomposed = R.robjects.r['stl'](series, **kwargs).rx2('time.series')
        decomposed = [ row for row in decomposed ]
        seasonal = decomposed[0:length]
        trend = decomposed[length:2*length]
        residual = decomposed[2*length:3*length]
        if rounded:
            seasonal = map(lambda y: int(round(y)), seasonal)
            trend = map(lambda y: int(round(y)), trend)
            residual = map(lambda y: int(round(y)), residual)
        seasonal = TimeSeries(zip(timestamps, seasonal))
        trend = TimeSeries(zip(timestamps, trend))
        residual = TimeSeries(zip(timestamps, residual))
        return TimeSeriesGroup(seasonal=seasonal, trend=trend, residual=residual)

    def plot(self, label=None, colour='g', style='-'): # pragma: no cover
        '''Plot the time series.'''
        pylab = LazyImport.pylab()
        pylab.plot(self.dates, self.y, '%s%s' % (colour, style), label=label)
        if label is not None:
            pylab.legend()
        pylab.show()

    def _to_datetime(self, time):
        '''Convert `time` to a datetime.'''
        if type(time) == IntType or type(time) == LongType:
            time = datetime.fromtimestamp(time // 1000)
        return time

    def __repr__(self):
        return 'TimeSeries(%s)' % repr(self.points)

class TimeSeriesGroup(MutableMapping):
    '''A group of TimeSeries.'''

    def __init__(self, *args, **kwargs):
        self.groups = {}
        self.update(dict(*args, **kwargs))

    def trend(self, **kwargs):
        '''Calculate a trend for all series in the group. See the
        `TimeSeries.trend()` method for more information.'''
        return TimeSeriesGroup({ name: series.trend(**kwargs) \
            for name, series in self.groups.iteritems() })

    def forecast(self, horizon, **kwargs):
        '''Forecast all time series in the group. See the
        `TimeSeries.forecast()` method for more information.'''
        return TimeSeriesGroup({ name: series.forecast(horizon, **kwargs) \
            for name, series in self.groups.iteritems() })

    def plot(self, overlay=True): # pragma: no cover
        '''Plot all time series in the group.'''
        pylab = LazyImport.pylab()
        colours = list('rgbymc')
        colours_len = len(colours)
        colours_pos = 0
        plots = len(self.groups)
        for name, series in self.groups.iteritems():
            colour = colours[colours_pos % colours_len]
            colours_pos += 1
            if not overlay:
                pylab.subplot(plots, 1, colours_pos)
            pylab.plot(series.dates, series.y, '%s-' % colour, label=name)
            pylab.legend()
        pylab.show()

    def rename(self, **kwargs):
        '''Rename series in the group.'''
        for old, new in kwargs.iteritems():
            if old in self.groups:
                self.groups[new] = self.groups[old]
                del self.groups[old]

    def __getitem__(self, key):
        return self.groups[key]

    def __setitem__(self, key, value):
        self.groups[key] = value

    def __delitem__(self, key):
        del self.groups[key]

    def __iter__(self):
        return iter(self.groups)

    def __len__(self):
        return len(self.groups)

    def __repr__(self):
        return 'TimeSeriesGroup(%s)' % repr(self.groups)

