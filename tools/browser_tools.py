"""Browser interaction tools for GenericAgent.

Provides tool definitions and handlers for web browser automation
using the TMWebDriver session wrapper.
"""

import json
from typing import Any
from TMWebDriver import Session


# Tool schema definitions (loaded by agentmain.py via load_tool_schema)
BROWSER_TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate the browser to a given URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to navigate to (including https://)."
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "click",
        "description": "Click on an element identified by a CSS selector.",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for the element to click."
                }
            },
            "required": ["selector"]
        }
    },
    {
        "name": "type_text",
        "description": "Type text into an input field identified by a CSS selector.",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {
                    "type": "string",
                    "description": "CSS selector for the input element."
                },
                "text": {
                    "type": "string",
                    "description": "The text to type into the field."
                },
                "clear_first": {
                    "type": "boolean",
                    "description": "Whether to clear the field before typing. Defaults to true."
                }
            },
            "required": ["selector", "text"]
        }
    },
    {
        "name": "get_page_content",
        "description": "Retrieve the current page title and visible text content.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "take_screenshot",
        "description": "Take a screenshot of the current browser state and save it to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "File path to save the screenshot (PNG format)."
                }
            },
            "required": ["filename"]
        }
    }
]


class BrowserToolHandler:
    """Handles execution of browser tool calls using a TMWebDriver Session."""

    def __init__(self, session: Session):
        self.session = session

    def handle(self, tool_name: str, tool_args: dict) -> Any:
        """Dispatch a tool call to the appropriate handler method.

        Args:
            tool_name: Name of the tool to execute.
            tool_args: Dictionary of arguments for the tool.

        Returns:
            A string result describing the outcome.

        Raises:
            ValueError: If the tool name is not recognized.
        """
        if not self.session.is_active():
            self.session.reconnect()

        dispatch = {
            "navigate": self._navigate,
            "click": self._click,
            "type_text": self._type_text,
            "get_page_content": self._get_page_content,
            "take_screenshot": self._take_screenshot,
        }

        handler = dispatch.get(tool_name)
        if handler is None:
            raise ValueError(f"Unknown browser tool: '{tool_name}'")

        return handler(**tool_args)

    def _navigate(self, url: str) -> str:
        self.session.driver.get(url)
        return f"Navigated to {url}. Current URL: {self.session.url}"

    def _click(self, selector: str) -> str:
        from selenium.webdriver.common.by import By
        element = self.session.driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        return f"Clicked element matching '{selector}'."

    def _type_text(self, selector: str, text: str, clear_first: bool = True) -> str:
        from selenium.webdriver.common.by import By
        element = self.session.driver.find_element(By.CSS_SELECTOR, selector)
        if clear_first:
            element.clear()
        element.send_keys(text)
        return f"Typed text into '{selector}'."

    def _get_page_content(self) -> str:
        title = self.session.driver.title
        body_text = self.session.driver.find_element(
            "tag name", "body"
        ).text[:4000]  # Limit to avoid overwhelming the LLM context
        return json.dumps({"title": title, "body_text": body_text})

    def _take_screenshot(self, filename: str) -> str:
        self.session.driver.save_screenshot(filename)
        return f"Screenshot saved to '{filename}'."
