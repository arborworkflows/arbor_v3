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
    selModel = params['selModel']
    disModel = params['disModel']
    print('RUN METHOD: params were',column,selModel,disModel)
    # now that we have all the data collected, run the R method
    r = robjects.r
    env = robjects.globalenv
    env['tree_file'] = '/tmp/tree_file.phy'
    env['table_file'] = '/tmp/table_file.csv'
    env['column'] = column
    env['selModel'] = selModel
    env['disModel'] = disModel
    env['modelfit_summary_file'] = '/tmp/modelfile.csv'
    env['plot_file'] = '/tmp/plotfile.png'
    r('''
require(aRbor)

tree <- read.tree(tree_file)
table <- read.csv(table_file, check.names = FALSE)

td <- make.treedata(tree, table) # Trying make.treedata for now...
td <- select(td, as.name(column))
phy <- td$phy
dat <- td$dat
type <- detectCharacterType(dat[[1]], cutoff = 0.2)

if (type == "discrete") {
    result <- physigArbor(td, charType=type, signalTest="pagelLambda", discreteModelType=disModel)
    analysisType <- "discrete lambda"
}

if (type == "continuous") {
    if(selModel=="Lambda") {
      result <- physigArbor(td, charType=type, signalTest="pagelLambda")
      analysisType <- "continuous lambda"
    }

    if (selModel=="K") {
      result <- physigArbor(td, charType=type, signalTest="Blomberg")
      analysisType <- "continuous K"
    }
}

result <- t(as.data.frame(unlist(result)))
rownames(result) <- analysisType
if(selModel == "Lambda"){
    colnames(result) <- c("Log-Likelihood (Lambda fixed at 0)",
                        "Log-Likelihood (Lambda estimated)",
                        "Chi-Squared Test Statistic",
                        "Chi-Squared P Value",
                        "AICc Score (Lambda fixed at 0)",
                        "AICc Score (Lambda Estimated)",
                        "Lambda Value")
}
if(selModel == "K") {
    colnames(result) <- c("K",
    		"vObs",
    		"vRnd",
    		"pVal",
    		"zScore")
}

write.csv(result, modelfit_summary_file)

    ''')
    print('** need to collect result from R here')

    result_df = pd.read_csv('/tmp/modelfile.csv')
    # Rename the first column (since R doesn't give it a name)
    result_df.rename(columns = {'Unnamed: 0':'Name'}, inplace = True)
    print(result_df)

    result_as_dict = result_df.to_dict('records')
    print('result as dict:',result_as_dict)

    returnString = json.dumps(result_as_dict)
    return returnString
