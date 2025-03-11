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

# def find_similar_option_semantic(options: List[str], user_options: List[str]):



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

        correct_answer = qa["answes"]
        explanation = qa.get("explanation", "Нет объяснения")

        msg_type = ", ".join(type_ans)

        dispatcher.utter_message(f"{msg_type} Правильный ответ: {correct_answer}\nОбъяснение: {explanation}")

        return []

class ActionAnswerMultipleChoice(Action):
    def name(self) -> Text:
        return "action_answer_multiple_choice"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        user_parts = user_message.rsplit(" ", 1)  # Разбиваем по последнему пробелу
        type_ans = ["action_answer_multiple_choice"]

        if len(user_parts) < 2:
            dispatcher.utter_message("Пожалуйста, укажите ваш ответ вместе с вопросом.")
            return []

        user_question, user_answer = user_parts[0], user_parts[1]

        # Находим наиболее похожий вопрос
        qa, _ = find_similar_question_fuzz(user_question)  # Используем RapidFuzz для нахождения схожего вопроса
        correct_answer = qa["answes"]
        type_ans.append("fuzz")

        msg_type = ", ".join(type_ans)

        # Проверяем правильность ответа
        if user_answer.strip().lower() in correct_answer.strip().lower():
            dispatcher.utter_message(f"{msg_type} Вы выбрали правильный ответ: {user_answer}")
        else:
            dispatcher.utter_message(f"{msg_type} Неправильный ответ. Правильный ответ: {correct_answer}")

        return []
