# Arbor Version 3

## Docker

Build container
```
docker build . -t arbor_v3
```

Run
```
docker run -p 9000:80 arbor_v3
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
