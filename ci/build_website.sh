
echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Clean tags directory
rm -rf DISCOVER/_tags/*

echo "Building English version..."
sphinx-build -b html DISCOVER/ DISCOVER/_build/html


# Copy root level files if they exist
if [ -f "DISCOVER/_static/404.html" ]; then
  cp DISCOVER/_static/404.html DISCOVER/_build/html/
fi

if [ -f "DISCOVER/_static/index.html" ]; then
  cp DISCOVER/_static/index.html DISCOVER/_build/html/
fi

echo "Build completed successfully"