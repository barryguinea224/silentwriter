# 🛡️ Branch Protection Setup Guide

This guide explains how to configure GitHub branch protection rules to enforce SilentWriter's architectural governance and automatically block PRs with breaking changes.

## Overview

SilentWriter's enhanced workflow creates a required status check called **"🤫 Silent Guardian Review"** that must pass before PRs can be merged. This ensures that no breaking changes slip through code review.

---

## Quick Setup (5 minutes)

### Step 1: Enable Branch Protection

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Branches**
3. Click **Add branch protection rule**
4. Enter branch name pattern: `main` (or `master`, `develop`)

### Step 2: Configure Required Status Checks

In the branch protection rule configuration:

1. ✅ Check **"Require status checks to pass before merging"**
2. ✅ Check **"Require branches to be up to date before merging"**
3. In the search box, type: `🤫 Silent Guardian Review`
4. Select the status check from the dropdown
5. Click **Create** or **Save changes**

### Step 3: Additional Recommended Settings

For maximum protection, also enable:

- ✅ **Require a pull request before merging**
  - Require approvals: `1` (or more)
  - Dismiss stale pull request approvals when new commits are pushed
- ✅ **Require conversation resolution before merging**
- ✅ **Do not allow bypassing the above settings** (unless you need admin override)
- ✅ **Restrict who can push to matching branches** (optional)

---

## Detailed Configuration

### Required Status Checks

The SilentWriter workflow creates multiple checkpoints:

| Status Check Name | Purpose | When It Fails |
|-------------------|---------|---------------|
| `🤫 Silent Guardian Review` | Main job status | Any critical violation detected |
| `SilentWriter Guardian` | Check run | Breaking changes found |

**Important:** Make sure to add `🤫 Silent Guardian Review` as a required status check.

### Branch Protection Rule Example

```yaml
Branch name pattern: main
Require status checks to pass before merging: ✅
  - 🤫 Silent Guardian Review
Require branches to be up to date before merging: ✅
Require pull request before merging: ✅
  - Required approvals: 1
  - Dismiss stale reviews: ✅
Require conversation resolution: ✅
Include administrators: ❌ (allows admin override)
```

---

## Verification

### Test the Protection

1. Create a test branch with a breaking change:
   ```bash
   git checkout -b test-breaking-change
   # Make a breaking change (e.g., modify a function signature)
   git commit -am "test: breaking change"
   git push origin test-breaking-change
   ```

2. Open a Pull Request

3. Verify the workflow runs and blocks the PR:
   - ❌ Status check should fail
   - 🛡️ PR comment should explain the violation
   - 🔴 "Merge" button should be disabled

4. Fix the violation and push again:
   ```bash
   # Revert the breaking change
   git commit -am "fix: revert breaking change"
   git push
   ```

5. Verify the workflow passes:
   - ✅ Status check should pass
   - ✅ "Merge" button should be enabled

---

## Status Check Behavior

### PASS (✅)
- **Status:** Success
- **Merge:** Allowed
- **Label:** `silentwriter:pass`
- **Behavior:** PR can be merged normally

### WARN (⚠️)
- **Status:** Neutral
- **Merge:** Allowed (with warnings)
- **Label:** `silentwriter:warn`
- **Behavior:** PR can be merged, but review recommended

### BLOCK (🛡️)
- **Status:** Failure
- **Merge:** **BLOCKED**
- **Label:** `silentwriter:block`, `breaking-change`
- **Behavior:** PR cannot be merged until violations are fixed

---

## Override Procedures

### When to Override

Overrides should be rare and require justification:
- Emergency hotfixes
- Intentional breaking changes with migration plan
- False positives (report to improve rules)

### How to Override

#### Option 1: Admin Override (Not Recommended)
If "Include administrators" is disabled in branch protection:
1. Admin can force merge despite failed checks
2. **Must document reason in PR**
3. **Must notify team in Slack**

#### Option 2: Rule Override (Recommended)
Use SilentWriter's built-in override system:
1. Comment on PR: `/silent-override SILENT-001 --reason='Emergency hotfix for production issue #1234'`
2. Requires approval from authorized role (tech-lead, architect)
3. Override is logged and tracked

#### Option 3: Temporary Disable
For planned breaking changes:
1. Temporarily remove the required status check
2. Merge the PR
3. Re-enable the status check immediately
4. **Document in CHANGELOG.md**

---

## Troubleshooting

### Status Check Not Appearing

**Problem:** The status check doesn't show up in branch protection settings.

**Solution:**
1. The workflow must run at least once before the check appears
2. Create a test PR to trigger the workflow
3. Wait for the workflow to complete
4. Refresh the branch protection settings page
5. The check should now appear in the search results

### Workflow Fails with "Configuration Not Found"

**Problem:** Workflow fails with error about missing `.silentwriter.yml`.

**Solution:**
1. Ensure `.silentwriter.yml` exists in the repository root
2. Validate the YAML syntax:
   ```bash
   python -c "import yaml; yaml.safe_load(open('.silentwriter.yml'))"
   ```
3. Commit and push the configuration file

### False Positives

**Problem:** Workflow blocks legitimate changes.

**Solution:**
1. Review the violation details in the PR comment
2. Check if the rule is too strict
3. Update `.silentwriter.yml` to adjust the rule
4. Use exceptions or allow_list if appropriate
5. Document the change in the constitution

### Workflow Times Out

**Problem:** Workflow exceeds 10-minute timeout.

**Solution:**
1. Check if WatsonX API is responding slowly
2. Increase timeout in workflow: `timeout-minutes: 15`
3. Consider using heuristic mode for faster analysis
4. Optimize diff size by splitting large PRs

---

## Advanced Configuration

### Multiple Protected Branches

Protect multiple branches with different rules:

```yaml
# main branch - strict
Branch: main
Required checks: 🤫 Silent Guardian Review
Required approvals: 2

# develop branch - moderate
Branch: develop
Required checks: 🤫 Silent Guardian Review
Required approvals: 1

# feature/* branches - lenient
Branch: feature/*
Required checks: (none)
Required approvals: 0
```

### Custom Workflow Triggers

Modify `.github/workflows/silentwriter.yml` to run on specific events:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - develop
      - release/*
  push:
    branches:
      - main  # Also run on direct pushes
```

### Integration with Other Checks

Combine SilentWriter with other required checks:

```yaml
Required status checks:
  - 🤫 Silent Guardian Review
  - CI / Build
  - CI / Test
  - CI / Lint
  - Security / CodeQL
```

---

## Monitoring and Metrics

### Track Blocked PRs

Monitor SilentWriter's effectiveness:

1. **GitHub Insights:**
   - Go to **Insights** → **Pull requests**
   - Filter by label: `silentwriter:block`
   - Track trends over time

2. **Workflow Artifacts:**
   - Download analysis reports from workflow runs
   - Review violation patterns
   - Identify common issues

3. **Slack Notifications:**
   - Configure in `.silentwriter.yml`:
     ```yaml
     notifications:
       slack: true
       slack_channel: "#code-review"
       mention_on_block: ["@tech-lead"]
     ```

### Success Metrics

Track these KPIs:
- **Block Rate:** % of PRs blocked by SilentWriter
- **False Positive Rate:** % of blocks that were overridden
- **Time to Fix:** Average time from block to resolution
- **Violation Types:** Most common rule violations

---

## Best Practices

### 1. Start with Warnings
When first implementing SilentWriter:
- Set `mode: passive` in `.silentwriter.yml`
- Monitor violations without blocking
- Adjust rules based on feedback
- Switch to `mode: active` after 1-2 weeks

### 2. Educate the Team
- Share this documentation with all developers
- Explain the purpose of each rule
- Provide examples of compliant code
- Hold a team meeting to discuss the constitution

### 3. Regular Rule Reviews
- Review `.silentwriter.yml` quarterly
- Update rules based on team feedback
- Remove obsolete rules
- Add new rules for emerging patterns

### 4. Document Overrides
- Require justification for all overrides
- Log overrides in a tracking document
- Review override patterns monthly
- Update rules to reduce false positives

### 5. Continuous Improvement
- Use SilentWriter's learning mode
- Track which rules are most violated
- Provide better error messages
- Create fix templates for common issues

---

## Support

### Getting Help

- **Documentation:** [README.md](../README.md)
- **Configuration:** [.silentwriter.yml](../.silentwriter.yml)
- **Issues:** [GitHub Issues](https://github.com/barryguinea224/silentwriter/issues)
- **Slack:** #code-review channel

### Reporting Issues

If you encounter problems:
1. Check this troubleshooting guide
2. Review workflow logs in GitHub Actions
3. Validate your `.silentwriter.yml` configuration
4. Open an issue with reproduction steps

---

## Next Steps

After setting up branch protection:

1. ✅ Read the [Testing Guide](TESTING_GUIDE.md)
2. ✅ Review the [Troubleshooting Guide](TROUBLESHOOTING.md)
3. ✅ Customize `.silentwriter.yml` for your project
4. ✅ Train your team on the new workflow
5. ✅ Monitor and iterate on the rules

---

*🤫 SilentWriter · Protecting architecture, one PR at a time.*