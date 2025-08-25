import uvicorn
from fastapi import FastAPI
from src.app.db.connection import lifespan
from src.app.core.config import get_settings
from src.api.routers import flow_router
from src.api.handlers.exception_handler import add_exception_handlers


settings = get_settings()

app = FastAPI(
    title='Decision Engine API',
    lifespan=lifespan
)

add_exception_handlers(app)

app.include_router(flow_router.router)


@app.get('/')
def read_root():
    return {'message': 'hello world!'}


if __name__ == "__main__":
    uvicorn.run('src.main:app',
                host=settings.API_HOST,
                port=settings.API_PORT,
                reload=True)
