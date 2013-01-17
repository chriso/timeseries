from unittest import TestCase
from timeseries import Series

class TestSeries(TestCase):

    def test_tuple_list_init(self):
        series = Series([ (1, 2), (3, 4), (5, 6) ])
        self.assertListEqual(series.x, [1, 3, 5])
        self.assertListEqual(series.y, [2, 4, 6])
        self.assertEquals(len(series), 3)

    def test_dict_init(self):
        series = Series({ 1: 2, 3: 4, 5: 6 })
        self.assertListEqual(series.x, [1, 3, 5])
        self.assertListEqual(series.y, [2, 4, 6])
        self.assertEquals(len(series), 3)

    def test_iteration(self):
        points = [ (1, 2), (3, 4), (5, 6) ]
        series = Series(points)
        self.assertListEqual([ s for s in series ], points)

    def test_map(self):
        series = Series([ (1, 2), (3, 4), (5, 6) ])
        double = series.map(lambda y: y * 2)
        self.assertTrue(isinstance(double, Series))
        self.assertListEqual([ (1, 4), (3, 8), (5, 12) ], double.points)

    def test_trend_of_empty_series(self):
        with self.assertRaises(ArithmeticError):
            series = Series([])
            trend = series.trend(order=Series.LINEAR)

    def test_trend_return_type(self):
        trend = Series([ (1, 3), (2, 5) ]).trend(order=Series.LINEAR)
        self.assertTrue(isinstance(trend, Series))

    def test_linear_trend(self):
        series = Series([ (1, 32), (2, 55), (3, 40) ])
        trend = series.trend(order=Series.LINEAR).round()
        self.assertListEqual(trend.x, [1, 2, 3])
        self.assertListEqual(trend.y, [38, 42, 46])

    def test_quadratic_trend(self):
        series = Series([ (1, 32), (2, 55), (3, 40), (4, 100) ])
        trend = series.trend(order=Series.QUADRATIC).round()
        self.assertListEqual(trend.x, [1, 2, 3, 4])
        self.assertListEqual(trend.y, [38, 38, 57, 94])

    def test_indexing(self):
        series = Series([ (1, 3), (2, 3), (3, 3) ])
        self.assertEquals(series[1], 3)
        self.assertEquals(series[2], 3)
        with self.assertRaises(KeyError):
            foo = series[4]

    def test_add(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 1), (1, 1), (2, 1), (3, 1), (4, 1) ])
        c = a + b
        self.assertListEqual(c.points, [ (1, 4), (2, 4), (3, 4) ])

    def test_add_update(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 1), (1, 1), (2, 1), (3, 1), (4, 1) ])
        a += b
        self.assertListEqual(a.points, [ (1, 4), (2, 4), (3, 4) ])

    def test_sub(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 1), (1, 1), (2, 1), (3, 1), (4, 1) ])
        c = a - b
        self.assertListEqual(c.points, [ (1, 2), (2, 2), (3, 2) ])

    def test_sub_update(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 1), (1, 1), (2, 1), (3, 1), (4, 1) ])
        a -= b
        self.assertListEqual(a.points, [ (1, 2), (2, 2), (3, 2) ])

    def test_mul(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 2), (1, 3), (2, 2), (3, 2), (4, 1) ])
        c = a * b
        self.assertListEqual(c.points, [ (1, 9), (2, 6), (3, 6) ])

    def test_mul_update(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 2), (1, 3), (2, 2), (3, 2), (4, 1) ])
        a *= b
        self.assertListEqual(a.points, [ (1, 9), (2, 6), (3, 6) ])

    def test_div(self):
        a = Series([ (1, 3), (2, 4), (3, 3) ])
        b = Series([ (0, 2), (1, 3), (2, 2), (3, 2), (4, 1) ])
        c = a / b
        self.assertListEqual(c.points, [ (1, 1), (2, 2), (3, 1.5) ])

    def test_div_update(self):
        a = Series([ (1, 3), (2, 4), (3, 3) ])
        b = Series([ (0, 2), (1, 3), (2, 2), (3, 2), (4, 1) ])
        a /= b
        self.assertListEqual(a.points, [ (1, 1), (2, 2), (3, 1.5) ])

    def test_pow(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 2), (1, 3), (2, 2), (3, 1), (4, 1) ])
        c = a ** b
        self.assertListEqual(c.points, [ (1, 27), (2, 9), (3, 3) ])

    def test_pow_update(self):
        a = Series([ (1, 3), (2, 3), (3, 3) ])
        b = Series([ (0, 2), (1, 3), (2, 2), (3, 1), (4, 1) ])
        a **= b
        self.assertListEqual(a.points, [ (1, 27), (2, 9), (3, 3) ])

    def test_simple_moving_average(self):
        points = [1, 2, 3, 4, 5, 6]
        series = Series(zip(points, points))
        ma = series.moving_average(3).round()
        self.assertListEqual(ma.points, [ (3, 2), (4, 3), (5, 4), (6, 5) ])
        ma = series.moving_average(5).round()
        self.assertListEqual(ma.points, [ (5, 3), (6, 4) ])

    def test_invalid_moving_average(self):
        series = Series([])
        with self.assertRaises(ArithmeticError):
            series.moving_average(3)
        series = Series([ (1, 1), (2, 2) ])
        with self.assertRaises(ArithmeticError):
            series.moving_average(3)

