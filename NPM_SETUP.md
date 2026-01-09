# NPM Setup and Publishing Guide

This guide walks you through setting up and publishing the `@monta/glossary` package to npm.

## Prerequisites

1. **npm account**: Create one at [npmjs.com](https://www.npmjs.com/signup)
2. **npm CLI**: Already installed with Node.js
3. **Organization access**: You need access to the `@monta` organization on npm

## One-Time Setup

### 1. Login to npm

```bash
npm login
```

Enter your npm credentials when prompted.

### 2. Verify Login

```bash
npm whoami
```

This should display your npm username.

### 3. Check Organization Access

```bash
npm org ls @monta
```

If you don't have access, request it from the organization admin.

## Building the Package

Before publishing, always build and test:

```bash
# Install dependencies
npm install

# Build TypeScript to JavaScript
npm run build

# Run tests
npm test

# Verify build output
ls -la dist/
```

You should see:
- `dist/index.js` - Compiled JavaScript
- `dist/index.d.ts` - TypeScript type definitions

## Publishing to npm

### First Time Publishing

```bash
# Make sure everything is committed
git status

# Publish to npm (public access for scoped package)
npm publish --access public
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

3. **Publish to npm**:
   ```bash
   npm publish --access public
   ```

## Package Configuration

The `package.json` is configured for npm publishing:

```json
{
  "name": "@monta/glossary",
  "version": "1.0.0",
  "main": "dist/index.js",          // Entry point for CommonJS
  "types": "dist/index.d.ts",        // TypeScript types
  "scripts": {
    "prepublishOnly": "npm run build"  // Auto-build before publish
  }
}
```

### What Gets Published

The package includes:
- ✅ `dist/` - Compiled JavaScript and type definitions
- ✅ `package.json`
- ✅ `README.md`
- ❌ `src/` - Source TypeScript (not needed in published package)
- ❌ `test/` - Tests (not needed in published package)
- ❌ `node_modules/` - Dependencies (automatically excluded)

To customize, add a `.npmignore` file or use the `files` field in package.json.

## Verifying the Published Package

After publishing, verify it's available:

```bash
# Check on npm registry
npm view @monta/glossary

# Install in a test project
npm install @monta/glossary

# Test the package
node -e "const { Glossary } = require('@monta/glossary'); console.log('Works!');"
```

## Testing Before Publishing

To test the package locally before publishing:

```bash
# Build the package
npm run build

# Create a tarball (simulates npm publish)
npm pack

# This creates: monta-glossary-1.0.0.tgz

# Install in a test project
cd /path/to/test-project
npm install /path/to/glossary/monta-glossary-1.0.0.tgz

# Or use npm link
cd /path/to/glossary
npm link
cd /path/to/test-project
npm link @monta/glossary
```

## Publishing Workflow

### Standard Release Process

1. **Make changes and test**:
   ```bash
   npm install
   npm test
   npm run build
   ```

2. **Update version**:
   ```bash
   npm version patch  # or minor, or major
   ```

3. **Commit and push**:
   ```bash
   git push && git push --tags
   ```

4. **Publish to npm**:
   ```bash
   npm publish --access public
   ```

5. **Verify**:
   ```bash
   npm view @monta/glossary
   ```

### Quick Publish (for patches)

```bash
npm run build && npm version patch && git push --tags && npm publish --access public
```

## Versioning Guidelines

Follow [Semantic Versioning](https://semver.org/):

- **Patch** (1.0.X): Bug fixes, no API changes
  - Example: Fix text normalization edge case

- **Minor** (1.X.0): New features, backwards compatible
  - Example: Add new `getTermById()` method

- **Major** (X.0.0): Breaking changes
  - Example: Change all methods from sync to async (like v1.0.0)

## Troubleshooting

### "Package name taken"

If `@monta/glossary` is taken, options:
1. Request access to the @monta organization
2. Use a different scope: `@your-org/glossary`
3. Use unscoped name: `monta-glossary`

### "You must be logged in"

```bash
npm login
npm whoami  # verify
```

### "No permission to publish"

You need to be added to the `@monta` organization:
```bash
npm org ls @monta  # check access
```

Contact the organization admin to add you.

### "prepublishOnly script failed"

The build failed. Check for TypeScript errors:
```bash
npm run build
```

Fix any compilation errors before publishing.

## Best Practices

1. ✅ **Always test before publishing**
   ```bash
   npm test
   ```

2. ✅ **Build before publishing** (automated via `prepublishOnly`)
   ```bash
   npm run build
   ```

3. ✅ **Update version appropriately**
   ```bash
   npm version patch/minor/major
   ```

4. ✅ **Keep README updated** with latest examples

5. ✅ **Tag releases in git**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push --tags
   ```

6. ✅ **Test the published package** in a real project

## Automated Publishing (CI/CD)

To automate publishing with GitHub Actions:

1. **Generate npm token**:
   - Go to [npmjs.com/settings/tokens](https://www.npmjs.com/settings/tokens)
   - Create "Automation" token
   - Copy the token

2. **Add to GitHub Secrets**:
   - Go to your repo → Settings → Secrets
   - Add secret: `NPM_TOKEN`

3. **Create `.github/workflows/publish.yml`**:
   ```yaml
   name: Publish to npm

   on:
     push:
       tags:
         - 'v*'

   jobs:
     publish:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-node@v3
           with:
             node-version: '20'
             registry-url: 'https://registry.npmjs.org'
         - run: npm install
         - run: npm test
         - run: npm run build
         - run: npm publish --access public
           env:
             NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
   ```

Now publishing is automatic when you push a tag:
```bash
npm version patch
git push --tags
```

## Support

- **npm docs**: [docs.npmjs.com](https://docs.npmjs.com/)
- **Package page**: [npmjs.com/package/@monta/glossary](https://www.npmjs.com/package/@monta/glossary)
- **Issues**: Report bugs in the GitHub repository
