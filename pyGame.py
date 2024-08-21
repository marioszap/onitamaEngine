import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import json
from engine import *
import random
import sys

MAX_FPS = 10
IMAGES = {}
cardToPlay = None

def initGame(pTypes) -> GameState:
    cardsInGame = loadCards()
    game = GameState(n, cardsInGame)
    game.activePlayerIndex = game.firstPlayerIdx
    game.playerTurn(game.activePlayerIndex, pTypes)
    return game

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


def engine(p1Type=0, p2Type=0) -> None:
    pygame.init()
    pTypes = [p1Type, p2Type]
    game = initGame(pTypes)
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    loadImages()
    running = True
    turnFinished = False
    x = game.getPlayerValidMoves('p2')

    for p in range(len(pTypes)): #if player is played by AI inactivate their cards
        if pTypes[p]:
            for card in game.players[p].cards:
                card.active = False
    
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        pygame.display.set_caption("Onitama engine: "+game.players[game.activePlayerIndex].name+ "'s turn")

        
        drawBackground(screen)
        game.drawBoard(screen)

        player = game.players[game.activePlayerIndex]
        inactivePlayer = game.players[(game.activePlayerIndex + 1) % 2]
        if game.endMessage:
            game.drawEndScreen(game.endMessage)
            for e in pygame.event.get():
                if pygame.key.get_pressed():
                    game = initGame(pTypes) #new game starts immediately

        else:
            game.drawFirstCardOut()
            for i in range(len(player.cards)):
                x = player.cards[i].draw(screen, player.cards[1-i])
                if pTypes[game.activePlayerIndex]: #if player is AI 
                    x = player.cards[0] 
                inactivePlayer.cards[i].draw(screen, player.cards[1-i])
                if not x is None:
                    global cardToPlay
                    cardToPlay = x
            
            if not cardToPlay is None:
                if pTypes[game.activePlayerIndex] == 0:
                    turnFinished = game.highlightSquares(screen, cardToPlay, player.name)
                elif int(pTypes[game.activePlayerIndex]) == 1:
                    game.movePawn([0,0], [1,1])
                    turnFinished = True
                elif int(pTypes[game.activePlayerIndex]) == 2:
                    game.movePawn([0,1], [1,1])
                    turnFinished = True
            
            drawPawns(screen, game.board, (SCREEN_WIDTH-BOARD_HEIGHT)/2, (SCREEN_HEIGHT-BOARD_HEIGHT)/2)

            if turnFinished:
                game.activePlayerIndex = (game.activePlayerIndex + 1) % 2
                game.playerTurn(game.activePlayerIndex, pTypes)
                player.unclickCards()
                game.cardOut = player.sendCard(cardToPlay, game.cardOut)
                cardToPlay = None
                turnFinished = False
        
        clock.tick(MAX_FPS)
        pygame.display.flip()


if __name__ == "__main__":
    typesOfPlayers = sys.argv[1:]
    if len(typesOfPlayers) <= 2:
        engine(*typesOfPlayers)