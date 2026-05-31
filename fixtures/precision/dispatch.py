# Precision fixture for the tool-dispatch rules
# (stop.tool-dispatcher-without-policy-gate, stop.direct-tool-bypasses-gateway).
# Real ungated dispatch (registry-named subscript + globals/getattr/locals) must
# fire; non-agent `obj[key](args)` shapes (Triton kernels, CLI dispatch dicts,
# test/cache dicts) must not.

result = tools[name](args)                       # EXPECT_MATCH
out = tool_registry[tool_name](payload)          # EXPECT_MATCH
res = globals()[fn](args)                        # EXPECT_MATCH
fn_out = getattr(self, action_name)(payload)     # EXPECT_MATCH
loc = locals()[handler_name](args)               # EXPECT_MATCH

launch = kernel[grid](kernel_args)               # EXPECT_NONE
out2 = {"drift": cmd_drift, "lint": cmd_lint}[args.cmd](args)  # EXPECT_NONE
val = m["_cancel_op"](cid)                        # EXPECT_NONE
data = cache[key](ctx)                            # EXPECT_NONE
