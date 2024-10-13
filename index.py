import pygame
import json
import random
import time

# Initialisation de Pygame
pygame.init()

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
HOVER_COLOR = (100, 100, 255)

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quiz Pygame")

# Police
font = pygame.font.Font(None, 36)

# Variables
score = 0
temps_restant = 30
question_actuelle = 0
scores = []
pseudo = ""
difficulte = ""
categorie = ""
questions = []
last_click_time = 0  # Variable pour stocker le temps du dernier clic
score_page = 0  # Page actuelle des scores
scores_per_page = 8  # Nombre de scores à afficher par page

def reinitialiser_jeu():
    global score, temps_restant, question_actuelle, pseudo, difficulte, categorie, questions, start_ticks, page
    score = 0
    temps_restant = 30
    question_actuelle = 0
    pseudo = ""
    difficulte = ""
    categorie = ""
    questions = [q for q in all_questions if q["categorie"] == categorie and q["difficulte"] == difficulte]
    random.shuffle(questions)  # Mélanger les questions
    start_ticks = pygame.time.get_ticks()
    page = "pseudo"

# Charger les questions depuis le fichier JSON
with open('questions.json', 'r', encoding='utf-8') as f:
    all_questions = json.load(f)

# Charger les scores depuis le fichier JSON
def charger_scores():
    try:
        with open('scores.json', 'r', encoding='utf-8') as f:
            data = f.read().strip()
            if data:
                scores = json.loads(data)
                # Trier les scores par ordre décroissant en fonction des points
                scores.sort(key=lambda x: x['score'], reverse=True)
                return scores
            else:
                return []
    except FileNotFoundError:
        return []

# Sauvegarder les scores dans le fichier JSON
def sauvegarder_scores():
    global scores
    # Ajouter le score actuel à la liste des scores
    scores.append({
        "pseudo": pseudo,
        "categorie": categorie,
        "difficulte": difficulte,
        "score": score,
    })
    # Trier les scores par ordre décroissant en fonction des points
    scores.sort(key=lambda x: x['score'], reverse=True)
    # Sauvegarder les scores triés dans le fichier JSON
    with open('scores.json', 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=4, ensure_ascii=False)

# Fonction pour afficher le texte
def afficher_texte(texte, x, y, couleur, taille=36):
    font = pygame.font.Font(None, taille)
    text_surface = font.render(texte, True, couleur)
    screen.blit(text_surface, (x, y))

# Fonction pour afficher le bouton
def afficher_bouton(texte, x, y, largeur, hauteur, couleur, action=None):
    global last_click_time
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(screen, couleur, (x, y, largeur, hauteur))
    afficher_texte(texte, x + (largeur // 2 - font.size(texte)[0] // 2), y + (hauteur // 2 - font.size(texte)[1] // 2), WHITE)
    if x + largeur > mouse[0] > x and y + hauteur > mouse[1] > y:
        if click[0] == 1 and action is not None:
            current_time = pygame.time.get_ticks()
            if current_time - last_click_time > 500: 
                last_click_time = current_time
                action()

# Fonction pour afficher les boutons de réponse
def afficher_bouton_reponse(texte, x, y, largeur, hauteur, couleur, hover_couleur, action=None):
    global last_click_time
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + largeur > mouse[0] > x and y + hauteur > mouse[1] > y:
        pygame.draw.rect(screen, hover_couleur, (x, y, largeur, hauteur))
        if click[0] == 1 and action is not None:
            current_time = pygame.time.get_ticks()
            if current_time - last_click_time > 500:  # Vérifier si 0.5 seconde s'est écoulée
                last_click_time = current_time
                action()
    else:
        pygame.draw.rect(screen, couleur, (x, y, largeur, hauteur))
    afficher_texte(texte, x + (largeur // 2 - font.size(texte)[0] // 2), y + (hauteur // 2 - font.size(texte)[1] // 2), WHITE)

# Fonction pour afficher la page principale
def afficher_page_principale():
    global page 
    page = "principale"

# Fonction pour afficher la page de score
def afficher_page_score():
    global page, score_page
    page = "score"
    screen.fill(WHITE)
    afficher_texte("Scores", SCREEN_WIDTH // 2 - 50, 40, BLACK, taille=48)
    
    # Afficher les en-têtes des colonnes
    afficher_texte("Pseudo", 100, 100, BLACK)
    afficher_texte("Catégorie", 300, 100, BLACK)
    afficher_texte("Difficulté", 500, 100, BLACK)
    afficher_texte("Score", 700, 100, BLACK)
    
    start_index = score_page * scores_per_page
    end_index = start_index + scores_per_page
    y_offset = 150
    
    for i, score_entry in enumerate(scores[start_index:end_index], start=start_index + 1):
        afficher_texte(f"{i}. {score_entry['pseudo']}", 100, y_offset, BLACK)
        afficher_texte(f"{score_entry['categorie']}", 300, y_offset, BLACK)
        afficher_texte(f"{score_entry['difficulte']}", 500, y_offset, BLACK)
        afficher_texte(f"{score_entry['score']}", 700, y_offset, BLACK)
        y_offset += 40
    
    if score_page > 0:
        afficher_bouton("Précédent", 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, lambda: changer_page_score(-1))
    
    if end_index < len(scores):
        afficher_bouton("Suivant", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100, 200, 50, BLUE, lambda: changer_page_score(1))
    
    afficher_bouton("Recommencer", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, reinitialiser_jeu)

# Fonction pour changer la page de score
def changer_page_score(direction):
    global score_page
    score_page += direction
    afficher_page_score()

# Fonction pour afficher la page de pseudo
def afficher_page_pseudo():
    global pseudo, page
    screen.fill(WHITE)
    afficher_texte("Entrez votre pseudo:", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, BLACK)
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50), 2)
    afficher_texte(pseudo, SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 10, BLACK)
    pygame.display.flip()

# Fonction pour afficher la page de difficulté
def afficher_page_difficulte():
    global page, difficulte
    screen.fill(WHITE)
    afficher_texte("Choisissez la difficulté:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, BLACK)
    afficher_bouton("Facile", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, BLUE, lambda: choisir_difficulte("Facile"))
    afficher_bouton("Moyen", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, BLUE, lambda: choisir_difficulte("Moyen"))
    afficher_bouton("Difficile", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, BLUE, lambda: choisir_difficulte("Difficile"))
    pygame.display.flip()

# Fonction pour choisir la difficulté
def choisir_difficulte(diff):
    global difficulte, page
    difficulte = diff
    page = "categorie"

# Fonction pour afficher la page de catégorie
def afficher_page_categorie():
    global page, categorie
    screen.fill(WHITE)
    afficher_texte("Choisissez la catégorie:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, BLACK)
    categories = list(set([q["categorie"] for q in all_questions]))
    for i, cat in enumerate(categories):
        afficher_bouton(cat, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 + i * 60, 200, 50, BLUE, lambda c=cat: choisir_categorie(c))
    pygame.display.flip()

# Fonction pour choisir la catégorie
def choisir_categorie(cat):
    global categorie, page, questions
    categorie = cat
    questions = [q for q in all_questions if q["categorie"] == categorie and q["difficulte"] == difficulte]
    random.shuffle(questions)  # Mélanger les questions
    page = "principale"

# Fonction pour vérifier la réponse
def verifier_reponse(index):
    global score, question_actuelle, page
    if questions[question_actuelle]["bonne_reponse"] == index:
        score += 1
    question_actuelle += 1
    if question_actuelle >= len(questions):
        sauvegarder_scores()
        page = "score"

# Boucle principale
running = True
clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()
page = "pseudo"
scores = charger_scores()

# Mélanger les questions au lancement de l'application
questions = [q for q in all_questions if q["categorie"] == categorie and q["difficulte"] == difficulte]
random.shuffle(questions)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and page == "pseudo":
            if event.key == pygame.K_RETURN:
                page = "difficulte"
            elif event.key == pygame.K_BACKSPACE:
                pseudo = pseudo[:-1]
            elif len(pseudo) < 8:
                pseudo += event.unicode

    if page == "pseudo":
        afficher_page_pseudo()
    elif page == "difficulte":
        afficher_page_difficulte()
    elif page == "categorie":
        afficher_page_categorie()
    elif page == "principale":
        # Effacer l'écran
        screen.fill(WHITE)

        # Afficher le score
        afficher_texte("Score: " + str(score), SCREEN_WIDTH - 150, 20, BLACK)

        # Calculer le temps restant
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        temps_restant = max(30 - seconds, 0)
        afficher_texte("Temps restant: " + str(temps_restant), 20, 20, RED)

        # Vérifier que la liste des questions n'est pas vide
        if questions:
            # Afficher la question
            question = questions[question_actuelle]
            afficher_texte(question["question"], SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100, BLACK)

            # Afficher les réponses
            for i, reponse in enumerate(question["reponses"]):
                afficher_bouton_reponse(str(i+1) + ". " + reponse, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + i*50, 400, 50, BLUE, HOVER_COLOR, lambda i=i: verifier_reponse(i))

            # Afficher le bouton pour aller à la page de score
            afficher_bouton("Voir Scores", SCREEN_WIDTH // 2 - 100, 50, 200, 50, BLUE, afficher_page_score)
        else:
            afficher_texte("Aucune question disponible.", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, RED)

    elif page == "score":
        afficher_page_score()

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la boucle
    clock.tick(60)

pygame.quit()