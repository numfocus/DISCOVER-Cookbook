
echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Clean tags directory
rm -rf DISCOVER/_tags/*

echo "Building English version..."
sphinx-build -b html DISCOVER/ DISCOVER/_build/html

echo "Build completed successfully"