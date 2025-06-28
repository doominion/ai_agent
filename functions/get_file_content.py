import os

def get_file_content(working_directory, file_path):
    try:
        fullpath = "/".join([working_directory, file_path])
        working_path = os.path.abspath(fullpath)
        working_abs_path = os.path.abspath(working_directory)

        if not working_path.startswith(working_abs_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(working_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(working_path, "r") as file:
            return file.read(10000)
    except Exception as err:
        return f"Error:{err}"
