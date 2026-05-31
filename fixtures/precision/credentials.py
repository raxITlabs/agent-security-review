# Precision fixture for sign.hardcoded-credential-literal.
# Lines tagged `# EXPECT_MATCH` must produce a finding; `# EXPECT_NONE` must not.
# Guards against the unsloth false-positive flood (empty strings / placeholders
# counted as "hardcoded credentials").

api_key = "sk-proj-Ab12Cd34Ef56Gh78Ij90"          # EXPECT_MATCH
OPENAI_API_KEY = "sk-1234567890abcdefghij"         # EXPECT_MATCH
password = "S3cr3tP@ssw0rd123"                      # EXPECT_MATCH
self.client_secret = "abcdef0123456789secret"      # EXPECT_MATCH

api_key = ""                                        # EXPECT_NONE
token = "hf_"                                        # EXPECT_NONE
api_key = "your-api-key-here"                        # EXPECT_NONE
secret = "changeme"                                  # EXPECT_NONE
base_url = "https://api.example.com/v1/long/path"    # EXPECT_NONE
provider_l = provider.lower()                        # EXPECT_NONE
