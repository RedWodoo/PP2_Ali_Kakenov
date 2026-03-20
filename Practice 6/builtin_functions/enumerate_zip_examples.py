students = ["Alice", "Bob", "Charlie", "David"]
scores = [85, 92, 78, 95]

print("Student Rankings:")
for index, name in enumerate(students, start=1):
    print(f"{index}. {name}")

print("\nStudent Scores:")
combined_data = list(zip(students, scores))
for name, score in zip(students, scores):
    print(f"Student: {name} | Score: {score}")

mixed_data = "1250"
print(f"\nInitial value: '{mixed_data}' (Type: {type(mixed_data).__name__})")

if isinstance(mixed_data, str):

    converted_data = int(mixed_data)
    print(f"Converted value: {converted_data} (Type: {type(converted_data).__name__})")

print(f"Is 'converted_data' an integer? {type(converted_data) == int}")