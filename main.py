from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

# import your apps
import fit_continuous
import trait_explorer

app = FastAPI()

# initialize your apps
#trait_explorer.init(app)
fit_continuous.init(app)

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/')
def index():
    with open('index.html') as indexFile:
        indexContent = indexFile.read()
    
    return Response(content=indexContent, media_type='text/html')


