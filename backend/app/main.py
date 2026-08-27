from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.core.config import (
    APP_NAME,
    APP_VERSION,
    API_V1_PREFIX,
    CORS_ORIGINS
)

from app.core.lifespan import (
    lifespan
)

from app.api.v1.router import (
    router as api_v1_router
)


from app.core.security import (
    SecurityHeadersMiddleware
)


# ==================================================
# CREATE APP
# ==================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Secure Local Edge AI API for "
        "RetailEdge smart billing "
        "queue monitoring."
    ),
    lifespan=lifespan
)


# ==================================================
# SECURITY HEADERS & CORS
# ==================================================

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True if CORS_ORIGINS != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"]
)




# ==================================================
# API V1
# ==================================================

app.include_router(

    api_v1_router,

    prefix=API_V1_PREFIX
)


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {

        "name":
            APP_NAME,

        "version":
            APP_VERSION,

        "feature":
            "Smart Queue Monitoring"
    }