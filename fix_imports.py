import os

# Set your project directory
PROJECT_DIR = "core"

for root, dirs, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            modified = False
            with open(filepath, 'w', encoding='utf-8') as f:
                for line in lines:
                    if "from core." in line:
                        line = line.replace("from core.", "from ")
                        modified = True
                    f.write(line)

            if modified:
                print(f"✅ Fixed imports in: {filepath}")
