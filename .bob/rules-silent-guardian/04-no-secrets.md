# SILENT-009 : No Secrets in Code

## Rule
NO API keys, tokens, or passwords should ever be committed.

## Detected Patterns
- `API_KEY = "sk-..."`
- `password = "..."`
- `token = "..."`
- `DATABASE_URL = "postgresql://user:pass@..."`
- `.pem` and `.key` files

## Immediate Action Required
1. DO NOT merge this PR
2. Fix the commit BEFORE pushing (amend + force push)
3. Replace with environment variables
4. If already pushed → alert security IMMEDIATELY

## Why This Matters
A secret in code = a security breach.
Even if deleted, it remains in Git history forever.

## Block Message Template
"🔑 SECRET DETECTED in code.
Do not merge. Use process.env instead.
If already pushed, alert @security-team now."
