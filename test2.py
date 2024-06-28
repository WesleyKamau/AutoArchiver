from dotenv import load_dotenv
import os

# Load environment variables from .env file
# load_dotenv()

# Retrieve values
username = os.getenv('YOUTUBE_USERNAME')
password = os.getenv('YOUTUBE_PASSWORD')

print(username, password)  # Check if values are loaded
