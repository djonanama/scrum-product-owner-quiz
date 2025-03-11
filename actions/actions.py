import json
import numpy as np
from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz
from scipy.spatial.distance import cosine
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Загружаем данные из JSON-файла
def load_questions_data(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

# Загружаем все вопросы из JSON
QA_DATABASE = load_questions_data('scripts/questions.json')

# Инициализация модели для sentence-transformers
model = SentenceTransformer('all-MiniLM-L6-v2')

# Функция для нахождения наиболее похожего вопроса с использованием sentence-transformers
def find_similar_question_semantic(user_question: str):
    # Преобразуем пользовательский вопрос в вектор (убираем лишнюю ось)
    user_question_embedding = model.encode([user_question]).squeeze()

    similarities = []
    for qa in QA_DATABASE:
        question_embedding = model.encode([qa["question"]]).squeeze()
        similarity = 1 - cosine(user_question_embedding, question_embedding)  # Преобразуем в меру схожести
        similarities.append((qa, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)  # Чем выше, тем лучше
    return similarities[0]  # Возвращаем кортеж (qa, similarity)

def find_similar_option_semantic(correct_options: List[str], user_options: List[str]):
    result = []

    for uqa in user_options:
        similarities = []
        for cqa in correct_options:
            similarity = 1 - cosine(model.encode([uqa]).squeeze(), model.encode([cqa]).squeeze())
            similarities.append((cqa, uqa, similarity))
        similarities.sort(key=lambda x: x[2], reverse=True)  # Чем выше, тем лучше
        result.append(similarities[0])

    return result

# Функция для нахождения наиболее похожего вопроса с использованием RapidFuzz
def find_similar_question_fuzz(user_question: str):
    similarities = []
    for qa in QA_DATABASE:
        similarity = fuzz.ratio(user_question.lower(), qa["question"].lower()) / 100.0  # Нормируем к 0-1
        similarities.append((qa, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)  # Чем выше, тем лучше
    return similarities[0]  # Возвращаем кортеж (qa, similarity)

class ActionAnswerQuestion(Action):
    def name(self) -> Text:
        return "action_answer_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_question = tracker.latest_message.get("text")
        type_ans = ["action_answer_question"]

        # Используем оба подхода
        semantic_match, semantic_score = find_similar_question_semantic(user_question)
        fuzz_match, fuzz_score = find_similar_question_fuzz(user_question)

        # Определяем лучший метод
        if fuzz_score >= semantic_score:
            type_ans.append("fuzz")
            qa = fuzz_match
        else:
            type_ans.append("semantic")
            qa = semantic_match

        correct_answer = qa["answers"]
        explanation = qa.get("explanation", "Explanation not found.")

        msg_type = ", ".join(type_ans)

        dispatcher.utter_message(f"{msg_type} \n\n\nCorrect answer: ✅ {correct_answer}\n\n\n Explanation: {explanation}")

        return []

class ActionAnswerMultipleChoice(Action):
    def name(self) -> Text:
        return "action_answer_multiple_choice"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        type_ans = ["action_answer_multiple_choice"]

        user_message = tracker.latest_message.get("text")
        user_parts = user_message.rsplit("\n")

        if len(user_parts) < 2:
            dispatcher.utter_message("Invalid input format.")
            return []

        user_question, user_options = user_parts[0], user_parts[1:]

        if len(user_question) < 2:
            dispatcher.utter_message("Invalid question.")
            return []

        # Используем оба подхода
        semantic_match, semantic_score = find_similar_question_semantic(user_question)
        fuzz_match, fuzz_score = find_similar_question_fuzz(user_question)

        # Определяем лучший метод
        if fuzz_score >= semantic_score:
            type_ans.append("fuzz")
            qa = fuzz_match
        else:
            type_ans.append("semantic")
            qa = semantic_match

        correct_options = []
        user_options = [s for s in user_options if s.strip()]

        for idx in qa["answer"]:
            correct_options.append(qa["options"][idx])

        correct_options_with_score = find_similar_option_semantic(correct_options, user_options)

        score_options_show = []

        for cows in correct_options_with_score:
            score_options_show.append(f"{cows[1]} score:{round(cows[2]*100,2)}%")

        score_options_show = "\n ".join(score_options_show)

        correct_answer = qa["answers"]
        explanation = qa.get("explanation", "Explanation not found.")

        msg_type = ", ".join(type_ans)

        dispatcher.utter_message(f"{msg_type}\n\n score:\n {score_options_show} \n\n\n Correct answer:✅ {correct_answer} \n\n Explanation: {explanation}")

        return []
