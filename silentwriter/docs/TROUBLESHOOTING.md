# 🔧 SilentWriter Troubleshooting Guide

This guide helps you diagnose and fix common issues with the SilentWriter GitHub Actions workflow and breaking change detection.

---

## Quick Diagnostics

### Is SilentWriter Working?

Run this quick check:

```bash
# 1. Check if workflow file exists
ls -la .github/workflows/silentwriter.yml

# 2. Check if configuration exists
ls -la .silentwriter.yml

# 3. Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.silentwriter.yml'))"

# 4. Check recent workflow runs
gh run list --workflow=silentwriter.yml --limit 5
```

If all checks pass, SilentWriter is properly configured.

---

## Common Issues

### Issue 1: Workflow Not Running

**Symptoms:**
- No workflow appears in the Actions tab
- PR has no status checks
- No comments from SilentWriter

**Possible Causes & Solutions:**

#### Cause A: Workflow file not in correct location

```bash
# Check file location
ls -la .github/workflows/silentwriter.yml

# If missing, ensure it's in the right place
mkdir -p .github/workflows
# Copy or create the workflow file
```

**Solution:** Workflow must be at `.github/workflows/silentwriter.yml`

#### Cause B: Workflow not triggered for this branch

```yaml
# Check workflow triggers in .github/workflows/silentwriter.yml
on:
  pull_request:
    branches:
      - main  # Add your branch here if missing
```

**Solution:** Add your target branch to the workflow triggers

#### Cause C: GitHub Actions disabled

1. Go to **Settings** → **Actions** → **General**
2. Ensure "Allow all actions and reusable workflows" is selected
3. Check "Allow GitHub Actions to create and approve pull requests"

#### Cause D: Workflow syntax error

```bash
# Validate workflow syntax
actionlint .github/workflows/silentwriter.yml

# Or use GitHub's workflow validator
gh workflow view silentwriter.yml
```

**Solution:** Fix YAML syntax errors in the workflow file

---

### Issue 2: Workflow Fails Immediately

**Symptoms:**
- Workflow runs but fails in first few steps
- Error: "Configuration not found" or "Python module not found"

**Possible Causes & Solutions:**

#### Cause A: Missing .silentwriter.yml

```bash
# Check if file exists
cat .silentwriter.yml

# If missing, create it
cp .silentwriter.yml.example .silentwriter.yml
```

**Solution:** Ensure `.silentwriter.yml` exists in repository root

#### Cause B: Invalid YAML syntax

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('.silentwriter.yml'))"

# Common issues:
# - Incorrect indentation
# - Missing colons
# - Unquoted special characters
```

**Solution:** Fix YAML syntax errors. Use a YAML validator.

#### Cause C: Missing dependencies

```bash
# Check requirements.txt
cat requirements.txt

# Should include:
# pyyaml
# requests
```

**Solution:** Ensure all required packages are in `requirements.txt`

#### Cause D: Python version mismatch

```yaml
# In .github/workflows/silentwriter.yml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Ensure this matches your code
```

**Solution:** Use Python 3.11+ for compatibility

---

### Issue 3: Workflow Times Out

**Symptoms:**
- Workflow runs for 10+ minutes and times out
- Error: "The job running on runner has exceeded the maximum execution time"

**Possible Causes & Solutions:**

#### Cause A: Large PR with many files

```yaml
# Increase timeout in workflow
jobs:
  silent-guardian:
    timeout-minutes: 15  # Increase from 10
```

**Solution:** Increase timeout or split large PRs

#### Cause B: WatsonX API slow or unresponsive

```bash
# Check if WatsonX credentials are set
echo $WATSONX_API_KEY
echo $WATSONX_PROJECT_ID

# Test API connectivity
curl -H "Authorization: Bearer $WATSONX_API_KEY" \
  https://api.watsonx.ai/v1/health
```

**Solution:** 
- Verify WatsonX credentials
- Use heuristic mode as fallback (automatic in workflow)
- Check WatsonX service status

#### Cause C: Network issues

**Solution:** Retry the workflow or check GitHub Actions status

---

### Issue 4: False Positives (Legitimate Changes Blocked)

**Symptoms:**
- Safe changes are marked as breaking
- Optional parameters flagged as violations
- Documentation changes blocked

**Possible Causes & Solutions:**

#### Cause A: Rule too strict

```yaml
# In .silentwriter.yml, adjust the rule
rules:
  - name: "Protect API contracts"
    id: "SILENT-001"
    exceptions:
      - "adding optional parameter"  # Add this
      - "adding overload"
      - "deprecation with @deprecated tag"
```

**Solution:** Add exceptions to the rule

#### Cause B: Pattern matching too broad

```yaml
# Make pattern more specific
rules:
  - name: "Protect API contracts"
    pattern: "src/api/**/*.py"  # More specific
    # Instead of: "src/**"
```

**Solution:** Narrow the file pattern

#### Cause C: Heuristic detection error

**Solution:** 
- Enable WatsonX for better analysis
- Report false positive to improve detection
- Use `/silent-override` command with justification

---

### Issue 5: False Negatives (Breaking Changes Not Detected)

**Symptoms:**
- Breaking changes pass through
- No violations reported for obvious issues
- Workflow shows PASS but changes are breaking

**Possible Causes & Solutions:**

#### Cause A: Rule not configured

```yaml
# Add missing rule to .silentwriter.yml
rules:
  - name: "Protect API contracts"
    id: "SILENT-001"
    pattern: "src/api/**"
    forbidden_changes:
      - "change function signature"
      - "remove exported function"
    auto_block: true  # Ensure this is true
```

**Solution:** Add or enable the appropriate rule

#### Cause B: File pattern doesn't match

```bash
# Check if your files match the pattern
# Pattern: "src/api/**"
# Your file: "api/users.py"  # Won't match!

# Fix: Update pattern or move files
```

**Solution:** Adjust pattern to match your file structure

#### Cause C: Detection logic limitation

**Solution:**
- Report the issue with example
- Enhance detection in `engine/run.py`
- Add custom detection pattern

---

### Issue 6: Status Check Not Appearing

**Symptoms:**
- Workflow runs successfully
- No status check in PR
- Can't add to branch protection

**Possible Causes & Solutions:**

#### Cause A: First run not completed

**Solution:** 
1. Create a test PR
2. Wait for workflow to complete
3. Status check will appear after first run
4. Refresh branch protection settings

#### Cause B: Permissions issue

```yaml
# In .github/workflows/silentwriter.yml
permissions:
  contents: read
  pull-requests: write
  checks: write        # Ensure this is present
  statuses: write      # Ensure this is present
```

**Solution:** Add missing permissions

#### Cause C: Job name mismatch

```yaml
# Ensure job name is consistent
jobs:
  silent-guardian:  # This becomes the status check name
    name: 🤫 Silent Guardian Review
```

**Solution:** Use consistent job naming

---

### Issue 7: PR Comment Not Posted

**Symptoms:**
- Workflow runs successfully
- No comment appears on PR
- Status check works but no details

**Possible Causes & Solutions:**

#### Cause A: Missing permissions

```yaml
permissions:
  pull-requests: write  # Required for comments
  issues: write         # Required for comments
```

**Solution:** Add required permissions

#### Cause B: GitHub token issue

```yaml
# In workflow step
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Solution:** Ensure GITHUB_TOKEN is passed correctly

#### Cause C: Script error

```bash
# Check workflow logs for JavaScript errors
# Look for: "Error: Cannot read property..."
```

**Solution:** Check workflow logs and fix script errors

---

### Issue 8: Labels Not Applied

**Symptoms:**
- Workflow runs successfully
- No labels added to PR
- Status check works but labels missing

**Possible Causes & Solutions:**

#### Cause A: Labels don't exist

**Solution:** Create labels in repository:
1. Go to **Issues** → **Labels**
2. Create these labels:
   - `silentwriter:pass` (green)
   - `silentwriter:warn` (yellow)
   - `silentwriter:block` (red)
   - `breaking-change` (red)

#### Cause B: Permission issue

```yaml
permissions:
  issues: write  # Required for labels
```

**Solution:** Add issues write permission

---

### Issue 9: Merge Not Blocked Despite BLOCK Verdict

**Symptoms:**
- Workflow shows BLOCK
- PR comment shows violations
- But merge button is still enabled

**Possible Causes & Solutions:**

#### Cause A: Branch protection not configured

**Solution:** Follow [BRANCH_PROTECTION_SETUP.md](BRANCH_PROTECTION_SETUP.md):
1. Go to **Settings** → **Branches**
2. Add branch protection rule
3. Enable "Require status checks to pass"
4. Select "🤫 Silent Guardian Review"

#### Cause B: Admin bypass enabled

```yaml
# In branch protection settings
Include administrators: ❌  # Should be unchecked
```

**Solution:** Disable admin bypass or use it responsibly

#### Cause C: Status check not required

**Solution:** Make the status check required in branch protection

---

### Issue 10: WatsonX Integration Issues

**Symptoms:**
- Workflow uses simulation mode
- Error: "WatsonX API key not found"
- Analysis quality is poor

**Possible Causes & Solutions:**

#### Cause A: Missing secrets

```bash
# Check if secrets are set
gh secret list

# Should include:
# WATSONX_API_KEY
# WATSONX_PROJECT_ID
```

**Solution:** Add secrets in repository settings:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add `WATSONX_API_KEY`
3. Add `WATSONX_PROJECT_ID`

#### Cause B: Invalid credentials

```bash
# Test credentials locally
export WATSONX_API_KEY=your_key
export WATSONX_PROJECT_ID=your_id
python engine/granite_client.py
```

**Solution:** Verify credentials with IBM WatsonX

#### Cause C: API quota exceeded

**Solution:** 
- Check WatsonX usage dashboard
- Upgrade plan if needed
- Use heuristic mode as fallback

---

## Advanced Debugging

### Enable Debug Logging

```yaml
# In .github/workflows/silentwriter.yml
- name: Run SilentWriter Analysis
  env:
    DEBUG: true  # Add this
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Run Locally

```bash
# Set up environment
export GITHUB_TOKEN=your_token
export WATSONX_API_KEY=your_key
export WATSONX_PROJECT_ID=your_id

# Run engine directly
python engine/run.py \
  --repo owner/repo \
  --pr 123 \
  --config .silentwriter.yml

# Check output
cat verdict.txt
```

### Inspect Workflow Artifacts

```bash
# Download analysis report
gh run download <run-id> -n silentwriter-report-pr-<number>

# View report
cat verdict.txt
```

### Check Workflow Logs

1. Go to **Actions** tab
2. Click on failed workflow run
3. Expand each step
4. Look for error messages
5. Check "Set up job" for environment issues

---

## Performance Issues

### Slow Workflow Execution

**Symptoms:** Workflow takes >5 minutes

**Solutions:**

1. **Enable caching:**
```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # Enable pip caching
```

2. **Optimize diff analysis:**
```bash
# Fetch only necessary history
- uses: actions/checkout@v4
  with:
    fetch-depth: 10  # Instead of 0
```

3. **Use heuristic mode:**
```yaml
# Disable WatsonX for faster analysis
env:
  WATSONX_API_KEY: ""  # Empty = heuristic mode
```

---

## Getting Help

### Before Asking for Help

Collect this information:

1. **Workflow run URL:**
   ```
   https://github.com/owner/repo/actions/runs/123456
   ```

2. **Error message:**
   ```
   Copy the exact error from workflow logs
   ```

3. **Configuration:**
   ```bash
   # Share relevant parts of .silentwriter.yml
   cat .silentwriter.yml
   ```

4. **PR details:**
   ```
   PR number, branch names, file changes
   ```

### Support Channels

- **Documentation:** [README.md](../README.md)
- **GitHub Issues:** [Report a bug](https://github.com/barryguinea224/silentwriter/issues)
- **Discussions:** [Ask a question](https://github.com/barryguinea224/silentwriter/discussions)

### Reporting Bugs

Include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Workflow logs
5. Configuration files
6. Environment details

---

## Preventive Measures

### Regular Maintenance

```bash
# Weekly checks
- Validate configuration
- Review workflow logs
- Check for updates
- Test with sample PRs
- Monitor false positive rate
```

### Best Practices

1. **Keep workflow updated:**
   ```bash
   # Check for updates
   git pull origin main
   ```

2. **Monitor metrics:**
   - Block rate
   - False positive rate
   - Average execution time
   - Rule violation patterns

3. **Regular testing:**
   - Run test suite monthly
   - Test each critical rule
   - Verify branch protection

4. **Team training:**
   - Share documentation
   - Explain common issues
   - Document overrides
   - Review violations together

---

## Emergency Procedures

### Disable SilentWriter Temporarily

If SilentWriter is blocking critical work:

#### Option 1: Disable workflow
```bash
# Rename workflow file
mv .github/workflows/silentwriter.yml \
   .github/workflows/silentwriter.yml.disabled
git commit -m "temp: disable silentwriter"
git push
```

#### Option 2: Remove from branch protection
1. Go to **Settings** → **Branches**
2. Edit branch protection rule
3. Uncheck "🤫 Silent Guardian Review"
4. Save changes

#### Option 3: Use admin override
- Admin can force merge despite failed checks
- **Must document reason**
- **Must re-enable protection after**

### Re-enable After Emergency

```bash
# Re-enable workflow
mv .github/workflows/silentwriter.yml.disabled \
   .github/workflows/silentwriter.yml
git commit -m "fix: re-enable silentwriter"
git push

# Re-add to branch protection
# Follow BRANCH_PROTECTION_SETUP.md
```

---

## FAQ

### Q: Can I test SilentWriter without blocking PRs?

**A:** Yes, use passive mode:
```yaml
# In .silentwriter.yml
settings:
  mode: "passive"  # Warns but doesn't block
```

### Q: How do I override a false positive?

**A:** Use the override command:
```
/silent-override SILENT-001 --reason='False positive: optional parameter'
```

### Q: Can I customize the blocking rules?

**A:** Yes, edit `.silentwriter.yml`:
```yaml
rules:
  - name: "Your custom rule"
    pattern: "src/**"
    auto_block: true
```

### Q: What if WatsonX is down?

**A:** Workflow automatically falls back to heuristic mode.

### Q: How do I add new rules?

**A:** Add to `.silentwriter.yml`:
```yaml
rules:
  - name: "New rule"
    id: "SILENT-011"
    pattern: "path/**"
    severity: critical
    auto_block: true
```

---

*🤫 SilentWriter · Troubleshooting architecture, one issue at a time.*