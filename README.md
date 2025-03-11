# Rasa Setup Guide

This guide outlines the steps to set up and run a Rasa chatbot with the required dependencies.

## Prerequisites

Make sure you have Python 3.10 installed on your system.

## Installation

1. **Upgrade `pip` and install dependencies**:
    ```bash
    python3.10 -m ensurepip --upgrade
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3.10 -m venv rasa_env
    source rasa_env/bin/activate
    ```

3. **Upgrade `pip` and install Rasa**:
    ```bash
    pip install --upgrade pip
    pip install rasa
    ```

4. **Install additional dependencies**:
    ```bash
    pip install transformers
    pip install rapidfuzz
    pip install sentence-transformers
    ```

5. **Set environment variables**:
    ```bash
    export SQLALCHEMY_SILENCE_UBER_WARNING=1
    ```

6. **Verify Rasa installation**:
    ```bash
    rasa --version
    ```

## Training
2. **Added data in yml rasa**:
    ```bash
    python3.10 questions-txt-to-json.py
    python3.10 generate_yml.py
    ```

2. **Train your Rasa model**:
    ```bash
    rasa train
    ```

## Running Rasa

1. **Start Rasa actions**:
    ```bash
    rasa run actions
    ```

2. **Start Rasa server with API**:
    ```bash
    rasa run  --cors "*" --enable-api
    ```

3. **Run Rasa with additional options (CORS, logging, etc.)**:
    ```bash
    rasa run --cors "*" --enable-api --log-file rasa_debug.log -vv
    ```

4. **Start Rasa shell for testing**:
    ```bash
    rasa shell
    rasa shell --debug
    ```
