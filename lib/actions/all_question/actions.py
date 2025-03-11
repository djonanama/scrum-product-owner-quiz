from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import json
from sentence_transformers import SentenceTransformer
import numpy as np

# Загружаем вопросы
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS_DB = json.load(f)

# Загружаем модель SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Создаём эмбеддинги для всех вопросов
question_texts = [q["question"] for q in QUESTIONS_DB]
question_embeddings = model.encode(question_texts)

class AnswerQuestion(Action):
    def name(self):
        return "action_answer_question"

    def run(self, dispatcher, tracker, domain):
        user_question = tracker.latest_message['text']
        intent = tracker.latest_message.get("intent", {}).get("name")

        # Если NLU нашёл точное совпадение — используем его
        if intent and intent.startswith("question_"):
            intent_index = int(intent.split("_")[1])  # Получаем номер вопроса из intent
            best_match = QUESTIONS_DB[intent_index]
        else:
            # Если точного совпадения нет — применяем семантический поиск
            user_embedding = model.encode([user_question])[0]
            similarities = np.dot(question_embeddings, user_embedding)
            best_match_idx = np.argmax(similarities)
            best_match = QUESTIONS_DB[best_match_idx]

        # Формируем ответ
        correct_answers =best_match["answers"]
        explanation = best_match["explanation"]

        dispatcher.utter_message(text=f"✅ The correct answer is: {correct_answers}")
        dispatcher.utter_message(text=f"📌 Explanation: {explanation}")

        return [SlotSet("answers", best_match["answers"])]
