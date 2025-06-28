import os

def write_file(working_directory, file_path, content):
    try:
        fullpath = "/".join([working_directory, file_path])
        working_path = os.path.abspath(fullpath)
        working_abs_path = os.path.abspath(working_directory)

        if not working_path.startswith(working_abs_path):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        wo = os.path.dirname(working_path)
        if not os.path.exists(wo):
            os.makedirs(wo)
        
        with open(working_path, "w") as file:
            file.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    except Exception as err:
        return f"Error:{err}"
