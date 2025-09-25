import json
import sys

file1 = "subset-200.jsonl"
fileclean = "out-8_cleaned.jsonl"

def check_for_error(file_path):
    print(f"## check_for_error: {file_path}...")
    with open(file_path) as f:
        for i, line in enumerate(f, 1):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON error on line {i}: {e}")
                print(line)
                break
                # .' "]}
        print(f"✅ OK! ")
        print (f"# P.S. Delete the original file and rename the cleaned file to original name after fixing!")

# check_for_error(file1)
check_for_error(fileclean)

def check_and_resave(input_file):
    fname = input_file.split("/")[-1].split(".")[0]
    output_file = fname+"_cleaned.jsonl"
    error_file = fname+"_error_lines.jsonl"
    corrected_file = fname+"_corrected_lines.jsonl"
    print (f"result: {output_file}, {error_file}")
    print (f"check_and_resave: {input_file}..")
    with open(input_file, 'r', encoding='utf-8') as infile, \
        open(output_file, 'w', encoding='utf-8') as outfile, \
        open(corrected_file, 'w', encoding='utf-8') as corrfile, \
        open(error_file, 'w', encoding='utf-8') as errfile:

        for line_number, line in enumerate(infile, 1):
            try:
                json.loads(line)  # Try parsing to check validity
                outfile.write(line)  # If valid, write to output
            except json.JSONDecodeError as e:
                print(f"[ERROR] Line {line_number}: {e}")
                errfile.write(f"Line {line_number}: {e}\n{line}\n")

# check_and_resave(file8)

def add_corrected_lines(file_path):
    fname = file_path.split("/")[-1].split(".")[0]
    fname="out-8"
    cleaned_file = fname+"_cleaned.jsonl"
    corrected_file = fname+"_corrected_lines.jsonl"  # Your manually fixed lines
    # corrected_file = fname+"_error_lines.jsonl"  # Your manually fixed lines
    print (f"add_corrected_lines: {cleaned_file} from {corrected_file}..")
    # sys.exit()
    with open(corrected_file, 'r', encoding='utf-8') as infile, \
        open(cleaned_file, 'a', encoding='utf-8') as outfile:

        for line_number, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                # Validate the line is valid JSON
                json.loads(line)
                # Append to cleaned file
                outfile.write(line + '\n')
                print(f"[APPENDED] Line {line_number}")
            except json.JSONDecodeError as e:
                print(f"[SKIPPED] Line {line_number}: Invalid JSON → {e}")

# add_corrected_lines(file8)

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def find_duplicates(file1, file2):
    print(f"## find_duplicates: {file1} {file2}...")
    data1 = load_jsonl(file1)
    data2 = load_jsonl(file2)

    # Convert each JSON object to a string representation for hashing/comparison
    set1 = set(json.dumps(obj, sort_keys=True) for obj in data1)
    set2 = set(json.dumps(obj, sort_keys=True) for obj in data2)

    duplicates = set1 & set2  # Intersection of both sets
    return [json.loads(line) for line in duplicates]


# duplicates = find_duplicates(file5, filex)

# print(f"Found {len(duplicates)} duplicate lines:")
# for dup in duplicates:
#     print(dup)



def fix_last_line(file_path):
    print(f"## fix_last_line: {file_path}...")
    fixed_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                obj = json.loads(line)
                fixed_lines.append(json.dumps(obj))
            except json.JSONDecodeError as e:
                print(f"❌ JSON error on line {i}: {e}")
                marker = "licenses.' "
                idx = line.find(marker)
                if idx != -1:
                    # Replace from marker to end of line
                    fixed_line = line[:idx] + "licenses.' \"]}\n"
                    try:
                        obj = json.loads(fixed_line)
                        print(f"✅ Fixed line {i} by replacing from '{marker}' to end")
                        fixed_lines.append(json.dumps(obj))
                    except json.JSONDecodeError as e2:
                        print(f"⚠️ Failed to fix line {i} after replacement: {e2}")
                        # If unfixable, you can choose to skip or append original broken line
                        # fixed_lines.append(line.strip())
                else:
                    print(f"⚠️ Marker '{marker}' not found in line {i}. Skipping fix.")
                    # Decide if you want to keep the broken line or skip
                    # fixed_lines.append(line.strip())

    # Overwrite original file
    with open(file_path, 'w', encoding='utf-8') as f:
        for l in fixed_lines:
            f.write(l + '\n')

    print(f"✅ Finished. Original file overwritten: {file_path}")

# fix_last_line(file5)
