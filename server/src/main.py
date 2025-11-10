import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.app.db.connection import lifespan
from src.app.core.config import get_settings
from src.api.routers import FlowRouter, UserRouter, AuthRouter
from src.api.handlers.exception_handler import add_exception_handlers


settings = get_settings()

app = FastAPI(
    title='Decision Engine API',
    lifespan=lifespan
)

add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(FlowRouter)
app.include_router(UserRouter)
app.include_router(AuthRouter)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint='/metrics')


@app.get('/')
def read_root():
    return {'message': 'hello world!'}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Insira o token no formato: **Bearer &lt;seu_token&gt;**"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


if __name__ == "__main__":
    uvicorn.run('src.main:app',
                host=settings.API_HOST,
                port=settings.API_PORT,
                reload=settings.API_RELOAD)
