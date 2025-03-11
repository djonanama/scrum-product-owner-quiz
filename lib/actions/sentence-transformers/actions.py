from rasa_sdk import Action
from sentence_transformers import SentenceTransformer, util
import json
import torch

class ActionAnswerQuestion(Action):
    def name(self):
        return "action_answer_question"

    def run(self, dispatcher, tracker, domain):
        question = tracker.latest_message.get("text")

        # Загружаем вопросы из JSON
        with open("questions.json", "r", encoding="utf-8") as f:
            questions_db = json.load(f)

        questions_list = list(questions_db.keys())  # Все вопросы

        # Загружаем предобученную модель для векторизации предложений
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # Кодируем вопрос пользователя и все вопросы из базы
        question_embedding = model.encode(question, convert_to_tensor=True)
        database_embeddings = model.encode(questions_list, convert_to_tensor=True)

        # Считаем косинусное сходство (поиск самого похожего вопроса)
        similarities = util.pytorch_cos_sim(question_embedding, database_embeddings)
        best_match_idx = torch.argmax(similarities)  # Индекс лучшего совпадения
        best_match_score = similarities[0][best_match_idx].item()

        if best_match_score >= 0.75:  # Если уверенность >= 75%
            best_match = questions_list[best_match_idx]
            response = questions_db[best_match]
            dispatcher.utter_message(text=f"✅ Best match: {best_match} (Score: {best_match_score:.2f})")


            dispatcher.utter_message(text=response["answers"])
            dispatcher.utter_message(text=response["explanation"])
        else:
            dispatcher.utter_message(text="I'm not sure about that. Can you rephrase?")

        return []
