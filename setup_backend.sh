#!/bin/bash

# Step 1: Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 2: Install required packages
echo "Installing Python packages..."
pip install -r requirements.txt

# Step 3: Create .env file and prompt for OpenAI API Key
echo "Creating .env file..."

read -p "Enter your OpenAI API Key: " openai_api_key

cat <<EOT > .env
OPENAI_KEY=$openai_api_key
AUTH0_DOMAIN='dev-2qo458j0ehopg3ae.us.auth0.com'
API_IDENTIFIER='https://dev-2qo458j0ehopg3ae.us.auth0.com/api/v2/'
ALGORITHMS=['RS256']
EOT

# Step 4: Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

# Step 5: Start Django server
echo "Starting Django server on localhost:8000..."
python manage.py runserver