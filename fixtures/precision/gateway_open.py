# Genuinely unauthenticated: no router-level dependencies=, no per-route Depends.
from fastapi import APIRouter
router = APIRouter(prefix="/public")

@router.post("/agent")
async def run_agent(body: dict):
    return dispatch(body)                              # EXPECT_MATCH:sign.gateway-unauthenticated-endpoint
