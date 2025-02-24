from tools.base import BaseTool
import os
import pathlib
from typing import List

class CreateFoldersTool(BaseTool):
    name = "create_folder"
    description = '''Creates a new folder at the specified absolute or relative path. Use this tool by providing a path parameter in the following format:
    
    {
        "path": "/absolute/path" or "relative/path"
    }
    
    Example:
    To create a folder named "test" in the current directory:
    {
        "path": "test"
    }
    
    To create a nested folder:
    {
        "path": "parent/child"
    }
    
    Note: The path can be absolute (e.g., /Users/username/Documents) or relative (e.g., myfolder).'''
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The absolute or relative path where the folder should be created"
            }
        },
        "required": ["path"]
    }

    def _execute(self, **kwargs) -> str:
        path = kwargs.get("path")
        if not path:
            return "No folder path provided"

        try:
            # Normalize path
            normalized_path = os.path.normpath(path)
            absolute_path = os.path.abspath(normalized_path)
            
            # Validate path
            if not all(c not in '<>:"|?*' for c in absolute_path):
                return {"response": "Error: Invalid characters in path"}

            # Create directory
            os.makedirs(absolute_path, exist_ok=True)
            return {"response": f"Successfully created folder: {path}"}

        except PermissionError:
            return {"response": "Permission denied: Unable to create folder"}
        except OSError as e:
            return {"response": f"Error creating folder: {str(e)}"}