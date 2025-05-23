# 🚀 Deployment Checklist

## ✅ Completed Steps

1. **✅ Project Configuration**

   - Updated `pyproject.toml` for dynamic versioning from Git tags
   - Added `hatch-vcs` for VCS-based versioning
   - Configured build targets for wheel and sdist
   - Added semantic-release configuration

2. **✅ GitHub Workflows**

   - Created `.github/workflows/release.yml` for automated PyPI publishing
   - Created `.github/workflows/semantic-release.yml` for automatic versioning
   - Configured proper permissions for OIDC/Trusted Publishing

3. **✅ Documentation**

   - Added badges to README (PyPI, CI, Publish, License)
   - Added comprehensive release process documentation
   - Created CHANGELOG.md for automatic changelog generation

4. **✅ Local Testing**
   - Verified build process works (`uv run python -m build`)
   - Validated packages with twine (`uv run twine check dist/*`)
   - All tests passing (19 tests, 76% coverage)

## 🔲 Remaining Steps (Manual Actions Required)

### 1. Set up PyPI Trusted Publishing (CRITICAL)

**Before pushing to production, you MUST configure Trusted Publishing on PyPI:**

1. **Create PyPI Account** (if you don't have one):

   - Go to https://pypi.org and create an account
   - Verify your email address

2. **Configure Trusted Publisher**:

   - Log into PyPI → Account settings → Trusted Publishers
   - Click "Add a trusted publisher"
   - Fill in the details:
     - **Repository**: `davidyen1124/caltrain-mcp`
     - **Workflow filename**: `release.yml`
     - **Environment**: (leave blank)
   - Save the configuration

3. **Test PyPI Setup** (Optional but Recommended):
   - You can also set up trusted publishing on Test PyPI first
   - Go to https://test.pypi.org → Account settings → Trusted Publishers
   - Use the same settings but test with Test PyPI first

### 2. Test the Full Release Process

1. **Commit with Conventional Commits**:

   ```bash
   git commit -m "feat: add automated versioning and PyPI publishing"
   git push origin main
   ```

2. **Monitor GitHub Actions**:

   - Check Actions tab in GitHub repo
   - Verify semantic-release workflow runs successfully
   - Should create a new tag (e.g., `v0.2.0`)

3. **Verify PyPI Upload**:
   - New tag should trigger release workflow
   - Package should appear on PyPI: https://pypi.org/project/caltrain-mcp/

### 3. Badge Verification

Once the first release is published, verify all badges work:

- [![PyPI](https://img.shields.io/pypi/v/caltrain-mcp)](https://pypi.org/project/caltrain-mcp/)
- [![CI](https://github.com/davidyen1124/caltrain-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/davidyen1124/caltrain-mcp/actions/workflows/ci.yml)
- [![Publish](https://github.com/davidyen1124/caltrain-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/davidyen1124/caltrain-mcp/actions/workflows/release.yml)

## 🎯 Quick Test Commands

```bash
# Test build locally
uv run python -m build --sdist --wheel
uv run twine check dist/*

# Test semantic-release locally (dry-run)
uv tool install python-semantic-release
uv tool run semantic-release version --print

# Clean up test artifacts
rm -rf dist/
```

## 🚨 Important Notes

1. **First Release**: The first automated release will be based on conventional commits since the last tag (`v0.1.0`)

2. **Commit Message Format**: Use conventional commits for automatic versioning:

   - `fix:` → patch version (0.1.0 → 0.1.1)
   - `feat:` → minor version (0.1.0 → 0.2.0)
   - `feat!:` or `BREAKING CHANGE:` → major version (0.1.0 → 1.0.0)

3. **Rollback**: If something goes wrong, you can always delete tags and re-release

4. **Manual Override**: You can still create releases manually with `git tag v1.2.3 && git push --tags`

## 🎉 Once Complete

Your project will have:

- ✅ Automatic versioning based on commit messages
- ✅ Automatic PyPI publishing on every release
- ✅ Professional badges showing build status and PyPI version
- ✅ Zero-maintenance release process
- ✅ Proper changelog generation

Happy shipping! 🚀
