# Precision fixture for stop.llm-output-to-control-flow: the common real shape is
# assign-then-branch, not the inline `if llm.invoke():` the old rule required.

def route(state):
    resp = llm.invoke(state)
    if resp.content == "delete":                       # EXPECT_MATCH:stop.llm-output-to-control-flow
        do_delete()

def route_chat(client, msg):
    result = client.chat.completions.create(messages=msg)
    if "yes" in result.choices[0].message.content:     # EXPECT_MATCH:stop.llm-output-to-control-flow
        proceed()

def route_runner(agent, q):
    out = Runner.run(agent, q)
    while out.final_output != "done":                  # EXPECT_MATCH:stop.llm-output-to-control-flow
        out = Runner.run(agent, q)

def inline(x):
    if llm.invoke(x):                                  # EXPECT_MATCH:stop.llm-output-to-control-flow
        go()

# Safe: branch is on a computed/typed value, not raw model output.
def safe(state):
    score = compute_score(state)
    if score > 5:                                      # EXPECT_NONE:stop.llm-output-to-control-flow
        go()

# Safe: model output is bound but never used in a branch (just returned).
def safe_return(state):
    resp = llm.invoke(state)
    return resp.content                                # EXPECT_NONE:stop.llm-output-to-control-flow
