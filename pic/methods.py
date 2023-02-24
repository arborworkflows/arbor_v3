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
    ind_var = params['ind_var']
    dep_var = params['dep_var']
    logop = params['logop']
    print('RUN METHOD: params were',ind_var,dep_var,logop)
    # now that we have all the data collected, run the R method
    r = robjects.r
    env = robjects.globalenv
    env['tree_file'] = '/tmp/tree_file.phy'
    env['table_file'] = '/tmp/table_file.csv'
    env['ind_var'] = ind_var
    env['dep_var'] = dep_var
    env['logop'] = logop
    env['modelfit_summary_file'] = '/tmp/modelfile.csv'
    env['plot_file'] = '/tmp/plotfile.png'
    env['pic_plot_file'] = '/tmp/pic_points.csv'
    r('''
require(geiger)
print('R is ready to execute the PIC method')
plotsize = 1000

tree <- read.tree(tree_file)
table <- read.csv(table_file, row.names = 1, check.names = FALSE)

td <- treedata(tree, table)
phy <- td$phy
df <- as.data.frame(td$data)

# Get the variable name for result DF later before messing with it
ind_name <- ind_var

# Get just variables we want and name based on tips
ind_var <- df[,ind_var]
names(ind_var) <- rownames(df)

dep_var <- df[,dep_var]
names(dep_var) <- rownames(df)

# If the user would like to log the values, do so
if(logop == "Yes"){
  ind_var <- log(ind_var)
  dep_var <- log(dep_var)
}

# Run PIC on each variable
pic_ind <- pic(ind_var, phy)
pic_dep <- pic(dep_var, phy)

# Regression forced through the origin
reg <- lm(pic_dep ~ pic_ind + 0)
output <- anova(reg)

# Create summary table
an_out <- output[,1:5] # Good stuff from anova
sum_reg <- summary(reg)
coef_sum <- as.data.frame(sum_reg[["coefficients"]]) # Good stuff from summary
coef_sum <- rbind(coef_sum, c(NA,NA,NA,NA)) # Make it match sum_reg
rownames(coef_sum)[2] <- "Residuals"

result <- cbind(an_out, coef_sum)
rownames(result)[1] <- ind_name
write.csv(result, modelfit_summary_file)

# Create CSV for plotting regression
pic <- cbind(pic_ind, pic_dep)
write.csv(pic, pic_plot_file, row.names = FALSE)

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

    # retreive the PIC information from the R result
    points_df = pd.read_csv('/tmp/pic_points.csv')
    points_json = points_df.to_dict('records')
    print(points_json)

    # [{},{}]
    # json:  {'data': []}

    # repack from pandas dataframe into a dictionary.
    # values are returned as a list of one dictionary, so pick the first list entry
    result = {}

    for key in result_as_dict[0].keys():
        result[key] = result_as_dict[0][key]

    result['points'] = points_json

    # return the data arrays here as a JSON blob to javascript
    # for javascript to render in vegalite
    returnString = json.dumps(result)
    return returnString

    # clean up the temporary files
    # os.deletefile()
