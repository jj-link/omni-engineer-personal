import asyncio
from tools.base import ProviderContext
from tools.create_folder_tool_impl import CreateFolderToolImpl
from pathlib import Path
import shutil

async def test_create_folder_integration():
    # Create test directory
    test_dir = Path("integration_test_workspace")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    try:
        # Test with Ollama function call format
        ollama_context = ProviderContext(
            provider_type="ollama",
            model="codellama",
            parameters={"temperature": 0.7}
        )
        
        ollama_tool = CreateFolderToolImpl(provider_context=ollama_context)
        result = await ollama_tool.execute(path=str(test_dir / "ollama_test"))
        print("\nOllama Integration Test:")
        print(f"Result: {result}")
        print(f"Folder exists: {(test_dir / 'ollama_test').exists()}")

        # Test with CBORG function call format
        cborg_context = ProviderContext(
            provider_type="cborg",
            model="lbl/cborg-coder:chat",
            parameters={"temperature": 0.0}
        )
        
        cborg_tool = CreateFolderToolImpl(provider_context=cborg_context)
        result = await cborg_tool.execute(path=str(test_dir / "cborg_test"))
        print("\nCBORG Integration Test:")
        print(f"Result: {result}")
        print(f"Folder exists: {(test_dir / 'cborg_test').exists()}")

        # Test error cases
        print("\nTesting error cases:")
        
        # Test invalid path
        result = await cborg_tool.execute(path=str(test_dir / "invalid<>:folder"))
        print("\nInvalid path test:")
        print(f"Result: {result}")

        # Test existing file path
        file_path = test_dir / "existing_file"
        file_path.touch()
        result = await cborg_tool.execute(path=str(file_path))
        print("\nExisting file path test:")
        print(f"Result: {result}")

        # Test unsupported provider
        try:
            unsupported_context = ProviderContext(
                provider_type="unsupported",
                model="test",
                parameters={}
            )
            print("\nUnsupported provider test:")
            print("Failed: Should have raised ValueError")
        except ValueError as e:
            print("\nUnsupported provider test:")
            print(f"Success: Caught expected error: {str(e)}")

    finally:
        # Clean up
        if test_dir.exists():
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    asyncio.run(test_create_folder_integration())
