from fastapi import Response
import pandas as pd
from tempfile import NamedTemporaryFile
import rpy2
from rpy2 import robjects

#from methods import testRInterface

def testRInterface():
    r = robjects.r
    r('''
    print('howdy from R')
    ''')


def init(app):

    # @app.get('/api/fit_continuous/')
    # def fit_continuous(
    #     tree_file : str,
    #     table_file : str,
    #     selectedColumn : str,
    #     model: str == 'BM',
    # ):
    #     returnvalue = '<html>fit continuous</html>'
    #     return Response(content=returnvalue, media_type='text/html')


    # we still need:
    # 1. read the tree and store in backend file system (/tmp)
    # 2. read the table and (ditto)
    # 3. Attach a method to the Go button  that calls R on the tree and table
    # 3.5 (Kristen) build a 
    # 4. reformat output to make a pretty picture (probaly return JSON )
    # 5. in Javascript, make a Vega chart(s) 

    @app.get('/fit_continuous')
    def index():
        with open('fit_continuous/index.html') as indexFile:
            indexContent = indexFile.read()
        
        testRInterface()
        return Response(content=indexContent, media_type='text/html')
