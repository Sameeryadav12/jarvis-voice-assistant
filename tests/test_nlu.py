"""
Test script for NLU (intent classification and entity extraction).
Sprint 2 - Tests enhanced NLU capabilities.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.nlu.intents import IntentClassifier, IntentType
from core.nlu.entity_extractor import EntityExtractor
from loguru import logger


def test_intent_classification():
    """Test intent classification with various inputs."""
    logger.info("=" * 60)
    logger.info("Testing Intent Classification")
    logger.info("=" * 60)
    logger.info("")
    
    classifier = IntentClassifier()
    
    test_cases = [
        # System Control
        ("turn up the volume", IntentType.VOLUME_UP),
        ("increase volume", IntentType.VOLUME_UP),
        ("louder", IntentType.VOLUME_UP),
        ("volume down", IntentType.VOLUME_DOWN),
        ("quieter", IntentType.VOLUME_DOWN),
        ("set volume to 50", IntentType.VOLUME_SET),
        ("mute", IntentType.MUTE),
        ("unmute", IntentType.UNMUTE),
        
        # Window Management
        ("open chrome", IntentType.OPEN_APP),
        ("launch visual studio", IntentType.OPEN_APP),
        ("close notepad", IntentType.CLOSE_APP),
        ("focus on chrome", IntentType.FOCUS_WINDOW),
        ("switch to firefox", IntentType.FOCUS_WINDOW),
        
        # Time & Reminders
        ("remind me to call mom", IntentType.CREATE_REMINDER),
        ("set a timer for 5 minutes", IntentType.SET_TIMER),
        ("set alarm for 7am", IntentType.SET_ALARM),
        ("list reminders", IntentType.LIST_REMINDERS),
        
        # Calendar
        ("create event tomorrow at 3pm", IntentType.CREATE_EVENT),
        ("schedule meeting with bob", IntentType.CREATE_EVENT),
        ("show my calendar", IntentType.LIST_EVENTS),
        
        # Information
        ("what time is it", IntentType.GET_TIME),
        ("what's the date", IntentType.GET_DATE),
        ("check battery", IntentType.GET_BATTERY),
        ("system info", IntentType.GET_SYSTEM_INFO),
        
        # Search
        ("search for python tutorials", IntentType.SEARCH_WEB),
        ("google machine learning", IntentType.SEARCH_WEB),
        
        # Control
        ("help", IntentType.HELP),
        ("stop", IntentType.STOP),
        ("thank you", IntentType.THANK_YOU),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for text, expected_intent in test_cases:
        intent = classifier.classify(text)
        status = "✅" if intent.type == expected_intent else "❌"
        
        if intent.type == expected_intent:
            correct += 1
        
        logger.info(f"{status} '{text}'")
        logger.info(f"   Expected: {expected_intent.value}")
        logger.info(f"   Got: {intent.type.value} (confidence: {intent.confidence:.2f})")
        
        if intent.entities:
            logger.info(f"   Entities: {[f'{e.type}={e.value}' for e in intent.entities]}")
        
        logger.info("")
    
    accuracy = (correct / total) * 100
    logger.info("=" * 60)
    logger.info(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    logger.info("=" * 60)
    
    return accuracy >= 80  # 80% accuracy threshold


def test_entity_extraction():
    """Test entity extraction capabilities."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Testing Entity Extraction")
    logger.info("=" * 60)
    logger.info("")
    
    extractor = EntityExtractor()
    
    test_cases = [
        ("set volume to 50", ["percentage"]),
        ("set volume to 75 percent", ["percentage"]),
        ("remind me in 5 minutes", ["duration"]),
        ("set timer for 2 hours", ["duration"]),
        ("meeting tomorrow at 3pm", ["date", "time"]),
        ("alarm at 7:30 am", ["time"]),
        ("open chrome", ["app_name"]),
        ("send email to john@example.com", ["email"]),
        ("go to https://google.com", ["urls"]),
    ]
    
    for text, expected_types in test_cases:
        entities = extractor.extract_all(text)
        found_types = list(entities.keys())
        
        status = "✅" if all(t in found_types for t in expected_types) else "⚠️"
        
        logger.info(f"{status} '{text}'")
        logger.info(f"   Expected types: {expected_types}")
        logger.info(f"   Found: {found_types}")
        
        for entity_type, entity_data in entities.items():
            if isinstance(entity_data, list):
                logger.info(f"   {entity_type}: {[e['value'] for e in entity_data]}")
            else:
                logger.info(f"   {entity_type}: {entity_data.get('value', entity_data)}")
        
        logger.info("")
    
    logger.info("=" * 60)
    logger.info("Entity Extraction Test Complete")
    logger.info("=" * 60)
    
    return True


def test_complex_commands():
    """Test complex commands with multiple entities."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Testing Complex Commands")
    logger.info("=" * 60)
    logger.info("")
    
    classifier = IntentClassifier()
    
    complex_cases = [
        "remind me to call john tomorrow at 3pm",
        "set volume to 75 percent",
        "create a meeting with the team next monday at 10am",
        "set a timer for 15 minutes",
        "search for the best restaurants near me",
    ]
    
    for text in complex_cases:
        intent = classifier.classify(text)
        
        logger.info(f"📝 '{text}'")
        logger.info(f"   Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
        logger.info(f"   Entities:")
        
        if intent.entities:
            for entity in intent.entities:
                logger.info(f"     - {entity.type}: {entity.value}")
        else:
            logger.info("     (none)")
        
        logger.info("")
    
    logger.info("=" * 60)
    logger.info("Complex Commands Test Complete")
    logger.info("=" * 60)
    
    return True


def main():
    """Main entry point."""
    # Configure logger
    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{message}</level>",
        level="INFO"
    )
    
    try:
        # Run tests
        test1 = test_intent_classification()
        test2 = test_entity_extraction()
        test3 = test_complex_commands()
        
        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        logger.info(f"Intent Classification: {'✅ PASS' if test1 else '❌ FAIL'}")
        logger.info(f"Entity Extraction: {'✅ PASS' if test2 else '❌ FAIL'}")
        logger.info(f"Complex Commands: {'✅ PASS' if test3 else '❌ FAIL'}")
        logger.info("=" * 60)
        
        success = all([test1, test2, test3])
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()





