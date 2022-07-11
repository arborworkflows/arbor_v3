from fastapi import Response
from fastapi import Request
import pandas as pd
from tempfile import NamedTemporaryFile
from fit_continuous.methods import table_upload
import rpy2
from rpy2 import robjects
import json
# use pandas to store CSV files
import pandas as pd

#from methods import testRInterface

def testRInterface():
    r = robjects.r
    r('''
    print('howdy from R')
    ''')


def store_the_table(table):
    print('table upload method')
    #print('recveived table:',table)
    print('recevied a table with ',len(table['table']),'rows')
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
    # Does not recognize the modelfit_summary_file variable
    return modelfit_summary_file, plot_file


def init(app):

    # @app.get('/api/fit_continuous/')
    # def fit_continuous(
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
    @app.get('/fit_continuous')
    def index():
        with open('fit_continuous/index.html') as indexFile:
            indexContent = indexFile.read()

        testRInterface()
        return Response(content=indexContent, media_type='text/html')

    # upload a CSV table to the server for use later
    @app.post('/fit_continuous/table_upload')
    async def table_upload(table : Request):
        json_table =  await table.json()
        print('received uploaded table:',json_table)
        #tableobj = json.loads(json_info)
        #print('decoded to object:',tableobj)
        store_the_table(json_table)
        returnContent = '<p>success</p>'
        return Response(content=returnContent, media_type='text/html')

    # upload a tree file in PHY format for use later
    @app.post('/fit_continuous/tree_upload')
    async def tree_upload(tree : Request):
        tree_obj =  await tree.json()
        print('received uploaded tree:',tree_obj['tree'])
        #tableobj = json.loads(json_info)
        #print('decoded to object:',tableobj)
        store_the_tree(tree_obj)
        returnContent = '<p>success</p>'
        return Response(content=returnContent, media_type='text/html')

    # run the method on the previously uploaded tree and table
    @app.post('/fit_continuous/run')
    async def run(params : Request):
        params_obj =  await params.json()
        print('run with column:',params_obj['column'])
        print('run with model',params_obj['model'])
        print('run with stdError:',params_obj['stdError'])
        returnContent =  run_method(params_obj)
        return Response(content=returnContent, media_type='text/html')
        #return await Response(content=json.dumps(run(params_obj)),media_type='text/html')
