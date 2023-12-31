import logging
import sys

from app.config import settings
from app.routes import (
    airline_router,
    airport_router,
    apis_router,
    city_router,
    grid_router,
    search_router,
    validate_router,
    autofill_router,
    book_router,
)
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist

from owjcommon.exceptions import (
    OWJException,
    http_exception_handler,
    owj_exception_handler,
    request_validation_exception_handler,
    tortoise_not_found_exception_handler,
)
from owjcommon.logger import TraceLogger
from owjcommon.middleware import TraceIDMiddleware
from owjcommon.redis import RedisManager

import os

# Basic logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "tortoise": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "aiosqlite": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}


# Assuming you have the LOGGING_CONFIG defined as above
logging.config.dictConfig(LOGGING_CONFIG)

logger = TraceLogger(__name__)

app = FastAPI(
    title="OWJ CRS Flight API",
    description="This is the API documentation for the OWJ CRS Flight Service.",
    version="1.0.0",
)
app.add_middleware(TraceIDMiddleware)


BASE_PREFIX = "/api/flight/v1"
app.include_router(search_router, prefix=BASE_PREFIX + "/search")
app.include_router(validate_router, prefix=BASE_PREFIX + "/validate")
app.include_router(book_router, prefix=BASE_PREFIX + "/book")
app.include_router(grid_router, prefix=BASE_PREFIX + "/grid")
app.include_router(apis_router, prefix=BASE_PREFIX + "/apis")
app.include_router(airline_router, prefix=BASE_PREFIX + "/airline")
app.include_router(city_router, prefix=BASE_PREFIX + "/city")
app.include_router(airport_router, prefix=BASE_PREFIX + "/airport")
app.include_router(autofill_router, prefix=BASE_PREFIX + "/autofill")


register_tortoise(
    app,
    config={
        "connections": {"default": settings.tortoise_orm.db_connection},
        "apps": {
            "models": {
                "models": ["app.models"],
                "default_connection": "default",
            }
        },
    },
    # This will create the DB tables on startup (useful for development)
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.exception_handler(OWJException)
async def _owj_exception_handler(request, exc):
    logger.info("OWJException: %s", jsonable_encoder(exc))
    return await owj_exception_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request, exc):
    logger.info("StarletteHTTPException: %s", jsonable_encoder(exc))
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def _request_validation_exception_handler(request, exc):
    logger.info("RequestValidationError: %s", jsonable_encoder(exc))
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(DoesNotExist)
async def _tortoise_not_found_exception_handler(request, exc):
    logger.info(
        f"Object not found in database. Request: {request.__dict__}",
        request.scope.get("trace_id"),
    )
    return await tortoise_not_found_exception_handler(request, exc)


redis = RedisManager(
    "redis://default:7ki4TLMGy26YTlehKD9Wj4w5XXt0GlyZ@redis-18399.c322.us-east-1-2.ec2.cloud.redislabs.com:18399"
)


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Redis")
    await redis.init_redis()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Closing Redis")
    await redis.close_redis()
