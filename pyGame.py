import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import json
from engine import *
import random

MAX_FPS = 10
IMAGES = {}
movesToPlay =[]


def loadCards() -> dict[str]:
    allCards = open('cardsMoves.json')
    allCards = json.load(allCards)
    cardsNames = [name for name in allCards]
    cardsNames = random.sample(cardsNames, 5)
    cardsInGame = {}
    for name in cardsNames:
        cardsInGame[name] = allCards[name]
    return cardsInGame


def loadImages() -> None:
    dir = 'images'
    pieces = ['p1S', 'p1M', 'p2S', 'p2M']
    j=0
    for file in os.listdir(dir):
        if (not file == "whiteCircle.png") and ('Circle' in file):
            IMAGES[pieces[j]] = pygame.transform.scale(pygame.image.load("images/"+file), (SQ_SIZE, SQ_SIZE))
            j+=1


def drawBackground(screen) -> None:
    pygame.draw.rect(screen, "grey5", pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))


def drawPawns(screen, board, stW, stH) -> None:
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(c*SQ_SIZE+stW, r*SQ_SIZE+stH, SQ_SIZE+stW, SQ_SIZE+stH))


def engine() -> None:
    pygame.init()
    pygame.display.set_caption('Onitama engine')
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))

    cardsInGame = loadCards()
    game = GameState(n, cardsInGame)
    loadImages()
    running = True


    game.players[1].playerTurn()

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        drawBackground(screen)
        game.drawBoard(screen)
        game.drawFirstCardOut(game.cardOut.name, game.cardOut.moves)

        for player in game.players:
            #player = players[1]
            for i in range(len(player.cards)):
                x = player.cards[i].draw(screen, player.cards[1-i])
                if not x is None:
                    global movesToPlay
                    movesToPlay = x
        
        if not movesToPlay is None:
            #print(movesToPlay)
            game.highlightSquares(screen, movesToPlay, player.name)
        drawPawns(screen, game.board, (SCREEN_WIDTH-BOARD_HEIGHT)/2, (SCREEN_HEIGHT-BOARD_HEIGHT)/2)
        
        clock.tick(MAX_FPS)
        pygame.display.flip()

if __name__ == "__main__":
    engine()