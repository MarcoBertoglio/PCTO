import pygame
import sys
import random
import cv2
import numpy as np
from pygame.constants import MOUSEBUTTONDOWN
pygame.init()

#dichiarazione variabili essenziali
main = True

width = 1200
height = 620
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))

VIRUS_POS_X = 100
speed = 5
game = True
score = 0
high_score = 0

RED = (255,0,0)
done = True

#dichiarazione variabili necessarie per il color tracking
kernel = np.ones((8 ,8), np.uint8)
cap = cv2.VideoCapture(0)  
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

#creazione font per le scritte sullo schermo
game_font = pygame.font.Font('04B_19.TTF',50)
game_over_font = pygame.font.Font('04B_30.TTF',90)

#settaggio del suono di sfondo
sound_backgrownd = pygame.mixer.music.load("sounds_backgrownd.wav")

#creazione dello sfondo e inizio della musica di sottofondo
backgrownd = pygame.image.load('sfondo1.png')
sound_backgrownd = pygame.mixer.music.play()
sound_backgrownd = pygame.mixer.music.set_volume(0.25)

#creazione e ridimensionamento del suolo
floor = pygame.image.load('base.png').convert()
floor = pygame.transform.scale(floor,(width,150))
floor_posizione_x = 0

#creazione e ridimensionamento virus
virus = pygame.image.load('virus.png').convert_alpha()
virus = pygame.transform.scale(virus,(75,75))

#creazione, ridimensionamento tubi
vaccine = pygame.image.load('vacine.png').convert()
vaccine = pygame.transform.scale(vaccine, (100,500))

#creazione variabili e cosanti necessarie
vaccine_list = []
SPAWNVACCINE = pygame.USEREVENT
pygame.time.set_timer(SPAWNVACCINE, 3000)
vaccine_heigh = [150,175,200,225,250,275,300,325,350,375]

#creazione tasto di restart
restart_buttom = pygame.image.load('restart.png')
restart_buttom = pygame.transform.scale(restart_buttom, (125,125))
restart_buttom_rect = restart_buttom.get_rect(center = (600, 450))

#funzione che genera gli ostacoli
def vaccineGenerator():     
    ran_vaccine_position = random.choice(vaccine_heigh)
    top_vaccine = vaccine.get_rect(midbottom = (width, ran_vaccine_position - 125))
    bottom_vaccine = vaccine.get_rect(midtop = (width, ran_vaccine_position))
    return bottom_vaccine, top_vaccine

#funzione che fa muovere gli ostacoli verso il personaggio 
def vaccineMooving(vaccines, speed):    
    for vaccine1 in vaccines:
        vaccine1.centerx -= speed
    return vaccines

#funzione che disegna gli ostacoli lungo il percorso
def drawVaccine(vaccines):      
    for vaccine1 in vaccines:
        if vaccine1.bottom >= 500:
            screen.blit(vaccine, vaccine1)
        else:
            flip_vaccine = pygame.transform.flip(vaccine, False, True)
            screen.blit(flip_vaccine, vaccine1)

#funzione che valuta quando si colpisce un ostacolo o so superano i margini
def gameRules(vaccines):    
    for vaccine1 in vaccines:
        if virus_rect.colliderect(vaccine1):
            return False

    if virus_rect.top <= -100 or virus_rect.bottom >= 1100:
        return False

    return True

#funzione che determina lo stato della partita
def scoreScreen(game_situation):    
    
    #situazione di gioco
    if game_situation == 'main_game':
        score_sur = game_font.render(str(int(score)),True,(255,153,0))
        score_rect = score_sur.get_rect(center = (600,75))
        screen.blit(score_sur,score_rect)
    
    #situazione sconfitta
    if game_situation == 'game_over':
        #stampa a schermo del punteggio
        score_sur = game_font.render(f'Score: {int(score)}' ,True,(255,153,0))
        score_rect = score_sur.get_rect(center = (600,100))
        screen.blit(score_sur,score_rect)

        #stampa a schermo del punteggio massimo raggiunto
        high_score_sur = game_font.render(f'High Score: {int(high_score)}' ,True,(255,153,0))
        high_score_rect = high_score_sur.get_rect(center = (600,175))
        screen.blit(high_score_sur,high_score_rect) 

        #stampa a schermo GAME OVER
        game_over_sur = game_over_font.render(f'GAME OVER' ,True,(255,0,0))
        game_over_rect = game_over_sur.get_rect(center = (600,310))
        screen.blit(game_over_sur,game_over_rect) 

#funzione che salva il punteggio massimo
def updateHighScore(score, high_score):     
    if score > high_score:
        high_score = score
    return high_score

def cv2ImageToSurface(cv2Image):
    if cv2Image.dtype.name == 'uint16':
        cv2Image = (cv2Image / 256).astype('uint8')
    size = cv2Image.shape[1::-1]
    if len(cv2Image.shape) == 2:
        cv2Image = np.repeat(cv2Image.reshape(size[1], size[0], 1), 3, axis = 2)
        format = 'RGB'
    else:
        format = 'RGBA' if cv2Image.shape[2] == 4 else 'RGB'
        cv2Image[:, :, [0, 2]] = cv2Image[:, :, [2, 0]]
    surface = pygame.image.frombuffer(cv2Image.flatten(), size, format)
    return surface.convert_alpha() if format == 'RGBA' else surface.convert()

#funzione rilevamento colore
def color_tracking(frame):
    # Converts images from BGR to HSV 
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_c=np.array([150, 100, 100])
    upper_c=np.array([250, 255, 255])
    mask = cv2.inRange(hsv, lower_c, upper_c) 
    mask = cv2.erode(mask, None, iterations=5)
    mask = cv2.dilate(mask, None, iterations=5)
    res = cv2.bitwise_and(frame,frame, mask= mask) 
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.boundingRect(opening)

#ciclo necessario per il riavvio della partita      
while done == True: 
    
    #risettaggio variabili necessarie
    main = True
    game = True
    score = 0
    speed = 5
    vaccine_list = []
    sound_backgrownd = pygame.mixer.music.play()
    
    #ciclo del gioco
    while main == True:   
       
       #uso fotocamera
        _, frame = cap.read()                               
        
        #eventi necessari per l'apertura della finestra
        for event in pygame.event.get():                    
            if event.type == pygame.QUIT:                   
                pygame.quit()
                sys.exit()          
            
            if event.type == SPAWNVACCINE:
                vaccine_list.extend(vaccineGenerator())                       
            
            #rilevamento input da mouse
            if event.type == MOUSEBUTTONDOWN:               
                k, j = pygame.mouse.get_pos()               
                if j >= 437 and j <= 437 + 125:             
                    if k >= 562 and k <= 562 + 125:         
                        main = False
                        break
        #disegna sfondo
        screen.blit(backgrownd,(0,0))

        #if che fa si che ogni 20 punti la velocità aumenta
        if score % 20 == 0:
            speed += 3 

        #richiamo alla funzione del riconoscimente del colore
        x, y, w, h = color_tracking(frame)
        y = y + h/2
        #settaggio delle coordinate dell'oggetto rilevato con la libreria openCv, al virus
        virus_rect = virus.get_rect(center = (VIRUS_POS_X, y))
        screen.blit(virus, virus_rect)

        if game:
            game = gameRules(vaccine_list)

            #disegna tubi
            vaccine_list = vaccineMooving(vaccine_list, speed) 
            drawVaccine(vaccine_list)   

            #settaggio della velocità di incremento dei punti
            score += 0.06
            scoreScreen('main_game')
        else:
            screen.blit(restart_buttom, restart_buttom_rect)    #stampa a video del pulsante di riavvio
            high_score = updateHighScore(score, high_score)     #salvataggio del punteggio massimo
            scoreScreen('game_over')                            #richiamo alla funzione scoreScreen
            sound_backgrownd = pygame.mixer.music.stop()        #stop musica di sottofondo

        #disegna pavimento
        screen.blit(floor,(floor_posizione_x,550))
        screen.blit(floor,(floor_posizione_x + width,550))
        floor_posizione_x -= speed

        #fa tornare l'immagine all'inizio dando un effetto di movimento
        if floor_posizione_x <= -width:
            floor_posizione_x = 0

        #aggiorna lo schermo ad ogni ciclo del while
        pygame.display.update()
        clock.tick(120)