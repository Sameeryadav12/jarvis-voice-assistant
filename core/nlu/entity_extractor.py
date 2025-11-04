"""
Enhanced entity extraction for more complex command parsing.
Extracts dates, times, numbers, durations, and custom entities.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
from loguru import logger


class EntityExtractor:
    """
    Enhanced entity extraction beyond spaCy's built-in capabilities.
    Handles dates, times, durations, numbers, and domain-specific entities.
    """

    def __init__(self):
        """Initialize entity extractor."""
        # Time patterns
        self.time_patterns = [
            (r'(\d{1,2}):(\d{2})\s*(am|pm)?', 'time_12h'),
            (r'(\d{1,2})\s*(am|pm)', 'time_simple'),
            (r'at\s+(\d{1,2})\s*o\'?clock', 'time_oclock'),
        ]
        
        # Date patterns
        self.date_patterns = [
            (r'(today|tonight)', 'today'),
            (r'tomorrow', 'tomorrow'),
            (r'(yesterday)', 'yesterday'),
            (r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', 'next_weekday'),
            (r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', 'weekday'),
            (r'in\s+(\d+)\s+(day|days|week|weeks|month|months)', 'relative_date'),
        ]
        
        # Duration patterns
        self.duration_patterns = [
            (r'(\d+)\s*(second|seconds|sec|secs)', 'seconds'),
            (r'(\d+)\s*(minute|minutes|min|mins)', 'minutes'),
            (r'(\d+)\s*(hour|hours|hr|hrs)', 'hours'),
            (r'(\d+)\s*(day|days)', 'days'),
        ]
        
        # Number patterns
        self.number_words = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
            'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000
        }
        
        logger.debug("EntityExtractor initialized")

    def extract_time(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract time from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with hour, minute, and datetime object
        """
        text_lower = text.lower()
        
        for pattern, pattern_type in self.time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if pattern_type == 'time_12h':
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    am_pm = match.group(3) if len(match.groups()) > 2 else None
                    
                    if am_pm == 'pm' and hour < 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                    
                    return {
                        'hour': hour,
                        'minute': minute,
                        'text': match.group(0),
                        'type': 'time'
                    }
                
                elif pattern_type == 'time_simple':
                    hour = int(match.group(1))
                    am_pm = match.group(2)
                    
                    if am_pm == 'pm' and hour < 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                    
                    return {
                        'hour': hour,
                        'minute': 0,
                        'text': match.group(0),
                        'type': 'time'
                    }
                
                elif pattern_type == 'time_oclock':
                    hour = int(match.group(1))
                    return {
                        'hour': hour,
                        'minute': 0,
                        'text': match.group(0),
                        'type': 'time'
                    }
        
        return None

    def extract_date(self, text: str, reference_date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Extract date from text.
        
        Args:
            text: Input text
            reference_date: Reference date for relative dates
            
        Returns:
            Dictionary with date information
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        text_lower = text.lower()
        
        for pattern, pattern_type in self.date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if pattern_type == 'today':
                    return {
                        'date': reference_date,
                        'text': match.group(0),
                        'type': 'date',
                        'relative': 'today'
                    }
                
                elif pattern_type == 'tomorrow':
                    date = reference_date + timedelta(days=1)
                    return {
                        'date': date,
                        'text': match.group(0),
                        'type': 'date',
                        'relative': 'tomorrow'
                    }
                
                elif pattern_type == 'yesterday':
                    date = reference_date - timedelta(days=1)
                    return {
                        'date': date,
                        'text': match.group(0),
                        'type': 'date',
                        'relative': 'yesterday'
                    }
                
                elif pattern_type == 'next_weekday':
                    weekday = match.group(1).lower()  # Fixed from group(2)
                    date = self._get_next_weekday(reference_date, weekday)
                    return {
                        'date': date,
                        'text': match.group(0),
                        'type': 'date',
                        'weekday': weekday
                    }
                
                elif pattern_type == 'weekday':
                    weekday = match.group(1).lower()
                    date = self._get_next_weekday(reference_date, weekday)
                    return {
                        'date': date,
                        'text': match.group(0),
                        'type': 'date',
                        'weekday': weekday
                    }
                
                elif pattern_type == 'relative_date':
                    amount = int(match.group(1))
                    unit = match.group(2)
                    
                    if 'day' in unit:
                        date = reference_date + timedelta(days=amount)
                    elif 'week' in unit:
                        date = reference_date + timedelta(weeks=amount)
                    elif 'month' in unit:
                        date = reference_date + timedelta(days=amount * 30)
                    else:
                        continue
                    
                    return {
                        'date': date,
                        'text': match.group(0),
                        'type': 'date',
                        'relative': f'{amount} {unit}'
                    }
        
        return None

    def _get_next_weekday(self, reference_date: datetime, weekday: str) -> datetime:
        """
        Get the next occurrence of a weekday.
        
        Args:
            reference_date: Starting date
            weekday: Weekday name
            
        Returns:
            Next occurrence of that weekday
        """
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_weekday = weekdays.get(weekday.lower())
        if target_weekday is None:
            return reference_date
        
        current_weekday = reference_date.weekday()
        days_ahead = target_weekday - current_weekday
        
        if days_ahead <= 0:
            days_ahead += 7
        
        return reference_date + timedelta(days=days_ahead)

    def extract_duration(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract duration from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with duration in seconds
        """
        text_lower = text.lower()
        total_seconds = 0
        
        for pattern, unit_type in self.duration_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                amount = int(match[0])
                
                if unit_type == 'seconds':
                    total_seconds += amount
                elif unit_type == 'minutes':
                    total_seconds += amount * 60
                elif unit_type == 'hours':
                    total_seconds += amount * 3600
                elif unit_type == 'days':
                    total_seconds += amount * 86400
        
        if total_seconds > 0:
            return {
                'seconds': total_seconds,
                'type': 'duration'
            }
        
        return None

    def extract_numbers(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract numbers from text (both digits and words).
        
        Args:
            text: Input text
            
        Returns:
            List of extracted numbers
        """
        numbers = []
        
        # Extract digit numbers
        digit_matches = re.finditer(r'\b(\d+)\b', text)
        for match in digit_matches:
            numbers.append({
                'value': int(match.group(1)),
                'text': match.group(0),
                'type': 'number',
                'format': 'digit'
            })
        
        # Extract word numbers
        text_lower = text.lower()
        for word, value in self.number_words.items():
            if word in text_lower.split():
                numbers.append({
                    'value': value,
                    'text': word,
                    'type': 'number',
                    'format': 'word'
                })
        
        return numbers

    def extract_percentage(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract percentage from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with percentage value
        """
        # Pattern: "50%", "50 percent", "fifty percent"
        match = re.search(r'(\d+)\s*(%|percent)', text.lower())
        if match:
            return {
                'value': int(match.group(1)),
                'text': match.group(0),
                'type': 'percentage'
            }
        
        # Word numbers with percent
        text_lower = text.lower()
        for word, value in self.number_words.items():
            if word in text_lower and 'percent' in text_lower:
                return {
                    'value': value,
                    'text': f'{word} percent',
                    'type': 'percentage'
                }
        
        return None

    def extract_app_name(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract application name from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with app name
        """
        # Common trigger words
        triggers = ['open', 'launch', 'start', 'run', 'focus', 'switch to', 'show']
        
        text_lower = text.lower()
        for trigger in triggers:
            if trigger in text_lower:
                # Extract words after trigger
                parts = text_lower.split(trigger)
                if len(parts) > 1:
                    app_name = parts[1].strip()
                    # Remove common stopwords
                    app_name = re.sub(r'\b(the|a|an)\b', '', app_name).strip()
                    # Get first few words (likely app name)
                    app_words = app_name.split()[:3]
                    app_name = ' '.join(app_words)
                    
                    if app_name:
                        return {
                            'value': app_name,
                            'text': app_name,
                            'type': 'app_name'
                        }
        
        return None

    def extract_url(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract URLs from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted URLs
        """
        url_pattern = r'https?://[^\s]+'
        matches = re.finditer(url_pattern, text)
        
        urls = []
        for match in matches:
            urls.append({
                'value': match.group(0),
                'text': match.group(0),
                'type': 'url'
            })
        
        return urls

    def extract_email(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract email addresses from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted emails
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.finditer(email_pattern, text)
        
        emails = []
        for match in matches:
            emails.append({
                'value': match.group(0),
                'text': match.group(0),
                'type': 'email'
            })
        
        return emails

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all entity types from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with all extracted entities
        """
        entities = {
            'time': self.extract_time(text),
            'date': self.extract_date(text),
            'duration': self.extract_duration(text),
            'numbers': self.extract_numbers(text),
            'percentage': self.extract_percentage(text),
            'app_name': self.extract_app_name(text),
            'urls': self.extract_url(text),
            'emails': self.extract_email(text)
        }
        
        # Remove None values
        entities = {k: v for k, v in entities.items() if v}
        
        return entities

