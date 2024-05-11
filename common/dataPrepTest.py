import unittest

import sys
sys.path.append('.')

from dataPrep import *

""" Testing replace_null function
"""

class TestReplaceNull(unittest.TestCase):
    def test_replace_null(self):
        
        data_src = pd.DataFrame({'a': [1, 2, 3, 4]})
        self.assertEqual(data_src['a'].isnull().sum(), 0)
        data_src = replace_null(data_src)
        self.assertEqual(data_src['a'].isnull().sum(), 0)
        
        data_src = pd.DataFrame({'a': [1, np.nan, 3, 4]})
        self.assertEqual(data_src['a'].isnull().sum(), 1)
        data_src = replace_null(data_src)
        self.assertEqual(data_src['a'].isnull().sum(), 1)
        
        data_src = pd.DataFrame({'a': [1, 2, 3, 4,'<Null>', '']})
        self.assertEqual(data_src['a'].isnull().sum(), 0)
        data_src = replace_null(data_src, ['<Null>', ''])
        self.assertEqual(data_src['a'].isnull().sum(), 2)
        
        data_src = pd.DataFrame({'a': [1, 'NaN', 3, '<Nul>', np.nan, float('nan')]})
        self.assertEqual(data_src['a'].isnull().sum(), 2)
        data_src = replace_null(data_src)
        self.assertEqual(data_src['a'].isnull().sum(), 4)
        
        
        
""" Run tests
"""
if __name__ == '__main__':
    unittest.main()
    