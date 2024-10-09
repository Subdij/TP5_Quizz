import pygame

pygame.init()

# Paramètres de la fenêtre
largeur, hauteur = 800, 600
écran = pygame.display.set_mode((largeur, hauteur))


# Police pour le score
police = pygame.font.Font(None, 36)

# Variable pour le score
score = 0

# Fonction pour afficher le score
def afficher_score(score):
    texte_score = police.render("Score: " + str(score), True, (255, 255, 255))
    écran.blit(texte_score, (10, 10))

# Boucle principale du jeu
while True:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            

            pygame.quit()
            quit()
        # Autres événements pour mettre à jour le score (par exemple, si un objet est attrapé)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                score += 10

    # Mise à jour de l'écran
    écran.fill((0, 0, 0))  # Effacer l'écran
    afficher_score(score)  # Afficher le score
    pygame.display.flip()