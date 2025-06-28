import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")


client = genai.Client(api_key=api_key)


if len(sys.argv) == 1:
    print("Prompt not provided")
    sys.exit(1)

system_prompt = """
You are a coding agent that can help users with Python code execution and file management tasks.

When a user asks a question or makes a request, make a function call plan. It is up to you to figure the request based on the following operations that you can perform:

- List files and directories
- Read the content of files
- Write content to files
- Execute Python files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
user_prompt = sys.argv[1]
messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Lists the content of the specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="the path to the file to read, relative to the working directory.",
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs the specified Python file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="the path to the file to execute, relative to the working directory.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="the path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="the content to write to the file.",
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file
    ]
)

def call_function(function_call_part, verbose=False):
    if "--verbose" in sys.argv:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    call_args = function_call_part.args
    call_args["working_directory"] = "./calculator"
    result = None
    match function_call_part.name:
        case "get_files_info":
            from functions.get_files_info import get_files_info
            result = get_files_info(**call_args)
        case "get_file_content":
            from functions.get_file_content import get_file_content
            result = get_file_content(**call_args)
        case "run_python_file":
            from functions.run_python import run_python_file
            result = run_python_file(**call_args)
        case "write_file":
            from functions.write_file import write_file
            result = write_file(**call_args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call_part.name,
                        response={"error": f"Unknown function: {function_call_part.name}"},
                    )
                ],
            )
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": result},
            )
        ],
    )


model_name = "gemini-2.0-flash-001"

function_called = True
idx = 0
response = None
while function_called and idx < 20:
    response = client.models.generate_content(
        model=model_name, 
        contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt)
    )
    
    for candidate in response.candidates:
        messages.append(candidate.content)

    if response.function_calls is None or len(response.function_calls) == 0:
        function_called = False
        continue

    for fun in response.function_calls:
        function_result = call_function(fun)
        messages.append(function_result)
    idx += 1
    





print(response.text)

if "--verbose" in sys.argv:
    print(f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    