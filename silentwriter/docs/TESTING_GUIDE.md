# 🧪 SilentWriter Testing Guide

This guide provides comprehensive testing scenarios to verify that SilentWriter correctly blocks PRs with breaking changes based on your `.silentwriter.yml` rules.

## Overview

SilentWriter analyzes pull requests and blocks them when critical architectural violations are detected. This guide helps you test each rule and verify the blocking mechanism works correctly.

---

## Prerequisites

Before testing, ensure:

1. ✅ `.silentwriter.yml` is configured in your repository
2. ✅ `.github/workflows/silentwriter.yml` is set up
3. ✅ Branch protection rules are enabled (see [BRANCH_PROTECTION_SETUP.md](BRANCH_PROTECTION_SETUP.md))
4. ✅ You have push access to create test branches

---

## Quick Test (5 minutes)

### Test 1: Breaking Change Detection

```bash
# Create a test branch
git checkout -b test-breaking-change

# Create a file with a function
cat > test_api.py << 'EOF'
def calculate_total(items):
    """Calculate total price."""
    return sum(items)
EOF

git add test_api.py
git commit -m "feat: add calculate_total function"
git push origin test-breaking-change

# Create PR and wait for it to pass
# Then modify the function signature (breaking change)
cat > test_api.py << 'EOF'
def calculate_total(items, tax_rate):
    """Calculate total price with tax."""
    return sum(items) * (1 + tax_rate)
EOF

git add test_api.py
git commit -m "feat: add tax calculation"
git push

# Expected: PR should be BLOCKED
# Check: PR comment should show breaking change violation
```

**Expected Result:**
- 🛡️ Status: BLOCKED
- 🔴 Label: `silentwriter:block`, `breaking-change`
- ❌ Merge button: Disabled
- 💬 Comment: Explains the function signature change violation

---

## Comprehensive Test Suite

### Test 2: API Contract Protection (SILENT-001)

**Rule:** Public API function signatures cannot be modified.

#### Test 2.1: Function Signature Change

```bash
git checkout -b test-api-signature-change

# Original function
cat > src/api/users.py << 'EOF'
def get_user(user_id):
    """Get user by ID."""
    return {"id": user_id, "name": "Test User"}
EOF

git add src/api/users.py
git commit -m "feat: add get_user function"
git push origin test-api-signature-change

# Modify signature (breaking change)
cat > src/api/users.py << 'EOF'
def get_user(user_id, include_details):
    """Get user by ID with optional details."""
    return {"id": user_id, "name": "Test User", "details": include_details}
EOF

git add src/api/users.py
git commit -m "feat: add include_details parameter"
git push
```

**Expected:** ⛔ BLOCKED - Required parameter added

#### Test 2.2: Function Removal

```bash
git checkout -b test-api-function-removal

# Create and commit function
cat > src/api/auth.py << 'EOF'
def login(username, password):
    """User login."""
    return {"token": "abc123"}

def logout(token):
    """User logout."""
    return {"success": True}
EOF

git add src/api/auth.py
git commit -m "feat: add auth functions"
git push origin test-api-function-removal

# Remove function (breaking change)
cat > src/api/auth.py << 'EOF'
def login(username, password):
    """User login."""
    return {"token": "abc123"}
EOF

git add src/api/auth.py
git commit -m "refactor: remove logout function"
git push
```

**Expected:** ⛔ BLOCKED - Function deleted

#### Test 2.3: Safe Change (Optional Parameter)

```bash
git checkout -b test-api-optional-param

# Original function
cat > src/api/products.py << 'EOF'
def list_products(category):
    """List products by category."""
    return []
EOF

git add src/api/products.py
git commit -m "feat: add list_products"
git push origin test-api-optional-param

# Add optional parameter (safe change)
cat > src/api/products.py << 'EOF'
def list_products(category, limit=10):
    """List products by category with optional limit."""
    return []
EOF

git add src/api/products.py
git commit -m "feat: add optional limit parameter"
git push
```

**Expected:** ✅ PASS - Optional parameter is allowed

---

### Test 3: Tests Required on Core (SILENT-002)

**Rule:** Changes to business logic must include unit tests.

#### Test 3.1: Core Change Without Tests

```bash
git checkout -b test-core-no-tests

# Add core logic without tests
cat > src/core/calculator.py << 'EOF'
def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    return price * (1 - discount_percent / 100)
EOF

git add src/core/calculator.py
git commit -m "feat: add discount calculation"
git push origin test-core-no-tests
```

**Expected:** ⛔ BLOCKED - Missing tests

#### Test 3.2: Core Change With Tests

```bash
git checkout -b test-core-with-tests

# Add core logic
cat > src/core/calculator.py << 'EOF'
def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    return price * (1 - discount_percent / 100)
EOF

# Add tests
cat > tests/test_calculator.py << 'EOF'
import pytest
from src.core.calculator import calculate_discount

def test_calculate_discount():
    assert calculate_discount(100, 10) == 90
    assert calculate_discount(50, 20) == 40
    assert calculate_discount(100, 0) == 100
EOF

git add src/core/calculator.py tests/test_calculator.py
git commit -m "feat: add discount calculation with tests"
git push origin test-core-with-tests
```

**Expected:** ✅ PASS - Tests included

---

### Test 4: Approved Dependencies Only (SILENT-003)

**Rule:** Only approved libraries can be added.

#### Test 4.1: Blocked Dependency

```bash
git checkout -b test-blocked-dependency

# Add blocked dependency
cat > requirements.txt << 'EOF'
pyyaml==6.0
requests==2.31.0
mongoose==1.0.0
EOF

git add requirements.txt
git commit -m "deps: add mongoose"
git push origin test-blocked-dependency
```

**Expected:** ⛔ BLOCKED - Unauthorized dependency

#### Test 4.2: Allowed Dependency

```bash
git checkout -b test-allowed-dependency

# Add allowed dependency
cat > requirements.txt << 'EOF'
pyyaml==6.0
requests==2.31.0
fastapi==0.104.0
EOF

git add requirements.txt
git commit -m "deps: add fastapi"
git push origin test-allowed-dependency
```

**Expected:** ✅ PASS - Approved dependency

---

### Test 5: Auth Layer Protection (SILENT-005)

**Rule:** Authentication functions are critical and require security review.

#### Test 5.1: Auth Function Modification

```bash
git checkout -b test-auth-modification

# Original auth function
cat > src/auth/security.py << 'EOF'
import hashlib

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()
EOF

git add src/auth/security.py
git commit -m "feat: add password hashing"
git push origin test-auth-modification

# Modify hashing algorithm (critical change)
cat > src/auth/security.py << 'EOF'
import hashlib

def hash_password(password):
    """Hash password using MD5."""
    return hashlib.md5(password.encode()).hexdigest()
EOF

git add src/auth/security.py
git commit -m "refactor: change to MD5"
git push
```

**Expected:** ⛔ BLOCKED - Security-critical change

---

### Test 6: No Secrets in Code (SILENT-009)

**Rule:** Secrets must not be committed to the repository.

#### Test 6.1: API Key in Code

```bash
git checkout -b test-secret-detection

# Add file with hardcoded secret
cat > src/config.py << 'EOF'
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:password@localhost/db"
EOF

git add src/config.py
git commit -m "feat: add configuration"
git push origin test-secret-detection
```

**Expected:** ⛔ BLOCKED - Secret detected

#### Test 6.2: Environment Variable Usage

```bash
git checkout -b test-env-vars

# Use environment variables (safe)
cat > src/config.py << 'EOF'
import os

API_KEY = os.environ.get("API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")
EOF

git add src/config.py
git commit -m "feat: use environment variables"
git push origin test-env-vars
```

**Expected:** ✅ PASS - No secrets in code

---

### Test 7: Database Migration Safety (SILENT-010)

**Rule:** Database migrations must be reversible and safe.

#### Test 7.1: Dangerous Migration

```bash
git checkout -b test-dangerous-migration

# Create dangerous migration
cat > migrations/001_drop_column.sql << 'EOF'
-- Drop user email column
ALTER TABLE users DROP COLUMN email;
EOF

git add migrations/001_drop_column.sql
git commit -m "migration: remove email column"
git push origin test-dangerous-migration
```

**Expected:** ⛔ BLOCKED - Dangerous operation (DROP COLUMN)

#### Test 7.2: Safe Migration

```bash
git checkout -b test-safe-migration

# Create safe migration with rollback
cat > migrations/002_add_column.sql << 'EOF'
-- up: Add user phone column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- down: Remove user phone column
ALTER TABLE users DROP COLUMN phone;
EOF

git add migrations/002_add_column.sql
git commit -m "migration: add phone column with rollback"
git push origin test-safe-migration
```

**Expected:** ✅ PASS - Safe migration with rollback

---

## Automated Test Script

Create a test script to run all scenarios:

```bash
#!/bin/bash
# test-silentwriter.sh

set -e

echo "🧪 SilentWriter Test Suite"
echo "=========================="

# Test 1: Breaking Change
echo "Test 1: Breaking Change Detection..."
git checkout -b test-1-breaking-change
echo "def calc(a, b): return a + b" > test.py
git add test.py && git commit -m "add calc"
git push origin test-1-breaking-change
echo "def calc(a, b, c): return a + b + c" > test.py
git add test.py && git commit -m "modify calc signature"
git push
echo "✓ Test 1 complete - Check PR for BLOCK status"

# Test 2: Safe Change
echo "Test 2: Safe Change..."
git checkout -b test-2-safe-change
echo "# Documentation update" > README.md
git add README.md && git commit -m "docs: update readme"
git push origin test-2-safe-change
echo "✓ Test 2 complete - Check PR for PASS status"

# Test 3: Blocked Dependency
echo "Test 3: Blocked Dependency..."
git checkout -b test-3-blocked-dep
echo "mongoose==1.0.0" >> requirements.txt
git add requirements.txt && git commit -m "add mongoose"
git push origin test-3-blocked-dep
echo "✓ Test 3 complete - Check PR for BLOCK status"

echo ""
echo "=========================="
echo "✅ All tests created!"
echo "Check GitHub PRs for results"
```

Run the script:
```bash
chmod +x test-silentwriter.sh
./test-silentwriter.sh
```

---

## Manual Testing Checklist

Use this checklist to verify all features:

### Workflow Execution
- [ ] Workflow triggers on PR open
- [ ] Workflow triggers on PR synchronize
- [ ] Workflow triggers on PR reopen
- [ ] Workflow completes within timeout (10 min)
- [ ] Workflow artifacts are uploaded

### Status Checks
- [ ] Status check appears in PR
- [ ] Status check name is correct: "🤫 Silent Guardian Review"
- [ ] Status check blocks merge when BLOCK verdict
- [ ] Status check allows merge when PASS verdict
- [ ] Status check shows neutral when WARN verdict

### PR Comments
- [ ] Comment is posted on every PR
- [ ] Comment shows verdict (PASS/WARN/BLOCK)
- [ ] Comment shows violation count
- [ ] Comment shows detailed violations
- [ ] Comment includes fix suggestions
- [ ] Comment links to constitution

### PR Labels
- [ ] Label `silentwriter:pass` added on PASS
- [ ] Label `silentwriter:warn` added on WARN
- [ ] Label `silentwriter:block` added on BLOCK
- [ ] Label `breaking-change` added on critical violations
- [ ] Old labels are removed when status changes

### Breaking Change Detection
- [ ] Function signature changes detected
- [ ] Function removals detected
- [ ] Parameter type changes detected
- [ ] Optional parameters allowed
- [ ] Deprecated functions allowed

### Rule Enforcement
- [ ] SILENT-001: API contracts protected
- [ ] SILENT-002: Tests required on core
- [ ] SILENT-003: Dependencies validated
- [ ] SILENT-005: Auth layer protected
- [ ] SILENT-009: Secrets detected
- [ ] SILENT-010: Migrations validated

### Error Handling
- [ ] Graceful fallback when WatsonX unavailable
- [ ] Clear error messages on configuration errors
- [ ] Workflow doesn't crash on invalid diff
- [ ] Timeout handling works correctly

---

## Performance Testing

### Test Large PRs

```bash
# Create PR with 100+ file changes
git checkout -b test-large-pr
for i in {1..100}; do
  echo "# File $i" > "file_$i.py"
done
git add .
git commit -m "test: large PR"
git push origin test-large-pr
```

**Expected:**
- Workflow completes within timeout
- Analysis is accurate despite size
- Performance is acceptable (<5 min)

### Test Concurrent PRs

```bash
# Open 5 PRs simultaneously
for i in {1..5}; do
  git checkout -b test-concurrent-$i
  echo "# Test $i" > "test_$i.py"
  git add . && git commit -m "test $i"
  git push origin test-concurrent-$i &
done
wait
```

**Expected:**
- All workflows run independently
- No race conditions
- Concurrency control works

---

## Debugging Failed Tests

### Check Workflow Logs

1. Go to **Actions** tab in GitHub
2. Click on the failed workflow run
3. Expand each step to see logs
4. Look for error messages

### Download Analysis Report

```bash
# Download artifact from workflow run
gh run download <run-id> -n silentwriter-report-pr-<number>
cat verdict.txt
```

### Validate Configuration

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.silentwriter.yml'))"

# Check workflow syntax
actionlint .github/workflows/silentwriter.yml
```

### Test Locally

```bash
# Run engine locally
export GITHUB_TOKEN=your_token
python engine/run.py --repo owner/repo --pr 123
```

---

## Continuous Testing

### Add to CI/CD

```yaml
# .github/workflows/test-silentwriter.yml
name: Test SilentWriter

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run test suite
        run: ./test-silentwriter.sh
```

### Monitor Metrics

Track these metrics over time:
- **Block Rate:** % of PRs blocked
- **False Positive Rate:** % of incorrect blocks
- **Average Fix Time:** Time from block to resolution
- **Rule Violations:** Most common violations

---

## Next Steps

After testing:

1. ✅ Review [BRANCH_PROTECTION_SETUP.md](BRANCH_PROTECTION_SETUP.md)
2. ✅ Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. ✅ Customize `.silentwriter.yml` based on test results
4. ✅ Train team on the workflow
5. ✅ Enable in production

---

*🤫 SilentWriter · Testing architecture, one scenario at a time.*