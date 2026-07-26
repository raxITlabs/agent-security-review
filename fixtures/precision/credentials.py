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

# --- PRECISION 2026-07: identifier-shaped values bound to credential-ish names.
# These are naming artifacts, not leaked secrets. Each fired before the tightening.
access_key = "fsap-0a1b2c3d4e5f6a7b8"                # EXPECT_NONE
efs_token = "fs-01234567890abcdef"                    # EXPECT_NONE
role_secret = "arn:aws:iam::123456789012:role/Agent"  # EXPECT_NONE
dataset_token = "openai/gsm8k-main-test"              # EXPECT_NONE
model_secret = "anthropic/claude-opus-4-20250514"     # EXPECT_NONE
key_path_secret = "/etc/agent/service_account"        # EXPECT_NONE
endpoint_token = "https://kb.raxit.ai/v1/search"      # EXPECT_NONE

# Tokenizer / counter names that merely END in _token or _key.
eos_token = "<|endoftext|>"                           # EXPECT_NONE
pad_token = "<pad>"                                    # EXPECT_NONE
special_token = "[CLS]"                                # EXPECT_NONE
prompt_tokens_key = "usage.prompt_tokens"              # EXPECT_NONE

# Retained true positives: high-entropy, mixed-case secrets still fire — including
# a base64 secret that legitimately contains "/", which must NOT be read as a slug.
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzTESTKEY"   # EXPECT_MATCH
client = Thing(api_key="sk-live-abc123def456ghi789")   # EXPECT_MATCH
cfg = {"password": "hunter2hunter2hunter2"}            # EXPECT_MATCH

# --- PRECISION 2026-07 (prose guard): a credential-named variable holding a SENTENCE
# is an error message / help string / validation hint, not a secret. Real secrets have
# no internal whitespace. These survived the identifier-shape guards above.
client_secret = "Must be valid Azure application secret"   # EXPECT_NONE
token = "This token expires after thirty minutes"          # EXPECT_NONE
api_key = "Contact the administrator to obtain a key"      # EXPECT_NONE
password = "Minimum twelve characters with one symbol"     # EXPECT_NONE
