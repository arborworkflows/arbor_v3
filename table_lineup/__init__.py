from fastapi import Response
from fastapi import Request
import pandas as pd
from tempfile import NamedTemporaryFile
from parsimony_tree.methods import *
import rpy2
from rpy2 import robjects
import json
# use pandas to store CSV files
import pandas as pd

def store_the_table(table):
    print('table upload method')
    #print('recveived table:',table)
    print('recevied a table with ',len(table['table']))
    # we might be able to save and use the JSON data directly, but
    # we know the R methods can read files, so lets write out the file
    table_df = pd.DataFrame(table['table'])
    # write out the data as a known filename we will use in R
    table_df.to_csv("/tmp/table_file.csv",index=False)


def store_the_tree(tree):
    print('tree upload method')
    # get the tree string from the json object
    treeString = tree['tree']
    # we might be able to save and use the  data directly, but
    # we know the R methods can read files, so lets write out the file
    with open("/tmp/tree_file.phy", mode = "w") as f:
        f.write(treeString)


def init(app):
    @app.get('/table_lineup')
    def index():
        with open('table_lineup/index.html') as indexFile:
            indexContent = indexFile.read()

        testRInterface()
        return Response(content=indexContent, media_type='text/html')


    # upload a CSV table to the server for use later
    @app.post('/table_lineup/table_upload')
    async def table_upload(table : Request):
        json_table =  await table.json()
        print('received uploaded table:',json_table)
        #tableobj = json.loads(json_info)
        #print('decoded to object:',tableobj)
        store_the_table(json_table)
        returnContent = '<p>success</p>'
        return Response(content=returnContent, media_type='text/html')


    # run the method on the previously uploaded tree and table
    @app.post('/table_lineup/run')
    async def run(params : Request):
        params_obj =  await params.json()
        print('run with column:', params_obj['column'])
        returnContent =  run_method(params_obj)
        return Response(content=returnContent, media_type='text/html')
