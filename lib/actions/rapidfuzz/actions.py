from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rapidfuzz import process, fuzz  # Добавляем fuzzy-поиск
import json

class ActionAnswerQuestion(Action):
    def name(self):
        return "action_answer_question"

    def run(self, dispatcher, tracker, domain):
        question = tracker.latest_message.get("text")  # Получаем сообщение пользователя

        # Загружаем вопросы из JSON-файла
        with open("questions.json", "r", encoding="utf-8") as f:
            questions_db = json.load(f)

        questions_list = list(questions_db.keys())  # Все вопросы из БД

        # Ищем наиболее похожий вопрос (порог похожести - 80%)
        best_match, score = process.extractOne(question, questions_list, scorer=fuzz.ratio)

        if score >= 80:  # Если уверенность >= 80%, отвечаем
            response = questions_db[best_match]
            dispatcher.utter_message(text=f"✅ Best match: {best_match}")
            dispatcher.utter_message(text=response["answers"])
            dispatcher.utter_message(text=response["explanation"])
        else:
            dispatcher.utter_message(text="I'm not sure about that. Can you rephrase?")

        return []
