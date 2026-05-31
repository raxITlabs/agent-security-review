// Precision fixture for sign.env-var-secret-at-module-scope-ts.
// Only secret-named module-scope env reads should fire.

const key = process.env.OPENAI_API_KEY;        // EXPECT_MATCH

const origins = process.env.CORS_ALLOW_ORIGINS; // EXPECT_NONE
const base = process.env.BASE_URL;              // EXPECT_NONE
