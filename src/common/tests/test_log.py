# -*- coding: utf-8 -*-
import unittest
from common.log import shrink


class LotTests(unittest.TestCase):

    def test_log_below_max_length(self):
        origin = u'origin'
        shrank = shrink(origin, 6)
        self.assertEqual(origin, shrank)

    def test_log_above_max_length(self):
        origin = u'origin_string'
        shrank = shrink(origin, 12)
        self.assertEqual(u'origin(...)string', shrank)
