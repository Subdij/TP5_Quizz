# pip install pygame
# faire cette commande si la precedente ne fonctionne pas (pip3 install pygame)
import pygame
import random
import time

# Initialisation de Pygame
pygame.init()

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

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
questions = [
    {"question": "Quelle est la capitale de la France ?", "reponses": ["Paris", "Londres", "Berlin"], "bonne_reponse": 0},
    # Ajouter d'autres questions ici
]
question_actuelle = 0

# Fonction pour afficher le texte
def afficher_texte(texte, x, y, couleur):
    text_surface = font.render(texte, True, couleur)
    screen.blit(text_surface, (x, y))

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Effacer l'écran
    screen.fill(WHITE)

    # Afficher le score
    afficher_texte("Score: " + str(score), SCREEN_WIDTH - 150, 20, BLACK)

    # Afficher le temps restant
    temps_restant -= 1
    if temps_restant < 0:
        temps_restant = 0
    afficher_texte("Temps restant: " + str(temps_restant), 20, 20, RED)

    # Afficher la question
    question = questions[question_actuelle]
    afficher_texte(question["question"], SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100, BLACK)

    # Afficher les réponses
    for i, reponse in enumerate(question["reponses"]):
        afficher_texte(str(i+1) + ". " + reponse, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + i*50, BLACK)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse
    pygame.time.delay(1000)

pygame.quit()