import sys

filepath = "src/main.ts"
with open(filepath, "r") as f:
    content = f.read()

# Replace the setTimeout after spawn_fresh_engine
old_code = """                    await invoke('spawn_fresh_engine', {
                        projectPath: activeProject,
                        engine: 'agy',
                    })
                    await new Promise((resolve) => setTimeout(resolve, 500))"""

new_code = """                    await invoke('spawn_fresh_engine', {
                        projectPath: activeProject,
                        engine: 'agy',
                    })
                    await new Promise((resolve) => setTimeout(resolve, 3000))"""

content = content.replace(old_code, new_code)

with open(filepath, "w") as f:
    f.write(content)
print("Updated main.ts successfully")
