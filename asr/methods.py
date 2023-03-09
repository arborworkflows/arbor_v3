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
    selColumn = params['selColumn']
    print('RUN METHOD: params were',selColumn)
    # now that we have all the data collected, run the R method
    r = robjects.r
    env = robjects.globalenv
    env['tree_file'] = '/tmp/tree_file.phy'
    env['table_file'] = '/tmp/table_file.csv'
    env['selColumn'] = selColumn
    env['modelfit_summary_file'] = '/tmp/modelfile.csv'
    env['plot_file'] = '/tmp/plotfile.png'
    env['points_file'] = '/tmp/points_file.csv'
    env['connect_file'] = '/tmp/connect_file.csv'
    r('''
require(ape)
require(aRbor)
require(dplyr)

# aRbor is not loaded anymore?? And treeplyr isn't on CRAN so I'll just paste make.treedata
# Luke Harmon (2020). treeplyr: 'dplyr' Functionality for Matched Tree and Data Objects. R package version 0.1.10. https://CRAN.R-project.org/package=treeplyr
make.treedata <- function(tree, data, name_column = "detect", as.is = FALSE)
{
    if (class(tree) != "phylo")
        stop("tree must be of class 'phylo'")
    if (is.vector(data)) {
        data <- as.matrix(data)
        colnames(data) <- "trait"
    }
    if (is.null(colnames(data))) {
        colnames(data) <- paste("trait", 1:ncol(data),
            sep = "")
    }
    coln <- colnames(data)
    if (name_column == "detect") {
        if (is.null(rownames(data))) {
            tmp.df <- data.frame(data)
            offset <- 0
        }
        else {
            tmp.df <- data.frame(rownames(data), data)
            offset <- 1
        }
        matches <- sapply(tmp.df, function(x) sum(x %in% tree$tip.label))
        if (all(matches == 0))
            stop("No matching names found between data and tree")
        name_column <- which(matches == max(matches)) - offset
    }
    else {
        if (is.character(name_column)) {
            name_column <- which(name_column == coln)[1]
        }
    }
    dat <- as_tibble(as.data.frame(lapply(1:ncol(data), function(x) type.convert(apply(data[,
        x, drop = FALSE], 1, as.character), as.is = as.is))))
    colnames(dat) <- coln
    if (name_column == 0) {
        clnm <- colnames(dat)
        dat <- dat[, clnm, drop = FALSE]
        dat.label <- as.character(rownames(data))
    }
    else {
        if (is.numeric(name_column)) {
            clnm <- (1:ncol(data))[-name_column]
        }
        else {
            clnm <- colnames(dat)[-which(colnames(dat) == name_column)]
        }
        dat <- dat[, clnm, drop = FALSE]
        dat.label <- as.character(as.data.frame(data)[[name_column]])
    }
    data_not_tree <- setdiff(dat.label, tree$tip.label)
    tree_not_data <- setdiff(tree$tip.label, dat.label)
    phy <- drop.tip(tree, tree_not_data)
    dat <- filter(dat, dat.label %in% phy$tip.label)
    dat.label <- dat.label[dat.label %in% phy$tip.label]
    if (any(duplicated(dat.label))) {
        warning("Duplicated data in dataset, selecting first unique entry for each species")
        dat <- filter(dat, !duplicated(dat.label))
        dat.label <- dat.label[!duplicated(dat.label)]
    }
    ...my.order... <- match(dat.label, phy$tip.label)
    dat <- arrange(dat, ...my.order...)
    td <- list(phy = phy, dat = dat)
    class(td) <- c("treedata", "list")
    attributes(td)$tip.label <- phy$tip.label
    attributes(td)$dropped <- list(dropped_from_tree = data_not_tree,
        dropped_from_data = tree_not_data)
    return(td)
}

tree <- read.tree(tree_file)
table <- read.csv(table_file, check.names = FALSE)

method <- "marginal"
td <- make.treedata(tree, table)
print("Treedata made")
print(selColumn)
td1 <- select(td, as.name(selColumn))
dat <- td1$dat
type <- detectCharacterType(dat[[1]], cutoff = 0.2)

if (type == "continuous") td1 <- forceNumeric(td1)
if (type == "discrete") td1 <- forceFactor(td1)

output <- ace.treedata(td1, charType = type, aceType = method)
print(output)
TH <- max(branching.times(td$phy))

plotsize = 1000

png(plot_file, width = plotsize, height = plotsize)
plot(output, label.offset = 0.05 * TH)
dev.off()

res <- output[[1]]
node_labels <- 1:td1$phy$Nnode + length(td1$phy$tip.label)
res <- cbind(node_labels, res)
write.csv(res, modelfit_summary_file)

# Get tree information for Vega
# First, get phylo object
lastPP <- get("last_plot.phylo", envir = .PlotPhyloEnv)

# Isolate edges and points
edges <- lastPP$edge
xx <- lastPP$xx
yy <- lastPP$yy

plot_points <- cbind(xx, yy)

# Get the tip names to add to points
tip_names <- td1$phy$tip.label
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
    #print(env['result'])
    #print(type(env['result']))
    print('feature type was:',env['type'])

    #valuesOnlyButNoKeys = np.asarray(env['result'])
    result_df = pd.read_csv('/tmp/modelfile.csv')
    # Rename the first column (since R doesn't give it a name)
    result_df.rename(columns = {'Unnamed: 0':'Name'}, inplace = True)
    print(result_df)

    result_as_dict = result_df.to_dict('records')
    print('result as dict:',result_as_dict)

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
    # values are returned as a list of dictionaries
    result['traits'] = result_as_dict

    # return the data arrays here as a JSON blob to javascript
    # for javascript to render in vegalite
    returnString = json.dumps(result)
    return returnString

    # clean up the temporary files
    # os.deletefile()
