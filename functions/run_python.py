import os
import subprocess

def run_python_file(working_directory, file_path):
    try:
        fullpath = "/".join([working_directory, file_path])
        working_path = os.path.abspath(fullpath)
        working_abs_path = os.path.abspath(working_directory)

        if not working_path.startswith(working_abs_path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.exists(working_path):
            return f'Error: File "{file_path}" not found.'
        
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'

        proc = subprocess.run(timeout=30, capture_output=True, cwd=working_directory, args=["python3", file_path], text=True)

        response = []
        if proc.stdout:
            response.append(f"STDOUT: {proc.stdout.strip()}")
        
        if proc.stderr:
            response.append(f"STDERR: {proc.stderr.strip()}")

        if proc.returncode != 0:
            response.append(f"Error: Process exited with code {proc.returncode}")

        if len(response) == 0:
            return "No output produced."
        
        return "\n".join(response)
    
    except Exception as err:
        return f"Error executing Python file: {err}"
