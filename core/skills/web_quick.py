"""
Web Quick-Actions Skills

Features:
- "Open [website]"
- "Search for [query]"
- "Bookmark this page"
- "Share current page"
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import webbrowser
from urllib.parse import quote, urlencode
from loguru import logger
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..nlu.intents import Intent, IntentType
from ..nlu.router import SkillResult


class WebQuickSkills:
    """
    Web quick-action skills for browser automation.
    
    Features:
    - Open websites
    - Search queries
    - Bookmark management
    - Page sharing
    """
    
    # Common website domains
    WEBSITE_MAP = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://www.stackoverflow.com",
        "reddit": "https://www.reddit.com",
        "linkedin": "https://www.linkedin.com",
        "gmail": "https://www.gmail.com",
        "outlook": "https://www.outlook.com",
        "amazon": "https://www.amazon.com",
        "netflix": "https://www.netflix.com",
        "spotify": "https://www.spotify.com",
    }
    
    # Search engine URLs
    SEARCH_ENGINES = {
        "google": "https://www.google.com/search?q={}",
        "bing": "https://www.bing.com/search?q={}",
        "duckduckgo": "https://www.duckduckgo.com/?q={}",
        "youtube": "https://www.youtube.com/results?search_query={}",
        "github": "https://github.com/search?q={}",
    }
    
    def __init__(self, bookmarks_file: Optional[Path] = None):
        """
        Initialize web quick-action skills.
        
        Args:
            bookmarks_file: Path to bookmarks JSON file (default: user config)
        """
        if bookmarks_file is None:
            bookmarks_file = Path.home() / ".jarvis" / "bookmarks.json"
        
        self.bookmarks_file = bookmarks_file
        self.bookmarks_file.parent.mkdir(parents=True, exist_ok=True)
        self.bookmarks: Dict[str, str] = {}
        self.load_bookmarks()
        
        logger.info("WebQuickSkills initialized")
    
    def load_bookmarks(self):
        """Load bookmarks from file."""
        if not self.bookmarks_file.exists():
            return
        
        try:
            with open(self.bookmarks_file, 'r') as f:
                self.bookmarks = json.load(f)
            logger.info(f"Loaded {len(self.bookmarks)} bookmarks")
        except Exception as e:
            logger.warning(f"Failed to load bookmarks: {e}")
            self.bookmarks = {}
    
    def save_bookmarks(self):
        """Save bookmarks to file."""
        try:
            with open(self.bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
            logger.info(f"Saved {len(self.bookmarks)} bookmarks")
        except Exception as e:
            logger.error(f"Failed to save bookmarks: {e}")
    
    def open_website(self, site_name: str) -> SkillResult:
        """
        Open a website by name or URL.
        
        Args:
            site_name: Website name (e.g., "google") or URL
            
        Returns:
            Skill result
        """
        # Normalize site name
        site_name = site_name.lower().strip()
        
        # Check if it's already a URL
        if site_name.startswith(('http://', 'https://')):
            url = site_name
        elif site_name in self.WEBSITE_MAP:
            url = self.WEBSITE_MAP[site_name]
        else:
            # Try adding https:// and .com
            if '.' not in site_name:
                url = f"https://www.{site_name}.com"
            else:
                url = f"https://{site_name}"
        
        try:
            webbrowser.open(url)
            logger.info(f"Opened website: {url}")
            
            return SkillResult(
                success=True,
                message=f"Opened {site_name}",
                data={"url": url}
            )
        except Exception as e:
            logger.error(f"Failed to open website: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to open {site_name}: {str(e)}"
            )
    
    def search(
        self,
        query: str,
        engine: str = "google",
    ) -> SkillResult:
        """
        Search the web.
        
        Args:
            query: Search query
            engine: Search engine ("google", "bing", "duckduckgo", "youtube", "github")
            
        Returns:
            Skill result
        """
        engine = engine.lower()
        
        if engine not in self.SEARCH_ENGINES:
            engine = "google"
            logger.warning(f"Unknown search engine, using Google")
        
        url_template = self.SEARCH_ENGINES[engine]
        url = url_template.format(quote(query))
        
        try:
            webbrowser.open(url)
            logger.info(f"Searching {engine} for: {query}")
            
            return SkillResult(
                success=True,
                message=f"Searching {engine} for '{query}'",
                data={"url": url, "query": query, "engine": engine}
            )
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to search: {str(e)}"
            )
    
    def bookmark_page(
        self,
        name: str,
        url: Optional[str] = None,
    ) -> SkillResult:
        """
        Bookmark a page.
        
        Args:
            name: Bookmark name
            url: URL to bookmark (if None, tries to get current page)
            
        Returns:
            Skill result
        """
        if url is None:
            # Try to get current page URL from clipboard or active browser
            # This is a simplified version - full implementation would require
            # browser automation (Playwright/Selenium)
            return SkillResult(
                success=False,
                message="Cannot determine current page URL. Please provide URL."
            )
        
        self.bookmarks[name] = url
        self.save_bookmarks()
        
        logger.info(f"Bookmarked: {name} -> {url}")
        
        return SkillResult(
            success=True,
            message=f"Bookmarked '{name}'",
            data={"name": name, "url": url}
        )
    
    def list_bookmarks(self) -> SkillResult:
        """
        List all bookmarks.
        
        Returns:
            Skill result with bookmarks
        """
        if not self.bookmarks:
            return SkillResult(
                success=True,
                message="No bookmarks found",
                data={"bookmarks": []}
            )
        
        bookmark_list = [{"name": name, "url": url} for name, url in self.bookmarks.items()]
        
        message = f"Found {len(bookmark_list)} bookmark(s):\n"
        for i, bookmark in enumerate(bookmark_list[:10], 1):  # Show first 10
            message += f"  {i}. {bookmark['name']}: {bookmark['url']}\n"
        
        if len(bookmark_list) > 10:
            message += f"  ... and {len(bookmark_list) - 10} more"
        
        return SkillResult(
            success=True,
            message=message.strip(),
            data={"bookmarks": bookmark_list}
        )
    
    def open_bookmark(self, name: str) -> SkillResult:
        """
        Open a bookmarked page.
        
        Args:
            name: Bookmark name
            
        Returns:
            Skill result
        """
        if name not in self.bookmarks:
            return SkillResult(
                success=False,
                message=f"Bookmark '{name}' not found"
            )
        
        url = self.bookmarks[name]
        
        try:
            webbrowser.open(url)
            logger.info(f"Opened bookmark: {name} -> {url}")
            
            return SkillResult(
                success=True,
                message=f"Opened bookmark '{name}'",
                data={"name": name, "url": url}
            )
        except Exception as e:
            logger.error(f"Failed to open bookmark: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to open bookmark: {str(e)}"
            )
    
    def delete_bookmark(self, name: str) -> SkillResult:
        """
        Delete a bookmark.
        
        Args:
            name: Bookmark name
            
        Returns:
            Skill result
        """
        if name not in self.bookmarks:
            return SkillResult(
                success=False,
                message=f"Bookmark '{name}' not found"
            )
        
        del self.bookmarks[name]
        self.save_bookmarks()
        
        logger.info(f"Deleted bookmark: {name}")
        
        return SkillResult(
            success=True,
            message=f"Deleted bookmark '{name}'"
        )
    
    def share_page(
        self,
        url: Optional[str] = None,
        method: str = "copy",
    ) -> SkillResult:
        """
        Share current page.
        
        Args:
            url: URL to share (if None, tries to get current page)
            method: Sharing method ("copy", "email", "message")
            
        Returns:
            Skill result
        """
        if url is None:
            # Simplified: would need browser automation
            return SkillResult(
                success=False,
                message="Cannot determine current page URL"
            )
        
        try:
            if method == "copy":
                import pyperclip
                pyperclip.copy(url)
                return SkillResult(
                    success=True,
                    message=f"Copied URL to clipboard: {url}",
                    data={"url": url}
                )
            elif method == "email":
                # Open email client with URL
                mailto = f"mailto:?subject=Shared%20Link&body={quote(url)}"
                webbrowser.open(mailto)
                return SkillResult(
                    success=True,
                    message="Opened email client to share link",
                    data={"url": url}
                )
            elif method == "message":
                # Create shareable message URL
                share_url = f"https://api.whatsapp.com/send?text={quote(url)}"
                webbrowser.open(share_url)
                return SkillResult(
                    success=True,
                    message="Opened messaging app to share link",
                    data={"url": url}
                )
            else:
                return SkillResult(
                    success=False,
                    message=f"Unknown sharing method: {method}"
                )
        
        except Exception as e:
            logger.error(f"Failed to share page: {e}")
            return SkillResult(
                success=False,
                message=f"Failed to share page: {str(e)}"
            )
    
    def handle_intent(self, intent: Intent) -> SkillResult:
        """
        Handle web quick-action intents.
        
        Args:
            intent: Classified intent
            
        Returns:
            Skill result
        """
        # Extract entities for website/query
        website = None
        query = None
        
        if intent.entities:
            for entity in intent.entities:
                if entity.type in ["ORG", "PERSON", "GPE"]:
                    website = entity.value
                elif entity.type in ["QUERY", "TEXT"]:
                    query = entity.value
        
        # Extract from intent text if no entities
        if not website and not query and hasattr(intent, 'text'):
            text = intent.text
            # Simple heuristic: if it contains spaces, it's likely a search query
            if ' ' in text or len(text) > 20:
                query = text
            else:
                website = text
        
        if intent.type == IntentType.OPEN_WEBSITE:
            if website:
                return self.open_website(website)
            else:
                return SkillResult(
                    success=False,
                    message="Please specify a website to open"
                )
        
        elif intent.type == IntentType.SEARCH:
            if query:
                return self.search(query)
            else:
                return SkillResult(
                    success=False,
                    message="Please specify a search query"
                )
        
        return SkillResult(
            success=False,
            message=f"Unknown web intent: {intent.type.value}"
        )

