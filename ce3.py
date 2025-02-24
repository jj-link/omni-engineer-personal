# ce3.py
import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from typing import List, Dict, Any
import importlib
import inspect
import pkgutil
import os
import json
import sys
import logging
import requests
from dotenv import load_dotenv
import ollama  # Add ollama import
import re
import uuid

from config import Config
from tools.base import BaseTool, ProviderContext  # Remove get_tools import
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompts.system_prompts import SystemPrompts

# Load environment variables
load_dotenv()

# Configure logging to only show ERROR level and above
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s: %(message)s'
)

class Assistant:
    """
    The Assistant class manages:
    - Loading of tools from a specified directory.
    - Interaction with AI providers (Anthropic, CBORG, Ollama).
    - Handling user commands such as 'refresh' and 'reset'.
    - Token usage tracking and display.
    - Tool execution upon request from model responses.
    """

    def __init__(self, provider='anthropic'):
        """Initialize the assistant with the specified provider"""
        self._provider = None  # Private provider field
        self.conversation_history: List[Dict[str, Any]] = []
        self.console = Console()
        self.thinking_enabled = getattr(Config, 'ENABLE_THINKING', False)
        self.temperature = getattr(Config, 'DEFAULT_TEMPERATURE', 0.7)
        self.total_tokens_used = 0
        
        # Set provider first
        self.provider = provider
        # Then load tools with proper provider context
        self.provider_context = ProviderContext(
            provider_type=self.provider,
            model=self.model,
            parameters={'temperature': self.temperature}
        )
        self.tools = self._load_tools()

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def provider(self, value):
        """Set the provider and initialize provider-specific settings"""
        if value not in ['anthropic', 'cborg', 'ollama']:
            raise ValueError(f"Unsupported provider: {value}")

        # Initialize provider-specific settings
        if value == 'anthropic':
            if not os.getenv('ANTHROPIC_API_KEY'):
                raise ValueError("No ANTHROPIC_API_KEY found in environment variables")
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            self.base_url = 'https://api.anthropic.com'
            self.model = Config.PROVIDER_MODELS['anthropic']
        elif value == 'cborg':
            if not os.getenv('CBORG_API_KEY'):
                raise ValueError("No CBORG_API_KEY found in environment variables")
            self.api_key = os.getenv('CBORG_API_KEY')
            self.base_url = 'https://api.cborg.lbl.gov'
            self.model = Config.PROVIDER_MODELS['cborg']
        elif value == 'ollama':
            self.base_url = 'http://localhost:11434'
            self.model = Config.PROVIDER_MODELS['ollama']

        self._provider = value

    def _get_completion(self):
        """
        Get a completion from the selected provider.
        Handles both text-only and multimodal messages.
        """
        try:
            if self.provider == 'anthropic':
                # Prepare conversation history for Anthropic
                messages = []
                last_assistant_with_tools = None
                
                for msg in self.conversation_history:
                    content = msg.get('content', '')
                    role = msg.get('role', '')
                    
                    # For assistant messages with tool calls, track the last one
                    if role == 'assistant' and 'tool_calls' in msg:
                        last_assistant_with_tools = {
                            'role': role,
                            'content': content,
                            'tool_calls': msg['tool_calls']
                        }
                        continue
                    
                    # For regular messages just pass content
                    if role != 'tool':  # Skip tool messages as they'll be added with their assistant
                        messages.append({
                            'role': role,
                            'content': content
                        })
                
                # If we have a pending assistant+tools message and it's followed by tool results,
                # add them together
                if last_assistant_with_tools:
                    messages.append(last_assistant_with_tools)
                    # Add the corresponding tool results
                    tool_results = [msg for msg in self.conversation_history 
                                  if msg.get('role') == 'tool' and 
                                  any(call['id'] == msg.get('tool_call_id') 
                                      for call in last_assistant_with_tools['tool_calls'])]
                    messages.extend(tool_results)

                # Make request to Anthropic API
                response = requests.post(
                    f"{self.base_url}/v1/messages",
                    headers={
                        'anthropic-version': '2023-06-01',
                        'x-api-key': self.api_key,
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': self.model,
                        'messages': [
                            {'role': 'system', 'content': f"{SystemPrompts.DEFAULT}\n\n{SystemPrompts.TOOL_USAGE}"},
                            *messages
                        ],
                        'temperature': self.temperature,
                        'tools': self.tools,
                        'tool_choice': 'auto'  # Enable automatic tool choice
                    }
                )
                response.raise_for_status()
                return response.json()

            elif self.provider == 'cborg':
                # Prepare conversation history for CBORG
                messages = []
                last_assistant_with_tools = None
                
                for msg in self.conversation_history:
                    content = msg.get('content', '')
                    role = msg.get('role', '')
                    
                    # For assistant messages with tool calls, track the last one
                    if role == 'assistant' and 'tool_calls' in msg:
                        last_assistant_with_tools = {
                            'role': role,
                            'content': content,
                            'tool_calls': msg['tool_calls']
                        }
                        continue
                    
                    # For regular messages just pass content
                    if role != 'tool':  # Skip tool messages as they'll be added with their assistant
                        messages.append({
                            'role': role,
                            'content': content
                        })
                
                # If we have a pending assistant+tools message and it's followed by tool results,
                # add them together
                if last_assistant_with_tools:
                    messages.append(last_assistant_with_tools)
                    # Add the corresponding tool results
                    tool_results = [msg for msg in self.conversation_history 
                                  if msg.get('role') == 'tool' and 
                                  any(call['id'] == msg.get('tool_call_id') 
                                      for call in last_assistant_with_tools['tool_calls'])]
                    messages.extend(tool_results)

                # Make request to CBORG API
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': self.model,
                        'messages': [
                            {'role': 'system', 'content': f"{SystemPrompts.DEFAULT}\n\n{SystemPrompts.TOOL_USAGE}"},
                            *messages
                        ],
                        'temperature': self.temperature,
                        'stream': False,
                        'tools': self.tools,
                        'tool_choice': 'auto'  # Enable automatic tool choice
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"CBORG API error: {response.text}")
                
                result = response.json()
                
                # Check for tool usage
                assistant_message = result['choices'][0]['message']
                tool_calls = assistant_message.get('tool_calls', [])
                if tool_calls:
                    self.console.print("\n[bold yellow]  Handling Tool Use...[/bold yellow]\n")
                    
                    tool_results = []
                    for tool_call in tool_calls:
                        # Create a tool use object compatible with our _execute_tool method
                        tool_call = {
                            'id': str(uuid.uuid4()),  # Generate a unique ID
                            'type': 'function',
                            'function': {
                                'name': tool_call['function']['name'],
                                'parameters': tool_call['function']['parameters']
                            }
                        }
                        
                        # Create tool use object
                        tool_use = type('ToolUse', (), {
                            'name': tool_call['function']['name'],
                            'input': tool_call['function']['parameters']  # Use parameters directly
                        })
                        
                        # Execute the tool
                        self.console.print("\n[bold yellow]  Handling Tool Use...[/bold yellow]\n")
                        result = self._execute_tool(tool_use)
                        
                        # Format tool result
                        tool_result = {
                            'role': 'tool',
                            'content': str(result),
                            'tool_call_id': tool_call['id'],
                            'name': tool_call['function']['name']
                        }
                        
                        # Add results to conversation history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": assistant_message.get('content', '')
                        })
                        # Add each tool result as a separate message
                        for tool_result in [tool_result]:
                            self.conversation_history.append(tool_result)
                        return self._get_completion()  # Recursive call to continue
                
                # If no tool usage, just return the response
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': assistant_message.get('content', '')
                })
                
                # Track token usage
                if 'usage' in result:
                    self.total_tokens_used += result['usage']['total_tokens']
                
                return assistant_message.get('content', '')

            elif self.provider == 'ollama':
                try:
                    # Prepare conversation history for Ollama
                    messages = []
                    
                    # Extract just the function part for each tool
                    ollama_tools = [tool['function'] for tool in self.tools]
                    
                    # Create dynamic tool list for system prompt
                    tool_descriptions = "\n    Available Tools:\n"
                    for tool in ollama_tools:
                        tool_descriptions += f"    - {tool['name']}: {tool['description']}\n"
                    
                    # Add system prompt first with dynamic tool list
                    messages.append({
                        'role': 'system',
                        'content': f"{SystemPrompts.OLLAMA_DEFAULT}\n\n{tool_descriptions}\n\nTo use a tool, format your response like this:\n\n<tool_calls>\n{{\n    \"type\": \"function\",\n    \"function\": {{\n        \"name\": \"tool_name\",\n        \"parameters\": {{\n            // parameters here\n        }}\n    }}\n}}\n</tool_calls>"
                    })
                    
                    # Add conversation history
                    for msg in self.conversation_history:
                        content = msg['content']
                        if isinstance(content, list):
                            # Handle multimodal content
                            text_parts = []
                            for part in content:
                                if part.get('type') == 'text':
                                    text_parts.append(part['text'])
                            content = ' '.join(text_parts)
                        messages.append({
                            'role': msg['role'],
                            'content': content
                        })

                    # Create Ollama client and make request
                    client = ollama.Client(host='http://localhost:11434')
                    
                    print("[DEBUG] Tools passed to Ollama:")
                    for tool in ollama_tools:
                        print(f"  - {tool['name']}: {tool['description'][:60]}...")
                    
                    response = client.chat(
                        model=self.model,
                        messages=messages,
                        stream=False,
                        options={
                            'temperature': self.temperature,
                            'top_p': 0.9,
                            'tools': ollama_tools,  # Pass just the function part
                            'tool_choice': 'auto'  # Enable automatic tool choice
                        }
                    )

                    # Check for tool usage in the response text
                    response_content = response['message']['content']
                    print("[DEBUG] Response content:", response_content[:200], "...")  # Show first 200 chars
                    tool_call_match = re.search(r'<tool_calls>(.*?)</tool_calls>', response_content, re.DOTALL)
                    
                    if tool_call_match:
                        print("[DEBUG] Found tool call")
                        try:
                            # Parse the tool call JSON
                            tool_call_text = tool_call_match.group(1).strip()
                            print("[DEBUG] Tool call text:", tool_call_text)
                            tool_call_json = json.loads(tool_call_text)
                            
                            # Validate tool call format
                            if tool_call_json.get('type') != 'function' or 'function' not in tool_call_json:
                                raise ValueError("Invalid tool call format: missing 'type' or 'function' field")
                            
                            # Create a tool call object
                            tool_call = {
                                'id': str(uuid.uuid4()),  # Generate a unique ID
                                'type': 'function',
                                'function': {
                                    'name': tool_call_json['function']['name'],
                                    'parameters': tool_call_json['function']['parameters']
                                }
                            }
                            
                            # Create tool use object
                            tool_use = type('ToolUse', (), {
                                'name': tool_call['function']['name'],
                                'input': tool_call['function']['parameters']  # Use parameters directly
                            })
                            
                            # Execute the tool
                            self.console.print("\n[bold yellow]  Handling Tool Use...[/bold yellow]\n")
                            result = self._execute_tool(tool_use)
                            
                            # Format tool result
                            tool_result = {
                                'role': 'tool',
                                'content': str(result),
                                'tool_call_id': tool_call['id'],
                                'name': tool_call['function']['name']
                            }
                            
                            # Add results to conversation history
                            self.conversation_history.append({
                                "role": "assistant",
                                "content": response_content
                            })
                            self.conversation_history.append(tool_result)
                            return self._get_completion()  # Recursive call to continue
                        except json.JSONDecodeError as e:
                            logging.error(f"Failed to parse tool call JSON: {str(e)}")
                            return f"Error: Invalid tool call format - {str(e)}"
                        except ValueError as e:
                            logging.error(f"Invalid tool call format: {str(e)}")
                            return f"Error: {str(e)}"
                        except Exception as e:
                            logging.error(f"Error handling tool call: {str(e)}")
                            return f"Error handling tool call: {str(e)}"

                    # If no tool usage, just return the response
                    assistant_message = {
                        'role': 'assistant',
                        'content': response_content
                    }
                    self.conversation_history.append(assistant_message)
                    return response_content

                except Exception as e:
                    logging.error(f"Ollama error: {str(e)}")
                    return f"Error: {str(e)}"

            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            logging.error(f"Error in _get_completion: {str(e)}")
            return f"Error: {str(e)}"

    def _execute_uv_install(self, package_name: str) -> bool:
        """
        Execute the uvpackagemanager tool directly to install the missing package.
        Returns True if installation seems successful (no errors in output), otherwise False.
        """
        class ToolUseMock:
            name = "uvpackagemanager"
            input = {
                "command": "install",
                "packages": [package_name]
            }

        result = self._execute_tool(ToolUseMock())
        if "Error" not in result and "failed" not in result.lower():
            self.console.print("[green]The package was installed successfully.[/green]")
            return True
        else:
            self.console.print(f"[red]Failed to install {package_name}. Output:[/red] {result}")
            return False

    def _load_tools(self) -> List[Dict[str, Any]]:
        """
        Dynamically load all tool classes from the tools directory.
        If a dependency is missing, prompt the user to install it via uvpackagemanager.
        
        Returns:
            A list of tools (dicts) containing their 'name', 'description', and 'input_schema'.
        """
        tools = []
        tools_path = getattr(Config, 'TOOLS_DIR', None)

        if tools_path is None:
            self.console.print("[red]TOOLS_DIR not set in Config[/red]")
            return tools

        self.console.print(f"[cyan]Loading tools from: {tools_path}[/cyan]")

        # Clear cached tool modules for fresh import
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('tools.') and module_name != 'tools.base':
                del sys.modules[module_name]

        try:
            modules = list(pkgutil.iter_modules([str(tools_path)]))
            self.console.print(f"[cyan]Found {len(modules)} modules[/cyan]")
            
            for module_info in modules:
                if module_info.name == 'base':
                    continue

                self.console.print(f"[cyan]Loading module: {module_info.name}[/cyan]")

                # Attempt loading the tool module
                try:
                    module = importlib.import_module(f'tools.{module_info.name}')
                    self._extract_tools_from_module(module, tools)
                except ImportError as e:
                    # Handle missing dependencies
                    missing_module = self._parse_missing_dependency(str(e))
                    self.console.print(f"\n[yellow]Missing dependency:[/yellow] {missing_module} for tool {module_info.name}")
                    user_response = input(f"Would you like to install {missing_module}? (y/n): ").lower()

                    if user_response == 'y':
                        success = self._execute_uv_install(missing_module)
                        if success:
                            # Retry loading the module after installation
                            try:
                                module = importlib.import_module(f'tools.{module_info.name}')
                                self._extract_tools_from_module(module, tools)
                            except Exception as retry_err:
                                self.console.print(f"[red]Failed to load tool after installation: {str(retry_err)}[/red]")
                        else:
                            self.console.print(f"[red]Installation of {missing_module} failed. Skipping this tool.[/red]")
                    else:
                        self.console.print(f"[yellow]Skipping tool {module_info.name} due to missing dependency[/yellow]")
                except Exception as mod_err:
                    self.console.print(f"[red]Error loading module {module_info.name}:[/red] {str(mod_err)}")

        except Exception as overall_err:
            self.console.print(f"[red]Error in tool loading process:[/red] {str(overall_err)}")

        self.console.print(f"[cyan]Successfully loaded {len(tools)} tools[/cyan]")
        return tools

    def _parse_missing_dependency(self, error_str: str) -> str:
        """
        Parse the missing dependency name from an ImportError string.
        """
        if "No module named" in error_str:
            parts = error_str.split("No module named")
            missing_module = parts[-1].strip(" '\"")
        else:
            missing_module = error_str
        return missing_module

    def _extract_tools_from_module(self, module, tools: List[Dict[str, Any]]) -> None:
        """
        Given a tool module, find and instantiate all tool classes (subclasses of BaseTool).
        Skips abstract base classes and loads their concrete implementations.
        """
        provider_context = self.provider_context
        print(f"Examining module {module.__name__}")

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                print(f"  Found class: {name}")
                if issubclass(obj, BaseTool):
                    print(f"    Is a BaseTool subclass")
                    print(f"    obj == BaseTool? {obj == BaseTool}")
                    print(f"    is abstract? {inspect.isabstract(obj)}")
                    if obj != BaseTool and not inspect.isabstract(obj):
                        print(f"    Not BaseTool itself and not abstract")
                        try:
                            tool_instance = obj(provider_context=provider_context)
                            print(f"    Created instance")
                            if all(hasattr(tool_instance, attr) for attr in ['name', 'description', 'input_schema']):
                                print(f"    Has all required attributes")
                                
                                # Validate tool attributes for CBORG
                                if self.provider == 'cborg':
                                    # Validate name is not empty and matches pattern
                                    if not tool_instance.name or not tool_instance.name.strip():
                                        print(f"    Skipping tool: empty name")
                                        continue
                                    if not all(c.isalnum() or c in '_-' for c in tool_instance.name):
                                        print(f"    Skipping tool: name contains invalid characters")
                                        continue
                                        
                                    # Validate description is not empty
                                    if not tool_instance.description or not tool_instance.description.strip():
                                        print(f"    Skipping tool: empty description")
                                        continue

                                    # Create tool spec
                                    tool_spec = {
                                        'name': tool_instance.name.strip(),
                                        'description': tool_instance.description.strip(),
                                        'parameters': tool_instance.input_schema
                                    }
                                    # Add both toolSpec and function fields
                                    tools.append({
                                        'toolSpec': tool_spec,
                                        'function': tool_spec  # CBORG requires both fields
                                    })
                                else:
                                    # Format tool for other providers
                                    tools.append({
                                        'type': 'function',
                                        'function': {
                                            'name': tool_instance.name,
                                            'description': tool_instance.description,
                                            'parameters': {
                                                '$schema': 'https://json-schema.org/draft/2020-12/schema',
                                                'type': 'object',
                                                'properties': tool_instance.input_schema,
                                                'required': list(tool_instance.input_schema.keys())
                                            }
                                        }
                                    })
                                print(f"    Successfully added tool: {tool_instance.name}")
                            else:
                                missing = [attr for attr in ['name', 'description', 'input_schema'] 
                                         if not hasattr(tool_instance, attr)]
                                print(f"    Missing attributes: {', '.join(missing)}")
                        except Exception as tool_init_err:
                            print(f"    Error initializing tool {name}: {str(tool_init_err)}")
                else:
                    print(f"    Not a BaseTool subclass")

    def refresh_tools(self):
        """
        Refresh the list of tools and show newly discovered tools.
        """
        current_tool_names = {tool['name'] for tool in self.tools}
        self.tools = self._load_tools()
        new_tool_names = {tool['name'] for tool in self.tools}
        new_tools = new_tool_names - current_tool_names

        if new_tools:
            self.console.print("\n")
            for tool_name in new_tools:
                tool_info = next((t for t in self.tools if t['name'] == tool_name), None)
                if tool_info:
                    description_lines = tool_info['description'].strip().split('\n')
                    formatted_description = '\n    '.join(line.strip() for line in description_lines)
                    self.console.print(f"[bold green]NEW[/bold green] 🔧 [cyan]{tool_name}[/cyan]:\n    {formatted_description}")
        else:
            self.console.print("\n[yellow]No new tools found[/yellow]")

    def display_available_tools(self):
        """
        Print a list of currently loaded tools.
        """
        self.console.print("\n[bold cyan]Available tools:[/bold cyan]")
        tool_names = [tool['name'] for tool in self.tools]
        if tool_names:
            formatted_tools = ", ".join([f"🔧 [cyan]{name}[/cyan]" for name in tool_names])
        else:
            formatted_tools = "No tools available."
        self.console.print(formatted_tools)
        self.console.print("---")

    def _display_tool_usage(self, tool_name: str, input_data: Dict, result: str):
        """
        If SHOW_TOOL_USAGE is enabled, display the input and result of a tool execution.
        Handles special cases like image data and large outputs for cleaner display.
        """
        if not getattr(Config, 'SHOW_TOOL_USAGE', False):
            return

        # Clean up input data by removing any large binary/base64 content
        cleaned_input = self._clean_data_for_display(input_data)
        
        # Clean up result data
        cleaned_result = self._clean_data_for_display(result)

        tool_info = f"""[cyan]📥 Input:[/cyan] {json.dumps(cleaned_input, indent=2)}
[cyan]📤 Result:[/cyan] {cleaned_result}"""
        
        panel = Panel(
            tool_info,
            title=f"Tool used: {tool_name}",
            title_align="left",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)

    def _clean_data_for_display(self, data):
        """
        Helper method to clean data for display by handling various data types
        and removing/replacing large content like base64 strings.
        """
        if isinstance(data, str):
            try:
                # Try to parse as JSON first
                parsed_data = json.loads(data)
                return self._clean_parsed_data(parsed_data)
            except json.JSONDecodeError:
                # If it's a long string, check for base64 patterns
                if len(data) > 1000 and ';base64,' in data:
                    return "[base64 data omitted]"
                return data
        elif isinstance(data, dict):
            return self._clean_parsed_data(data)
        else:
            return data

    def _clean_parsed_data(self, data):
        """
        Recursively clean parsed JSON/dict data, handling nested structures
        and replacing large data with placeholders.
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                # Handle image data in various formats
                if key in ['data', 'image', 'source'] and isinstance(value, str):
                    if len(value) > 1000 and (';base64,' in value or value.startswith('data:')):
                        cleaned[key] = "[base64 data omitted]"
                    else:
                        cleaned[key] = value
                else:
                    cleaned[key] = self._clean_parsed_data(value)
            return cleaned
        elif isinstance(data, list):
            return [self._clean_parsed_data(item) for item in data]
        elif isinstance(data, str) and len(data) > 1000 and ';base64,' in data:
            return "[base64 data omitted]"
        return data

    def _execute_tool(self, tool_use):
        """
        Given a tool usage request (with tool name and inputs),
        dynamically load and execute the corresponding tool.
        """
        try:
            # Search for tool in all tool modules
            tools_path = getattr(Config, 'TOOLS_DIR', None)
            if not tools_path:
                return "Error: TOOLS_DIR not set in Config"

            # Attempt to find and execute the tool
            for module_info in pkgutil.iter_modules([str(tools_path)]):
                if module_info.name == 'base':
                    continue

                try:
                    module = importlib.import_module(f'tools.{module_info.name}')
                    tool_instance = self._find_tool_instance_in_module(module, tool_use.name)
                    
                    if tool_instance:
                        # Display tool usage if enabled
                        self._display_tool_usage(tool_use.name, tool_use.input, "Executing...")
                        
                        # Execute the tool and get result
                        result = tool_instance.execute(**tool_use.input)
                        
                        # Handle dictionary responses with 'response' key
                        if isinstance(result, dict) and 'response' in result:
                            return result['response']
                        
                        return str(result)
                        
                except Exception as e:
                    self.console.print(f"[red]Error executing tool {tool_use.name}:[/red] {str(e)}")
                    return f"Error: {str(e)}"

            return f"Tool {tool_use.name} not found"

        except Exception as e:
            self.console.print(f"[red]Error in tool execution:[/red] {str(e)}")
            return f"Error: {str(e)}"

    def _find_tool_instance_in_module(self, module, tool_name: str):
        """
        Search a given module for a tool class matching tool_name and return an instance of it.
        """
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseTool) and 
                obj != BaseTool and 
                not inspect.isabstract(obj)):  # Skip abstract classes
                try:
                    tool_instance = obj(provider_context=self.provider_context)
                    if tool_instance.name == tool_name:
                        return tool_instance
                except Exception as e:
                    self.console.print(f"[red]Error creating tool instance {name}:[/red] {str(e)}")
        return None

    def _display_token_usage(self, usage):
        """
        Display a visual representation of token usage and remaining tokens.
        Uses only the tracked total_tokens_used.
        """
        used_percentage = (self.total_tokens_used / Config.MAX_CONVERSATION_TOKENS) * 100
        remaining_tokens = max(0, Config.MAX_CONVERSATION_TOKENS - self.total_tokens_used)

        self.console.print(f"\nTotal used: {self.total_tokens_used:,} / {Config.MAX_CONVERSATION_TOKENS:,}")

        bar_width = 40
        filled = int(used_percentage / 100 * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        color = "green"
        if used_percentage > 75:
            color = "yellow"
        if used_percentage > 90:
            color = "red"

        self.console.print(f"[{color}][{bar}] {used_percentage:.1f}%[/{color}]")

        if remaining_tokens < 20000:
            self.console.print(f"[bold red]Warning: Only {remaining_tokens:,} tokens remaining![/bold red]")

        self.console.print("---")

    def chat(self, user_input):
        """
        Process a chat message from the user.
        user_input can be either a string (text-only) or a list (multimodal message)
        """
        # Handle special commands only for text-only messages
        if isinstance(user_input, str):
            if user_input.lower() == 'refresh':
                self.refresh_tools()
                return "Tools refreshed successfully!"
            elif user_input.lower() == 'reset':
                self.reset()
                return "Conversation reset!"
            elif user_input.lower() == 'quit':
                return "Goodbye!"

        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input  # This can be either string or list
            })

            # Show thinking indicator if enabled
            if self.thinking_enabled:
                with Live(Spinner('dots', text='Thinking...', style="cyan"), 
                         refresh_per_second=10, transient=True):
                    response = self._get_completion()
            else:
                response = self._get_completion()

            return response

        except Exception as e:
            logging.error(f"Error in chat: {str(e)}")
            return f"Error: {str(e)}"

    def reset(self):
        """
        Reset the assistant's memory and token usage.
        """
        self.conversation_history = []
        self.total_tokens_used = 0
        self.console.print("\n[bold green]🔄 Assistant memory has been reset![/bold green]")

        welcome_text = """
# Claude Engineer v3. A self-improving assistant framework with tool creation

Type 'refresh' to reload available tools
Type 'reset' to clear conversation history
Type 'quit' to exit

Available tools:
"""
        self.console.print(Markdown(welcome_text))
        self.display_available_tools()


def main():
    """
    Entry point for the assistant CLI loop.
    Provides a prompt for user input and handles 'quit' and 'reset' commands.
    """
    console = Console()
    style = Style.from_dict({'prompt': 'orange'})

    try:
        assistant = Assistant()
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("Please ensure ANTHROPIC_API_KEY is set correctly.")
        return

    welcome_text = """
# Claude Engineer v3. A self-improving assistant framework with tool creation

Type 'refresh' to reload available tools
Type 'reset' to clear conversation history
Type 'quit' to exit

Available tools:
"""
    console.print(Markdown(welcome_text))
    assistant.display_available_tools()

    while True:
        try:
            user_input = prompt("You: ", style=style).strip()

            if user_input.lower() == 'quit':
                console.print("\n[bold blue]👋 Goodbye![/bold blue]")
                break
            elif user_input.lower() == 'reset':
                assistant.reset()
                continue

            response = assistant.chat(user_input)
            console.print("\n[bold purple]Claude Engineer:[/bold purple]")
            if isinstance(response, str):
                safe_response = response.replace('[', '\\[').replace(']', '\\]')
                console.print(safe_response)
            else:
                console.print(str(response))

        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()