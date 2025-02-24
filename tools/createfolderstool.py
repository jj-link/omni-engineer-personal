from tools.base import BaseTool
import os
import pathlib
from typing import List

class CreateFoldersTool(BaseTool):
    name = "createfolderstool"
    description = '''Creates a new folder at the specified path. Use forward slashes in paths - they will be automatically converted to the correct format for your system.
    
    {
        "path": "test/subfolder"  # Use forward slashes - they will be converted automatically
    }
    
    Examples:
    1. Create a folder in current directory:
    {
        "path": "test"
    }
    
    2. Create a nested folder:
    {
        "path": "test/subfolder/nested"  # Forward slashes will be converted automatically
    }
    
    3. Create a folder relative to current:
    {
        "path": "./test/folder"  # Explicit relative paths are supported
    }
    
    Notes:
    - Always use forward slashes (/) in paths
    - Paths are relative to the project root
    - No need to escape slashes or use backslashes
    - Avoid absolute paths unless specifically required'''
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
            # Validate path components
            path_parts = pathlib.Path(path).parts
            if any(any(c in '<>:"|?*' for c in part) for part in path_parts):
                return {"response": "Error: Invalid characters in path"}

            # Normalize and create directory
            normalized_path = os.path.normpath(path)
            absolute_path = os.path.abspath(normalized_path)
            os.makedirs(absolute_path, exist_ok=True)
            return {"response": f"Successfully created folder: {path}"}

        except PermissionError:
            return {"response": "Permission denied: Unable to create folder"}
        except OSError as e:
            return {"response": f"Error creating folder: {str(e)}"}