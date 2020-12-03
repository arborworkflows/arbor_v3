# Terra Analytics

## Docker

Build container
```
docker build . -t terra-analytics
```

Run
```
docker run -p 9000:80 terra-analytics
```

Visit [localhost:9000](http://localhost:9000)

## Development

Install dependencies
```
pip install -r requirements.txt
```

Run
```
uvicorn main:app --reload
```

Visit [localhost:8000](http://localhost:8000)
