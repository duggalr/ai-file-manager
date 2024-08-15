import os
import platform


def is_hidden(filepath):
    if platform.system() != 'Windows':
        return os.path.basename(filepath).startswith('.')
    else:
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attrs != -1 and (attrs & 2)
        except Exception:
            return False

def _is_valid_file(filepath):
    if is_hidden(filepath):
        return False
    try:
        file_extension = filepath.split('.')[-1]
        file_size_in_bytes = os.path.getsize(filepath)
        valid_file_size_bytes = 50000000 if file_extension == 'pdf' else 10000000
        return file_size_in_bytes <= valid_file_size_bytes
    except Exception as e:
        print(f"Error checking file {filepath}: {e}")
        return False

def is_valid_directory(dir_path):
    """
    Checks if the directory is a valid directory (not a virtual environment).
    A directory is considered invalid if it contains a 'pyvenv.cfg' file.
    """
    try:
        return 'pyvenv.cfg' not in os.listdir(dir_path)
    except Exception as e:
        print(f"Error checking directory {dir_path}: {e}")
        return False

def process_directory(fp, invalid_directories, valid_file_paths, invalid_file_paths):
    """
    Processes the directory recursively, filtering out invalid directories (like virtualenvs)
    and categorizing valid and invalid file paths.
    """
    try:
        directory_file_paths = os.listdir(fp)
    except Exception as e:
        print(f"Error accessing directory {fp}: {e}")
        return
    
    for fn in directory_file_paths:
        current_fn_full_path = os.path.join(fp, fn)
        
        if '.app' not in current_fn_full_path:
            if os.path.isdir(current_fn_full_path):
                # Check if the directory is valid (i.e., not a virtual environment)
                if is_valid_directory(current_fn_full_path):
                    # Recursively process the subdirectory
                    process_directory(current_fn_full_path, invalid_directories, valid_file_paths, invalid_file_paths)
                else:
                    # Mark the directory as invalid
                    invalid_directories.append(current_fn_full_path)
            else:
                # Check if the file is valid
                if _is_valid_file(current_fn_full_path):
                    valid_file_paths.append(current_fn_full_path)
                else:
                    invalid_file_paths.append(current_fn_full_path)

        else: # .app files are not valid
            invalid_file_paths.append(current_fn_full_path)

    return valid_file_paths, invalid_directories, invalid_file_paths


# # Initial directory path
# dir_path = '/Users/rahulduggal/Desktop/test_directory_three'
# invalid_directories = []
# valid_file_paths = []
# invalid_file_paths = []

# # Start processing from the initial directory path
# process_directory(
#     dir_path,
#     invalid_directories,
#     valid_file_paths,
#     invalid_file_paths
# )

# print(f"Number of Valid File Paths: {len(valid_file_paths)}")
# print(f"Number of Invalid Directories: {len(invalid_directories)}")
# print(f"Number of Invalid File Paths: {len(invalid_file_paths)}")

# # for invalid_dir in invalid_directories:
# #     print(f"Invalid Directory: {invalid_dir}")

# # for valid_file in valid_file_paths:
# #     print(f"Valid File: {valid_file}")

# # for invalid_fp in invalid_file_paths:
# #     print(f"Invalid File: {invalid_fp}")