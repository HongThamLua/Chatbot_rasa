import pymysql
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from fuzzywuzzy import fuzz, process  # Thư viện fuzzy matching

class ActionFetchChapterAndSuggestTopics(Action):
    def name(self):
        return "action_fetch_chapter_and_suggest_topics"

    def run(self, dispatcher, tracker, domain):
        # Lấy chapter_id từ slot
        chapter_id = tracker.get_slot("chapter_id")

        # Kết nối MySQL
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="analogcmos"
        )
        cursor = conn.cursor()

        # Truy vấn thông tin chương
        query_chapter = "SELECT Name, Description FROM chapter WHERE Chapter_id = %s"
        cursor.execute(query_chapter, (chapter_id,))
        chapter_result = cursor.fetchone()

        # Truy vấn danh sách chủ đề trong chương
        query_topics = "SELECT Name FROM topics WHERE Chapter_id = %s"
        cursor.execute(query_topics, (chapter_id,))
        topics_result = cursor.fetchall()

        # Xử lý phản hồi
        if chapter_result:
            name, description = chapter_result
            response = f"Chương {chapter_id}: {name} - {description}.\n\n"
        else:
            response = f"Tôi không tìm thấy thông tin về chương {chapter_id}.\n"
            dispatcher.utter_message(text=response)
            conn.close()
            return []

        # Gợi ý câu hỏi dựa trên danh sách chủ đề
        if topics_result:
            topic_names = [row[0] for row in topics_result]
            response += "Bạn muốn tìm hiểu thêm về chủ đề nào? Ví dụ:\n"
            for i, topic in enumerate(topic_names, start=1):
                response += f"- {i}. {topic}\n"
        else:
            response += "Hiện không có chủ đề nào được liên kết với chương này."

        dispatcher.utter_message(text=response)
        conn.close()
        return []

class ActionFetchTopicDetails(Action):
    def name(self):
        return "action_fetch_topic_details"

    def run(self, dispatcher, tracker, domain):
        # Lấy topic_name từ slot
        topic_name = tracker.get_slot("topic_name")

        if not topic_name:
            dispatcher.utter_message(text="Tôi không nhận được thông tin về chủ đề bạn muốn tìm.")
            return []

        try:
            # Kết nối MySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="analogcmos"
            )
            cursor = conn.cursor()

            # Truy vấn tất cả các chủ đề từ bảng topics để tìm kiếm gần đúng
            query_all_topics = "SELECT Name FROM topics"
            cursor.execute(query_all_topics)
            all_topics = [row[0] for row in cursor.fetchall()]

            # Sử dụng fuzzy matching để tìm chủ đề phù hợp nhất
            best_match = process.extractOne(topic_name, all_topics, scorer=fuzz.token_sort_ratio)

            if best_match and best_match[1] >= 90:  # Ngưỡng độ chính xác 80%
                matched_topic_name = best_match[0]

                # Truy vấn chi tiết về chủ đề khớp
                query_topic = "SELECT topic_id, Description FROM topics WHERE Name = %s"
                cursor.execute(query_topic, (matched_topic_name,))
                topic_result = cursor.fetchone()

                if topic_result:
                    topic_id, description = topic_result
                    response = f"Chi tiết về chủ đề '{matched_topic_name}': {description}\n\n"
                else:
                    response = f"Tôi không tìm thấy thông tin cho chủ đề '{matched_topic_name}'."
                    dispatcher.utter_message(text=response)
                    return []

                # Truy vấn danh sách subtopics trong topic
                query_subtopics = "SELECT Name FROM subtopics WHERE Topic_id = %s"
                cursor.execute(query_subtopics, (topic_id,))
                subtopics_result = cursor.fetchall()

                # Gợi ý câu hỏi dựa trên danh sách subtopics
                if subtopics_result:
                    subtopic_names = [row[0] for row in subtopics_result]
                    response += "Bạn muốn tìm hiểu thêm về tiểu chủ đề nào? Ví dụ:\n"
                    for i, subtopic in enumerate(subtopic_names, start=1):
                        response += f"- {i}. {subtopic}\n"
                else:
                    response += "Hiện không có tiểu chủ đề nào được liên kết với chủ đề này."
            else:
                response = f"Tôi không tìm thấy chủ đề phù hợp với '{topic_name}'. Bạn có thể thử nhập lại tên khác."

        except pymysql.Error as e:
            response = f"Lỗi truy vấn cơ sở dữ liệu: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

        dispatcher.utter_message(text=response)
        return []

class ActionFetchSubtopicDetails(Action):
    def name(self):
        return "action_fetch_subtopic_details"

    def run(self, dispatcher, tracker, domain):
        # Lấy subtopic_name từ slot
        subtopic_name = tracker.get_slot("subtopic_name")

        if not subtopic_name:
            dispatcher.utter_message(text="Tôi không nhận được thông tin về tiểu chủ đề bạn muốn hỏi.")
            return []

        try:
            # Kết nối MySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="analogcmos"
            )
            cursor = conn.cursor()

            # Truy vấn tất cả subtopics để fuzzy matching
            query_all_subtopics = "SELECT Name FROM subtopics"
            cursor.execute(query_all_subtopics)
            all_subtopics = [row[0] for row in cursor.fetchall()]

            # Tìm subtopic gần đúng
            best_match = process.extractOne(subtopic_name, all_subtopics, scorer=fuzz.token_sort_ratio)

            if best_match and best_match[1] >= 80:  # Ngưỡng độ chính xác 80%
                matched_subtopic_name = best_match[0]

                # Truy vấn chi tiết về subtopic
                query_subtopic = "SELECT subtopic_id, Description FROM subtopics WHERE lower(Name) LIKE lower(%s)"
                cursor.execute(query_subtopic, (f"%{subtopic_name}%",))
                subtopic_result = cursor.fetchone()

                if subtopic_result:
                    subtopic_id, description = subtopic_result
                    response = f"Chi tiết về tiểu chủ đề '{subtopic_name}': {description}\n\n"
                else:
                    response = f"Tôi không tìm thấy thông tin cho tiểu chủ đề '{subtopic_name}'."
                    dispatcher.utter_message(text=response)
                    return []

                # Truy vấn từ bảng details
                query_details = "SELECT Description, Conditions, Characteristics FROM details WHERE Subtopic_id = %s"
                cursor.execute(query_details, (subtopic_id,))
                details_result = cursor.fetchone()

                if details_result:
                    detail_desc, conditions, characteristics = details_result
                    response += (
                        f"Bạn có thể hỏi thêm:\n"
                        f"1. Mô tả kỹ hơn: {detail_desc}\n"
                        f"2. Điều kiện: {conditions}\n"
                        f"3. Mối quan hệ cần quan tâm: {characteristics}\n"
                    )
                else:
                    response += "Hiện không có thông tin chi tiết về tiểu chủ đề này.\n"

                # Gợi ý nếu người dùng hỏi về ví dụ cụ thể hoặc ứng dụng
                if "Mối quan hệ cần quan tâm" in response:
                    query_examples = "SELECT Example_description, Application FROM examples WHERE Detail_id = %s"
                    cursor.execute(query_examples, (subtopic_id,))
                    examples_result = cursor.fetchall()

                    if examples_result:
                        response += "Bạn có thể hỏi thêm:\n"
                        for example_desc, application in examples_result:
                            response += f"- Ví dụ cụ thể: {example_desc}\n"
                            response += f"- Ứng dụng: {application}\n"
                else:
                    response += "Không có ví dụ hoặc ứng dụng liên quan.\n"
            else:
                response += "Không có thông tin thêm.\n"

        except pymysql.Error as e:
            response = f"Lỗi truy vấn cơ sở dữ liệu: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

        dispatcher.utter_message(text=response)
        return []

class ActionFetchApplicationDetails(Action):
    def name(self):
        return "action_fetch_application_details"

    def run(self, dispatcher, tracker, domain):
        # Lấy subtopic_name từ slot
        subtopic_name = tracker.get_slot("subtopic_name")

        if not subtopic_name:
            dispatcher.utter_message(text="Tôi không nhận được thông tin về tiểu chủ đề bạn muốn hỏi.")
            return []

        try:
            # Kết nối MySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="analogcmos"
            )
            cursor = conn.cursor()

            # Truy vấn tất cả subtopics để fuzzy matching
            query_all_subtopics = "SELECT Name FROM subtopics"
            cursor.execute(query_all_subtopics)
            all_subtopics = [row[0] for row in cursor.fetchall()]

            # Tìm subtopic gần đúng
            best_match = process.extractOne(subtopic_name, all_subtopics, scorer=fuzz.token_sort_ratio)

            if best_match and best_match[1] >= 80:
                matched_subtopic_name = best_match[0]

                # Truy vấn chi tiết về subtopic để lấy Subtopic_id
                query_subtopic = "SELECT subtopic_id FROM subtopics WHERE lower(Name) LIKE lower(%s)"
                cursor.execute(query_subtopic, (f"%{subtopic_name}%",))
                subtopic_result = cursor.fetchone()

                if subtopic_result:
                    subtopic_id = subtopic_result[0]
                else:
                    dispatcher.utter_message(text=f"Tôi không tìm thấy thông tin về tiểu chủ đề '{subtopic_name}'.")
                    return []

                # Truy vấn thông tin về ứng dụng từ bảng examples
                query_application = "SELECT Application FROM examples WHERE Detail_id = %s"
                cursor.execute(query_application, (subtopic_id,))
                applications_result = cursor.fetchall()

                if applications_result:
                    response = f"Ứng dụng của '{subtopic_name}':\n"
                    for i, app in enumerate(applications_result, start=1):
                        response += f"- {i}. {app[0]}\n"
                else:
                    response = f"Hiện không có thông tin về ứng dụng của '{subtopic_name}'."
            else:
                response = f"Hiện không có thông tin về ứng dụng của '{subtopic_name}'."

        except pymysql.Error as e:
            response = f"Lỗi truy vấn cơ sở dữ liệu: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

        dispatcher.utter_message(text=response)
        return []

class ActionFetchSubtopicConditions(Action):
    def name(self):
        return "action_fetch_subtopic_conditions"

    def run(self, dispatcher, tracker, domain):
        # Lấy subtopic_name từ slot
        subtopic_name = tracker.get_slot("subtopic_name")

        if not subtopic_name:
            dispatcher.utter_message(text="Tôi không nhận được thông tin về tiểu chủ đề bạn muốn hỏi.")
            return []

        try:
            # Kết nối MySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="analogcmos"
            )
            cursor = conn.cursor()

            # Truy vấn tất cả subtopics để fuzzy matching
            query_all_subtopics = "SELECT Name FROM subtopics"
            cursor.execute(query_all_subtopics)
            all_subtopics = [row[0] for row in cursor.fetchall()]

            # Tìm subtopic gần đúng
            best_match = process.extractOne(subtopic_name, all_subtopics, scorer=fuzz.token_sort_ratio)

            if best_match and best_match[1] >= 80:
                matched_subtopic_name = best_match[0]

                # Truy vấn Id của subtopic
                query_subtopic = "SELECT subtopic_id FROM subtopics WHERE lower(Name) LIKE lower(%s)"
                cursor.execute(query_subtopic, (f"%{subtopic_name}%",))
                subtopic_result = cursor.fetchone()

                if subtopic_result:
                    subtopic_id = subtopic_result[0]
                else:
                    dispatcher.utter_message(text=f"Tôi không tìm thấy thông tin cho tiểu chủ đề '{subtopic_name}'.")
                    return []

                # Truy vấn điều kiện từ bảng details
                query_conditions = "SELECT Conditions FROM details WHERE Subtopic_id = %s"
                cursor.execute(query_conditions, (subtopic_id,))
                conditions_result = cursor.fetchone()

                if conditions_result:
                    response = f"Điều kiện của '{subtopic_name}': {conditions_result[0]}"
                else:
                    response = f"Không có thông tin về điều kiện của '{subtopic_name}'."
            else:
                response = f"Không có thông tin về điều kiện của '{subtopic_name}'."

        except pymysql.Error as e:
            response = f"Lỗi truy vấn cơ sở dữ liệu: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

        dispatcher.utter_message(text=response)
        return []

class ActionFetchSubtopicDetailsDescription(Action):
    def name(self):
        return "action_fetch_subtopic_details_description"

    def run(self, dispatcher, tracker, domain):
        # Lấy subtopic_name từ slot
        subtopic_name = tracker.get_slot("subtopic_name")

        if not subtopic_name:
            dispatcher.utter_message(text="Tôi không nhận được thông tin về tiểu chủ đề bạn muốn hỏi.")
            return []

        try:
            # Kết nối MySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="analogcmos"
            )
            cursor = conn.cursor()

            # Truy vấn tất cả subtopics để fuzzy matching
            query_all_subtopics = "SELECT Name FROM subtopics"
            cursor.execute(query_all_subtopics)
            all_subtopics = [row[0] for row in cursor.fetchall()]

            # Tìm subtopic gần đúng
            best_match = process.extractOne(subtopic_name, all_subtopics, scorer=fuzz.token_sort_ratio)

            if best_match and best_match[1] >= 80:
                matched_subtopic_name = best_match[0]

                # Truy vấn Id của subtopic
                query_subtopic = "SELECT subtopic_id FROM subtopics WHERE lower(Name) LIKE lower(%s)"
                cursor.execute(query_subtopic, (f"%{subtopic_name}%",))
                subtopic_result = cursor.fetchone()

                if subtopic_result:
                    subtopic_id = subtopic_result[0]
                else:
                    dispatcher.utter_message(text=f"Tôi không tìm thấy thông tin cho tiểu chủ đề '{subtopic_name}'.")
                    return []

                # Truy vấn mô tả kỹ hơn từ bảng details
                query_description = "SELECT Description FROM details WHERE Subtopic_id = %s"
                cursor.execute(query_description, (subtopic_id,))
                description_result = cursor.fetchone()

                if description_result:
                    response = f"Mô tả kỹ hơn về '{subtopic_name}': {description_result[0]}"
                else:
                    response = f"Không có thông tin mô tả thêm về '{subtopic_name}'."
            else:
                response = f"Không có thông tin mô tả thêm về '{subtopic_name}'."

        except pymysql.Error as e:
            response = f"Lỗi truy vấn cơ sở dữ liệu: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

        dispatcher.utter_message(text=response)
        return []


class ActionFetchSubtopicCharacteristics(Action):
    def name(self):
        return "action_fetch_subtopic_characteristics"

    def run(self, dispatcher, tracker, domain):
        # Lấy subtopic_name từ slot
        subtopic_name = tracker.get_slot("subtopic_name")

        if not subtopic_name:
            dispatcher.utter_message(text="Tôi không nhận được thông tin về tiểu chủ đề bạn muốn hỏi.")
            return []

        try:
            # Kết nối MySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="analogcmos"
            )
            cursor = conn.cursor()

            # Truy vấn tất cả subtopics để fuzzy matching
            query_all_subtopics = "SELECT Name FROM subtopics"
            cursor.execute(query_all_subtopics)
            all_subtopics = [row[0] for row in cursor.fetchall()]

            # Tìm subtopic gần đúng
            best_match = process.extractOne(subtopic_name, all_subtopics, scorer=fuzz.token_sort_ratio)

            if best_match and best_match[1] >= 80:
                matched_subtopic_name = best_match[0]

                # Truy vấn Id của subtopic
                query_subtopic = "SELECT subtopic_id FROM subtopics WHERE lower(Name) LIKE lower(%s)"
                cursor.execute(query_subtopic, (f"%{subtopic_name}%",))
                subtopic_result = cursor.fetchone()

                if subtopic_result:
                    subtopic_id = subtopic_result[0]
                else:
                    dispatcher.utter_message(text=f"Tôi không tìm thấy thông tin cho tiểu chủ đề '{subtopic_name}'.")
                    return []

                # Truy vấn mối quan hệ từ bảng details
                query_characteristics = "SELECT Characteristics FROM details WHERE Subtopic_id = %s"
                cursor.execute(query_characteristics, (subtopic_id,))
                characteristics_result = cursor.fetchone()

                if characteristics_result:
                    response = f"Mối quan hệ cần quan tâm về '{subtopic_name}': {characteristics_result[0]}"

                    # Đề xuất ví dụ cụ thể
                    query_examples = "SELECT Example_description FROM examples WHERE Detail_id = %s"
                    cursor.execute(query_examples, (subtopic_id,))
                    examples_result = cursor.fetchall()

                    if examples_result:
                        response += "\n\nBạn có muốn xem ví dụ cụ thể không? Các ví dụ gồm:\n"
                        for i, example in enumerate(examples_result, start=1):
                            response += f"- {i}. {example[0]}\n"
                else:
                    response = f"Không có thông tin mối quan hệ về '{subtopic_name}'."
            else:
                response = f"Không có thông tin mối quan hệ về '{subtopic_name}'."

        except pymysql.Error as e:
            response = f"Lỗi truy vấn cơ sở dữ liệu: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

        dispatcher.utter_message(text=response)
        return []

class ActionFetchExampleDetails(Action):
    def name(self):
        return "action_fetch_example_details"

    def run(self, dispatcher, tracker, domain):
        # Lấy subtopic_name từ slot
        subtopic_name = tracker.get_slot("subtopic_name")

        if not subtopic_name:
            dispatcher.utter_message(text="Tôi không nhận được thông tin về tiểu chủ đề bạn muốn hỏi.")
            return []

        try:
            # Kết nối MySQL
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="1234",
                database="analogcmos"
            )
            cursor = conn.cursor()

            # Truy vấn tất cả subtopics để fuzzy matching
            query_all_subtopics = "SELECT Name FROM subtopics"
            cursor.execute(query_all_subtopics)
            all_subtopics = [row[0] for row in cursor.fetchall()]

            # Tìm subtopic gần đúng
            best_match = process.extractOne(subtopic_name, all_subtopics, scorer=fuzz.token_sort_ratio)

            if best_match and best_match[1] >= 80:
                matched_subtopic_name = best_match[0]

                # Truy vấn Id của subtopic
                query_subtopic = "SELECT subtopic_id FROM subtopics WHERE lower(Name) LIKE lower(%s)"
                cursor.execute(query_subtopic, (f"%{subtopic_name}%",))
                subtopic_result = cursor.fetchone()

                if subtopic_result:
                    subtopic_id = subtopic_result[0]
                else:
                    dispatcher.utter_message(text=f"Tôi không tìm thấy thông tin cho tiểu chủ đề '{subtopic_name}'.")
                    return []

                # Truy vấn ví dụ từ bảng examples
                query_examples = "SELECT Example_description, Application FROM examples WHERE Detail_id = %s"
                cursor.execute(query_examples, (subtopic_id,))
                examples_result = cursor.fetchall()

                if examples_result:
                    response = f"Các ví dụ về '{subtopic_name}':\n"
                    for i, (example_desc, application) in enumerate(examples_result, start=1):
                        response += f"- Ví dụ {i}: {example_desc}\n"
                        response += f"  Ứng dụng: {application}\n"
                else:
                    response = f"Không có ví dụ cụ thể nào cho tiểu chủ đề '{subtopic_name}'."
            else:
                response = f"Không có ví dụ cụ thể nào cho tiểu chủ đề '{subtopic_name}'."

        except pymysql.Error as e:
            response = f"Lỗi truy vấn cơ sở dữ liệu: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

        dispatcher.utter_message(text=response)
        return []