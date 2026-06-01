# Regression fixture for the overfit-audit generalization pass.
# Locks in the rules that were structurally DEAD (fired 0 on their own canonical
# case) or overfit, now revived/generalized. Each tag sits on the firing line.

# --- skill-without-description: was function_definition+child decorator (dead);
# now decorated_definition. Undocumented @tool must fire; documented must not.
@tool
def lookup(x):                                          # EXPECT_MATCH:scope.skill-without-description
    return x

@function_tool
def documented(y):
    "Look up a value by key."
    return y                                            # EXPECT_NONE:scope.skill-without-description

# --- skill-bypasses-permission: bare pattern couldn't match a keyword_argument
# (dead); now matches the kwarg form across SDKs.
_opts = ClaudeAgentOptions(permission_mode="bypassPermissions")   # EXPECT_MATCH:sign.skill-bypasses-permission
_go = make_agent(dangerously_skip_permissions=True)              # EXPECT_MATCH:sign.skill-bypasses-permission

# --- log-output-with-secrets: f-string required text on BOTH sides + only
# logger./print (dead on common forms); now catches log./logger. + var-at-end.
def emit(api_key, token, user):
    log.info(f"api_key={api_key}")                      # EXPECT_MATCH:stop.log-output-with-secrets
    logger.warning(f"auth token {token}")              # EXPECT_MATCH:stop.log-output-with-secrets
    logger.info(f"user {user} logged in")              # EXPECT_NONE:stop.log-output-with-secrets
