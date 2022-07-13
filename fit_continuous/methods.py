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
    stdError = params['stdError']
    print('RUN METHOD: params were',column,model,stdError)
    # now that we have all the data collected, run the R method
    r = robjects.r
    env = robjects.globalenv
    env['tree_file'] = '/tmp/tree_file.phy'
    env['table_file'] = '/tmp/table_file.csv'
    env['column'] = column
    env['model'] = model
    env['stdError'] = stdError
    env['modelfit_summary_file'] = '/tmp/modelfile.csv'
    env['plot_file'] = '/tmp/plotfile.png'
    r('''
require(ape)
require(geiger)
require(phytools)
print('R is ready to execute the fit continuous method')

plotsize = 1000

tree <- read.tree(tree_file)
table <- read.csv(table_file, row.names = 1, check.names = FALSE)

td <- treedata(tree, table)
df <- as.data.frame(td$data)
dat <- df[,column, drop = FALSE] # Note: originally called selectedColumn
phy <- td$phy

# stdError might come over as a character instead of a number
stderror <- as.numeric(stdError)

# If the user inputs a non-number, stdError will be NA
# Just make SE = 0 in that case
if(is.na(stderror)) {
    stderror <- 0
}

result <- fitContinuous(phy = phy, dat = dat, SE = stderror, model = model)
result <- t(as.data.frame(unlist(result$opt)))
rownames(result) <- "Primary results"
result <- cbind(result, stderror) # Just to double-check the SE

# Can I just use write.csv as before?
write.csv(result, modelfit_summary_file)

# Before the plot is made, dat needs to be named numbers
dat <- dat[,1]
names(dat) <- rownames(table)

# Can I use normal png saving here? I guess this will be replaced by vega anyway
png(plot_file, width = plotsize, height = plotsize)
phenogram(phy, dat, fsize = 0.8, color = "darkgreen")
dev.off()

    ''')
    print('** need to collect result from R here')
    #print(env['result'])
    #print(type(env['result']))
 
    #valuesOnlyButNoKeys = np.asarray(env['result'])
    result_df = pd.read_csv('/tmp/modelfile.csv')
    print(result_df)
    result_as_dict = result_df.to_dict('records')
    print('result as dict:',result_as_dict)

    # repack from pandas dataframe into a dictionary. 
    # values are returned as a list of one dictionary, so pick the first list entry
    result = {}
    for key in result_as_dict[0].keys():
        result[key] = result_as_dict[0][key]

    # return the data arrays here as a JSON blob to javascript
    # for javascript to render in vegalite 
    returnString = json.dumps(result)
    return returnString

    # clean up the temporary files
    # os.deletefile()
