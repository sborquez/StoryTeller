import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


# This is the main entry point of the application
print("Hello from story_teller/__main__.py")


# Print environment variables
print("Environment variables:")
valid_env_vars = [
    "STORYTELLER_LOGS_DIR",
    "STORYTELLER_DATA_DIR",
    "STORYTELLER_OPENAI_API_KEY",
    "STORYTELLER_GUI_WIDTH",
    "STORYTELLER_GUI_HEIGHT",
    "STORYTELLER_GUI_FULLSCREEN",
]

for env_var in valid_env_vars:
    print(f"{env_var}={os.environ.get(env_var)}")