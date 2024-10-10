import time
from questions import questions  # Importer les questions depuis le fichier questions.py

# Fonction pour poser les questions et calculer le score
def poser_questions():
    score = 0
    start_time = time.time()
    for i, q in enumerate(questions):
        print(f"Question {i + 1}: {q['question']}")
        for choice in q['choices']:
            print(choice)
        reponse = input("Votre réponse: ")
        if reponse == q['answer']:
            score += 1
            elapsed_time = time.time() - start_time
            if elapsed_time < 10:  # Bonus pour réponse rapide
                score += 0.5
        start_time = time.time()  # Reset timer for next question
    return score

# Fonction pour sauvegarder les scores
def sauvegarder_score(pseudo, score):
    with open("scores.txt", "a") as file:
        file.write(f"Pseudo: {pseudo}, Score: {score}\n")

# Fonction principale
def main():
    print("Bienvenue au quiz!")
    pseudo = input("Entrez votre pseudo: ")
    score = poser_questions()
    print(f"Votre score final est: {score}")
    sauvegarder_score(pseudo, score)

if __name__ == "__main__":
    main()