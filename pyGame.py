import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import json
from engine import *
import random

MAX_FPS = 8
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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    game = GameState(n)

    cardsInGame = loadCards()
    players = [None] * 2
    pNames = ['p1', 'p2']
    for i in range(len(players)):
        players[i] = Player(i-1, cardsInGame, pNames[i])
    players[i].playerTurn()
    loadImages()
    running = True
    print('p1: ', players[0].cards[0].name, players[0].cards[0].moves, players[0].cards[1].name, players[0].cards[1].moves)
    print('p2: ', players[1].cards[0].name, players[1].cards[0].moves, players[1].cards[1].name, players[1].cards[1].moves)

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        drawBackground(screen)
        game.drawBoard(screen, bigOffset)

        for player in players:
            for i in range(len(player.cards)):
                x = player.cards[i].draw(screen, player.cards[1-i])
                if not x is None:
                    global movesToPlay
                    movesToPlay = x
        
        if not movesToPlay is None:
            #print(movesToPlay)
            game.highlightSquares(screen, movesToPlay, 'p2')
        drawPawns(screen, game.board, (SCREEN_WIDTH-BOARD_HEIGHT)/2, (SCREEN_HEIGHT-BOARD_HEIGHT)/2)
        
        clock.tick(MAX_FPS)
        pygame.display.flip()

if __name__ == "__main__":
    engine()