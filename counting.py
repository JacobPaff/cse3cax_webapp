import os

def count_lines_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return sum(1 for line in file)

def count_lines_in_folder(folder_path):
    total_lines = {"json": 0, "py": 0, "html": 0}
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.json', '.py', '.html')):
                file_path = os.path.join(root, file)
                line_count = count_lines_in_file(file_path)
                file_ext = file.split('.')[-1]
                total_lines[file_ext] += line_count
                print(f"{file}: {line_count} lines")
    
    return total_lines

folder_path = input("Enter the folder path: ")
line_counts = count_lines_in_folder(folder_path)

print("\nSummary:")
for ext, count in line_counts.items():
    print(f"Total {ext.upper()} files: {count} lines")