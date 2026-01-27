import re
import os
import sys

config_path = "/root/AI_EMPLOYEE_APP/process-manager/pm2.cloud.config.js"

# Get API key from environment variable
api_key = os.getenv('GLM_API_KEY', '')
if not api_key:
    print("Error: GLM_API_KEY environment variable not set")
    sys.exit(1)

try:
    with open(config_path, 'r') as f:
        content = f.read()

    # Replace process.env.ANTHROPIC_API_KEY with the actual key from env
    content = re.sub(r"process\.env\.ANTHROPIC_API_KEY", f"'{api_key}'", content)

    with open(config_path, 'w') as f:
        f.write(content)

    print("Config updated successfully")
except FileNotFoundError:
    print(f"Error: Config file not found at {config_path}")
    sys.exit(1)
except Exception as e:
    print(f"Error updating config: {e}")
    sys.exit(1)
