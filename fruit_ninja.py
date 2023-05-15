import pygame
import sys
import cv2
from cvzone.HandTrackingModule import HandDetector
import random
from pygame import mixer

width = 1366
height = 768

# opencv code
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detector = HandDetector(maxHands=2, detectionCon=0.8)

# Initialize the pygame
pygame.init()

# background sounds
mixer.music.load('music/background.mp3')
mixer.music.play(loops=-1)



catching_sound = mixer.Sound('music/catching_sound.wav')




# Define the screen
screen = pygame.display.set_mode((width, height))

# Timer
clock = pygame.time.Clock()
currentTime = 1


# Title and Icon


load_screen = pygame.image.load('images/load.png').convert_alpha()
pygame.display.set_icon(load_screen )
pygame.display.set_caption("Fruit Ninja Game")
icon = pygame.image.load('images/melon.png').convert_alpha()
pygame.display.set_icon(icon)
icon1 = pygame.image.load('images/apple.png').convert_alpha()
pygame.display.set_icon(icon1)
icon2 = pygame.image.load('images/banana.png').convert_alpha()
pygame.display.set_icon(icon2)
icon3 = pygame.image.load('images/pineapple.png').convert_alpha()
pygame.display.set_icon(icon3)
start = pygame.transform.scale(pygame.image.load('images/page.png'), (64, 64))
pygame.display.set_icon(start)
backgroundImg = pygame.image.load('images/Background.png').convert()


# Player
playerPosition = [370, 480]
playerMovement = [0, 0]
x = width/2 - 64
y = height/2 - 64


openHandImg = pygame.image.load('images/openHand.png').convert_alpha()
openHandImg = pygame.transform.scale(openHandImg, (128, 128))
openHand_rect = openHandImg.get_rect(topleft=(x, y))

openHandImg2 = pygame.image.load('images/closedHand.png').convert_alpha()
openHandImg2 = pygame.transform.scale(openHandImg2, (128, 128))
openHand_rect2 = openHandImg2.get_rect(topleft=(x, y))



closedHandImg = pygame.image.load('images/openHand.png').convert_alpha()
closedHandImg = pygame.transform.scale(closedHandImg, (128, 128))
closedHand_rect = closedHandImg.get_rect(topleft=(x, y))

closedHandImg2 = pygame.image.load('images/closedHand.png').convert_alpha()
closedHandImg2 = pygame.transform.scale(closedHandImg2, (128, 128))
closedHand_rect2 = closedHandImg2.get_rect(topleft=(x, y))




# Insects
InsectImg = []
InsectX = []
InsectY = []
insect_rect = []
insectMoveX = []
insectMoveY = []
numberOfInsects = 10
for i in range(numberOfInsects):
    InsectX.append(random.randint(0, 1366))
    InsectY.append(random.randint(0, 768))
    InsectImg.append(pygame.image.load('images/melon.png').convert_alpha())
    InsectImg.append(pygame.image.load('images/apple.png').convert_alpha())
    InsectImg.append(pygame.image.load('images/banana.png').convert_alpha())
    InsectImg.append(pygame.image.load('images/pineapple.png').convert_alpha())
    #InsectImg.append(pygame.transform.scale(InsectImg, (32, 32)))
    insect_rect.append(InsectImg[i].get_rect(topleft=(InsectX[i], InsectY[i])))
    insect_rect.append(InsectImg[i].get_rect(topright=(InsectX[i], InsectY[i])))
    insectMoveX.append(10)
    insectMoveY.append(8)

## Game Texts
 # Score Text
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
gameOver_font = pygame.font.Font('freesansbold.ttf', 100)
textX = 50
textY = 30
def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))
def show_timer():
    time_limit = 60  # Set the time limit to 10 seconds

    if currentTime / 1000 >= time_limit:
        time_remaining = 0
    else:
        time_remaining = time_limit - int(currentTime / 1000)

    if time_remaining > 0:
        timer = font.render("Time: " + str(time_remaining), True, (255, 255, 255))
        screen.blit(timer, (1210, 10))
    else:
        gameOver = True
        game_over_text = gameOver_font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (width/2 - 300, height/2 - 30))
        # Add code to end the game or perform any necessary actions




indexes_for_closed_fingers = [8, 12, 16, 20]
#### Game Loop#####
catch_insect_with_openHand = False
fingers = [0, 0, 0, 0]



while True:
    # Game code
   
    screen.blit(backgroundImg, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
       
    # opencv code
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # Mediapipe code for hand detection and Landmarks
    hands, frame = detector.findHands(frame)

    # Landmarks value - (x,y,z) * 21
    if hands:
        #Get the first hand detected
        lmList = hands[0]

        
        positionOfTheHand = lmList['lmList']

        openHand_rect.left = (positionOfTheHand[9][0] - 200) * 1.5
        openHand_rect.top = (positionOfTheHand[9][1] - 200) * 1.5
        closedHand_rect.left = (positionOfTheHand[9][0] - 200) * 1.5
        closedHand_rect.top = (positionOfTheHand[9][1] - 200) * 1.5
        
        
        ## open or closed hand
        hand_is_closed = 0 #for playing the sound once when hand is closed
        for index in range(0, 4):
            if positionOfTheHand[indexes_for_closed_fingers[index]][1] > positionOfTheHand[indexes_for_closed_fingers[index] - 2][1]:
                fingers[index] = 1
            else:
                fingers[index] = 0
            if fingers[0]*fingers[1]*fingers[2]*fingers[3]:
                # playing close hand sound
                
                hand_is_closed = 0
                screen.blit(closedHandImg, closedHand_rect)
                
                # detect catching
                for iteration in range(numberOfInsects):
                    if openHand_rect.colliderect(insect_rect[iteration]) and catch_insect_with_openHand:
                        score_value += 1
                        catching_sound.play()
                        catch_insect_with_openHand = False
                        insect_rect[iteration] = InsectImg[iteration].get_rect(topleft=(random.randint(0, 1366), random.randint(0, 768)))

                catch_insect_with_openHand = False
            else:
                screen.blit(openHandImg, openHand_rect)
                hand_is_closed = 1
                for iterate in range(numberOfInsects):
                    if openHand_rect.colliderect(insect_rect[iterate]):
                        catch_insect_with_openHand = True
    if hands:
            if len(hands) >= 2:
                lmList = hands[1]
                positionOfTheHand = lmList['lmList']
    
                openHand_rect2.right = (positionOfTheHand[9][0] - 200) * 1.5
                openHand_rect2.top = (positionOfTheHand[9][1] - 200) * 1.5
                closedHand_rect2.right = (positionOfTheHand[9][0] - 200) * 1.5
                closedHand_rect2.top = (positionOfTheHand[9][1] - 200) * 1.5
                
                
        
        
        
                ## open or closed hand
                hand_is_closed = 0 #for playing the sound once when hand is closed
                for index in range(0, 4):
                    if positionOfTheHand[indexes_for_closed_fingers[index]][1] > positionOfTheHand[indexes_for_closed_fingers[index] - 2][1]:
                        fingers[index] = 1
                    else:
                        fingers[index] = 0
                    if fingers[0]*fingers[1]*fingers[2]*fingers[3]:
                        # playing close hand sound
                        
                        hand_is_closed = 0
                        screen.blit(closedHandImg2, closedHand_rect2)
                        
                        # detect catching
                        for iteration in range(numberOfInsects):
                            if openHand_rect2.colliderect(insect_rect[iteration]) and catch_insect_with_openHand:
                                score_value += 1
                                catching_sound.play()
                                catch_insect_with_openHand = False
                                insect_rect[iteration] = InsectImg[iteration].get_rect(topleft=(random.randint(0, 1366), random.randint(0, 768)))
        
                        catch_insect_with_openHand = False
                    else:
                        screen.blit(openHandImg2, openHand_rect2)
                        hand_is_closed = 1
                        for iterate in range(numberOfInsects):
                            if openHand_rect2.colliderect(insect_rect[iterate]):
                                catch_insect_with_openHand = True


    
    cv2.imshow("webcam", frame)

  
    for i in range(numberOfInsects):
            # moving X
        insect_rect[i].right += insectMoveX[i]
        if insect_rect[i].right <= 16:
            insectMoveX[i] += 10
        elif insect_rect[i].right >= width:
            insectMoveX[i] -= 10

            # moving Y
        insect_rect[i].top += insectMoveY[i]
        if insect_rect[i].top <= 0:
            insectMoveY[i] += 8
        elif insect_rect[i].top >= height-32:
            insectMoveY[i] -= 8
        screen.blit(InsectImg[i], insect_rect[i])

    # showing texts
    show_score(textX, textY)
    currentTime = pygame.time.get_ticks()
    show_timer()
    
    
    # display update
    pygame.display.update()
    clock.tick(60)
