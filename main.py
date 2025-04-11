import psycopg2
import random

conn = psycopg2.connect(
    dbname="db_project",
    user="stani",
    password="1234",
    host="localhost"
)
cursor = conn.cursor()


def get_topics():
    """Fetch all topics from the database."""
    try:
        cursor.execute("SELECT id, name FROM topics")
        return cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Error fetching topics: {e}")
        return []


def display_menu():
    """Display the main menu and handle user selection."""
    while True:
        print("\nCommand Line Quiz")
        print("1. Select a topic to start the quiz")
        print("2. Add a new topic")
        print("3. Add a new question to an existing topic")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            topics = get_topics()
            if not topics:
                print("No topics available. Please add one first.")
                continue
            
            print("\nAvailable Topics:")
            for topic in topics:
                print(f"{topic[0]}. {topic[1]}")
            
            topic_choice = input("Enter topic number: ")
            if topic_choice.isdigit() and int(topic_choice) in [t[0] for t in topics]:
                start_quiz(int(topic_choice))
            else:
                print("Invalid selection. Try again.")

        elif choice == "2":
            topic_name = input("Enter the new topic name: ").strip()
            if topic_name:
                try:
                    cursor.execute("INSERT INTO topics (name) VALUES (%s)", (topic_name,))
                    conn.commit()
                    print(f"Topic '{topic_name}' added successfully!")
                except psycopg2.Error as e:
                    conn.rollback()
                    print("Error adding topic:", e)

        elif choice == "3":
            add_new_question()

        elif choice == "4":
            exit_choice = input("Are you sure you want to exit? (y/n): ").strip().lower()
            if exit_choice == 'y':
                print("Exiting quiz application.")
                break  # Exit the loop, effectively exiting the program
            else:
                print("Returning to the menu.")

        else:
            print("Invalid choice. Please try again.")


def add_new_question():
    """Allow the user to add a new question to an existing topic."""
    topics = get_topics()
    if not topics:
        print("No topics available. Please add one first.")
        return
    
    print("\nAvailable Topics:")
    for topic in topics:
        print(f"{topic[0]}. {topic[1]}")

    topic_choice = input("Enter topic number: ")
    if not topic_choice.isdigit() or int(topic_choice) not in [t[0] for t in topics]:
        print("Invalid topic selection.")
        return

    topic_id = int(topic_choice)

    # Get the question text
    question_text = input("Enter the new question text: ").strip()
    if not question_text:
        print("Question cannot be empty.")
        return

    # Get the correct answer
    correct_answer = input("Enter the correct answer: ").strip()
    if not correct_answer:
        print("Correct answer cannot be empty.")
        return

    # Get wrong answers
    wrong_answers = []
    while len(wrong_answers) < 3:  # Ensure at least 3 wrong answers
        wrong_answer = input(f"Enter a wrong answer ({len(wrong_answers) + 1}/3): ").strip()
        if wrong_answer and wrong_answer != correct_answer and wrong_answer not in wrong_answers:
            wrong_answers.append(wrong_answer)
        else:
            print("Wrong answer cannot be empty or the same as the correct one.")

    # Insert question into the database
    cursor.execute("""
        INSERT INTO questions (topic_id, question_text) 
        VALUES (%s, %s) RETURNING id
    """, (topic_id, question_text))
    question_id = cursor.fetchone()[0]

    # Insert the correct answer first
    cursor.execute("""
        INSERT INTO choices (question_id, choice_text, is_correct)
        VALUES (%s, %s, TRUE)
    """, (question_id, correct_answer))

    # Insert the wrong answers
    for wrong_answer in wrong_answers:
        cursor.execute("""
            INSERT INTO choices (question_id, choice_text, is_correct)
            VALUES (%s, %s, FALSE)
        """, (question_id, wrong_answer))

    conn.commit()
    print(f"Question added successfully to the '{topics[topic_id-1][1]}' topic!")



def start_quiz(topic_id, num_questions=3):
    """Start a quiz by selecting random questions for the given topic."""

    # Get all questions for the topic
    cursor.execute("""
        SELECT id, question_text FROM questions
        WHERE topic_id = %s
        ORDER BY RANDOM()
        LIMIT %s
    """, (topic_id, num_questions))
    
    questions = cursor.fetchall()

    if not questions:
        print("No questions available for this topic.")
        return

    score = 0

    for q_index, (question_id, question_text) in enumerate(questions, 1):
        print(f"\nQuestion {q_index}: {question_text}")

        # Get all choices for the question
        cursor.execute("""
            SELECT id, choice_text, is_correct FROM choices
            WHERE question_id = %s
        """, (question_id,))
        choices = cursor.fetchall()

        # Shuffle choices
        random.shuffle(choices)

        # Display choices
        for idx, (_, choice_text, _) in enumerate(choices, 1):
            print(f"{idx}. {choice_text}")

        # Get user input
        while True:
            answer = input("Your answer (number): ").strip()
            if answer.isdigit() and 1 <= int(answer) <= len(choices):
                break
            print("Invalid input. Please enter a number corresponding to the choices.")

        selected_choice = choices[int(answer) - 1]
        if selected_choice[2]:  # is_correct
            print("✅ Correct!")
            score += 1
        else:
            print("❌ Incorrect!")

    print(f"\n🎉 Quiz complete! You scored {score} out of {len(questions)}.")

"""
sample_topics = ["Math", "Science", "History", "Programming"]

for topic in sample_topics:
    try:
        cursor.execute("INSERT INTO topics (name) VALUES (%s)", (topic,))
        conn.commit()
        print(f"Added topic: {topic}")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print(f"Topic '{topic}' already exists.")
"""


def seed_sample_questions():
    sample_data = {
        "Math": {
            "question": "What is 5 + 7?",
            "choices": [("12", True), ("10", False), ("13", False), ("15", False)]
        },
        "Science": {
            "question": "What planet is known as the Red Planet?",
            "choices": [("Mars", True), ("Venus", False), ("Jupiter", False), ("Saturn", False)]
        },
        "History": {
            "question": "Who was the first president of the United States?",
            "choices": [("George Washington", True), ("Abraham Lincoln", False), ("John Adams", False), ("Thomas Jefferson", False)]
        },
        "Programming": {
            "question": "What does HTML stand for?",
            "choices": [("HyperText Markup Language", True), ("High Transfer Machine Language", False), ("HyperText Machine Language", False), ("Hyper Training Markup Language", False)]
        }
    }

    for topic, qdata in sample_data.items():
        # Get topic_id
        cursor.execute("SELECT id FROM topics WHERE name = %s", (topic,))
        result = cursor.fetchone()
        if result:
            topic_id = result[0]
        else:
            print(f"Topic '{topic}' not found.")
            continue

        # Insert question
        cursor.execute(
            "INSERT INTO questions (topic_id, question_text) VALUES (%s, %s) RETURNING id",
            (topic_id, qdata["question"])
        )
        question_id = cursor.fetchone()[0]

        # Insert choices
        for choice_text, is_correct in qdata["choices"]:
            cursor.execute(
                "INSERT INTO choices (question_id, choice_text, is_correct) VALUES (%s, %s, %s)",
                (question_id, choice_text, is_correct)
            )

    conn.commit()
    print("Sample questions seeded!")


def add_more_questions():
    more_data = {
        "Math": [
            ("What is the square root of 64?", [("8", True), ("6", False), ("7", False), ("9", False)]),
            ("What is 9 × 3?", [("27", True), ("21", False), ("36", False), ("24", False)])
        ],
        "Science": [
            ("What gas do plants absorb from the atmosphere?", [("Carbon Dioxide", True), ("Oxygen", False), ("Nitrogen", False), ("Helium", False)]),
            ("What is H2O commonly known as?", [("Water", True), ("Hydrogen", False), ("Salt", False), ("Steam", False)])
        ],
        "History": [
            ("In what year did World War II end?", [("1945", True), ("1940", False), ("1939", False), ("1950", False)]),
            ("Which empire built the Colosseum?", [("Roman Empire", True), ("Greek Empire", False), ("Ottoman Empire", False), ("British Empire", False)])
        ],
        "Programming": [
            ("Which language is primarily used for web development?", [("JavaScript", True), ("C++", False), ("Python", False), ("Java", False)]),
            ("What does 'print()' do in Python?", [("Displays output", True), ("Saves a file", False), ("Compiles code", False), ("Creates a variable", False)])
        ]
    }

    for topic, questions in more_data.items():
        cursor.execute("SELECT id FROM topics WHERE name = %s", (topic,))
        result = cursor.fetchone()
        if not result:
            print(f"Topic '{topic}' not found. Skipping...")
            continue
        topic_id = result[0]

        for question_text, choices in questions:
            cursor.execute(
                "INSERT INTO questions (topic_id, question_text) VALUES (%s, %s) RETURNING id",
                (topic_id, question_text)
            )
            question_id = cursor.fetchone()[0]

            for choice_text, is_correct in choices:
                cursor.execute(
                    "INSERT INTO choices (question_id, choice_text, is_correct) VALUES (%s, %s, %s)",
                    (question_id, choice_text, is_correct)
                )

    conn.commit()
    print("Additional questions added!")



if __name__ == "__main__":
    #seed_sample_questions()
    #add_more_questions()
    display_menu()


cursor.close()
conn.close()