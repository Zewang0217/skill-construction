"""Browser and Page classes for automation."""

import json
import os
import re
import urllib.request
from typing import Any, Dict, List, Optional

from .utils import normalize_selector, safe_eval


class Browser:
    """Manages browser instances and pages."""

    def __init__(self, headless: bool = None, timeout: int = None):
        self.headless = headless if headless is not None else os.environ.get('BROWSER_HEADLESS', 'false').lower() == 'true'
        self.timeout = timeout if timeout is not None else int(os.environ.get('BROWSER_TIMEOUT', '10'))
        self.user_agent = os.environ.get('BROWSER_USER_AGENT', 'Mozilla/5.0 (compatible; BrowserAutomation/1.2)')
        self.pages: List[Page] = []
        self._active_page = None
        self._state = {}

    def new_page(self, url: str) -> 'Page':
        """Open a new page in a new tab.

        Args:
            url: The URL to navigate to.

        Returns:
            Page: The newly created page object.
        """
        page = Page(self, url)
        self.pages.append(page)
        self._active_page = page
        return page

    def close(self):
        """Close all pages and release resources."""
        self.pages.clear()
        self._active_page = None

    def save_state(self, filepath: str):
        """Save browser state to a JSON file.

        Args:
            filepath: Path where to save the state file.
        """
        state = {
            'pages': [p.url for p in self.pages],
            'active_page': self._active_page.url if self._active_page else None,
            'saved_data': self._state,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f)

    def load_state(self, filepath: str):
        """Load browser state from a JSON file.

        Args:
            filepath: Path to the state file.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        self._state = state.get('saved_data', {})
        self.pages = [Page(self, url) for url in state.get('pages', [])]
        if state.get('active_page'):
            self._active_page = self.pages[0]

    def evaluate(self, script: str, context: Optional[Dict] = None):
        """Execute a script in the browser context.

        Args:
            script: JavaScript or Python expression to evaluate.
            context: Additional context variables.

        Returns:
            The result of the evaluation.
        """
        if context is None:
            context = {}
        # Support simple expressions and variable lookups
        if script in self._state:
            return self._state[script]
        if script in context:
            return context[script]
        # Fall back to safe eval for simple expressions
        return safe_eval(script, {**self._state, **context})

    def set_variable(self, name: str, value: Any):
        """Set a browser-level variable.

        Args:
            name: Variable name.
            value: Variable value.
        """
        self._state[name] = value


class Page:
    """Represents a single browser page."""

    def __init__(self, browser: Browser, url: str):
        self.browser = browser
        self.url = url
        self._content = ""
        self._elements = {}
        self._forms = {}

    def _fetch_content(self):
        """Fetch page content if not already loaded."""
        if not self._content:
            try:
                self._content = self._http_get(self.url)
            except Exception:
                self._content = ""

    def _http_get(self, url: str) -> str:
        """Simple HTTP GET for demonstration purposes.

        In a real implementation this would use a headless browser.
        """
        req = urllib.request.Request(url, headers={'User-Agent': self.browser.user_agent})
        with urllib.request.urlopen(req, timeout=self.browser.timeout) as resp:
            return resp.read().decode('utf-8', errors='ignore')

    def fill_form(self, data: Dict[str, Any]):
        """Fill form fields with provided data.

        Args:
            data: Dictionary mapping field names to values.
        """
        self._fetch_content()
        self._forms.update(data)
        # Store input data for later processing
        self.browser.set_variable('_form_data', {**self._forms, **data})

    def click(self, selector: str):
        """Click an element matching the selector.

        Args:
            selector: CSS selector or XPath expression.
        """
        normalized = normalize_selector(selector)
        self._elements[normalized] = {'clicked': True}

    def get_text(self, selector: str) -> str:
        """Get text content of an element.

        Args:
            selector: CSS selector or XPath expression.

        Returns:
            Text content of the matched element.
        """
        normalized = normalize_selector(selector)
        # In a real impl, extract from DOM. Here return placeholder.
        pattern = r'<' + re.escape(normalized) + r'[^>]*>(.*?)</' + re.escape(normalized) + r'>'
        match = re.search(pattern, self._content, re.DOTALL)
        return match.group(1) if match else ""

    def wait_for_element(self, selector: str, timeout: int = None):
        """Wait for an element to appear.

        Args:
            selector: CSS selector or XPath expression.
            timeout: Maximum wait time in seconds.
        """
        t = timeout or self.browser.timeout
        # In a real impl, poll until element appears. Here we just return.
        return True

    def wait_for_url(self, url_partial: str, timeout: int = None):
        """Wait until URL contains the given partial string.

        Args:
            url_partial: Partial URL string to match.
            timeout: Maximum wait time in seconds.
        """
        t = timeout or self.browser.timeout
        # In a real impl, poll URL. Here we just check.
        return url_partial in self.url

    def extract_table(self, selector: str) -> List[Dict[str, str]]:
        """Extract table data as list of dicts.

        Args:
            selector: CSS selector for the table.

        Returns:
            List of dicts with column names as keys.
        """
        # Parse simple HTML table from content
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', self._content, re.DOTALL)
        result = []
        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            if cells:
                result.append({'value': cells[0]} if len(cells) == 1 else dict(enumerate(cells)))
        return result

    def get_source(self) -> str:
        """Get the full page source HTML.

        Returns:
            HTML source of the page.
        """
        self._fetch_content()
        return self._content