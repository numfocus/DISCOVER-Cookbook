
echo "Starting build process..."

# Get parameters with defaults 
VERSION=${1:-"dev"}
LANGUAGE=${2:-"en"}

echo "Building version: $VERSION, language: $LANGUAGE"

# Install dependencies
pip install -r requirements.txt

# Clean tags directory
rm -rf DISCOVER/_tags/*

echo "Building $LANGUAGE version..."
sphinx-build -b html \
  -D version="$VERSION" \
  -D language="$LANGUAGE" \
  DISCOVER/ DISCOVER/_build/html

# Copy root level files if they exist
if [ -f "DISCOVER/_static/404.html" ]; then
  cp DISCOVER/_static/404.html DISCOVER/_build/html/
fi

if [ -f "DISCOVER/_static/index.html" ]; then
  cp DISCOVER/_static/index.html DISCOVER/_build/html/
fi

echo "Build completed successfully: $VERSION/$LANGUAGE"