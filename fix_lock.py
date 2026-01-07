import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer lock_states[env_name]["locked"] par lock_states[env_name]
content = content.replace('lock_states[env_name]["locked"]', 'lock_states[env_name]')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Remplacement effectué")
