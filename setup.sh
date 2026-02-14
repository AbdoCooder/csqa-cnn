#!/bin/bash

echo "🚀 Setting up Streamlit Dashboard for deployment..."

# Create .streamlit directory if it doesn't exist
mkdir -p ~/.streamlit/

# Create credentials file
echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

# Create config file
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = \$PORT\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
" > ~/.streamlit/config.toml

echo "✅ Setup complete!"
