import os
import pygame
import json
import random
import time
from pygame import mixer

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
pygame.display.set_caption("QuizDown")

# Police
font = pygame.font.Font(None, 36)

# Variables
dropdown_open = False
difficulte_selectionnee = "Global"
dernier_score_index = -1
cursor_visible = True
cursor_last_switch = 0
cursor_switch_delay = 500  # Délai pour le clignotement du curseur

quiz_termine = False
score = 0
temps_restant = 30
temps_global = 60  # Temps global de 1 minute
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
streak = 0  # "Compteur" de bonnes réponses d'affilée, afin d'activer des bonus de temps
musique = 1
active_field = "question"  # Champ actif pour la proposition de question

# Proposition de question
proposition_question = {
    "question": "",
    "reponses": ["", "", "", ""],
    "bonne_reponse": 3
}


# Charger les images de fond
background_image_accueil = pygame.image.load(os.path.join('images', 'questions.jpg'))
background_image_accueil = pygame.transform.scale(background_image_accueil, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_image_pseudo = pygame.image.load(os.path.join('images', 'pseudo.jpg'))
background_image_pseudo = pygame.transform.scale(background_image_pseudo, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_image_difficulte = pygame.image.load(os.path.join('images', 'difficulte.jpg'))
background_image_difficulte = pygame.transform.scale(background_image_difficulte, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_image_categorie = pygame.image.load(os.path.join('images', 'categorie.jpg'))
background_image_categorie = pygame.transform.scale(background_image_categorie, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_image_score = pygame.image.load(os.path.join('images', 'score.jpg'))
background_image_score = pygame.transform.scale(background_image_score, (SCREEN_WIDTH, SCREEN_HEIGHT))

# background sound
mixer.music.load('background.mp3')
mixer.music.play(-1)

def reinitialiser_jeu():
    global score, temps_restant, question_actuelle, pseudo, difficulte, categorie, questions, start_ticks, page, indices_melanges, streak, dernier_score_index
    score = 0
    streak = 0
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
    dernier_score_index = -1  # Réinitialiser l'index du dernier score enregistré

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


def afficher_bouton_deroulant(texte, x, y, largeur, hauteur, options, couleur, hover_couleur, action=None):
    global last_click_time, dropdown_open
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    dropdown_rect = pygame.Rect(x, y, largeur, hauteur)
    
    if dropdown_rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_couleur, dropdown_rect)
        if click[0] == 1 and action is not None:
            current_time = pygame.time.get_ticks()
            if current_time - last_click_time > 100:
                last_click_time = current_time
                dropdown_open = not dropdown_open
    else:
        pygame.draw.rect(screen, couleur, dropdown_rect)
    
    afficher_texte(texte, x + (largeur // 2 - font.size(texte)[0] // 2), y + (hauteur // 2 - font.size(texte)[1] // 2), WHITE)
    
    if dropdown_open:
        for i, option in enumerate(options):
            option_rect = pygame.Rect(x, y + (i + 1) * hauteur, largeur, hauteur)
            if option_rect.collidepoint(mouse):
                pygame.draw.rect(screen, hover_couleur, option_rect)
                if click[0] == 1 and action is not None:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_click_time > 100:
                        last_click_time = current_time
                        action(option)
                        dropdown_open = False
            else:
                pygame.draw.rect(screen, couleur, option_rect)
            afficher_texte(option, x + (largeur // 2 - font.size(option)[0] // 2), y + (i + 1) * hauteur + (hauteur // 2 - font.size(option)[1] // 2), WHITE)

# Sauvegarder les scores dans le fichier JSON
def sauvegarder_scores():
    global scores, dernier_score_index, score_page
    # Ajouter le score actuel à la liste des scores
    scores.append({
        "pseudo": pseudo,
        "categorie": categories_selectionnees,
        "difficulte": difficulte,
        "score": score,
    })
    # Trier les scores par ordre décroissant en fonction des points
    scores.sort(key=lambda x: x['score'], reverse=True)
    # Mettre à jour l'index du dernier score enregistré
    dernier_score_index = scores.index(next(s for s in scores if s["pseudo"] == pseudo and s["score"] == score))
    # Calculer la page du dernier score enregistré
    score_page = calculer_page_score(dernier_score_index)
    # Sauvegarder les scores triés dans le fichier JSON
    with open('scores.json', 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=4, ensure_ascii=False)
    # Trier les scores immédiatement après la sauvegarde
    trier_scores(difficulte_selectionnee)
    # Afficher la page de score après la mise à jour
    afficher_page_score()


def render_text_wrapped(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_surface = font.render(word, True, WHITE)
        word_width = word_surface.get_width()
        if current_width + word_width >= max_width:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width + font.size(' ')[0]

    lines.append(' '.join(current_line))
    return lines        

def afficher_texte_avec_curseur(texte, x, y, couleur, taille, is_active, cursor_position=None):
    font = pygame.font.Font(None, taille)
    text_surface = font.render(texte, True, couleur)
    screen.blit(text_surface, (x, y))
    
    # Si le champ est actif et que le curseur doit être visible
    if is_active and cursor_visible:
        # Calculer la position du curseur à la fin du texte ou à la position donnée
        cursor_x = x + font.size(texte[:cursor_position])[0] if cursor_position is not None else x + text_surface.get_width()

        # Ajuster la hauteur du curseur en fonction de la hauteur de la police
        cursor_height = font.get_height()  # Hauteur du curseur correspondant à la hauteur du texte
        pygame.draw.line(screen, couleur, (cursor_x, y), (cursor_x, y + cursor_height), 2)



# Fonction pour afficher le texte
def afficher_texte(texte, x, y, couleur, taille=36, max_width=None):
    font = pygame.font.Font(None, taille)
    if max_width:
        lines = render_text_wrapped(texte, font, max_width)
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, couleur)
            screen.blit(text_surface, (x, y + i * taille))
    else:
        text_surface = font.render(texte, True, couleur)
        screen.blit(text_surface, (x, y))

# Fonction pour afficher le bouton
def afficher_bouton(texte, x, y, largeur, hauteur, couleur, hover_couleur, action=None):
    global last_click_time
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + largeur > mouse[0] > x and y + hauteur > mouse[1] > y:
        pygame.draw.rect(screen, hover_couleur, (x, y, largeur, hauteur), border_radius=50)
        if click[0] == 1 and action is not None:
            current_time = pygame.time.get_ticks()
            if current_time - last_click_time > 100: 
                last_click_time = current_time
                action()
    else:
        pygame.draw.rect(screen, couleur, (x, y, largeur, hauteur), border_radius=50)
    afficher_texte(texte, x + (largeur // 2 - font.size(texte)[0] // 2), y + (hauteur // 2 - font.size(texte)[1] // 2), WHITE)

def render_text_wrapped(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_surface = font.render(word, True, WHITE)
        word_width = word_surface.get_width()
        if current_width + word_width >= max_width:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width + font.size(' ')[0]

    lines.append(' '.join(current_line))
    return lines

def pause():
        global musique
        if musique == 1:
            mixer.music.pause()
            musique = 0
        else:
            mixer.music.unpause()
            musique = 1

# Fonction pour afficher la page d'accueil
def afficher_page_accueil():
    global page
    screen.blit(background_image_accueil, (0, 0))
    afficher_texte("Bienvenue au Quiz Down!", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100, WHITE, taille=48)
    afficher_bouton("Play", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, BLUE, HOVER_COLOR, lambda: changer_page("pseudo"))
    afficher_bouton("Classement", SCREEN_WIDTH // 2 - 100, 370, 200, 50, BLUE, HOVER_COLOR, afficher_page_score)
    afficher_bouton("mute sound", 580, 25, 200, 50, BLUE, HOVER_COLOR, lambda: pause())
    afficher_bouton("Proposer des questions", SCREEN_WIDTH // 2 - 150, 440, 300, 50, BLUE, HOVER_COLOR, lambda: changer_page("proposition_question"))

    pygame.display.flip()


def afficher_page_proposition_question():
    global proposition_question, page, cursor_visible, cursor_last_switch
    screen.blit(background_image_pseudo, (0, 0))  # Réutilisation d'un arrière-plan déjà chargé
    afficher_texte("Proposez une nouvelle question:", SCREEN_WIDTH // 2 - 150, 50, WHITE)
    
    # Champ pour la question
    afficher_texte("Question:", 100, 150, WHITE)
    pygame.draw.rect(screen, WHITE, (300, 150, 400, 40), 2)
    afficher_texte_avec_curseur(proposition_question["question"], 310, 160, WHITE, 36, active_field == "question")

    # Champs pour les réponses
    for i in range(2):
        afficher_texte(f"Réponse {i+1}:", 100, 230 + i * 60, WHITE)
        pygame.draw.rect(screen, WHITE, (300, 230 + i * 60, 400, 40), 2)
        afficher_texte_avec_curseur(proposition_question["reponses"][i], 310, 240 + i * 60, WHITE, 36, active_field == i)

    afficher_texte(f"Bonne réponse :", 100, 230 + 2 * 60, WHITE)
    pygame.draw.rect(screen, WHITE, (300, 230 + 2 * 60, 400, 40), 2)
    afficher_texte_avec_curseur(proposition_question["reponses"][2], 310, 240 + 2 * 60, WHITE, 36, active_field == 2)

    # Champ pour la bonne réponse
    afficher_texte("La bonne réponse est a mettre dans la dernière case", 100, 430, WHITE)
    """pygame.draw.rect(screen, WHITE, (350, 425, 50, 40), 2)
    afficher_texte_avec_curseur(str(proposition_question["bonne_reponse"]+ 1), 360, 435, WHITE, 36, active_field == "bonne_reponse")"""

    # Bouton de soumission
    afficher_bouton("Soumettre", SCREEN_WIDTH // 2 - 100, 560, 200, 50, BLUE, HOVER_COLOR, soumettre_proposition_question)
    
    afficher_bouton("<-- Accueil <--", 80, 70, 200, 50, BLUE, HOVER_COLOR, lambda: changer_page("accueil"))

    # Gérer le clignotement du curseur
    current_time = pygame.time.get_ticks()
    if current_time - cursor_last_switch > cursor_switch_delay:
        cursor_visible = not cursor_visible
        cursor_last_switch = current_time

    pygame.display.flip()


def soumettre_proposition_question():
    global proposition_question
    nouvelle_question = {
        "question": proposition_question["question"],
        "reponses": proposition_question["reponses"],
        "bonne_reponse": proposition_question["bonne_reponse"],
        "categorie": "Propose",  # Catégorie par défaut pour les questions proposées
        "difficulte": "Facile"   # Difficulté par défaut
    }
    
    # Charger les propositions existantes
    try:
        with open('propositionQuestion.json', 'r', encoding='utf-8') as f:
            propositions = json.load(f)
    except FileNotFoundError:
        propositions = []
    
    # Ajouter la nouvelle question
    propositions.append(nouvelle_question)
    
    # Sauvegarder dans le fichier JSON
    with open('propositionQuestion.json', 'w', encoding='utf-8') as f:
        json.dump(propositions, f, indent=4, ensure_ascii=False)
    
    # Réinitialiser le formulaire
    proposition_question = {
        "question": "",
        "reponses": ["", "", "", ""],
        "bonne_reponse": 3
    }
    
    # Revenir à la page d'accueil
    changer_page("accueil")




# Fonction pour afficher les boutons de réponse
def afficher_bouton_reponse(texte, x, y, largeur, hauteur, couleur, HOVER_COLOR, action=None):
    global last_click_time
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + largeur > mouse[0] > x and y + hauteur > mouse[1] > y:
        pygame.draw.rect(screen, HOVER_COLOR, (x, y, largeur, hauteur))
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
    screen.blit(background_image_accueil, (0, 0))


def trier_scores(difficulte):
    global scores, score_page, difficulte_selectionnee
    score_page = 0
    difficulte_selectionnee = difficulte  # Mettre à jour la difficulté sélectionnée
    if difficulte == "Global":
        scores = charger_scores()
    else:
        scores = [score for score in charger_scores() if score['difficulte'] == difficulte]
    afficher_page_score()

def calculer_page_score(index):
    return index // scores_per_page

# Fonction pour afficher la page de score
def afficher_page_score():
    global page, score_page, dernier_score_index
    page = "score"
    screen.blit(background_image_score, (0, 0))
    
    afficher_texte("Scores", SCREEN_WIDTH // 2 - 50, 70, WHITE, taille=48)
    
    # Afficher les en-têtes des colonnes
    afficher_texte("Pseudo", 80, 140, WHITE)
    afficher_texte("Difficulté", 350, 140, WHITE)
    afficher_texte("Score", 590, 140, WHITE)
    
    start_index = score_page * scores_per_page
    end_index = start_index + scores_per_page
    y_offset = 200
    
    for i, score_entry in enumerate(scores[start_index:end_index], start=start_index + 1):
        couleur = BLUE if i - 1 == dernier_score_index else WHITE
        afficher_texte(f"{i}. {score_entry['pseudo']}", 80, y_offset, couleur)
        afficher_texte(f"{score_entry['difficulte']}", 350, y_offset, couleur)
        afficher_texte(f"{score_entry['score']}", 590, y_offset, couleur)
        y_offset += 40
    
    if score_page > 0:
        afficher_bouton("Précédent", 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, HOVER_COLOR, lambda: changer_page_score(-1))
    
    if end_index < len(scores):
        afficher_bouton("Suivant", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100, 200, 50, BLUE, HOVER_COLOR, lambda: changer_page_score(1))
    
    afficher_bouton("Recommencer", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, HOVER_COLOR, reinitialiser_jeu)
    
    afficher_bouton("Accueil", 70, 60, 230, 50, BLUE, HOVER_COLOR, lambda: changer_page("accueil"))
    
    options = ["Global", "Facile", "Moyen", "Difficile"]
    afficher_bouton_deroulant("Trier", SCREEN_WIDTH - 280, 60, 200, 50, options, BLUE, HOVER_COLOR, trier_scores)

# Fonction pour changer de page
def changer_page(nouvelle_page):
    global page
    if nouvelle_page == "accueil":
        reinitialiser_jeu()
    page = nouvelle_page


# Fonction pour changer la page de score
def changer_page_score(direction):
    global score_page
    score_page += direction
    afficher_page_score()

# Fonction pour afficher la page de pseudo
def afficher_page_pseudo():
    global pseudo, page, cursor_visible, cursor_last_switch
    screen.blit(background_image_pseudo, (0, 0))
    afficher_texte("Entrez votre pseudo:", SCREEN_WIDTH // 2 -125, SCREEN_HEIGHT // 2 - 50, WHITE)
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50), 2)
    afficher_texte(pseudo, SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 10, WHITE)
    
    afficher_bouton("Accueil", 80, 70, 200, 50, BLUE, HOVER_COLOR, lambda: changer_page("accueil"))
    
    # Gérer le curseur clignotant
    current_time = pygame.time.get_ticks()
    if current_time - cursor_last_switch > 500:  # Changer l'état du curseur toutes les 500 ms
        cursor_visible = not cursor_visible
        cursor_last_switch = current_time
    
    if cursor_visible:
        cursor_x = SCREEN_WIDTH // 2 - 90 + font.size(pseudo)[0]
        pygame.draw.line(screen, WHITE, (cursor_x, SCREEN_HEIGHT // 2 + 10), (cursor_x, SCREEN_HEIGHT // 2 + 40), 2)
    
    pygame.display.flip()

# Fonction pour afficher la page de difficulté
def afficher_page_difficulte():
    global page, difficulte
    screen.blit(background_image_difficulte, (0, 0))
    afficher_texte("Choisissez la difficulté:", SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 100, WHITE)
    spacing = 20  # Espacement entre les boutons
    afficher_bouton("Facile", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, BLUE, HOVER_COLOR, lambda: choisir_difficulte("Facile"))
    afficher_bouton("Moyen", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 + 50 + spacing, 200, 50, BLUE, HOVER_COLOR, lambda: choisir_difficulte("Moyen"))
    afficher_bouton("Difficile", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 + 2 * (50 + spacing), 200, 50, BLUE, HOVER_COLOR, lambda: choisir_difficulte("Difficile"))
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
    screen.blit(background_image_categorie, (0, 0))
    afficher_texte("Choisissez les catégories:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150, WHITE)
    
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
        afficher_bouton(cat, x, y, button_width, button_height, couleur, HOVER_COLOR, lambda c=cat: choisir_categorie(c))
    
    if categories_selectionnees:
        afficher_bouton("Commencer", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, HOVER_COLOR, commencer_quiz)
    
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
    global score, question_actuelle, page, temps_question, start_ticks, temps_global, streak
    if questions[question_actuelle]["bonne_reponse"] == index:
        streak += 1  # Ajouter 1 à la streak en cas de bonne réponse
        score += 1 * multiplicateur
        score += temps_question * multiplicateur  # Ajouter le temps restant au score avec le multiplicateur
    else:
        streak = 0  # Remise à 0 de la streak en cas de mauvaise réponse
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
page = "accueil"  # Commencer par la page d'accueil
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

        elif page == "proposition_question":
            afficher_page_proposition_question()
            if event.type == pygame.KEYDOWN:
                if active_field == "question":
                    if event.key == pygame.K_BACKSPACE:
                        proposition_question["question"] = proposition_question["question"][:-1]
                    elif event.unicode:
                        proposition_question["question"] += event.unicode
                elif active_field in range(3):  # Si on est sur une des réponses
                    if event.key == pygame.K_BACKSPACE:
                        proposition_question["reponses"][active_field] = proposition_question["reponses"][active_field][:-1]
                    elif event.unicode:
                        proposition_question["reponses"][active_field] += event.unicode
                elif active_field == "bonne_reponse":
                    if event.unicode.isdigit():
                        num = int(event.unicode) - 1
                        if 0 <= num < 3:
                            proposition_question["bonne_reponse"] = num

                # Changer de champ actif avec la touche Entrée
                if event.key == pygame.K_RETURN:
                    if active_field == "question":
                        active_field = 0  # Passer au champ de la première réponse
                    elif active_field in range(3):
                        active_field = (active_field + 1) % 3  # Passer à la réponse suivante
                    elif active_field == "bonne_reponse":
                        active_field = "question"
    

    

    if page == "accueil":
        afficher_page_accueil()
    elif page == "pseudo":
        afficher_page_pseudo()
    elif page == "difficulte":
        afficher_page_difficulte()
    elif page == "categorie":
        afficher_page_categorie()
    elif page == "principale":
        # Effacer l'écran
        screen.blit(background_image_accueil, (0, 0)),

        # Afficher le score
        afficher_texte("Score: " + str(score), SCREEN_WIDTH - 150, 20, WHITE)

        # Afficher la streak
        afficher_texte("Streak: " + str(streak), SCREEN_WIDTH - 150, 50, WHITE)
        
        # Calculer le temps restant pour la question
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        temps_question = max(10 - seconds, 0)
        afficher_texte("Temps restant: " + str(temps_question), 20, 50, RED)

        # Calculer le temps global restant
        seconds_global = (pygame.time.get_ticks() - start_ticks_global) // 1000
        temps_global = max(60 - seconds_global, 0)
        if streak>3:    # Vérifier si le joueur a répondu correctement à plus de 3 questions d'affilée
            temps_global += streak-3    # On ajoute x secondes au timer global en fonction du nombre de bonnes réponses qui dépassent 3 (ex: 1 seconde pour streak de 4,...)
        afficher_texte("Temps global: " + str(temps_global), 20, 20, RED)

        # Vérifier que la liste des questions n'est pas vide
        if questions:
            # Afficher la question
            question = questions[question_actuelle]
            afficher_texte(question["question"], SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100, WHITE, taille=36, max_width=550)

            # Afficher les réponses
            for i, idx in enumerate(indices_melanges[question_actuelle]):
                reponse = question["reponses"][idx]
                afficher_bouton_reponse(str(i+1) + ". " + reponse, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + i*50, 400, 50, BLUE, HOVER_COLOR, lambda idx=idx: verifier_reponse(idx))

    

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