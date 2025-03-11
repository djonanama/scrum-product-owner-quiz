import json
import re

def parse_test_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []
    question_blocks = re.split(r'Question \d+:\n', content)[1:]  # Разбиваем текст по "Question X:"

    for block in question_blocks:
        parts = re.split(r'\n\nAnswer: ', block)
        if len(parts) < 2:
            continue

        question_and_options = parts[0].strip('\n').split('\n')
        question_text = question_and_options[0].strip()
        options = question_and_options[1:]

        answer_expl = parts[1].split('\n\nExplanation\n')
        answer_keys = [a.strip().rstrip('.') for a in answer_expl[0].split(',')]
        explanation = answer_expl[1].strip() if len(answer_expl) > 1 else ""

        variants = {}
        idx_variant = 0;
        option_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']  # Поддержка нескольких вариантов
        for idx, option in enumerate(options):
            if len(option) < 1 or "(choose" in option or "All of the above" in option :
                continue

            variants[option_labels[idx_variant]] = option.strip().rstrip('.')
            idx_variant+=1

        correct_answers = " and ".join(variants[ans] for ans in answer_keys)
        correct_answers = "Yes" if correct_answers == "True" else "No" if correct_answers == "False" else correct_answers

        if "____" in question_text:
            correct_answers = re.sub(r'____.*', correct_answers,question_text)

        question_text = re.sub(r' \(choose.*', '', question_text.strip())
        question_text = re.sub(r'\? Choose.*', '?', question_text)
        question_text = re.sub(r'\. Choose.*', '?', question_text)

        questions.append({
            "question": question_text,
            "options": variants,
            "answer": answer_keys,
            "answers": correct_answers,
            "explanation": explanation
        })

    return questions

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Использование
file_path = "questions.txt"  # Укажи путь к своему файлу
output_file = "questions.json"
parsed_data = parse_test_file(file_path)
save_to_json(parsed_data, output_file)
print(f"✅ Parsed data saved to {output_file}")
