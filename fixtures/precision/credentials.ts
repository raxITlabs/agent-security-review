// Precision fixture for sign.hardcoded-credential-literal-ts.
// `// EXPECT_MATCH` must produce a finding; `// EXPECT_NONE` must not.

const apiKey = "sk-proj-Ab12Cd34Ef56Gh78";   // EXPECT_MATCH
const dbPassword = "S3cr3tP@ssw0rd123xyz";    // EXPECT_MATCH

const apiKey2 = "";                            // EXPECT_NONE
const token = "hf_";                           // EXPECT_NONE
const apiKey3 = "your-api-key";                // EXPECT_NONE

// --- PRECISION 2026-07: identifier-shaped values (mirrors the Python fixture).
const accessKey = "fsap-0a1b2c3d4e5f6a7b8";                 // EXPECT_NONE
const roleSecret = "arn:aws:iam::123456789012:role/Agent";  // EXPECT_NONE
const datasetToken = "openai/gsm8k-main-test";              // EXPECT_NONE
const endpointToken = "https://kb.raxit.ai/v1/search";      // EXPECT_NONE
const keyPathSecret = "/etc/agent/service_account";         // EXPECT_NONE
const maxTokens = "1024000000";                              // EXPECT_NONE
const eos_token = "<|endoftext|>";                           // EXPECT_NONE

// Retained true positive: base64 secret containing "/" must still fire.
const awsSecretAccessKey = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzTESTKEY";  // EXPECT_MATCH

// --- PRECISION 2026-07 (prose guard): sentences, not secrets.
const clientSecret = "Must be valid Azure application secret";  // EXPECT_NONE
const authToken = "This token expires after thirty minutes";    // EXPECT_NONE

// --- PRECISION 2026-07 (env-var-name guard): the aeon FP class.
const authSecret = 'LITEBEAM_API_KEY_VALUE';           // EXPECT_NONE
const apiKey4 = "OPENAI_API_KEY_PRODUCTION";           // EXPECT_NONE
// All-caps with no underscore is a real key shape and must still fire.
const awsAccessKey = "AKIAIOSFODNN7QWERTZXC";          // EXPECT_MATCH
