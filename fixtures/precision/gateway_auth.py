# Precision fixture: decorated FastAPI routes must be REACHABLE by the gateway
# rule. Regression guard for the decorated_definition anchor fix — the old
# function_definition anchor matched no decorated route at all.

from fastapi import FastAPI, Depends
app = FastAPI()

@app.post("/agent")
def run_agent(body: dict):
    return dispatch(body)                              # EXPECT_MATCH:sign.gateway-unauthenticated-endpoint

@app.get("/secure")
def secure(user=Depends(get_current_user)):
    return {"ok": True}                                # EXPECT_NONE:sign.gateway-unauthenticated-endpoint
