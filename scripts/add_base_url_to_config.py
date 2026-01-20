#!/usr/bin/env python3
import re

config_path = "/root/AI_EMPLOYEE_APP/process-manager/pm2.cloud.config.js"

with open(config_path, 'r') as f:
    content = f.read()

# Add ANTHROPIC_BASE_URL after ANTHROPIC_API_KEY line
content = re.sub(
    r"('ANTHROPIC_API_KEY': 'c414057ceccd4e8dae4ae3198f760c7a\.BW9M3G4m8ers9woM',)",
    r"\1,\n        'ANTHROPIC_BASE_URL': 'https://api.z.ai/api/coding/paas/v4'",
    content
)

with open(config_path, 'w') as f:
    f.write(content)

print("Config updated with base URL")
