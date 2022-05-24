import rpy2
from rpy2 import robjects

def testRInterface():
    r = robjects.r
    r('''
    print('howdy from R')
    ''')