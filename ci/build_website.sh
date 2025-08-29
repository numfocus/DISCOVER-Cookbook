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

# Build the documentation
echo "Building $LANGUAGE version..."
WEBSITE_VERSION="$VERSION" WEBSITE_LANGUAGE="$LANGUAGE" sphinx-build -b html DISCOVER/ DISCOVER/_build/html
