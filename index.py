import pygame
import json
import os
import random
import os
os.chdir('C:/Users/MSI/Desktop/TP5_Quizz')

# Initialiser Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Charger  sons
click_sound = pygame.mixer.Sound('click.wav/background.mp3') # Remplacez par le chemin de votre musique de fond
pygame.mixer.music.load('click.wav/background.mp3')

# Démarrer la musique de fond
pygame.mixer.music.play(-1)

# Variables globales
page = "menu"
scores = []
score_page = 0
scores_per_page = 10

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

# Initialiser les scores
scores = charger_scores()  # Charger les scores au début

# Fonction pour afficher le texte
def afficher_texte(texte, x, y, couleur, taille=32):
    font = pygame.font.Font(None, taille)
    text_surface = font.render(texte, True, couleur)
    screen.blit(text_surface, (x, y))

# Fonction pour afficher les boutons
def afficher_bouton(texte, x, y, largeur, hauteur, couleur, action=None):
    rect = pygame.Rect(x, y, largeur, hauteur)
    pygame.draw.rect(screen, couleur, rect)
    afficher_texte(texte, x + 10, y + 10, WHITE)
    
    # Événements de clic
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                if action:
                    action()
                    click_sound.play()  # Jouer le son du clic

# Fonction pour changer la page de score
def changer_page_score(delta):
    global score_page
    score_page += delta
    score_page = max(0, min(score_page, (len(scores) - 1) // scores_per_page))

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
    
    # Afficher les scores
    for i, score_entry in enumerate(scores[start_index:end_index], start=start_index + 1):
        afficher_texte(f"{i}. {score_entry['pseudo']}", 80, y_offset, WHITE)
        afficher_texte(f"{score_entry['difficulte']}", 350, y_offset, WHITE)
        afficher_texte(f"{score_entry['score']}", 590, y_offset, WHITE)
        y_offset += 40
    
    # Afficher les boutons de navigation
    if score_page > 0:
        afficher_bouton("Précédent", 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, lambda: changer_page_score(-1))
    
    if end_index < len(scores):
        afficher_bouton("Suivant", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100, 200, 50, BLUE, lambda: changer_page_score(1))
    
    afficher_bouton("Recommencer", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50, BLUE, reinitialiser_jeu)

# Fonction principale
def main():
    global screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Quiz Game")

    clock = pygame.time.Clock()
    
    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Affichage du menu ou de la page de score selon l'état
        if page == "menu":
            
            afficher_texte("Menu Principal", SCREEN_WIDTH // 2 - 100, 70, WHITE, taille=48)
            afficher_bouton("Commencer", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50, BLUE, afficher_page_score)
        
        # Affiche la page de score
        elif page == "score":
            afficher_page_score()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
