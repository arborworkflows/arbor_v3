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
    env['graph_file'] = '/tmp/graphfile.csv'
    env['point_file'] = '/tmp/graphpoints.csv'
    env['forward_file'] = '/tmp/forwardpoints.csv'
    env['backward_file'] = '/tmp/backwardpoints.csv'
    r('''
require(ape)
require(geiger)
require(phytools)
require(dplyr)

tree <- read.tree(tree_file)
table <- read.csv(table_file, row.names = 1, check.names = FALSE)

td <- treedata(tree, table)
df <- as.data.frame(td$data)
dat <- df[,column, drop = FALSE]
phy <- td$phy

print(column)

result <- fitDiscrete(phy, dat, model, transform)

# Save transposed results as result CSV for user
res <- t(as.data.frame(unlist(result$opt)))
rownames(res) <- "Primary results"
print(res)

write.csv(res, modelfit_summary_file)

# Get coordinates and other information needed to plot in VEGA
# First, find the names of the discrete characters
names <- unique(dat[,column])

# Find the number of discrete states
len <- length(names)

# The total number of transitions is states * (states-1)
tot <- len * (len - 1)

# Get the transition rates and AIC info
transitions <- as.data.frame(unlist(result$opt))

# The row names tell us the transition direction
direction <- row.names(transitions)
# We only need the first tot though
direction <- direction[1:tot]

# Split direction into 3 columns
test <- strsplit(direction, "")
direction_mat <- matrix(unlist(test), ncol = 3, byrow = T)
direction_df <- as.data.frame(direction_mat)
# Remove first column
direction_df <- direction_df[,-1]

# Grab all of the transition rates
transitions <- transitions[1:tot,]
# Add them to direction_df
direction_df <- cbind(direction_df, transitions)
# Change colnames to be more descriptive
colnames(direction_df) <- c("From", "To", "TransRate")

# Discrete categories are numbered in alpha order
alpha_names <- sort(names)

# In order to plot letters as points in VEGA, we need a key I think?
# Thanks to https://stackoverflow.com/questions/40279052/coordinates-of-equally-distanced-n-points-on-a-circle-in-r
#   for circle information
points = exp(2i * pi * (1:len)/len)
# Translate from complex to Cartesian plane
cart_points = data.frame(x=Re(points), y = Im(points))
# Create key dataframe
key <- cbind(cart_points, alpha_names)

# Should we write the key to a file too?
write.csv(key, point_file, row.names = FALSE)

# Create a VEGA-useable dataframe with points and info
x1 <- 1:tot
y1 <- 1:tot
x2 <- 1:tot
y2 <- 1:tot
name1 <- 1:tot
name2 <- 1:tot
transrate <- direction_df$TransRate
midpoint_x <- 1:tot
midpoint_y <- 1:tot

for(i in 1:tot) {
  from <- direction_df[i,1] # ith row, 1st column
  to <- direction_df[i,2] #ith row, 2nd column

  x1[i] <- key[from,1] #from-th row, 1st column (x)
  y1[i] <- key[from,2] #from-th row, 2nd column (y)
  name1[i] <- key[from,3] #from-th row, 3rd column (alpha_name)

  x2[i] <- key[to,1]
  y2[i] <- key[to,2]
  name2[i] <- key[to,3]

  midpoint_x[i] <- (x1[i] + x2[i])/2
  midpoint_y[i] <- (y1[i] + y2[i])/2
}

# Create final combined dataframe
combo_df <- cbind(x1,y1,name1,x2,y2,name2,transrate,midpoint_x,midpoint_y)
write.csv(combo_df, graph_file, row.names = FALSE)

# Separate combo_df into two different ones - forward and backward
rows_backward <- rep(NA, (tot/2)) # Create empty vector to hold backward rows

for(i in 1:tot) {
  # Grab name1 and name2
  name1_for <- combo_df[i,3]
  name2_for <- combo_df[i,6]
  for(j in ((i+1):tot)){
    # Start the range at i+1 because we don't want to match the current forward
    # For the end case:
    if(j == (tot+1)) {
        break
    }
    compare <- combo_df[j,3] # Grab the name1 column

    # If the current name1 == the original name2
    if(compare == name2_for){
      compare2 <- combo_df[j,6] # Grab the next new name2 column

      # If the new name2 column == the original name1, then that's the backward row
      if(compare2 == name1_for){
        rows_backward[i] <- j
      }
    }
  }
}

# Grab all backward rows from combo_df
rows_backward <- rows_backward[!(is.na(rows_backward))]
combo_df_back <- combo_df[rows_backward,]
write.csv(combo_df_back, backward_file, row.names = FALSE)

# Grab all forward rows from combo_df
combo_df_for <- as.data.frame(combo_df) %>%  filter(!row_number() %in% rows_backward)
write.csv(combo_df_for, forward_file, row.names=FALSE)


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

    # retreive the graph information from the R result
    graph_df = pd.read_csv('/tmp/graphfile.csv')
    graph_json = graph_df.to_dict('records')
    print(graph_json)

    key_df = pd.read_csv('/tmp/graphpoints.csv')
    key_json = key_df.to_dict('records')
    print(key_json)

    forward_df = pd.read_csv('/tmp/forwardpoints.csv')
    forward_json = forward_df.to_dict('records')
    print(forward_json)

    backward_df = pd.read_csv('/tmp/backwardpoints.csv')
    backward_json = backward_df.to_dict('records')
    print(backward_json)

    # [{},{}]
    # json:  {'data': []}

    # repack from pandas dataframe into a dictionary.
    # values are returned as a list of one dictionary, so pick the first list entry
    result = {}
    result['graph'] = graph_json
    result['points'] = key_json
    result['forward'] = forward_json
    result['backward'] = backward_json

    for key in result_as_dict[0].keys():
        result[key] = result_as_dict[0][key]

    # return the data arrays here as a JSON blob to javascript
    # for javascript to render in vegalite
    returnString = json.dumps(result)
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
