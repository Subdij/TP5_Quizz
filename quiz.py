import time
from questions import questions  # Importer les questions depuis le fichier questions.py

# Fonction pour poser les questions et calculer le score
def poser_questions():
    score = 0
    for i, q in enumerate(questions):
        print(f"Question {i + 1}: {q['question']}")
        for choice in q['choices']:
            print(choice)
        start_time = time.time()
        reponse = input("Votre réponse: ")
        elapsed_time = time.time() - start_time
        if reponse == q['answer']:
            points = max(0, 10 - int(elapsed_time))  # Calcul des points en fonction du temps restant
            score += points
        print(f"Temps écoulé: {elapsed_time:.2f} secondes, Points gagnés: {points}")
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