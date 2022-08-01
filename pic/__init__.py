from fastapi import Response
from fastapi import Request
import pandas as pd
from tempfile import NamedTemporaryFile
#from pic.methods import table_upload
from pic.methods import *
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

    # @app.get('/api/pic/')
    # def pic(
    #     tree_file : str,
    #     table_file : str,
    #     selectedColumn : str,
    #     model: str == 'BM',
    # ):
    #     returnvalue = '<html>fit continuous</html>'
    #     return Response(content=returnvalue, media_type='text/html')


    # we still need:
    # 1. read the tree and store in backend file system (/tmp) (*DONE)
    # 2. read the table and (ditto) (*DONE)
    # 2.5 init R: ape, geiger, phytools, aRbor?
    # 3. Attach a method to the Go button  that calls R on the tree and table (*DONE)
    # 3.5 (Kristen) build a
    # 4. reformat output to make a pretty picture (probaly return JSON )
    # 5. in Javascript, make a Vega chart(s)

    # this is the method that generates the single page for the app
    @app.get('/pic')
    def index():
        with open('pic/index.html') as indexFile:
            indexContent = indexFile.read()

        testRInterface()
        return Response(content=indexContent, media_type='text/html')

    # upload a CSV table to the server for use later
    @app.post('/pic/table_upload')
    async def table_upload(table : Request):
        json_table =  await table.json()
        print('received uploaded table:',json_table)
        #tableobj = json.loads(json_info)
        #print('decoded to object:',tableobj)
        store_the_table(json_table)
        returnContent = '<p>success</p>'
        return Response(content=returnContent, media_type='text/html')

    # upload a tree file in PHY format for use later
    @app.post('/pic/tree_upload')
    async def tree_upload(tree : Request):
        tree_obj =  await tree.json()
        print('received uploaded tree:',tree_obj['tree'])
        #tableobj = json.loads(json_info)
        #print('decoded to object:',tableobj)
        store_the_tree(tree_obj)
        returnContent = '<p>success</p>'
        return Response(content=returnContent, media_type='text/html')

    # run the method on the previously uploaded tree and table
    @app.post('/pic/run')
    async def run(params : Request):
        params_obj =  await params.json()
        print('run with independent variable:',params_obj['ind_var'])
        print('run with dependent variable',params_obj['dep_var'])
        print('run with log choice:',params_obj['logop'])
        returnContent =  run_method(params_obj)
        return Response(content=returnContent, media_type='text/html')
        #return await Response(content=json.dumps(run(params_obj)),media_type='text/html')
