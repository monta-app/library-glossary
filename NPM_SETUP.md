# GitHub Packages Setup and Publishing Guide

This guide walks you through setting up and publishing the `@monta/glossary` package to GitHub Packages.

## Why GitHub Packages?

- ✅ **Private by default** - Perfect for organization-internal packages
- ✅ **Integrated with GitHub** - Uses existing GitHub authentication
- ✅ **No extra accounts** - No need for separate npm account
- ✅ **Organization control** - Managed through GitHub organization settings
- ✅ **Free for public repos** - No cost for open source packages

## Prerequisites

1. **GitHub account** with access to the `monta-app` organization
2. **npm CLI** - Already installed with Node.js
3. **Personal Access Token (PAT)** - For authentication

## One-Time Setup

### 1. Create a GitHub Personal Access Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a descriptive name: `npm-publish-glossary`
4. Set expiration (recommended: 90 days, then renew)
5. Select scopes:
   - ✅ `write:packages` - Upload packages
   - ✅ `read:packages` - Download packages
   - ✅ `delete:packages` - Delete package versions (optional)
   - ✅ `repo` - Required for private repos
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)

### 2. Configure npm to Use GitHub Packages

Create/edit `~/.npmrc` (in your home directory):

```bash
# Open your global .npmrc
nano ~/.npmrc
```

Add these lines:

```
@monta:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=YOUR_GITHUB_TOKEN_HERE
```

Replace `YOUR_GITHUB_TOKEN_HERE` with the token you created.

**Security Note**: Keep this file private! It contains your authentication token.

### 3. Verify Configuration

```bash
# Check your .npmrc
cat ~/.npmrc

# Test authentication
npm whoami --registry=https://npm.pkg.github.com
```

This should display your GitHub username.

## Publishing to GitHub Packages

### First Time Publishing

```bash
# Install dependencies
npm install

# Build and test
npm run build
npm test

# Publish to GitHub Packages
npm publish
```

The `publishConfig` in `package.json` automatically directs the package to GitHub Packages:

```json
{
  "publishConfig": {
    "registry": "https://npm.pkg.github.com"
  }
}
```

### Publishing Updates

1. **Update version in package.json**:
   ```bash
   # Patch: 1.0.0 -> 1.0.1 (bug fixes)
   npm version patch

   # Minor: 1.0.0 -> 1.1.0 (new features, backwards compatible)
   npm version minor

   # Major: 1.0.0 -> 2.0.0 (breaking changes)
   npm version major
   ```

2. **Push changes and tags**:
   ```bash
   git push && git push --tags
   ```

3. **Publish to GitHub Packages**:
   ```bash
   npm publish
   ```

## Installing the Package (For Consumers)

### Setup for Consumers

Anyone wanting to use your package needs to configure their npm:

**Option 1: Project-level `.npmrc`** (Recommended)

Create `.npmrc` in the project root:

```
@monta:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

Then set the environment variable:

```bash
# In .env (don't commit!)
GITHUB_TOKEN=ghp_your_token_here

# Or export in shell
export GITHUB_TOKEN=ghp_your_token_here
```

**Option 2: Global `.npmrc`**

Add to `~/.npmrc`:

```
@monta:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=ghp_your_token_here
```

### Installing the Package

```bash
# Install
npm install @monta/glossary

# Or with yarn
yarn add @monta/glossary
```

### Usage

```typescript
import { Glossary } from '@monta/glossary';

const glossary = new Glossary();
const term = await glossary.getTerm('charging cable');
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to GitHub Packages

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://npm.pkg.github.com'
          scope: '@monta'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Publish to GitHub Packages
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Now publishing is automatic when you push a tag:

```bash
npm version patch
git push --tags
```

## Viewing Published Packages

1. Go to your repository on GitHub
2. Click on **"Packages"** in the right sidebar
3. Or visit: https://github.com/orgs/monta-app/packages?repo_name=library-glossary

## Package Visibility

By default, packages inherit the repository's visibility:
- **Public repo** → Public package
- **Private repo** → Private package

To change package visibility:
1. Go to the package page on GitHub
2. Click **"Package settings"**
3. Change visibility under **"Danger Zone"**

## Managing Access

### Organization Members

All organization members with read access to the repo can install the package.

### External Users

To allow external users:
1. Go to the package settings
2. Under **"Manage Actions access"**
3. Add users or teams

### CI/CD Access

For GitHub Actions in other repos:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    registry-url: 'https://npm.pkg.github.com'
    scope: '@monta'

- name: Install dependencies
  run: npm ci
  env:
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The `GITHUB_TOKEN` is automatically provided by GitHub Actions.

## Versioning Guidelines

Follow [Semantic Versioning](https://semver.org/):

- **Patch** (1.0.X): Bug fixes, no API changes
  ```bash
  npm version patch
  ```

- **Minor** (1.X.0): New features, backwards compatible
  ```bash
  npm version minor
  ```

- **Major** (X.0.0): Breaking changes
  ```bash
  npm version major
  ```

## Publishing Workflow

### Standard Release Process

```bash
# 1. Make changes and test
npm install
npm test
npm run build

# 2. Update version
npm version patch  # or minor, or major

# 3. Push with tags
git push && git push --tags

# 4. Publish to GitHub Packages
npm publish
```

### Quick Publish

```bash
npm run build && npm test && npm version patch && git push --tags && npm publish
```

## Troubleshooting

### "Unable to authenticate"

**Solution**: Check your PAT in `~/.npmrc`:
```bash
cat ~/.npmrc
# Verify the token is correct and hasn't expired
```

### "Package name must match repository"

**Solution**: Ensure package name matches the pattern:
```json
{
  "name": "@monta/glossary"
}
```

The scope `@monta` must match your GitHub organization.

### "403 Forbidden"

**Possible causes**:
1. Token doesn't have `write:packages` scope
2. You don't have write access to the repository
3. Token has expired

**Solution**: Create a new PAT with correct scopes.

### "Cannot find module '@monta/glossary'"

**For consumers**: They need to configure `.npmrc`:

```
@monta:registry=https://npm.pkg.github.com
```

### "prepublishOnly script failed"

**Solution**: Fix build errors:
```bash
npm run build
# Fix any TypeScript errors
```

## Comparing to Public npm

| Feature | GitHub Packages | Public npm |
|---------|----------------|------------|
| **Privacy** | Private by default | Public by default |
| **Authentication** | GitHub PAT | npm account |
| **Cost** | Free for public repos | Free for public packages |
| **Organization** | GitHub orgs | npm orgs (paid) |
| **Discovery** | Limited to org | Global registry |
| **Setup** | `.npmrc` config needed | Works out of the box |

## Best Practices

1. ✅ **Use environment variables for tokens**:
   ```bash
   # In .npmrc
   //npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
   ```

2. ✅ **Add .npmrc to .gitignore** (for project-level configs with tokens)

3. ✅ **Rotate tokens regularly** (90-day expiration recommended)

4. ✅ **Use GitHub Actions** for automated publishing

5. ✅ **Document setup** in your README for package consumers

6. ✅ **Version properly** with semantic versioning

7. ✅ **Test before publishing**:
   ```bash
   npm run build && npm test
   ```

## Example: Complete Setup for New Developer

As a new developer wanting to use `@monta/glossary`:

```bash
# 1. Create GitHub PAT with read:packages scope
# (Follow steps above)

# 2. Configure npm
echo "@monta:registry=https://npm.pkg.github.com" >> ~/.npmrc
echo "//npm.pkg.github.com/:_authToken=YOUR_TOKEN" >> ~/.npmrc

# 3. Install in your project
cd your-project
npm install @monta/glossary

# 4. Use it
# See README.md for usage examples
```

## Migrating from Public npm (Future)

If you later want to publish to public npm:

1. Update `package.json`:
   ```json
   {
     "publishConfig": {
       "registry": "https://registry.npmjs.org",
       "access": "public"
     }
   }
   ```

2. Login to npm:
   ```bash
   npm login
   ```

3. Publish:
   ```bash
   npm publish
   ```

## Resources

- [GitHub Packages Documentation](https://docs.github.com/en/packages)
- [Working with npm registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry)
- [Managing PATs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [Package visibility](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)

## Support

- **Package page**: https://github.com/orgs/monta-app/packages?repo_name=library-glossary
- **Issues**: Report bugs in the GitHub repository
- **Help**: Ask in the #engineering Slack channel
