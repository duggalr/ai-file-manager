# AI File Companion - Self-Hosted Setup

AI File Companion is an AI-powered file organizer that automatically organizes files into folders based on their content and metadata. 

This guide will help you self-host the AI File Companion on your local machine using Python and Electron.


## Prerequisites

Before starting, make sure you have the following installed on your machine:

- Git
- Python 3.8+ and pip
- Node.js and npm
- PostgreSQL


## Setup Instructions

Follow these steps to get the AI File Companion up and running:


### 1. Clone the Repositories

You need to clone two repositories to your local machine.

```
git clone https://github.com/duggalr/ai-file-manager.git
git clone https://github.com/duggalr/ai-file-manager-electron.git
```

### 2. Set Up the Backend

Navigate to the backend repository and run the provided shell script to set up the backend environment.

```
cd ai-file-manager
chmod +x setup_backend.sh
./setup_backend.sh

```

**This script will:**
- Create a Python virtual environment.
- Install the required Python packages from requirements.txt.
- Set up a local PostgreSQL database.
- Initialize environment variables in a .env file.
- Ask for your OPENAI_API_KEY and save it to the .env file.
- Run Django migrations.
- Start the Django server on localhost:8000.


### 3. Set up Redis + Celery Worker

In a new terminal window, run the following command:

```
redis-server
```

Then, in another new terminal window, run the following:
```
cd ai-file-manager
source venv/bin/activate
python -m celery -A ai_file_manager worker
```

This will setup the celery worker with a redis message queue.


### 4. Set Up the Electron App

In a new terminal window, navigate to the Electron repository and run the provided shell script to set up the frontend environment.

```
cd ../ai-file-manager-electron
chmod +x setup_electron.sh
./setup_electron.sh
```

**This script will:**
- Install the necessary Node.js packages.
- Run the Electron app locally.


### 5. Congrats, the application should now run!

After both setups are complete, your AI File Companion should be running successfully:
- Backend server: http://localhost:8000
- Electron frontend: Launches automatically after the setup script.

---

### Notes

- Make sure PostgreSQL is running on your machine.
- Ensure the OPENAI_API_KEY is correct for the AI functionality to work.


### Contributing

- Feel free to submit issues, fork the repository, and make pull requests.