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
    file_extension = filepath.split('.')[-1]
    file_size_in_bytes = os.path.getsize(filepath)
    valid_file_size_bytes = 50000000 if file_extension == 'pdf' else 10000000
    return file_size_in_bytes <= valid_file_size_bytes

def is_valid_directory(dir_path):
    """
    Checks if the directory is a valid directory (not a virtual environment).
    A directory is considered invalid if it contains a 'pyvenv.cfg' file.
    """
    return 'pyvenv.cfg' not in os.listdir(dir_path)

def process_directory(fp, invalid_directories, valid_file_paths, invalid_file_paths):
    """
    Processes the directory, filtering out invalid directories (like virtualenvs)
    and categorizing valid and invalid file paths.
    """
    # invalid_directories = []
    # valid_file_paths = []
    # invalid_file_paths = []
    
    # List all files and directories in the given path
    directory_file_paths = os.listdir(fp)
    
    for fn in directory_file_paths:
        current_fn_full_path = os.path.join(fp, fn)
        
        if os.path.isdir(current_fn_full_path):
            # Check if the directory is valid (i.e., not a virtual environment)
            if is_valid_directory(current_fn_full_path):

                print(f"VALID DIRECTORY: {current_fn_full_path}")

                # Iterate through files in this valid directory
                for inner_fn in os.listdir(current_fn_full_path):
                    tmp_full_fn_path = os.path.join(current_fn_full_path, inner_fn)
                    if _is_valid_file(tmp_full_fn_path):
                        valid_file_paths.append(tmp_full_fn_path)
                    else:
                        invalid_file_paths.append(tmp_full_fn_path)
            else:
                # Mark the directory as invalid
                invalid_directories.append(current_fn_full_path)
        else:
            # Check if the file in the root directory is valid
            if _is_valid_file(current_fn_full_path):
                valid_file_paths.append(current_fn_full_path)
            else:
                invalid_file_paths.append(current_fn_full_path)
    
    # Output results
    print(f"Valid File Paths: {valid_file_paths}")
    print(f"Invalid Directories: {invalid_directories}")
    print(f"Invalid File Paths: {invalid_file_paths}")

    return valid_file_paths, invalid_directories, invalid_file_paths



dir_path = '/Users/rahulduggal/Desktop/test_directory_four'
invalid_directories = []
valid_file_paths = []
invalid_file_paths = []
process_directory(
    dir_path,
    invalid_directories, 
    valid_file_paths, 
    invalid_file_paths
)
