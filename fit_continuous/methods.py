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
    env['pheno_points_file'] = '/tmp/pheno_points.csv'
    env['pheno_connect_file'] = '/tmp/pheno_connections.csv'
    r('''
require(ape)
require(geiger)
require(phytools)
print('R is ready to execute the fit continuous method')

# Phytools phenogram method, but edited to return edges
## written by Liam J. Revell 2011, 2012, 2013, 2014, 2015, 2016, 2020, 2021
custom_phenogram <- function(tree, x, fsize = 1.0, ftype = "reg", colors = NULL, axes = list(), add = FALSE, spread.labels = FALSE) {
    # Are the if-else statements causing the parsing error?
    xlim <- NULL
    ylim <- NULL
    log <- ""
    main <- NULL
    sub <- NULL
    xlab <- "time"
    ylab <- "phenotype"
    asp <- NA
    type <- "l"
    lty <- 1
    lwd <- 2
    offset <- 0.2
    offsetFudge <- 1.37
    digits <- 2
    nticks <- 5
    spread.labels <- FALSE
    spread.cost <- c(1,0.4)
    spread.range <- range(x)
    link <- 0
    hold <- TRUE
    quiet <- FALSE
    label.pos <- NULL
    cex.axis <- par()$cex.axis
    cex.lab <- par()$cex.lab
    las <- par()$las
    # End optional arguments

    # I'm going to assume that the tree is fine

    # check font
    ftype<-which(c("off","reg","b","i","bi")==ftype)-1
    if(!ftype&&!add) fsize=0
    H<-nodeHeights(tree)
    if(length(x)<(length(tree$tip)+tree$Nnode)) {
        x<-c(x,fastAnc(tree,x))
    }
    else {
        x<-c(x[tree$tip.label],x[as.character(length(tree$tip)+1:tree$Nnode)])
    }
    x[1:length(tree$tip)]<-x[tree$tip.label]
    names(x)[1:length(tree$tip)]<-1:length(tree$tip)
    X<-matrix(x[as.character(tree$edge)],nrow(tree$edge),ncol(tree$edge))

    # legacy 'axes' argument trumps ylim & xlim from optional (...)
  if(is.null(axes$trait)&&is.null(ylim)) ylim<-c(min(x),max(x))
  else if(!is.null(axes$trait)) ylim<-axes$trait
  if(!is.null(axes$time)) xlim<-axes$time
  if(!add&&is.null(xlim)){
    pp<-par("pin")[1]
    sw<-fsize*(max(strwidth(tree$tip.label,units="inches")))+
      offsetFudge*offset*fsize*strwidth("W",units="inches")
    alp<-optimize(function(a,H,link,sw,pp) (a*1.04*(max(H)+link)+sw-pp)^2,H=H,
                  link=link,sw=sw,pp=pp,interval=c(0,1e6))$minimum
    xlim<-c(min(H),max(H)+link+sw/alp)
  }
  if(!quiet&&Ntip(tree)>=40&&spread.labels){
    cat("Optimizing the positions of the tip labels...\n")
    flush.console()
  }

  ## matrix for tip coordinates
  tip.coords<-matrix(NA,Ntip(tree),2,dimnames=list(tree$tip.label,c("x","y")))
  if(hold) null<-dev.hold()
  if(is.null(tree$maps)){
    if(is.null(colors)) colors<-"black"
    if(!add){
      plot(H[1,],X[1,],type=type,lwd=lwd,lty=lty,col=colors,xlim=xlim,ylim=ylim,
           log=log,asp=asp,xlab="",ylab="",frame=FALSE,axes=FALSE)
      if(spread.labels) tt<-spreadlabels(tree,x,fsize=fsize,cost=spread.cost,
                                         range=spread.range,label.pos=label.pos,log=log) else tt<-x[1:length(tree$tip)]
                                         if(tree$edge[1,2]<=length(tree$tip)){
                                           if(fsize&&!add){
                                             text(gsub("_"," ",tree$tip.label[tree$edge[1,2]]),x=H[1,2]+link,
                                                  y=tt[tree$edge[1,2]],cex=fsize,font=ftype,pos=4,offset=offset)
                                             tip.coords[tree$tip.label[tree$edge[1,2]],]<-c(H[1,2]+link,
                                                                                            tt[tree$edge[1,2]])
                                             if(link>0) lines(x=c(H[1,2],H[1,2]+link),y=c(X[1,2],
                                                                                          tt[tree$edge[1,2]]),lty=3)
                                           }
                                         }
                                         s<-2
    } else s<-1
    for(i in s:nrow(H)){
      lines(H[i,],X[i,],type=type,lwd=lwd,lty=lty,col=colors)
      if(tree$edge[i,2]<=length(tree$tip)){
        if(fsize&&!add){
          text(gsub("_"," ",tree$tip.label[tree$edge[i,2]]),x=H[i,2]+link,
               y=tt[tree$edge[i,2]],cex=fsize,font=ftype,pos=4,offset=offset)
          tip.coords[tree$tip.label[tree$edge[i,2]],]<-c(H[i,2]+link,
                                                         tt[tree$edge[i,2]])
          if(link>0) lines(x=c(H[i,2],H[i,2]+link),y=c(X[i,2],tt[tree$edge[i,2]]),
                           lty=3)
        }
      }
    }
  } else {
    if(is.null(colors)){
      nn<-sort(unique(c(getStates(tree,"tips"),getStates(tree,"nodes"))))
      colors<-setNames(palette()[1:length(nn)],nn)
    }
    for(i in 1:nrow(H)){
      y<-H[i,1]
      m<-diff(X[i,])/diff(H[i,])
      for(j in 1:length(tree$maps[[i]])){
        a<-c(y,y+tree$maps[[i]][j])
        b<-m*(a-H[i,1])+X[i,1]
        if(i==1&&j==1&&!add) {
          plot(a,b,col=colors[names(tree$maps[[i]])[j]],type=type,lwd=lwd,
               lty=lty,xlim=xlim,ylim=ylim,log=log,asp=asp,axes=FALSE,xlab="",
               ylab="")
          if(spread.labels) tt<-spreadlabels(tree,x[1:length(tree$tip)],
                                             fsize=fsize,cost=spread.cost,range=spread.range,log=log) else
                                               tt<-x[1:length(tree$tip)]
        } else lines(a,b,col=colors[names(tree$maps[[i]])[j]],lwd=lwd,lty=lty,
                     type=type)
        y<-a[2]
      }
      if(tree$edge[i,2]<=length(tree$tip)){
        if(fsize&&!add){
          text(gsub("_"," ",tree$tip.label[tree$edge[i,2]]),x=H[i,2]+link,
               y=tt[tree$edge[i,2]],cex=fsize,font=ftype,pos=4,offset=offset)
          tip.coords[tree$tip.label[tree$edge[i,2]],]<-c(H[i,2]+link,
                                                         tt[tree$edge[i,2]])
          if(link>0) lines(x=c(H[i,2],H[i,2]+link),y=c(X[i,2],
                                                       tt[tree$edge[i,2]]),lty=3)
        }
      }
    }
  }
  if(!add){
    at<-round(0:(nticks-1)*max(H)/(nticks-1),digits)
    axis(1,at=at,cex.axis=cex.axis,cex.lab=cex.lab,las=las)
    axis(2,cex.axis=cex.axis,cex.lab=cex.lab,las=las)
    title(xlab=xlab,ylab=ylab,main=main,sub=sub)
  }
  if(hold) null<-dev.flush()
  xx<-setNames(c(H[1,1],H[,2]),c(tree$edge[1,1],tree$edge[,2]))
  xx<-xx[order(as.numeric(names(xx)))]
  yy<-setNames(c(X[1,1],X[,2]),c(tree$edge[1,1],tree$edge[,2]))
  yy<-yy[order(as.numeric(names(yy)))]
  PP<-list(type="phenogram",use.edge.length=TRUE,node.pos=1,
           show.tip.label=if(ftype!="off") TRUE else FALSE,show.node.label=TRUE,
           font=ftype,cex=fsize,adj=0,srt=NULL,no.margin=FALSE,label.offset=offset,
           x.lim=par()$usr[1:2],y.lim=par()$usr[3:4],
           direction=NULL,tip.color="black",Ntip=Ntip(tree),Nnode=tree$Nnode,
           edge=tree$edge,xx=xx,yy=yy)
  assign("last_plot.phylo",PP,envir=.PlotPhyloEnv)
  invisible(tip.coords)
  print("Custom_phenogram happened")
  return(PP) # IMPORTANT RETURN
}

# Back to regularly scheduled fitContinuous

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

# Confirmed: writes to tmp directory as expected
write.csv(result, modelfit_summary_file)

# Before the plot is made, dat needs to be named numbers
dat <- dat[,1]
names(dat) <- rownames(table)

# Can I use normal png saving here? I guess this will be replaced by vega anyway
png(plot_file, width = plotsize, height = plotsize)
phenogram(phy, dat, fsize = 0.8, color = "darkgreen")
dev.off()

# Getting the phenogram information for Vega
# First, get the phenogram object
pheno_object <- custom_phenogram(phy, dat, fsize = 0.8, color = "darkgreen")

# Isolate edges and points
pheno_edges <- pheno_object$edge
pheno_xx <- pheno_object$xx
pheno_yy <- pheno_object$yy

pheno_points <- cbind(pheno_xx, pheno_yy)

# Get the tip names to add to the points file
tip_names <- phy$tip.label
# Figure out how many NAs we need for filler
filler_length <- length(pheno_xx) - length(tip_names)
# Create filler vector
filler <- rep("None", filler_length)
# Concatenate vectors
names_filler <- c(tip_names, filler)
# Now create final dataframe
pheno_output <- cbind.data.frame(pheno_xx, pheno_yy, names_filler)
# Rename columns
colnames(pheno_output) <- c("Node_x_coord", "Node_y_coord", "Species")

# Write pheno_points to a file for use with Vega
write.csv(pheno_output, pheno_points_file, row.names = FALSE)

# Now create CSV for drawing edges in Vega
# Temporary first two rows because R is silly about creating dfs iteratively
bloop <- c(1,1,1,1)
blarp <- c(1,1,1,1)
pheno_df <- rbind(bloop, blarp)
colnames(pheno_df) <- c("V1_x", "V1_y", "V2_x", "V2_y")

for(i in 1:length(pheno_edges[,1])){
  v1 <- pheno_edges[i,1] # first column, ith row: V1
  v2 <- pheno_edges[i,2] # second column, ith row: V2
  # find the v1st row in points
  v1_x <- pheno_points[v1, 1]
  v1_y <- pheno_points[v1, 2]

  # find the v2nd row in points
  v2_x <- pheno_points[v2, 1]
  v2_y <- pheno_points[v2, 2]

  # Create row to add to dataframe
  row <- c(v1_x, v1_y, v2_x, v2_y)
  pheno_df <- rbind(pheno_df, row)

}
pheno_df <- pheno_df[-1:-2,] # remove first two rows (bloop and blarp)

# Write edge/connection csv
write.csv(pheno_df, pheno_connect_file, row.names = FALSE)

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
    connections_df = pd.read_csv('/tmp/pheno_connections.csv')
    points_df = pd.read_csv('/tmp/pheno_points.csv')
    connections_json = connections_df.to_dict('records')
    points_json = points_df.to_dict('records')
    print(points_json)

    # [{},{}]
    # json:  {'data': []}

    # repack from pandas dataframe into a dictionary.
    # values are returned as a list of one dictionary, so pick the first list entry
    result = {}
    result['points'] = points_json
    result['connections'] = connections_json
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
