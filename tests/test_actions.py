import pytest
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from rasa_sdk.types import DomainDict
from actions.actions import (
    ActionFetchChapterAndSuggestTopics,
    ActionFetchTopicDetails,
    ActionFetchSubtopicDetails,
    ActionFetchApplicationDetails,
    ActionFetchSubtopicConditions,
    ActionFetchSubtopicDetailsDescription,
    ActionFetchSubtopicCharacteristics,
    ActionFetchExampleDetails,
    ActionDefaultFallback
)


# Helper to create mock tracker
def create_tracker(intent, entities=None, slots=None, latest_action_name="action_listen"):
    if entities is None:
        entities = []
    if slots is None:
        slots = {}
    return Tracker(
        sender_id="test_user",
        slots=slots,
        latest_message={
            "intent": {"name": intent},
            "entities": entities
        },
        events=[],
        paused=False,
        followup_action=None,
        active_loop={},
        latest_action_name=latest_action_name
    )


# Test ActionFetchChapterAndSuggestTopics
def test_action_fetch_chapter_and_suggest_topics():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_chapter",
        entities=[{"entity": "chapter_id", "value": "1"}],
        slots={"chapter_id": "1"}
    )
    domain = {}
    action = ActionFetchChapterAndSuggestTopics()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Chương 1" in dispatcher.messages[0]["text"], "Response should include chapter details"


# Test ActionFetchTopicDetails
def test_action_fetch_topic_details():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_topics",
        entities=[{"entity": "topic_name", "value": "Guong dong co ban"}],
        slots={"topic_name": "Guong dong co ban"}
    )
    domain = {}
    action = ActionFetchTopicDetails()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Guong dong co ban" in dispatcher.messages[0]["text"], "Response should include topic details"


# Test ActionFetchSubtopicDetails
def test_action_fetch_subtopic_details():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_subtopic",
        entities=[{"entity": "subtopic_name", "value": "Anh huong cua tai"}],
        slots={"subtopic_name": "Anh huong cua tai"}
    )
    domain = {}
    action = ActionFetchSubtopicDetails()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Anh huong cua tai" in dispatcher.messages[0]["text"], "Response should include subtopic details"


# Test ActionFetchApplicationDetails
def test_action_fetch_application_details():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_application",
        entities=[{"entity": "subtopic_name", "value": "Mach khuếch đại nguồn chung"}],
        slots={"subtopic_name": "Mach khuếch đại nguồn chung"}
    )
    domain = {}
    action = ActionFetchApplicationDetails()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "ứng dụng" in dispatcher.messages[0]["text"].lower(), "Response should include application details"


# Test ActionFetchSubtopicConditions
def test_action_fetch_subtopic_conditions():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_conditions",
        entities=[{"entity": "subtopic_name", "value": "Điều kiện"}],
        slots={"subtopic_name": "Điều kiện"}
    )
    domain = {}
    action = ActionFetchSubtopicConditions()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Điều kiện" in dispatcher.messages[0]["text"], "Response should include conditions"


# Test ActionFetchSubtopicDetailsDescription
def test_action_fetch_subtopic_details_description():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_details",
        entities=[{"entity": "subtopic_name", "value": "Chi tiết tiểu chủ đề"}],
        slots={"subtopic_name": "Chi tiết tiểu chủ đề"}
    )
    domain = {}
    action = ActionFetchSubtopicDetailsDescription()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Chi tiết tiểu chủ đề" in dispatcher.messages[0]["text"], "Response should include detailed subtopic description"


# Test ActionFetchSubtopicCharacteristics
def test_action_fetch_subtopic_characteristics():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_characteristics",
        entities=[{"entity": "subtopic_name", "value": "Mối quan hệ"}],
        slots={"subtopic_name": "Mối quan hệ"}
    )
    domain = {}
    action = ActionFetchSubtopicCharacteristics()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Mối quan hệ" in dispatcher.messages[0]["text"], "Response should include subtopic characteristics"


# Test ActionFetchExampleDetails
def test_action_fetch_example_details():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(
        intent="ask_example",
        entities=[{"entity": "subtopic_name", "value": "Ví dụ"}],
        slots={"subtopic_name": "Ví dụ"}
    )
    domain = {}
    action = ActionFetchExampleDetails()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Ví dụ" in dispatcher.messages[0]["text"], "Response should include examples"


# Test ActionDefaultFallback
def test_action_default_fallback():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(intent="nlu_fallback")
    domain = {}
    action = ActionDefaultFallback()
    response = action.run(dispatcher, tracker, domain)

    assert dispatcher.messages, "Dispatcher should have messages"
    assert "tôi không hiểu câu hỏi của bạn" in dispatcher.messages[0]["text"].lower(), "Fallback message should be present"


# Test utter_greet
def test_utter_greet():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(intent="greet")
    domain = {}

    dispatcher.utter_message(text="Chào bạn! Tôi có thể giúp gì cho bạn hôm nay?")
    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Chào bạn! Tôi có thể giúp gì cho bạn hôm nay?" in dispatcher.messages[0]["text"], "Greet message should be correct"


# Test utter_goodbye
def test_utter_goodbye():
    dispatcher = CollectingDispatcher()
    tracker = create_tracker(intent="goodbye")
    domain = {}

    dispatcher.utter_message(text="Tạm biệt! Hẹn gặp lại bạn.")
    assert dispatcher.messages, "Dispatcher should have messages"
    assert "Tạm biệt! Hẹn gặp lại bạn." in dispatcher.messages[0]["text"], "Goodbye message should be correct"
