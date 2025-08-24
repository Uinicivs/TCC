import uvicorn
from fastapi import FastAPI
from src.app.db.connection import lifespan
from src.api.routers import flow_router


app = FastAPI(
    title='Decision Engine API',
    lifespan=lifespan
)


app.include_router(flow_router.router)


@app.get('/')
def read_root():
    return {'message': 'hello world!'}


if __name__ == "__main__":
    uvicorn.run('src.main:app', host='localhost', port=8000, reload=True)
