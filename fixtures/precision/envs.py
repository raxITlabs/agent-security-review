# Precision fixture for sign.env-var-secret-at-module-scope.
# Only secret-named module-scope env reads should fire; non-secret config
# (CORS, base URL, release tag) must not.
import os

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]        # EXPECT_MATCH
tavily = os.getenv("TAVILY_API_KEY")                  # EXPECT_MATCH

allowed_origins = os.getenv("CORS_ALLOW_ORIGINS")     # EXPECT_NONE
base = os.environ["BASE_URL"]                          # EXPECT_NONE
tag = os.getenv("UNSLOTH_LLAMA_RELEASE_TAG")           # EXPECT_NONE
