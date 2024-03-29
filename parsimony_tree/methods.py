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
    mult_op = params['mult_op']
    column = params['column']
    print('RUN METHOD: params were ', mult_op, column)
    # now that we have all the data collected, run the R method
    r = robjects.r
    env = robjects.globalenv
    env['tree_file'] = '/tmp/tree_file.phy'
    env['table_file'] = '/tmp/table_file.csv'
    env['mult_op'] = mult_op
    env['column'] = column
    env['modelfit_summary_file'] = '/tmp/modelfile.csv'
    env['plot_file'] = '/tmp/plotfile.png'
    env['points_file'] = '/tmp/points_file.csv'
    env['connect_file'] = '/tmp/connect_file.csv'
    r('''
require(phangorn)

# Read in character matrix (assumes first column is row names (species names))
charMat <- read.csv(table_file, row.names = 1)
# Turn the df into a matrix
charMat <- as.matrix(charMat)

# In order to turn it into a phyDat object, we need to figure out the factors
fac <- unique(as.vector(charMat))
fac_start <- fac[1]
fac_end <- tail(fac, 1)

if(mult_op == "Yes"){
    # Create tree using all characters

    # Create phyDat object to ultimately create tree
    charMat_phyDat <- phyDat(as.matrix(charMat), type = "USER", levels = fac_start:fac_end)

    # Create a starting tree
    tree_start <- random.addition(charMat_phyDat)
    # Use pratchet to create a maximum parsimony tree
    tree_mp <- pratchet(charMat_phyDat, start = tree_start,
                        minit = 100, maxit = 1000,
                        all = TRUE, trace = 0)

    # Root tree
    outgroup <- row.names(charMat)[1] # Assume outgroup is the first row
    tree_rooted <- root(tree_mp, outgroup = outgroup,
                        resolve.root = TRUE, edgelabel = TRUE)
}

if(mult_op == "No"){
    # Create tree using just the chosen character

    # Trim matrix to single out chosen character
    selectedChar <- column
    charMat <- charMat[,selectedChar]

    # Create phyDat object to ultimately create tree
    charMat_phyDat <- phyDat(as.matrix(charMat), type = "USER", levels = fac_start:fac_end)

    # Create a starting tree
    tree_start <- random.addition(charMat_phyDat)
    # Use pratchet to create a maximum parsimony tree
    tree_mp <- pratchet(charMat_phyDat, start = tree_start,
                        minit = 100, maxit = 1000,
                        all = TRUE, trace = 0)

    # Root tree
    outgroup <- names(charMat)[1] # For single character, assume outgroup is first row
    tree_rooted <- root(tree_mp, outgroup = outgroup,
                        resolve.root = TRUE, edgelabel = TRUE)
}

# Plot tree to png
plotsize = 1000
png(plot_file, width = plotsize, height = plotsize)
plot(tree_rooted)
dev.off()

# Get tree information for VEGA
# First, get phylo object
lastPP <- get("last_plot.phylo", envir = .PlotPhyloEnv)

# Isolate edges and points
edges <- lastPP$edge
xx <- lastPP$xx
yy <- lastPP$yy

plot_points <- cbind(xx, yy)

# Get the tip names to add to points
tip_names <- tree_rooted[["tip.label"]]
# Figure out how many NAs we need for filler
filler_length <- length(xx) - length(tip_names)
# Create filler vector
filler <- rep(" ", filler_length)
# Concatenate vectors
names_filler <- c(tip_names, filler)
# Now create final dataframe
tree_output <- cbind.data.frame(xx, yy, names_filler)
# Rename columns
colnames(tree_output) <- c("Node_x_coord", "Node_y_coord", "Species")

# Write points to a file for use with Vega
write.csv(tree_output, points_file, row.names = FALSE)

# Now create CSV for drawing edges in Vega
# Temporary first two rows because R is silly about creating dfs iteratively
bloop <- c(1,1,1,1)
blarp <- c(1,1,1,1)
edge_df <- rbind(bloop, blarp)
colnames(edge_df) <- c("V1_x", "V1_y", "V2_x", "V2_y")

for(i in 1:length(edges[,1])){
  v1 <- edges[i,1] # first column, ith row: V1
  v2 <- edges[i,2] # second column, ith row: V2
  # find the v1st row in points
  v1_x <- plot_points[v1, 1]
  v1_y <- plot_points[v1, 2]

  # find the v2nd row in points
  v2_x <- plot_points[v2, 1]
  v2_y <- plot_points[v2, 2]

  # Create row to add to dataframe
  row <- c(v1_x, v1_y, v2_x, v2_y)
  edge_df <- rbind(edge_df, row)

}
edge_df <- edge_df[-1:-2,] # remove first two rows (bloop and blarp)

# Write edge/connection csv
write.csv(edge_df, connect_file, row.names = FALSE)
    ''')

    print('** need to collect result from R here')

    # retreive the tree information from the R result
    connections_df = pd.read_csv('/tmp/connect_file.csv')
    points_df = pd.read_csv('/tmp/points_file.csv')
    connections_json = connections_df.to_dict('records')
    points_json = points_df.to_dict('records')
    #print(points_json)

    # repack from pandas dataframe into a dictionary.

    result = {}
    result['points'] = points_json
    result['connections'] = connections_json

    # return the data arrays here as a JSON blob to javascript
    # for javascript to render in vegalite
    returnString = json.dumps(result)
    return returnString

    # clean up the temporary files
    # os.deletefile()
