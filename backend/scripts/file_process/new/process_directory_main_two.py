import os
import platform


VALID_EXTENSIONS = {
    '.txt', '.md', '.rst', '.csv', '.json', '.xml', '.yaml', '.yml', '.ini', '.log', '.cfg',   # Text & Config files
    '.py', '.java', '.js', '.ts', '.cpp', '.c', '.cs', '.rb', '.go', '.sh', '.bat', '.ps1', '.sql',    # Source code files
    '.html', '.htm', '.css', '.scss', '.sass', '.php', '.jsp', '.asp', '.aspx',                # Web development files
    '.pdf', '.doc', '.docx', '.odt', '.rtf',                                                   # Document files
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.ico', '.avif',                 # Image files
    '.mp3', '.wav', '.ogg', '.flac', '.m4a',                                                   # Audio files
    '.mp4', '.mkv', '.mov', '.avi', '.wmv', '.flv', '.webm',                                   # Video files
    '.zip', '.tar', '.gz', '.bz2', '.rar', '.7z',                                              # Archive files
}

def is_hidden(filepath):
    """Check if a file or directory is hidden."""
    if platform.system() != 'Windows':
        return os.path.basename(filepath).startswith('.')
    else:
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attrs != -1 and (attrs & 2)
        except Exception:
            return False

def is_system_directory(file_path):
    """Check if a directory is a system or virtual environment directory."""
    system_dirs = ['__pycache__', '.git', '.svn', '.hg', '.DS_Store', 'node_modules', 'venv', '.venv']
    return any(part in system_dirs for part in os.path.normpath(file_path).split(os.sep))

def _is_valid_file(filepath):
    """Determine if the file is valid based on size, extension, and other checks."""
    if is_hidden(filepath) or is_system_directory(filepath):
        return False
    try:
        file_extension = os.path.splitext(filepath)[-1].lower()
        if file_extension not in VALID_EXTENSIONS:
            return False
        
        # Set size limits based on file type (50MB for PDF, 10MB for others)
        file_size_in_bytes = os.path.getsize(filepath)
        valid_file_size_bytes = 50000000 if file_extension == '.pdf' else 10000000
        return file_size_in_bytes <= valid_file_size_bytes
    except Exception as e:
        print(f"Error checking file {filepath}: {e}")
        return False

def is_valid_directory(dir_path):
    """Check if a directory is a valid directory (not a virtual environment or system directory)."""
    try:
        if is_system_directory(dir_path) or is_hidden(dir_path):
            return False
        return 'pyvenv.cfg' not in os.listdir(dir_path)
    except Exception as e:
        print(f"Error checking directory {dir_path}: {e}")
        return False

def process_directory(fp, invalid_directories, valid_file_paths, invalid_file_paths):
    """Process a directory, categorizing valid and invalid files and directories."""
    try:
        directory_file_paths = os.listdir(fp)
    except Exception as e:
        print(f"Error accessing directory {fp}: {e}")
        return
    
    for fn in directory_file_paths:
        current_fn_full_path = os.path.join(fp, fn)
        
        if '.app' not in current_fn_full_path:  # Skip `.app` bundles
            if os.path.isdir(current_fn_full_path):
                if is_valid_directory(current_fn_full_path):
                    # Recursively process the subdirectory
                    process_directory(current_fn_full_path, invalid_directories, valid_file_paths, invalid_file_paths)
                else:
                    invalid_directories.append(current_fn_full_path)
            else:
                if _is_valid_file(current_fn_full_path):
                    valid_file_paths.append(current_fn_full_path)
                else:
                    invalid_file_paths.append(current_fn_full_path)
        else:
            invalid_file_paths.append(current_fn_full_path)

    return valid_file_paths, invalid_directories, invalid_file_paths
