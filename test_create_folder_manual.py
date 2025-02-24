import asyncio
from tools.base import ProviderContext
from tools.create_folder_tool_impl import CreateFolderToolImpl
from pathlib import Path
import shutil
import json

def verify_ollama_response(result):
    """Verify Ollama response format"""
    assert "response" in result, "Missing 'response' key"
    assert "name" in result, "Missing 'name' key"
    assert "tool_call_id" in result, "Missing 'tool_call_id' key"
    print("\nOllama Response Format:")
    print(json.dumps(result, indent=2))

def verify_cborg_response(result):
    """Verify CBORG response format"""
    assert "choices" in result, "Missing 'choices' key"
    assert len(result["choices"]) == 1, "Expected 1 choice"
    message = result["choices"][0]["message"]
    assert "role" in message, "Missing 'role' key"
    assert "content" in message, "Missing 'content' key"
    assert "tool_call_result" in message, "Missing 'tool_call_result' key"
    print("\nCBORG Response Format:")
    print(json.dumps(result, indent=2))

async def test_create_folder():
    # Create test directory
    test_dir = Path("manual_test_workspace")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    try:
        # Test with Ollama provider
        ollama_context = ProviderContext(
            provider_type="ollama",
            model="codellama",
            parameters={"temperature": 0.7}
        )
        ollama_tool = CreateFolderToolImpl(provider_context=ollama_context)
        
        print("\n=== Testing Ollama Provider ===")
        
        # Test creating a folder
        result = await ollama_tool.execute(path=str(test_dir / "ollama_test"))
        print("\nCreate Folder Test:")
        verify_ollama_response(result)
        print(f"Folder exists: {(test_dir / 'ollama_test').exists()}")

        # Test error case
        result = await ollama_tool.execute(path=str(test_dir / "invalid<>:folder"))
        print("\nInvalid Path Test:")
        verify_ollama_response(result)

        # Test with CBORG provider
        cborg_context = ProviderContext(
            provider_type="cborg",
            model="lbl/cborg-coder:chat",
            parameters={"temperature": 0.0}
        )
        cborg_tool = CreateFolderToolImpl(provider_context=cborg_context)
        
        print("\n=== Testing CBORG Provider ===")
        
        # Test creating a folder
        result = await cborg_tool.execute(path=str(test_dir / "cborg_test"))
        print("\nCreate Folder Test:")
        verify_cborg_response(result)
        print(f"Folder exists: {(test_dir / 'cborg_test').exists()}")

        # Test error case
        result = await cborg_tool.execute(path=str(test_dir / "invalid<>:folder"))
        print("\nInvalid Path Test:")
        verify_cborg_response(result)

        # Test existing file path
        test_file = test_dir / "existing_file"
        test_file.touch()
        result = await cborg_tool.execute(path=str(test_file))
        print("\nExisting File Test:")
        verify_cborg_response(result)

    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    asyncio.run(test_create_folder())
