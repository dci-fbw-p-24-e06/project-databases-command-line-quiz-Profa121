import psycopg2


conn = psycopg2.connect(
    dbname="database name "",
    user="stani",
    password="1234",
    host="localhost"
)
cursor = conn.cursor()


def get_topics():
    """Fetch all topics from the database."""
    cursor.execute("SELECT id, name FROM topics")
    return cursor.fetchall()


def display_menu():
    """Display the main menu and handle user selection."""
    while True:
        print("\nCommand Line Quiz")
        print("1. Select a topic to start the quiz")
        print("2. Add a new topic")
        print("3. Exit")
        
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
            print("Exiting quiz application.")
            break
        else:
            print("Invalid choice. Please try again.")


def start_quiz(topic_id):
    """Placeholder for the quiz logic (to be implemented)."""
    print(f"\nStarting quiz for topic {topic_id}... (Coming soon!)")


if __name__ == "__main__":
    display_menu()


cursor.close()
conn.close()