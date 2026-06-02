# Regression: routes authenticated at the ROUTER level (APIRouter(dependencies=...))
# must NOT fire — they're centrally authenticated, not per-route. (~40 such routes
# false-fired on OpenHands before this exemption.)
from fastapi import APIRouter
router = APIRouter(prefix="/git", tags=["Git"], dependencies=get_dependencies())

@router.get("/search")
async def search(q: str):
    return do(q)                                       # EXPECT_NONE:sign.gateway-unauthenticated-endpoint

@router.post("/branches")
async def branches(body: dict):
    return mk(body)                                    # EXPECT_NONE:sign.gateway-unauthenticated-endpoint
