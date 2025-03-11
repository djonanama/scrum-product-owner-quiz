import re
import random
import time

# Colors
RESET = "\033[0m"
QUESTION_COLOR = "\033[96m"     # light blue
OPTION_COLOR = "\033[93m"       # light yellow
CORRECT_COLOR = "\033[92m"      # light green
INCORRECT_COLOR = "\033[91m"    # light red
EXPLANATION_COLOR = "\033[95m"  # light purple
DEFAULT_COLOR = "\033[97m"      # light white

def format_time(seconds):
    """
    Convert seconds to a formatted string: X hours, Y minutes, Z.ZZ seconds.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = seconds % 60
    return f"{hours} hours, {minutes} minutes, {sec:.2f} seconds"

def parse_questions(filename):
    """
    Reads and parses the question bank from a file.
    Expected structure for each question block:
    
      Question <number>:
      <question statement paragraphs>
      
      <answer option lines>
      
      Answer: <correct answer letters, e.g., D or C, D>
      [Explanation
      <explanation text>]

    If the text after "Question" can be split into two or more paragraphs (by double newline),
    then all paragraphs except the last one are part of the question text,
    and the last paragraph is considered as the answer options.
    Otherwise, fallback to previous logic.
    """
    with open(filename, encoding='utf-8') as f:
        content = f.read()

    pattern = r"Question\s+\d+:\s*(.*?)\s*Answer:\s*(.*?)(?:\s*Explanation\s*(.*?))?(?=Question\s+\d+:|$)"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    questions = []
    for match in matches:
        full_text, ans, expl = match
        full_text = full_text.strip()
        ans = ans.strip()
        expl = expl.strip() if expl else None

        # Split blocks into paragraphs
        paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        if len(paragraphs) >= 2:
            question_statement = " ".join(paragraphs[:-1])
            options_text = paragraphs[-1]
            answer_options = [line.strip() for line in options_text.splitlines() if line.strip()]
        else:
            lines = [line.strip() for line in full_text.splitlines() if line.strip()]
            if len(lines) >= 3:
                question_statement = " ".join(lines[:2])
                answer_options = lines[2:]
            elif len(lines) == 2:
                question_statement = " ".join(lines)
                answer_options = []
            else:
                question_statement = full_text
                answer_options = []
        
        questions.append({
            'question': question_statement,
            'options': answer_options,
            'answer': ans,
            'explanation': expl
        })
    return questions

def normalize_answer(answer):
    """
    Normalize an answer string: remove dots and commas,
    convert to uppercase, and split into a set of answer tokens.
    """
    answer = answer.replace('.', '').replace(',', ' ')
    return set(answer.upper().split())

def quiz(questions, colors):
    """
    Runs the quiz by displaying each question along with its options,
    accepting user input, checking the answer, and showing the result
    along with the explanation (if available).
    If the user enters 'exit', the quiz terminates immediately and results are displayed.
    Additionally, it shows the time spent on each question and the cumulative test time.
    """
    score = 0
    attempted = 0
    total_time = 0.0
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    for i, q in enumerate(questions, start=1):
        print(colors["question"] + f"\nQuestion {i}:" + RESET)
        print(colors["question"] + q['question'] + RESET)
        if q['options']:
            print(colors["option"] + "\nOptions:" + RESET)
            for idx, option in enumerate(q['options']):
                if idx < len(letters):
                    print(colors["option"] + f"{letters[idx]}) {option}" + RESET)
                else:
                    print(colors["option"] + option + RESET)
        
        start_time = time.time()
        user_ans = input(colors["default"] + "\nYour answer: ")
        print(RESET, end="")
        question_time = time.time() - start_time
        total_time += question_time
        
        if user_ans.strip().upper() == "EXIT":
            break

        attempted += 1
        
        correct_set = normalize_answer(q['answer'])
        user_set = normalize_answer(user_ans.strip().upper())
        
        if user_set == correct_set:
            print(colors["correct"] + "\n✅ Correct!\n" + RESET)
            score += 1
        else:
            print(colors["incorrect"] + "\n❌ Incorrect.\n" + RESET)
            print(colors["incorrect"] + f"Correct answer: {q['answer']}\n" + RESET)
        
        if q['explanation']:
            explanation_clean = "\n".join([line for line in q['explanation'].splitlines() if line.strip()])
            print(colors["explanation"] + f"Explanation:\n{explanation_clean}\n" + RESET)
        
        print(colors["default"] + f"Time for this question: {format_time(question_time)}" + RESET)
        print(colors["default"] + f"Total test time so far: {format_time(total_time)}\n" + RESET)
        print(colors["default"] + "=" * 50 + RESET)
    
    incorrect = attempted - score
    percentage = (score / attempted) * 100 if attempted else 0
    print(colors["default"] + f"\nTotal test time: {format_time(total_time)}" + RESET)
    print(colors["default"] + f"Correct {score} out of {attempted} questions ({percentage:.2f}% correct)" + RESET)

def main():
    questions = parse_questions("bank.txt")
    
    # Color scheme
    use_color = input("Use color scheme? (yes/no, default yes): ").strip().lower()
    if use_color in ("", "yes", "y"):
        colors = {
            "question": QUESTION_COLOR,
            "option": OPTION_COLOR,
            "correct": CORRECT_COLOR,
            "incorrect": INCORRECT_COLOR,
            "explanation": EXPLANATION_COLOR,
            "default": DEFAULT_COLOR
        }
    else:
        colors = {
            "question": "",
            "option": "",
            "correct": "",
            "incorrect": "",
            "explanation": "",
            "default": ""
        }
    
    if not questions:
        print(colors["incorrect"] + "Failed to parse questions from the file" + RESET)
        return

    choice = input(colors["default"] + "Random question order? (yes/no, default yes): ")
    print(RESET, end="")
    choice = choice.strip().lower()
    if choice in ("", "yes", "y"):
        random.shuffle(questions)

    print(colors["default"] + f"\nTotal questions in the bank: {len(questions)}" + RESET)
    print(colors["default"] + "Answer input format: a/a,b,c" + RESET)
    print(colors["default"] + "Enter 'exit' to finish" + RESET)
    
    quiz(questions, colors)

if __name__ == "__main__":
    main()