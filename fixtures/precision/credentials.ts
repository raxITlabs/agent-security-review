// Precision fixture for sign.hardcoded-credential-literal-ts.
// `// EXPECT_MATCH` must produce a finding; `// EXPECT_NONE` must not.

const apiKey = "sk-proj-Ab12Cd34Ef56Gh78";   // EXPECT_MATCH
const dbPassword = "S3cr3tP@ssw0rd123xyz";    // EXPECT_MATCH

const apiKey2 = "";                            // EXPECT_NONE
const token = "hf_";                           // EXPECT_NONE
const apiKey3 = "your-api-key";                // EXPECT_NONE
