from datetime import datetime
from types import IntType, LongType, DictType

def table_output(data):
    '''Get a table representation of a dictionary.'''
    if type(data) == DictType:
        data = data.items()
    headings = [ item[0] for item in data ]
    rows = [ item[1] for item in data ]
    columns = zip(*rows)
    widths = [ max(map(lambda y: len(str(y)), row)) for row in rows ]
    for c, heading in enumerate(headings):
        widths[c] = max(widths[c], len(heading))
    column_count = range(len(rows))
    table = [ ' '.join([ headings[c].ljust(widths[c]) for c in column_count ]) ]
    table.append(' '.join([ '=' * widths[c] for c in column_count ]))
    for column in columns:
        table.append(' '.join([ str(column[c]).ljust(widths[c]) for c in column_count ]))
    return '\n'.join(table)

def to_datetime(time):
    '''Convert `time` to a datetime.'''
    if type(time) == IntType or type(time) == LongType:
        time = datetime.fromtimestamp(time // 1000)
    return time

