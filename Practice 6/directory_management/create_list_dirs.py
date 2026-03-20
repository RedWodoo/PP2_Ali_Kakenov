import os

path = os.path.join("data", "projects", "practice_06")
os.makedirs(path, exist_ok=True)
print(f"Created directory: {path}")

for name in ["notes.txt", "script.py", "readme.md", "data.txt"]:
    with open(os.path.join(path, name), "w") as f:
        f.write("Sample content")


print("\nItems in directory:")
content = os.listdir(path)
for item in content:
    print(f"- {item}")

extension = ".txt"
txt_files = [f for f in os.listdir(path) if f.endswith(extension)]
print(f"\nFiles with extension {extension}:")
print(txt_files)