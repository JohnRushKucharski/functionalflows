'''Test the characteristic module.'''
import unittest
import operator

from src.characteristic import match_symbol

class TestMatchSymbol(unittest.TestCase):
    '''Tests the match_symbol function.'''
    def test_match_symbol(self):
        '''Test the match_symbol function.'''
        self.assertEqual(match_symbol('>'), operator.gt)
