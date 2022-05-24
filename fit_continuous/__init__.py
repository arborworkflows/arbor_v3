from fastapi import Response
import pandas as pd
from tempfile import NamedTemporaryFile


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


    @app.get('/fit_continuous')
    def index():
        with open('fit_continuous/index.html') as indexFile:
            indexContent = indexFile.read()
        
        return Response(content=indexContent, media_type='text/html')
