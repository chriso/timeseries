from collections import MutableMapping
from .lazy_import import LazyImport
from .series import Series
from .utilities import table_output, to_datetime

class DataFrame(MutableMapping):
    '''A group of TimeSeries.'''

    def __init__(self, *args, **kwargs):
        self.groups = {}
        self.update(dict(*args, **kwargs))

    @property
    def timestamps(self):
        '''Get all timestamps from all series in the group.'''
        timestamps = set()
        for series in self.groups.itervalues():
            timestamps |= set(series.timestamps)
        return sorted(list(timestamps))

    def trend(self, **kwargs):
        '''Calculate a trend for all series in the group. See the
        `TimeSeries.trend()` method for more information.'''
        return DataFrame({ name: series.trend(**kwargs) \
            for name, series in self.groups.iteritems() })

    def forecast(self, horizon, **kwargs):
        '''Forecast all time series in the group. See the
        `TimeSeries.forecast()` method for more information.'''
        return DataFrame({ name: series.forecast(horizon, **kwargs) \
            for name, series in self.groups.iteritems() })

    def plot(self, overlay=True, **labels): # pragma: no cover
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
            kwargs = {}
            if name in labels:
                name = labels[name]
            if name is not None:
                kwargs['label'] = name
            pylab.plot(series.dates, series.y, '%s-' % colour, **kwargs)
            if name is not None:
                pylab.legend()
        pylab.show()

    def rename(self, **kwargs):
        '''Rename series in the group.'''
        for old, new in kwargs.iteritems():
            if old in self.groups:
                self.groups[new] = self.groups[old]
                del self.groups[old]

    def round(self):
        # Manual delegation for v2.x
        self.__round__(0)
        return self

    def __abs__(self):
        for key, series in self.groups.iteritems():
            self.groups[key] = abs(series)
        return self

    def __round__(self, n):
        for key, series in self.groups.iteritems():
            self.groups[key] = series.round()
        return self

    def __getitem__(self, key):
        return self.groups[key]

    def __setitem__(self, key, value):
        self.groups[key] = value

    def __getattr__(self, key):
        return self.groups[key]

    def __delitem__(self, key):
        del self.groups[key]

    def __iter__(self):
        return iter(self.groups)

    def __len__(self):
        return len(self.groups)

    def __str__(self): # pragma: no cover
        data = []
        timestamps = self.timestamps
        dates = map(lambda date: to_datetime(date).isoformat(' '), timestamps)
        data = [ ( 'Date', dates ) ]
        for key, series in self.groups.iteritems():
            row = []
            series = dict(series.points)
            for timestamp in timestamps:
                if timestamp in series:
                    row.append(series[timestamp])
                else:
                    row.append('')
            data.append(( key, row ))
        return table_output(data)

    def __repr__(self):
        return 'DataFrame(%s)' % repr(self.groups)

