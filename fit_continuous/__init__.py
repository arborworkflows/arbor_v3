from fastapi import Response
import pandas as pd
from tempfile import NamedTemporaryFile


#--------- support routines for processing TERRA-Ref season measurements ----------------

def addPlotMarker(plotlist,cultivar,rng,column,selectedFeatureName,featureValue):
    mark = {}
    mark['cultivar'] = cultivar
    mark['range'] = rng
    mark['column'] = column
    mark[selectedFeatureName] = featureValue
    plotlist.append(mark)



#

def init(app):

    @app.get('/api/fit_continuous/')
    def fit_continuous(
        tree_file,
        table_file,
        selectedColumn,
        model: str == 'BM'
    ):
        from rpy2 import robjects
        r = robjects.r
        results_file = NamedTemporaryFile(delete=False).name
        plot_file = NamedTemporaryFile(delete=False).name
        env = robjects.globalenv
        env['tree_file'] = tree_file
        env['table_file'] = table_file
        env['selectedColumn'] = selectedColumn 
        env['model'] = model
        env['stdError'] = stdError 
        env['results_file'] = results_file
        env['plot_file'] = plot_file
        r('''
require(ape)
require(treeplyr)
require(geiger)
require(phytools)

plotsize = 1000

tree <- read.tree(tree_file)
table <- read.csv(table_file, row.names = 1, check.names = FALSE)

# Note: using treedata instead of make.treedata because the tibble
# was leaving out the row names, which we need for this function
td <- treedata(tree, table)
df <- as.data.frame(td$data)
dat <- df[,selectedColumn, drop = FALSE]
phy <- td$phy

# stdError might come over as a character instead as a number
stderror <- as.numeric(stdError)

# If the user inputs a non-number, conv_stderror will be NA
# In that case, just make SE = 0
if(is.na(stderror)) {
    stderror <- 0
}

result <- fitContinuous(phy = phy, dat = dat, SE = stderror, model = model)
result <- t(as.data.frame(unlist(result$opt)))
rownames(result) <- "Primary results"
write.csv(result, results_file)
'''
        )

        return Response(content=result, media_type='text/csv')


    @app.get('/fit_continuous')
    def index():
        with open('fit_continuous/index.html') as indexFile:
            indexContent = indexFile.read()
        
        return Response(content=indexContent, media_type='text/html')
