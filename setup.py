from setuptools import setup, find_packages

setup(
    name="omni_engineer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic",
        "python-dotenv",
        "rich",
        "requests",
        "beautifulsoup4",
        "validators>=0.34.0",
        "PyAutoGUI",
        "Pillow",
        "prompt-toolkit",
        "matplotlib>=3.9.2",
        "flask>=3.0.3",
        "werkzeug>=3.1.2",
        "markdownify>=0.14.1",
        "protego>=0.3.1",
        "readability-lxml>=0.8.1",
        "e2b-code-interpreter>=1.0.3",
        "aiohttp>=3.9.3",
    ],
    python_requires=">=3.9",
)
