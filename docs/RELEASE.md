# Release flow

```
PR merged to main
  → GitHub Action validates
  → uploads to s3://raxit-prod-scanner-rules/
  → AgentCore scanners detect ETag change on next scan
  → new rules in effect within one scan window
```

See [`docs/controls-platform/rule-registry-architecture-2026-05-16.html`](https://github.com/raxITlabs/raxit-app-cdk-v1) in the main app repo for the full architecture.
