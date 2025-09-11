# DISCOVER Cookbook Version Release Guide

This guide walks you through the process of releasing a new version of the DISCOVER Cookbook. Follow these steps to ensure a smooth update when a new version is ready.

## Step 1: Create a X.Y Version Tag and X.Y-translations Branch

First, create a X.Y version tag and a X.Y-translations branch specifically for the new version. This naming pattern is important - the system automatically detects branches ending with `-translations` and uses the prefix as the version number.

```bash
# Create and checkout a new branch
git checkout -b X.Y-translations

# Push the branch to GitHub
git push origin X.Y-translations
```

## Step 2: Update Version Configuration Files

### Update the Versions List

Edit `DISCOVER/_static/versions.json` to include your new version.

```json
[
    {
        "version": "dev",
        "url": "https://discover-cookbook.numfocus.org/dev/"
    },
    {
        "version": "X.Y",
        "url": "https://discover-cookbook.numfocus.org/X.Y/",
        "preferred": true
    },
    {
        "version": "2.0",
        "url": "https://discover-cookbook.numfocus.org/2.0/"
    },
    {
        "version": "1.0",
        "url": "https://discover-cookbook.numfocus.org/1.0/"
    }
]
```

Make sure to:

  * Add your new version entry.
  * Move the `"preferred": true` flag to the new version.
  * Keep the order from newest to oldest.

### Update Language Settings

Edit `DISCOVER/_static/languages.json` to manage available languages.

```json
[
    {
        "code": "en",
        "name_local": "English",
        "direction": "ltr"
    },
    {
        "code": "es",
        "name_local": "Español",
        "direction": "ltr"
    },
    {
        "code": "hi",
        "name_local": "हिन्दी",
        "direction": "ltr"
    }
]
```

To manage language visibility and preferences:

  * **Add a new language**: Add a new entry with the language code, local name, and text direction.
  * **Make a language visible**: Remove the `"hidden": true` property from any language you want to show.
  * **Hide a language**: Add `"hidden": true` to languages that aren't ready for public use.
  * **Set default language**: The first non-hidden language is typically used as the default.

For example, to unhide Spanish and add Hindi:

```json
[
    {
        "code": "en",
        "name_local": "English",
        "direction": "ltr"
    },
    {
        "code": "es",
        "name_local": "Español",
        "direction": "ltr"
        // "hidden": true was removed to make Spanish visible
    },
    {
        "code": "hi",
        "name_local": "हिन्दी",
        "direction": "ltr"
        // New language added
    }
]
```

> **Note**: When you add a new language, ensure all documentation files have been translated and placed in the appropriate directory in the `locales/` folder (e.g., `locales/hi/LC_MESSAGES/`). See the [`Translation.md`](Translation.md) file for how to update translatable sources.

## Step 3: Update the Landing Page

Edit `index.html` to reflect the new version in these sections:

### Update the Read the Cookbook Button (around line 60)

```html
<!-- Update this URL to point to your new version -->
<a href="https://discover-cookbook.numfocus.org/X.Y/en/" class="btn btn-success btn-lg"><i class="bi bi-book"></i> Read the Cookbook</a>
```

### Update the Latest Version Section (around line 98)

Replace the existing "Latest" version card with your new version:

```html
<!-- Latest Version Card - Replace X.Y with your actual version number -->
<div class="col-lg-6">
    <div class="bg-success bg-opacity-10 p-4 rounded border border-success border-opacity-25 h-100">
        <div class="d-flex align-items-center mb-3">
            <i class="bi bi-star-fill text-warning me-2"></i>
            <!-- UPDATE: Replace X.Y with your version number (e.g., Version 3.0) -->
            <h4 class="mb-0">Version X.Y</h4>
            <span class="badge bg-success ms-2">Latest</span>
        </div>
        <p class="text-muted mb-3">The current stable release, recommended for all users. Includes the latest best practices and comprehensive updates.</p>
        <div class="d-flex flex-wrap gap-2">
            <!-- UPDATE: Replace X.Y with your version number in all URLs below -->
            <a href="https://discover-cookbook.numfocus.org/X.Y/en" class="btn btn-success btn-sm">English</a>
            <a href="https://discover-cookbook.numfocus.org/X.Y/es" class="btn btn-outline-secondary btn-sm">Español</a>
            <!-- ADD: New language link (add this line if Hindi is available) -->
            <a href="https://discover-cookbook.numfocus.org/X.Y/hi" class="btn btn-outline-secondary btn-sm">हिन्दी</a>
        </div>
    </div>
</div>
```

### Move the Previous Version to Second Position (around line 116)

Find the current "Latest" version and change it to look like this:

```html
<!-- Previous Version Card - This should be the version that was previously "Latest" -->
<div class="col-lg-6">
    <div class="p-4 rounded h-100 border">
        <div class="d-flex align-items-center mb-3">
            <i class="bi bi-archive text-muted me-2"></i>
            <!-- UPDATE: This should show the previous version number (e.g., Version 2.0) -->
            <h4 class="mb-0">Version 2.0</h4>
        </div>
        <p class="text-muted mb-3">Previous stable release, archived for reference.</p>
        <div class="d-flex flex-wrap gap-2">
            <!-- Keep existing language links for the previous version -->
            <a href="https://discover-cookbook.numfocus.org/2.0/en" class="btn btn-outline-secondary btn-sm">English</a>
            <a href="https://discover-cookbook.numfocus.org/2.0/es" class="btn btn-outline-secondary btn-sm">Español</a>
            <!-- Only list languages that were supported in the previous version -->
        </div>
    </div>
</div>
```
## Step 4: Commit and Push Changes

```bash
# Add your changes
git add .

# Commit with a clear message
git commit -m "Release X.Y: Update version references and language settings"

# Push to the translation branch
git push origin X.Y-translations
```

## Step 5: Create a X.Y Version Tag

```bash
# Create a tag for the release
git tag -a X.Y -m "Release version X.Y"

# Push the tag to GitHub
git push origin X.Y
```

## Step 6: Wait for Deployment

The GitHub Actions workflow will:

  * Detect your new branch and tag.
  * Build the documentation for each language.
  * Deploy to the correct version path.
  * Create redirect files.

Check the **GitHub Actions** tab to monitor progress.

## Step 7: Merge Back to Main

After the release is deployed and verified:

```bash
# Switch back to main
git checkout main

# Merge the changes
git merge X.Y-translations

# Push the updated main branch
git push origin main
```

## Step 8: Verify the Release

Check these links to confirm everything is working:

  * **Main version**: `https://discover-cookbook.numfocus.org/X.Y/en/`
  * **Landing page**: `https://discover-cookbook.numfocus.org/`
  * Version switcher works in the documentation.
  * All language options appear correctly in the language switcher.
  * Confirm a banner appears on old versions linking to the