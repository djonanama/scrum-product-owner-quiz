import json
import yaml

# Загружаем JSON с вопросами
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS_DB = json.load(f)

version_yml = "3.1"

# Создаём структуру YAML для NLU
nlu_data = {
    "version": version_yml,
    "nlu": [
        { "intent": "ask_question", "examples" : [] },
        { "intent": "multiple_choice_question", "examples" : [] },
    ]
}

# Создаём структуру YAML для domain
domain_data = {
    "version": version_yml,
    "intents": ["query_question"],
    "responses": {},
    "actions": ["action_answer_question"]
}

# Создаём структуру YAML для stories
stories_data = {
    "version": version_yml,
    "stories": []
}

for index, q in enumerate(QUESTIONS_DB):
    intent_name = f"question_{index}"
    explanation_name = f"explanation_{index}"

    # Формируем вариант ответа
    options = [f"[{q['options'][opt]}](option)" for opt in q['options']]
    nlu_option = " ; ".join(options)

    nlu_data["nlu"][0]["examples"].append(f"- {q['question']}")
    nlu_data["nlu"][1]["examples"].append(f"- [{q['question']}](question) {nlu_option}")

    domain_data["intents"].append(intent_name)

    # Формируем ответ
    text_response = " ".join(q["answers"].split('\n'))
    text_response = "Yes" if text_response == "True" else "No" if text_response == "False" else text_response
    domain_data["responses"][f"utter_{intent_name}"] = [{"text": text_response}]
    domain_data["actions"].append(f"utter_{intent_name}")

    # Формируем story
    stories_data["stories"].append({
        "story": f"Answer Question {index}",
        "steps": [
            {"intent": intent_name},
            {"action": f"utter_{intent_name}"}
        ]
    })

# Записываем в nlu.yml
def dict_to_yaml(data, indent=0):
    yaml_str = ""
    spaces = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            yaml_str += f"{spaces}{key}:"
            if isinstance(value, (dict, list)):
                yaml_str += "\n" + dict_to_yaml(value, indent + 1)
            else:
                yaml_str += f" {value}\n"
    elif isinstance(data, list):
        for item in data:
            yaml_str += f"{spaces}-"
            if isinstance(item, (dict, list)):
                yaml_str += "\n" + dict_to_yaml(item, indent + 1)
            else:
                yaml_str += f" {item}\n"

    return yaml_str

# Генерируем YAML вывод в нужном формате
def generate_yaml(data):
    result = "version: '{}'\n".format(data['version'])
    result += "nlu:\n"

    for item in data['nlu']:
        result += "  - intent: {}\n".format(item["intent"])
        result += "    examples: |\n"
        for example in item["examples"]:
            result += "      {}\n".format(example.replace('\n', ' ').strip())

    # result += "domain:\n"
    # result += "  version: '{}'\n".format(data['version'])
    # result += "  intents:\n"
    # for intent in domain_data["intents"]:
    #     result += "    - {}\n".format(intent)

    # result += "  responses:\n"
    # for response in domain_data["responses"]:
    #     result += "    utter_{}:\n".format(response.split('_')[1])
    #     result += "      - text: {}\n".format(domain_data["responses"][response][0]["text"])

    # result += "  actions:\n"
    # for action in domain_data["actions"]:
    #     result += "    - {}\n".format(action)

    # result += "stories:\n"
    # for story in stories_data["stories"]:
    #     result += "  - story: {}\n".format(story["story"])
    #     result += "    steps:\n"
    #     for step in story["steps"]:
    #         result += "      - intent: {}\n".format(step.get('intent', ''))
    #         result += "      - action: {}\n".format(step.get('action', ''))

    return result

# Выводим результат в формате YAML
yaml_output = generate_yaml({
    'version': version_yml,
    'nlu': nlu_data['nlu']
})

with open("../data/nlu.yml", "w", encoding="utf-8") as f:
    f.write(yaml_output)
