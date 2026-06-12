import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# List the keys you expect to see in your .env file for PostgreSQL
db_keys = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']

print("--- Checking Environment Variables ---")
for key in db_keys:
    val = os.getenv(key)
    # Mask the password in output for safety
    display_val = "********" if "PASSWORD" in key and val else val
    print(f"{key}: {display_val}")

if all(os.getenv(k) for k in db_keys):
    print("\nSUCCESS: All PostgreSQL variables found.")
else:
    print("\nERROR: Some variables are missing.")