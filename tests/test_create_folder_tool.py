import unittest
import asyncio
import tempfile
from pathlib import Path
from tools.create_folder_tool_impl import CreateFolderToolImpl
from tools.base import ProviderContext
import shutil

class TestCreateFolderTool(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.tool = CreateFolderToolImpl()
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        self.loop.close()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_tool_properties(self):
        """Test tool name, description and schema"""
        self.assertEqual(self.tool.name, "create_folder")
        self.assertIsInstance(self.tool.description, str)
        self.assertIsInstance(self.tool.input_schema, dict)
        self.assertIn("path", self.tool.input_schema["properties"])

    def test_create_single_folder(self):
        """Test creating a single folder"""
        async def run_test():
            test_path = self.test_dir / "test_folder"
            result = await self.tool.execute(path=str(test_path))
            self.assertIn("response", result)
            self.assertEqual(result["response"], f"Created folder: {test_path}")
            self.assertTrue(test_path.exists())
            self.assertTrue(test_path.is_dir())
        self.loop.run_until_complete(run_test())

    def test_create_nested_folders(self):
        """Test creating nested folders"""
        async def run_test():
            test_path = self.test_dir / "nested" / "test_folder"
            result = await self.tool.execute(path=str(test_path))
            self.assertIn("response", result)
            self.assertEqual(result["response"], f"Created folder: {test_path}")
            self.assertTrue(test_path.exists())
            self.assertTrue(test_path.is_dir())
        self.loop.run_until_complete(run_test())

    def test_create_existing_folder(self):
        """Test creating a folder that already exists"""
        async def run_test():
            test_path = self.test_dir / "existing_folder"
            test_path.mkdir()
            result = await self.tool.execute(path=str(test_path))
            self.assertIn("response", result)
            self.assertEqual(result["response"], f"Folder already exists: {test_path}")
        self.loop.run_until_complete(run_test())

    def test_create_folder_with_invalid_path(self):
        """Test creating a folder with invalid characters in path"""
        async def run_test():
            test_path = self.test_dir / "invalid<>path"
            result = await self.tool.execute(path=str(test_path))
            self.assertIn("response", result)
            self.assertTrue("Error" in result["response"])
            self.assertFalse(test_path.exists())
        self.loop.run_until_complete(run_test())

    def test_create_folder_with_file_path(self):
        """Test creating a folder where a file already exists"""
        async def run_test():
            test_path = self.test_dir / "existing_file"
            test_path.touch()
            result = await self.tool.execute(path=str(test_path))
            self.assertIn("response", result)
            self.assertTrue("Error" in result["response"])
            self.assertTrue(test_path.exists())
            self.assertTrue(test_path.is_file())
        self.loop.run_until_complete(run_test())

    def test_provider_specific_response_format(self):
        """Test that responses are formatted according to provider"""
        async def run_test():
            # Test Ollama format
            ollama_path = self.test_dir / "ollama_test"
            ollama_result = await self.tool.execute(path=str(ollama_path))
            self.assertIn("response", ollama_result)
            self.assertEqual(ollama_result["response"], f"Created folder: {ollama_path}")

            # Test CBORG format
            self.tool.provider_context = ProviderContext(provider_type="cborg")
            cborg_path = self.test_dir / "cborg_test"
            cborg_result = await self.tool.execute(path=str(cborg_path))
            self.assertIn("choices", cborg_result)
            self.assertEqual(cborg_result["choices"][0]["message"]["content"], f"Created folder: {cborg_path}")

            # Test invalid provider type
            with self.assertRaises(ValueError) as cm:
                ProviderContext(provider_type="unsupported")
            self.assertEqual(str(cm.exception), "Invalid provider type: unsupported")

        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    unittest.main()
