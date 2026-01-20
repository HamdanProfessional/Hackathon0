import re

config_path = "/root/AI_EMPLOYEE_APP/process-manager/pm2.cloud.config.js"

with open(config_path, 'r') as f:
    content = f.read()

# Replace process.env.ANTHROPIC_API_KEY with the actual key
content = re.sub(r"process\.env\.ANTHROPIC_API_KEY", "'c414057ceccd4e8dae4ae3198f760c7a.BW9M3G4m8ers9woM'", content)

with open(config_path, 'w') as f:
    f.write(content)

print("Config updated successfully")
