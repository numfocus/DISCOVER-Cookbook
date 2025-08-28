#!/usr/bin/env bash
echo "Starting build process..."

# Get parameters with defaults 
VERSION=${VERSION:-${1:-"dev"}}
LANGUAGE=${LANGUAGE:-${2:-"en"}}

echo "Building version: $VERSION, language: $LANGUAGE"

# Install dependencies
pip install -r requirements.txt

# Clean tags directory
rm -rf DISCOVER/_tags/*


echo "Building $LANGUAGE version..."
WEBSITE_VERSION="$VERSION" WEBSITE_LANGUAGE="$LANGUAGE" sphinx-build -b html DISCOVER/ DISCOVER/_build/html


# Install dependencies
pip install -r requirements.txt
pip install sphinx-intl

# Build English site
sphinx-build -b html DISCOVER/ DISCOVER/_build/html -D language=en

# Build Spanish site (translations live in locales/es/)
sphinx-build -b html DISCOVER/ DISCOVER/_build/html/es -D language=es