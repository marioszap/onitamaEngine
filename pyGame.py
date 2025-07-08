import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import json
from engine import *
from minMax import *
import random
import sys
import time
from UserInterface import runSetupWindow

MAX_FPS = 10
IMAGES = {}
cardToPlay = None

def initGame(pTypes, json=None) -> GameState:

    if json is None:
        cardsInGame = loadCards()
        game = GameState(n, cardsInGame)
        game.activePlayerIndex = game.firstPlayerIdx
        game.playerTurn(pTypes)
    else:
        print(pTypes)
        if 'randomCards' in json and json['randomCards']:
            cardsInGame = loadCards()
        else:
            print({'p1': json['p1'], 'p2': json['p2'], 'cardOut': json['cardOut']})
            cardsInGame = loadCards({'p1': json['p1'], 'p2': json['p2'], 'cardOut': json['cardOut']})
        game = GameState(n, cardsInGame)
        
        if json['playsFirst'] == 'p1':
            game.activePlayerIndex = game.firstPlayerIdx = 0
        elif json['playsFirst'] == 'p2':
            game.activePlayerIndex = game.firstPlayerIdx = 1
        else:
            game.activePlayerIndex = game.firstPlayerIdx
        game.playerTurn(pTypes)

    return game


def loadCards(cardsPerPlayer = None) -> dict[str]:
    if cardsPerPlayer is None:
        allCards = open('cardsMoves.json')
        allCards = json.load(allCards)
        cardsNames = [name for name in allCards]
        cardsNames = random.sample(cardsNames, 5)
        cardsInGame = {}
        for name in cardsNames:
            cardsInGame[name] = allCards[name]
        print('cardsInGame: ', cardsInGame)
    else:
        allCards = open('cardsMoves.json')
        allCards = json.load(allCards)
        cardsInGame = {}
        for playerName in cardsPerPlayer:
            cardsInGame[playerName] = {}
            for cardName in cardsPerPlayer[playerName]:
                cardsInGame[playerName][cardName] = allCards[cardName]
        print('cardsInGame: ', cardsInGame)
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


def engine(p1Type=0, p2Type=0, jsonGameSetup = None) -> None:

    pTypes = [int(p1Type), int(p2Type)]
    if jsonGameSetup is not None:
        pTypes = [1 if 'p1_type' in jsonGameSetup else 0, 1 if 'p2_type' in jsonGameSetup else 0]

    game = initGame(pTypes, jsonGameSetup)

    #root = node(game, True)
    pygame.init()

    clock = pygame.time.Clock()
    screen.fill(pygame.Color("white"))
    loadImages()
    running = True
    turnFinished = False

    for p in range(len(pTypes)): #if player is played by AI deactivate their cards
        if pTypes[p]:
            for card in game.players[p].cards:
                card.active = False
                #print('deactivated')


    algorithmMovesMade = 0
    while running:

        try:
            validMoves
        except NameError:
            validMoves = None
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        pygame.display.set_caption("Onitama engine: "+game.players[game.activePlayerIndex].name+ "'s turn")

        drawBackground(screen)
        game.drawBoard(screen)

        player = game.players[game.activePlayerIndex]
        inactivePlayer = game.players[(game.activePlayerIndex + 1) % 2]

        if game.endMessage or validMoves == 'Mate':
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
                if int(pTypes[game.activePlayerIndex]) == 0:
                    turnFinished = game.highlightSquares(screen, cardToPlay, player.name)

                elif int(pTypes[game.activePlayerIndex]) == 1 and jsonGameSetup is not None:
                    if(algorithmMovesMade == 0):
                        elapsedTime = 0
                        movesDurations = []
                        try:
                            depth = int(jsonGameSetup[game.players[game.activePlayerIndex].name+'_depth'])
                        except: 
                            depth = 5
                        algorithmName = jsonGameSetup[game.players[game.activePlayerIndex].name+'_type']
                        if jsonGameSetup[game.players[game.activePlayerIndex].name+'_transpositionTbale']:
                            zobrist = ZobristHashing(game)
                        else:
                            zobrist = None
                        try:
                            moveOrdering: bool = jsonGameSetup[game.players[game.activePlayerIndex].name+'_moveOrdering']
                        except:
                            moveOrdering = False
                        print()
                        print(f"For depth {depth}, algorithmName: {algorithmName}, zobrist: {zobrist}, alpha_beta: {bool(jsonGameSetup[game.players[game.activePlayerIndex].name+'_alpthaBeta'])}")
                        print(type(algorithmName))
                    start = time.perf_counter()
                    move: dict = findNextMove(game, depth, zobrist, algorithmName, ordering=moveOrdering, alpha_beta=bool(jsonGameSetup[game.players[game.activePlayerIndex].name+'_alpthaBeta']))
                    end = time.perf_counter()
                    elapsedTime += end - start
                    movesDurations.append(f"{end - start:.5f}")
                    movesDurations[-1] += ' sec'
                    algorithmMovesMade += 1

                    print(f"\tAverage Move Duration: {elapsedTime/algorithmMovesMade:.5f} sec")
                    print("\tMoves durations: ", str(movesDurations).replace("'", "")[1:-1])
                    print()

                    movesDurations[-1] = movesDurations[-1].split(' ')[0]
                    cardToPlayName = list(move.keys())[0]
                    cardToPlay = game.getCardByName(cardToPlayName)
                    game.movePawn(move[cardToPlayName][0][::-1], move[cardToPlayName][1][::-1], cardToPlayName)
                    turnFinished = True

                elif int(pTypes[game.activePlayerIndex]) == 1:
                    if(algorithmMovesMade == 0):
                        elapsedTime = 0
                        movesDurations = []
                        depth = 5
                        algorithmName = 'MinMax'
                        zobrist = ZobristHashing(game)
                        print()
                        print(f"For depth {depth}:")
                    start = time.perf_counter()
                    move: dict = findNextMove(game, depth, zobrist, algorithmName, ordering=False, alpha_beta=True)
                    end = time.perf_counter()
                    elapsedTime += end - start
                    movesDurations.append(f"{end - start:.5f}")
                    movesDurations[-1] += ' sec'
                    algorithmMovesMade += 1

                    print(f"\tAverage Move Duration: {elapsedTime/algorithmMovesMade:.5f} sec")
                    print("\tMoves durations: ", str(movesDurations).replace("'", "")[1:-1])
                    print()

                    movesDurations[-1] = movesDurations[-1].split(' ')[0]
                    cardToPlayName = list(move.keys())[0]
                    cardToPlay = game.getCardByName(cardToPlayName)
                    game.movePawn(move[cardToPlayName][0][::-1], move[cardToPlayName][1][::-1], cardToPlayName)
                    turnFinished = True

            
            drawPawns(screen, game.board, (SCREEN_WIDTH-BOARD_HEIGHT)/2, (SCREEN_HEIGHT-BOARD_HEIGHT)/2)

            if turnFinished:
                game.playerTurn(pTypes)
                player.unclickCards()
                game.cardOut = player.sendCard(cardToPlay, game.cardOut)

                #game.undoMove()
                #cardRarity(game.cardsInGame)
                validMoves = game.getPlayerValidMoves(game.players[game.activePlayerIndex])
                cardToPlay = None
                turnFinished = False
                #game.getPlayerValidMoves(game.players[game.activePlayerIndex])

        clock.tick(MAX_FPS)
        pygame.display.flip()


if __name__ == "__main__":
    terminalArgs = sys.argv[1:]
    if len(terminalArgs) == 0:
        jsonToSetup = runSetupWindow()
        print(jsonToSetup)
        engine(jsonGameSetup = jsonToSetup)

        print(jsonToSetup)
    elif len(terminalArgs) <= 2:
        engine(*terminalArgs)
