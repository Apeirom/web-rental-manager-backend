from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.utils.rate_limit import setup_rate_limit, limiter
from sqlalchemy.orm import Session
from fastapi import Request

from src.database.config import get_db, engine
from src.models.base import Base
from src.middlewares.auth_middleware import AuthMiddleware

from src.routers import (
    auth_router,
    users_router,
    tenant_router,
    property_router,
    real_estate_router,
    guarantee_router,
    contract_router,
    payment_router,
    extract_batch_router,
    analysis_router
)

from src.controller.health_controller import HealthController

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rental Manager API",
    description="API robusta para gestão de inquilinos, imóveis e contratos.",
    version="1.0.0"
)

setup_rate_limit(app)

origins = [
    "http://localhost:3000",
    "https://web-rental-manager-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)


@app.get("/", tags=["0. Monitoramento e Sistema"])
@limiter.limit("100/minute")
def root(request: Request):
    return {"status": "Rental Manager API is online"}


@app.get("/health", tags=["0. Monitoramento e Sistema"])
@limiter.limit("20/minute")
def health_check(request: Request, db: Session = Depends(get_db)):
    controller = HealthController(db)
    return controller.check_status()


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tenant_router)
app.include_router(property_router)
app.include_router(real_estate_router)
app.include_router(guarantee_router)
app.include_router(contract_router)
app.include_router(payment_router)
app.include_router(extract_batch_router)
app.include_router(analysis_router)