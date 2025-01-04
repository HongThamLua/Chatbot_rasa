import time
import asyncio
import pytest
from rasa.core.agent import Agent
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from actions.actions import (
    ActionFetchChapterAndSuggestTopics,
    ActionFetchTopicDetails,
    ActionFetchSubtopicDetails,
    ActionFetchSubtopicDetailsDescription,
    ActionFetchApplicationDetails,
    ActionFetchSubtopicConditions,
    ActionFetchSubtopicCharacteristics,
    ActionFetchExampleDetails,
)

# Helper để tạo mock Tracker
def create_tracker(intent, entities=None, slots=None):
    if entities is None:
        entities = []
    if slots is None:
        slots = {}
    return Tracker(
        sender_id="test_user",
        slots=slots,
        latest_message={
            "intent": {"name": intent},
            "entities": entities,
        },
        events=[],
        paused=False,
        followup_action=None,
        active_loop={},
        latest_action_name="action_listen",
    )

# Test đo thời gian xử lý NLU với nhiều test case
@pytest.mark.asyncio
async def test_multiple_nlu_processing():
    agent = Agent.load("models")  # Load mô hình Rasa
    test_cases = [
        f"Câu hỏi mẫu {i}" for i in range(1, 101)  # 100 câu hỏi mẫu tự động
    ]
    for user_input in test_cases:
        start_time = time.time()
        response = await agent.handle_text(user_input)
        elapsed_time = time.time() - start_time
        print(f"[DEBUG] NLU Processing Time for '{user_input}': {elapsed_time:.4f} seconds")
        with open("performance_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"[DEBUG] NLU Processing Time for '{user_input}': {elapsed_time:.4f} seconds\n")

# Test đo thời gian phản hồi trong hội thoại thực tế
@pytest.mark.asyncio
async def test_full_conversation():
    agent = Agent.load("models")
    conversation = [
        f"Hội thoại câu hỏi {i}" for i in range(1, 21)  # 20 câu hỏi hội thoại tự động
    ]
    total_start_time = time.time()
    for user_input in conversation:
        start_time = time.time()
        response = await agent.handle_text(user_input)
        elapsed_time = time.time() - start_time
        print(f"[DEBUG] Response Time for '{user_input}': {elapsed_time:.4f} seconds")
        with open("performance_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"[DEBUG] Response Time for '{user_input}': {elapsed_time:.4f} seconds\n")
    total_elapsed_time = time.time() - total_start_time
    print(f"[DEBUG] Total Conversation Time: {total_elapsed_time:.4f} seconds")
    with open("performance_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[DEBUG] Total Conversation Time: {total_elapsed_time:.4f} seconds\n")

# Test đo thời gian thực thi từng action
@pytest.mark.asyncio
async def test_all_actions_execution():
    actions = [
        (ActionFetchChapterAndSuggestTopics, "ask_chapter", {"chapter_id": "1"}, [{"entity": "chapter_id", "value": "1"}]),
        (ActionFetchTopicDetails, "ask_topics", {"topic_name": "Guong dong co ban"}, [{"entity": "topic_name", "value": "Guong dong co ban"}]),
        (ActionFetchSubtopicDetails, "ask_subtopic", {"subtopic_name": "Anh huong cua tai"}, [{"entity": "subtopic_name", "value": "Anh huong cua tai"}]),
        (ActionFetchApplicationDetails, "ask_application", {"subtopic_name": "Anh huong cua tai"}, [{"entity": "subtopic_name", "value": "Anh huong cua tai"}]),
        (ActionFetchSubtopicConditions, "ask_conditions", {"subtopic_name": "Anh huong cua tai"}, [{"entity": "subtopic_name", "value": "Anh huong cua tai"}]),
        (ActionFetchSubtopicDetailsDescription, "ask_details", {"subtopic_name": "Anh huong cua tai"}, [{"entity": "subtopic_name", "value": "Anh huong cua tai"}]),
        (ActionFetchSubtopicCharacteristics, "ask_characteristics", {"subtopic_name": "Anh huong cua tai"}, [{"entity": "subtopic_name", "value": "Anh huong cua tai"}]),
        (ActionFetchExampleDetails, "ask_example", {"subtopic_name": "Anh huong cua tai"}, [{"entity": "subtopic_name", "value": "Anh huong cua tai"}]),
    ]

    for action_class, intent, slots, entities in actions:
        dispatcher = CollectingDispatcher()
        tracker = create_tracker(intent=intent, slots=slots, entities=entities)
        domain = {}

        action = action_class()
        start_time = time.time()
        events = action.run(dispatcher, tracker, domain)
        elapsed_time = time.time() - start_time
        print(f"[DEBUG] Action: {action.name()} Execution Time: {elapsed_time:.4f} seconds")
        with open("performance_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"[DEBUG] Action: {action.name()} Execution Time: {elapsed_time:.4f} seconds\n")
        assert elapsed_time < 2, f"{action.name()} execution quá lâu"

if __name__ == "__main__":
    asyncio.run(test_multiple_nlu_processing())
    asyncio.run(test_full_conversation())
    asyncio.run(test_all_actions_execution())
