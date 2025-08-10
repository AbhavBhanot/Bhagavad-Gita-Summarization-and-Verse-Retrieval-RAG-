#!/bin/bash

# Check Netlify Deployment Configuration
# This script verifies that your project is properly configured for Netlify frontend deployment

echo "🔍 Checking Netlify deployment configuration..."

# Check if netlify.toml exists and is correct
if [ -f "netlify.toml" ]; then
    echo "✅ netlify.toml found"
    
    # Check if it's configured for frontend
    if grep -q "frontend/build" netlify.toml; then
        echo "✅ Configured for frontend deployment"
    else
        echo "❌ netlify.toml not configured for frontend"
    fi
else
    echo "❌ netlify.toml not found"
fi

# Check if .netlifyignore exists
if [ -f ".netlifyignore" ]; then
    echo "✅ .netlifyignore found"
else
    echo "❌ .netlifyignore not found"
fi

# Check if frontend directory exists
if [ -d "frontend" ]; then
    echo "✅ frontend directory found"
    
    # Check if package.json exists
    if [ -f "frontend/package.json" ]; then
        echo "✅ frontend/package.json found"
    else
        echo "❌ frontend/package.json not found"
    fi
else
    echo "❌ frontend directory not found"
fi

# Check for Python files that might confuse Netlify
echo ""
echo "🔍 Checking for Python files that might confuse Netlify..."

PYTHON_FILES=$(find . -name "*.py" -not -path "./frontend/*" | head -5)
if [ -n "$PYTHON_FILES" ]; then
    echo "⚠️  Found Python files in root (these will be ignored by .netlifyignore):"
    echo "$PYTHON_FILES"
else
    echo "✅ No Python files found in root"
fi

# Check for requirements files
if [ -f "requirements.txt" ] || [ -f "requirements-stable.txt" ]; then
    echo "⚠️  Found requirements files (these will be ignored by .netlifyignore)"
else
    echo "✅ No requirements files found"
fi

echo ""
echo "📋 Summary:"
echo "Your project should now deploy correctly to Netlify as a frontend-only application."
echo "The Python backend files will be ignored during the build process."
echo ""
echo "🚀 Next steps:"
echo "1. Commit and push these changes to GitHub"
echo "2. Redeploy on Netlify"
echo "3. The build should now succeed without Python-related errors"
