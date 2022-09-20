from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

# import your apps
import fit_continuous
import pic
import phylosignal
import asr
import fit_discrete

app = FastAPI()

# initialize your apps
#trait_explorer.init(app)
fit_continuous.init(app)
pic.init(app)
phylosignal.init(app)
asr.init(app)
fit_discrete.init(app)

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/')
def index():
    with open('index.html') as indexFile:
        indexContent = indexFile.read()

    return Response(content=indexContent, media_type='text/html')
