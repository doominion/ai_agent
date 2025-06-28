import os

def get_files_info(working_directory, directory=None):
    try:
        if directory is None:
            directory = "."
        fullpath = "/".join([working_directory, directory])
        working_path = os.path.abspath(fullpath)
        working_abs_path = os.path.abspath(working_directory)

        if not working_path.startswith(working_abs_path):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
            
        if not os.path.isdir(working_path):
            return f'Error: "{directory}" is not a directory'

        files = os.listdir(working_path)
        res = []
        for file in files:
            abs_path = os.path.join(working_path, file)
            res.append(f"- {file}: file_size={os.path.getsize(abs_path)}, is_dir={os.path.isdir(abs_path)}")

        return "\n".join(res)

    except Exception as err:
        return f"Error:{err}"
