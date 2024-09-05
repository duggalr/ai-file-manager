#!/bin/bash

# Function to check the OS
check_os() {
  case "$(uname -s)" in
    Linux*)   os="linux";;
    Darwin*)  os="mac";;
    CYGWIN*|MINGW32*|MSYS*|MINGW*) os="windows";;
    *)        os="unknown";;
  esac
}

# Step 1: Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 2: Install required packages
echo "Installing Python packages..."
pip install -r requirements.txt

# Step 3: Set up PostgreSQL database
echo "Setting up local PostgreSQL database..."
check_os

# Default database credentials
DB_NAME="ai_file_organizer"
DB_USER="postgres"
DB_PASSWORD=""
DB_HOST="localhost"
DB_PORT="5432"

# OS-specific PostgreSQL commands
if [ "$os" == "linux" ] || [ "$os" == "mac" ]; then
  # Check if PostgreSQL is running
  if ! pg_isready -q; then
    echo "PostgreSQL is not running. Please start PostgreSQL and rerun the script."
    exit 1
  fi

  # Create the database
  PSQL_CMD="psql -U $DB_USER -h $DB_HOST -c"
  $PSQL_CMD "DROP DATABASE IF EXISTS $DB_NAME;"
  $PSQL_CMD "CREATE DATABASE $DB_NAME;"
  
elif [ "$os" == "windows" ]; then
  # Check if PostgreSQL is running (Windows specific)
  if ! pg_isready -q; then
    echo "PostgreSQL is not running. Please start PostgreSQL and rerun the script."
    exit 1
  fi

  # Create the database (Windows PowerShell command)
  PSQL_CMD="psql -U $DB_USER -h $DB_HOST -c"
  $PSQL_CMD "DROP DATABASE IF EXISTS $DB_NAME;"
  $PSQL_CMD "CREATE DATABASE $DB_NAME;"

else
  echo "Unsupported operating system."
  exit 1
fi

# Step 4: Create .env file and prompt for OpenAI API Key
echo "Creating .env file..."
echo "DB_NAME=$DB_NAME" > .env
echo "DB_USER=$DB_USER" >> .env
echo "DB_PASSWORD=$DB_PASSWORD" >> .env
echo "DB_HOST=$DB_HOST" >> .env
echo "DB_PORT=$DB_PORT" >> .env

read -p "Enter your OpenAI API Key: " openai_api_key
echo "OPENAI_API_KEY=$openai_api_key" >> .env

# Step 5: Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

# Step 6: Start Django server
echo "Starting Django server on localhost:8000..."
python manage.py runserver