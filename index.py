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
quiz_termine = False
score = 0
temps_restant = 30
temps_global = 1000  # Temps global de 1 minute
question_actuelle = 0
scores = []
pseudo = ""
difficulte = ""
categories_selectionnees = []
indices_melanges = []
categorie = ""
questions = []
last_click_time = 0  # Variable pour stocker le temps du dernier clic
score_page = 0  # Page actuelle des scores
scores_per_page = 7  # Nombre de scores à afficher par page
multiplicateur = 1  # Multiplicateur de points basé sur la difficulté
temps_question = 10  # Temps restant pour chaque question

# Charger l'image de fond
background_image = pygame.image.load('images/score.jpg')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

def reinitialiser_jeu():
    global score, temps_restant, question_actuelle, pseudo, difficulte, categorie, questions, start_ticks, page, indices_melanges
    score = 0
    temps_restant = 30
    question_actuelle = 0
    pseudo = ""
    difficulte = ""
    categorie = ""
    questions = [q for q in all_questions if q["categorie"] == categorie and q["difficulte"] == difficulte]
    random.shuffle(questions)  # Mélanger les questions
    indices_melanges = [random.sample(range(len(q["reponses"])), len(q["reponses"])) for q in questions]  # Mélanger les indices des réponses
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
        "categorie": categories_selectionnees,
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
            if current_time - last_click_time > 200: 
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
    
    # Afficher l'image de fond
    screen.blit(background_image, (0, 0))
    
    afficher_texte("Scores", SCREEN_WIDTH // 2 - 50, 70, WHITE, taille=48)
    
    # Afficher les en-têtes des colonnes
    afficher_texte("Pseudo", 80, 140, WHITE)
    afficher_texte("Difficulté", 350, 140, WHITE)
    afficher_texte("Score", 590, 140, WHITE)
    
    start_index = score_page * scores_per_page
    end_index = start_index + scores_per_page
    y_offset = 200
    
    for i, score_entry in enumerate(scores[start_index:end_index], start=start_index + 1):
        afficher_texte(f"{i}. {score_entry['pseudo']}", 80, y_offset, WHITE)
        afficher_texte(f"{score_entry['difficulte']}", 350, y_offset, WHITE)
        afficher_texte(f"{score_entry['score']}", 590, y_offset, WHITE)
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
    global difficulte, page, multiplicateur
    difficulte = diff
    if diff == "Facile":
        multiplicateur = 1
    elif diff == "Moyen":
        multiplicateur = 2
    elif diff == "Difficile":
        multiplicateur = 4
    page = "categorie"

# Fonction pour afficher la page de catégorie
def afficher_page_categorie():
    global page, categories_selectionnees
    screen.fill(WHITE)
    afficher_texte("Choisissez les catégories:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150, BLACK)
    
    categories = list(set([q["categorie"] for q in all_questions]))
    num_columns = 3
    button_width = 200
    button_height = 50
    padding = 10
    column_width = button_width + padding
    row_height = button_height + padding
    
    for i, cat in enumerate(categories):
        col = i % num_columns
        row = i // num_columns
        x = 90 + col * column_width
        y = SCREEN_HEIGHT // 2 - 50 + row * row_height
        couleur = BLUE if cat not in categories_selectionnees else HOVER_COLOR
        afficher_bouton(cat, x, y, button_width, button_height, couleur, lambda c=cat: choisir_categorie(c))
    
    if categories_selectionnees:
        afficher_bouton("Commencer", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, commencer_quiz)
    
    pygame.display.flip()

def choisir_categorie(cat):
    global categories_selectionnees
    if cat in categories_selectionnees:
        categories_selectionnees.remove(cat)
    else:
        categories_selectionnees.append(cat)
    afficher_page_categorie()

def commencer_quiz():
    global questions, start_ticks, start_ticks_global, page, indices_melanges
    questions = [q for q in all_questions if q["categorie"] in categories_selectionnees and q["difficulte"] == difficulte]
    random.shuffle(questions)  # Mélanger les questions
    indices_melanges = [random.sample(range(len(q["reponses"])), len(q["reponses"])) for q in questions]
    start_ticks = pygame.time.get_ticks()  # Réinitialiser le timer au début des questions
    start_ticks_global = pygame.time.get_ticks()  # Réinitialiser le timer global
    page = "principale"

# Fonction pour vérifier la réponse
def verifier_reponse(index):
    global score, question_actuelle, page, temps_question, start_ticks, temps_global
    if questions[question_actuelle]["bonne_reponse"] == index:
        score += 1 * multiplicateur
        score += temps_question * multiplicateur  # Ajouter le temps restant au score avec le multiplicateur
    question_actuelle += 1
    temps_question = 10  # Réinitialiser le temps pour la prochaine question
    start_ticks = pygame.time.get_ticks()  # Réinitialiser le timer pour la prochaine question
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
            elif len(pseudo) < 12:
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

        # Calculer le temps restant pour la question
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        temps_question = max(10 - seconds, 0)
        afficher_texte("Temps restant: " + str(temps_question), 20, 20, RED)

        # Calculer le temps global restant
        seconds_global = (pygame.time.get_ticks() - start_ticks_global) // 1000
        temps_global = max(60 - seconds_global, 0)
        afficher_texte("Temps global: " + str(temps_global), 20, 50, RED)

        # Vérifier que la liste des questions n'est pas vide
        if questions:
            # Afficher la question
            question = questions[question_actuelle]
            afficher_texte(question["question"], SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100, BLACK)

            # Afficher les réponses
            for i, idx in enumerate(indices_melanges[question_actuelle]):
                reponse = question["reponses"][idx]
                afficher_bouton_reponse(str(i+1) + ". " + reponse, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + i*50, 400, 50, BLUE, HOVER_COLOR, lambda idx=idx: verifier_reponse(idx))

        # Afficher le bouton pour aller à la page de score
        afficher_bouton("Voir Scores", SCREEN_WIDTH // 2 - 100, 50, 200, 50, BLUE, afficher_page_score)
    else:
        afficher_texte("Aucune question disponible.", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, RED)

    # Vérifier si le temps pour la question est écoulé
    if temps_question <= 0:
        question_actuelle += 1
        temps_question = 10  # Réinitialiser le temps pour la prochaine question
        start_ticks = pygame.time.get_ticks()  # Réinitialiser le timer pour la prochaine question
        if question_actuelle >= len(questions) and not quiz_termine:
            sauvegarder_scores()
            page = "score"
            quiz_termine = True

    # Vérifier si le temps global est écoulé
    if temps_global <= 0 and not quiz_termine:
        sauvegarder_scores()
        page = "score"
        quiz_termine = True

    elif page == "score":
        afficher_page_score()

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la boucle
    clock.tick(60)

pygame.quit()