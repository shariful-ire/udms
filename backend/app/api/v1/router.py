from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.dining import (
    dining_router,
    customers_router,
    meals_router,
    requests_router,
    expenses_router,
    earnings_router,
    member_payments_router,
    payment_proofs_router,
    reports_router,
    audit_router,
    dashboard_router,
)
from app.api.v1.endpoints.profile import profile_router, settings_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(dining_router)
api_v1_router.include_router(customers_router)
api_v1_router.include_router(meals_router)
api_v1_router.include_router(requests_router)
api_v1_router.include_router(expenses_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(earnings_router)
api_v1_router.include_router(member_payments_router)
api_v1_router.include_router(payment_proofs_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(settings_router)
