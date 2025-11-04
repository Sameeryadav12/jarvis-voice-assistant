"""
Web automation skills using Playwright.
Provides browser automation and web scraping capabilities.
"""

from typing import Optional, Dict, Any
from loguru import logger

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


class WebSkills:
    """
    Web automation skills using Playwright.
    Supports browser automation, scraping, and form filling.
    """

    def __init__(self):
        """Initialize web skills."""
        self.playwright = None
        self.browser = None
        logger.info("WebSkills initialized")

    async def _ensure_browser(self) -> None:
        """Ensure browser is initialized."""
        if self.browser:
            return

        try:
            from playwright.async_api import async_playwright
            
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                headless=True
            )
            logger.info("Browser initialized")
        except ImportError:
            logger.warning(
                "Playwright not installed. "
                "Run: pip install playwright && playwright install"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    async def search_web(self, query: str) -> SkillResult:
        """
        Search the web using default search engine.
        
        Args:
            query: Search query
            
        Returns:
            Skill result
        """
        try:
            await self._ensure_browser()
            
            page = await self.browser.new_page()
            
            # Navigate to Google
            search_url = f"https://www.google.com/search?q={query}"
            await page.goto(search_url)
            
            # Get page title
            title = await page.title()
            
            await page.close()
            
            logger.info(f"Searched web for: {query}")
            return SkillResult(
                success=True,
                message=f"Searched for '{query}'",
                data={"query": query, "title": title}
            )
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return SkillResult(
                success=False,
                message=f"Web search failed: {str(e)}"
            )

    async def scrape_page(self, url: str, selector: Optional[str] = None) -> SkillResult:
        """
        Scrape content from a web page.
        
        Args:
            url: URL to scrape
            selector: Optional CSS selector for specific content
            
        Returns:
            Skill result with scraped content
        """
        try:
            await self._ensure_browser()
            
            page = await self.browser.new_page()
            await page.goto(url)
            
            if selector:
                content = await page.inner_text(selector)
            else:
                content = await page.content()
            
            await page.close()
            
            logger.info(f"Scraped page: {url}")
            return SkillResult(
                success=True,
                message=f"Scraped content from {url}",
                data={"url": url, "content": content}
            )
        except Exception as e:
            logger.error(f"Page scraping failed: {e}")
            return SkillResult(
                success=False,
                message=f"Page scraping failed: {str(e)}"
            )

    async def fill_form(
        self,
        url: str,
        form_data: Dict[str, str]
    ) -> SkillResult:
        """
        Fill and submit a web form.
        
        Args:
            url: URL with form
            form_data: Dictionary of field selectors and values
            
        Returns:
            Skill result
        """
        try:
            await self._ensure_browser()
            
            page = await self.browser.new_page()
            await page.goto(url)
            
            # Fill form fields
            for selector, value in form_data.items():
                await page.fill(selector, value)
            
            # Form submission would go here
            # await page.click("button[type='submit']")
            
            await page.close()
            
            logger.info(f"Filled form at: {url}")
            return SkillResult(
                success=True,
                message=f"Filled form at {url}"
            )
        except Exception as e:
            logger.error(f"Form filling failed: {e}")
            return SkillResult(
                success=False,
                message=f"Form filling failed: {str(e)}"
            )

    async def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle web-related intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        if intent.type == IntentType.SEARCH_WEB:
            # Extract query from raw text
            query = intent.raw_text.lower()
            for trigger in ["search for", "google", "look up", "find"]:
                query = query.replace(trigger, "")
            query = query.strip()
            
            if not query:
                return SkillResult(
                    success=False,
                    message="Please specify what to search for"
                )
            
            return await self.search_web(query)

        return SkillResult(
            success=False,
            message=f"Unknown web intent: {intent.type.value}"
        )

    async def close(self) -> None:
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("WebSkills closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()





