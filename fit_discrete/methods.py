import rpy2
import pandas as pd
import numpy as np
from rpy2 import robjects
import rpy2.robjects.numpy2ri as rpyn
import os
import json

def testRInterface():
    r = robjects.r
    r('''
    print('howdy from R')
    ''')


def table_upload():
    print('table upload method')


def run_method(params):
    # pull the arguments from the JSON object
    print(   'got to the run method'   )
    column = params['column']
    model = params['model']
    transform = params['transform']
    print('RUN METHOD: params were',column,model,transform)
    # now that we have all the data collected, run the R method
    r = robjects.r
    env = robjects.globalenv
    env['tree_file'] = '/tmp/tree_file.phy'
    env['table_file'] = '/tmp/table_file.csv'
    env['column'] = column
    env['model'] = model
    env['transform'] = transform
    env['modelfit_summary_file'] = '/tmp/modelfile.csv'
    env['plot_file'] = '/tmp/plotfile.png'
    r('''
require(ape)
require(geiger)
require(phytools)

tree <- read.tree(tree_file)
table <- read.csv(table_file, row.names = 1, check.names = FALSE)

td <- treedata(tree, table)
df <- as.data.frame(td$data)
dat <- df[,column, drop = FALSE]
phy <- td$phy

print(column)

result <- fitDiscrete(phy, dat, model, transform)

result <- t(as.data.frame(unlist(result$opt)))
rownames(result) <- "Primary results"
print(result)

write.csv(result, modelfit_summary_file)
    ''')
    print('** need to collect result from R here')
    #print(env['result'])
    #print(type(env['result']))

    #valuesOnlyButNoKeys = np.asarray(env['result'])
    result_df = pd.read_csv('/tmp/modelfile.csv')
    # Rename the first column (since R doesn't give it a name)
    result_df.rename(columns = {'Unnamed: 0':'Name'}, inplace = True)
    print(result_df)

    result_as_dict = result_df.to_dict('records')
    print('result as dict:',result_as_dict)

    # retreive the phenogram information from the R result
    #connections_df = pd.read_csv('/tmp/pheno_connections.csv')
    #points_df = pd.read_csv('/tmp/pheno_points.csv')
    #connections_json = connections_df.to_dict('records')
    #points_json = points_df.to_dict('records')
    #print(points_json)

    # [{},{}]
    # json:  {'data': []}

    # repack from pandas dataframe into a dictionary.
    # values are returned as a list of one dictionary, so pick the first list entry
    #result = {}
    #result['points'] = points_json
    #result['connections'] = connections_json
    #for key in result_as_dict[0].keys():
    #    result[key] = result_as_dict[0][key]

    # return the data arrays here as a JSON blob to javascript
    # for javascript to render in vegalite
    returnString = json.dumps(result_as_dict)
    return returnString

    ## Kristen wanted to try pandas.DataFrame.to_json! Might be more streamlined?

    # Rename the first column (since R doesn't give it a name)
    #result_df.rename(columns = {'Unnamed: 0':'Name'}, inplace = True)

    #print(result_df)

    # Now that first column is renamed, turn it into a JSON
    # 'records' orient is most similar to dictionary -> json.dumps (I think)
    #returnString = result_df.to_json(orient = 'records')

    #return returnString


    # clean up the temporary files
    # os.deletefile()