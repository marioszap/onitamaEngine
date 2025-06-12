import ast
import random, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import math
import itertools
import sys
import copy
from collections import defaultdict

n = 5
COLORS = ['red', 'blue']
SCREEN_HEIGHT = 1000 #pygame.display.set_mode().get_size()[1] - 25
SCREEN_WIDTH = SCREEN_HEIGHT
CARD_SQUARE = SCREEN_HEIGHT // 30
CARD_HEIGHT = CARD_SQUARE * 5
CARD_LENGTH = 9 * CARD_SQUARE
BOARD_WIDTH = BOARD_HEIGHT = SCREEN_HEIGHT//2
DIMENSION = n
SQ_SIZE = BOARD_HEIGHT // DIMENSION
bigOffset = SCREEN_HEIGHT // 40
smallOffset = SCREEN_HEIGHT // 100
squareClicked = [None] * 2
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def drawTransparentRect(screen, color, stW, stH, sideX, sideY, alpha=64) -> None:
    s = pygame.Surface((sideX, sideY))
    s.set_alpha(alpha)
    s.fill(color)
    screen.blit(s, (stW, stH))


class Card():
    def __init__(self, name:str, moves:list[list[int]], stPoint=list[int], cardL=CARD_LENGTH, cardH=CARD_HEIGHT) -> None:
        self.name = name
        self.moves = moves
        self.cardL = cardL
        self.cardH = cardH
        self.stPoint = stPoint
        self.clicked = False
        self.active = False #Is this card in hand of the player whose turn it is?
        self.rarity = 0

    def mirrorCoord(self, coord) -> None:
        for i in range(len(self.moves)):
            self.moves[i][coord] = -1 * self.moves[i][coord]


    def swapCoordinates(self) -> None:
        for i in range(len(self.moves)):
            temp = self.moves[i][0]
            self.moves[i][0] = self.moves[i][1]
            self.moves[i][1] = temp


    def swapHeightWithWidth(self) -> None:
        temp = self.cardL
        self.cardL = self.cardH
        self.cardH = temp


    def draw(self, screen, otherCardInHand, sq=CARD_SQUARE, offset=smallOffset) -> None:
        """
        isUserView: -1 if it is, 1 otherwise
        """
        mousePosition = pygame.mouse.get_pos()
        clickArea = pygame.Rect(self.stPoint[0], self.stPoint[1], self.cardL, self.cardH)

        if self.active:
            cardHighlightColor = 'yellow'
            if clickArea.collidepoint(mousePosition) and not self.clicked:
                drawTransparentRect(screen, cardHighlightColor, self.stPoint[0]-offset/2, self.stPoint[1]-offset/2, self.cardL+offset, self.cardH+offset, 128)
            
                if pygame.mouse.get_pressed()[0]:
                    self.clicked = True
                    otherCardInHand.clicked = False
                    return self
            
            if self.clicked:
                drawTransparentRect(screen, cardHighlightColor, self.stPoint[0]-offset/2, self.stPoint[1]-offset/2, self.cardL+offset, self.cardH+offset, 250)

        pygame.draw.rect(screen, "bisque1", clickArea)
        
        centerStPoint = [None] * 2
        centerStPoint[0] = self.stPoint[0] + self.cardL/2 - sq/2
        centerStPoint[1] = self.stPoint[1] + self.cardH/2 - sq/2
        #centerStPoint is set to the starting point of the central square

        lineColor = 'bisque2'
        lineThickness = sq//33
        for i in range(self.cardL // sq //2 + 1):
            pygame.draw.line(screen, lineColor, ((i+1)*sq + centerStPoint[0],self.stPoint[1]), ((i+1)*sq + centerStPoint[0], self.stPoint[1]+self.cardH), lineThickness)
            pygame.draw.line(screen, lineColor, (centerStPoint[0] - i*sq,self.stPoint[1]), (centerStPoint[0] - i*sq, self.stPoint[1]+self.cardH), lineThickness)
        
        for i in range(self.cardH // sq // 2 + 1):
            pygame.draw.line(screen, lineColor, (self.stPoint[0], (i+1)*sq+centerStPoint[1]), (self.stPoint[0]+self.cardL, (i+1)*sq+centerStPoint[1]), lineThickness)
            pygame.draw.line(screen, lineColor, (self.stPoint[0], centerStPoint[1] - i*sq), (self.stPoint[0]+self.cardL, centerStPoint[1] - i*sq), lineThickness)

        pygame.draw.rect(screen, "black", pygame.Rect(centerStPoint[0], centerStPoint[1], sq, sq))

        for move in self.moves:
            pygame.draw.rect(screen, "navy", pygame.Rect(centerStPoint[0]+move[0]*sq, centerStPoint[1]+move[1]*sq, sq, sq))

        font = pygame.font.Font('freesansbold.ttf', 15)
        text = font.render(self.name, True, 'bisque3')
        textRect = text.get_rect()
        textRect.center = (self.stPoint[0] + text.get_size()[0]/2, self.stPoint[1] + text.get_size()[1]/2)
        screen.blit(text, textRect)


class Player():
    def __init__(self, userView, cardsInGame, name, color) -> None:
        self.cards = [None] * 2
        cardX = [None] * 2
        self.userView = userView
        self.color = color
        cardX[0] = SCREEN_WIDTH // 4 - CARD_LENGTH // 2
        cardX[1] = cardX[0] + SCREEN_WIDTH // 2
        cardY = (SCREEN_HEIGHT-BOARD_HEIGHT)/4 - CARD_HEIGHT // 2 - bigOffset//2 - smallOffset//2
        if not userView:
            cardY =+ 3*SCREEN_HEIGHT // 4 + 2.5*bigOffset
        self.cards = self.pickCards(cardsInGame, cardX, cardY)
        self.plays = False
        self.name = name
        if not userView:
            for card in self.cards:
                card.mirrorCoord(1)#"""
        else:
            for card in self.cards:
                card.mirrorCoord(0)#"""

    def getCardIndexByName(self, cardName) -> int :
        for i in range(2):
            if self.cards[i].name == cardName:
                return i

    def pickCards(self, cardsDict: dict, coorsX: list[int], coorY: int) -> list[Card]:
        cardsToChooseFrom = random.sample([card for card in cardsDict], 2)
        cards = [None] * len(coorsX)
        for i in range(len(cardsToChooseFrom)):
            cards[i] = Card(cardsToChooseFrom[i], cardsDict[cardsToChooseFrom[i]], [coorsX[i], coorY])
            cardsDict.pop(cardsToChooseFrom[i])
        return cards


    def sendCard(self, card, cardOut: Card, p1OutCoord=0, p2OutCoord=0):
        #stW = (SCREEN_WIDTH-BOARD_HEIGHT)/2, stH = (SCREEN_HEIGHT-BOARD_HEIGHT)/2)
        coords = [p1OutCoord, p2OutCoord]
        if cardOut.stPoint[0] >= BOARD_HEIGHT:
            cardOutStPoint = [((SCREEN_WIDTH-BOARD_HEIGHT)/2-CARD_HEIGHT+4*smallOffset)/2, (SCREEN_WIDTH-BOARD_HEIGHT)/2 + SQ_SIZE/2 + smallOffset]
        else:
            cardOutStPoint = [((SCREEN_WIDTH-BOARD_HEIGHT)/2-CARD_HEIGHT+4*smallOffset)/2 + BOARD_WIDTH + 2*bigOffset + CARD_HEIGHT,
                                SCREEN_WIDTH/2 + BOARD_HEIGHT/2 - SQ_SIZE/2 - smallOffset - CARD_LENGTH]
        idx = self.cards.index(card)
        playedCardCoords = self.cards[idx].stPoint

        self.cards[idx].swapHeightWithWidth()
        self.cards[idx].swapCoordinates()
        self.cards[idx].mirrorCoord(0)
        self.cards[idx].stPoint = cardOutStPoint

        cardOut.swapHeightWithWidth()
        cardOut.swapCoordinates()
        cardOut.mirrorCoord(0)
        cardOut.stPoint = playedCardCoords
        cardToSend = self.cards[idx]
        self.cards[idx] = cardOut
        return cardToSend


    def unclickCards(self):
        for card in self.cards:
            card.clicked = False


class GameState():
    def __init__(self, n: int, cardsInGame, colors=COLORS, stW = (SCREEN_WIDTH-BOARD_HEIGHT)/2, stH = (SCREEN_HEIGHT-BOARD_HEIGHT)/2) -> None:
        """
        :n:is an odd integer larger than one
        :return:None
        """
        self.board = [["p1S" for i in range(n)]] \
                    + [["--" for i in range(n)] for i in range(n-2)] \
                    + [["p2S" for i in range(n)]]
        self.p1Throne = [0, n//2]
        self.p2Throne = [n-1, n//2]
        #self.p2Throne = [n-3, n//2] #this is to be replaced with code above
        self.board[self.p1Throne[0]][self.p1Throne[1]] = "p1M"
        self.board[self.p2Throne[0]][self.p2Throne[1]] = "p2M"
        ########################################to be removed################################################
        """self.board[self.p2Throne[0]][self.p2Throne[1]+1] = '--'
        self.board[self.p1Throne[0]][self.p1Throne[1]+1] = '--'
        self.board[self.p2Throne[0]][self.p2Throne[1]-1] = '--'
        self.board[self.p1Throne[0]][self.p1Throne[1]-1] = '--'
        self.board[self.p2Throne[0]][self.p2Throne[1]] = "--"
        self.board[self.p1Throne[0]][self.p1Throne[1]] = "--"
        self.board[1][3] = "p1M"
        self.board[1][1] = "p2M"#"""
        ########################################to be removed################################################
        self.clicked = False
        self.clickArea = pygame.Rect(stW, stH, BOARD_HEIGHT, BOARD_HEIGHT)
        self.stW = stW
        self.stH = stH
        self.players = [Player] * 2
        for i in range(len(self.players)):
            self.players[i] = Player(1-i, cardsInGame, f'p{i+1}', colors[i])
        self.firstPlayerIdx = random.randint(0,1)
        self.firstPlayer = self.players[self.firstPlayerIdx]
        self.endMessage = None
        self.activePlayerIndex = None
        for el in cardsInGame:
            if self.firstPlayer.userView:
                self.cardOut = Card(el, cardsInGame[el], [(self.stW-CARD_HEIGHT+4*smallOffset)/2, self.stW + SQ_SIZE/2 + smallOffset])            
            else:
                self.cardOut = Card(el, cardsInGame[el], [(self.stW-CARD_HEIGHT+4*smallOffset)/2 + BOARD_WIDTH + 2*bigOffset + CARD_HEIGHT,
                                                        self.stW + BOARD_HEIGHT - SQ_SIZE/2 - 2*smallOffset- CARD_LENGTH + smallOffset])
                self.cardOut.mirrorCoord(0)
                self.cardOut.mirrorCoord(1)
        self.moveLog = [{self.cardOut.name+'_--_--': []}]
        self.previousState = None
        self.cardOut.swapCoordinates()
        self.cardOut.swapHeightWithWidth()
        self.cardsInGame = []
        for player in self.players:
            for card in player.cards:
                self.cardsInGame.append(card)
        self.cardsInGame.append(self.cardOut)


    def drawFirstCardOut(self) -> None:
        if self.firstPlayer.userView:
            self.cardOut.draw(screen, None)
        else:
            self.cardOut.draw(screen, None)


    def drawBoard(self, screen, offset=bigOffset, smallOffset=smallOffset) -> None:
        pygame.draw.rect(screen, "grey16", pygame.Rect(self.stW-offset, self.stH-offset, BOARD_HEIGHT+2*offset, BOARD_HEIGHT+2*offset))
        pygame.draw.rect(screen, "burlywood", self.clickArea)
        lineColor = 'burlywood3'
        for i in range(0, DIMENSION+1):
            pygame.draw.line(screen, lineColor, (i*SQ_SIZE+self.stW, self.stH), (i*SQ_SIZE+self.stW, BOARD_HEIGHT+self.stH), SQ_SIZE//20) #Vertical
            pygame.draw.line(screen, lineColor, (self.stW, i*SQ_SIZE+self.stH), (BOARD_HEIGHT+self.stW, i*SQ_SIZE+self.stH), SQ_SIZE//20) #Horizontal
        drawTransparentRect(screen, "navy", (n//2)*SQ_SIZE+self.stW, 0*SQ_SIZE+self.stH, SQ_SIZE, SQ_SIZE)
        drawTransparentRect(screen, "red", (n//2)*SQ_SIZE+self.stW, (n-1)*SQ_SIZE+self.stH, SQ_SIZE, SQ_SIZE)
        for player in self.players:
            for card in player.cards:
                pygame.draw.rect(screen, "grey16", pygame.Rect(card.stPoint[0]-smallOffset, card.stPoint[1]-smallOffset, card.cardL+2*smallOffset, card.cardH+2*smallOffset))
        pygame.draw.rect(screen, "grey16", pygame.Rect((self.stW-card.cardH+2*smallOffset)/2, self.stW + SQ_SIZE/2, card.cardH+2*smallOffset, card.cardL+2*smallOffset)) #left
        pygame.draw.rect(screen, "grey16", pygame.Rect((self.stW-card.cardH+2*smallOffset)/2 + BOARD_WIDTH + 2*offset + card.cardH, self.stW + BOARD_HEIGHT - SQ_SIZE/2 - 2*smallOffset
                                                        - card.cardL, card.cardH+2*smallOffset, card.cardL+2*smallOffset))#"""



    def highlightSquares(self, screen, card: Card, playerName: str) -> bool:
        mousePosition = pygame.mouse.get_pos()
        squareHovered = [None] * 2
        sqHighlightColor = 'yellow'
        squareHovered[1] = int((mousePosition[0] - self.stW) / SQ_SIZE)
        squareHovered[0] = int((mousePosition[1] - self.stH) / SQ_SIZE)

        if self.clickArea.collidepoint(mousePosition):
            
            if (self.board[squareHovered[0]][squareHovered[1]] != '--') and (self.board[squareHovered[0]][squareHovered[1]][:2] == playerName):
                if pygame.mouse.get_pressed()[0]:
                    if self.clicked:
                        self.clicked = False
                        return
                    self.clicked = True
                    global squareClicked
                    squareClicked = squareHovered
        if self.clicked:
            drawTransparentRect(screen, sqHighlightColor, (squareClicked[1]) * SQ_SIZE + self.stW, (squareClicked[0]) * SQ_SIZE + self.stH, SQ_SIZE, SQ_SIZE, 64)
            if self.board[squareClicked[0]][squareClicked[1]][-1] == 'M':
                dangerousSquares = self.getPlayerValidMoves(self.players[(self.activePlayerIndex + 1) % 2], False, True)
                

            for i in range(len(card.moves)):
                try:
                    sqToMove = [(squareClicked[1] + card.moves[i][0]), (squareClicked[0] + card.moves[i][1])]
                    sqToMoveCoords = [(squareClicked[1] + card.moves[i][0]) * SQ_SIZE + self.stW, (squareClicked[0] + card.moves[i][1]) * SQ_SIZE + self.stH]
                    if self.clickArea.collidepoint((sqToMoveCoords[0], sqToMoveCoords[1])) \
                    and self.board[squareClicked[0]][squareClicked[1]][:2] != self.board[sqToMove[1]][sqToMove[0]][:2] \
                    and (self.board[squareClicked[0]][squareClicked[1]][2] != 'M' or not sqToMove in dangerousSquares):
                        drawTransparentRect(screen, sqHighlightColor, sqToMoveCoords[0], sqToMoveCoords[1], SQ_SIZE, SQ_SIZE, 64)
                        if pygame.Rect(sqToMoveCoords[0], sqToMoveCoords[1], SQ_SIZE, SQ_SIZE).collidepoint(mousePosition) and pygame.mouse.get_pressed()[0]:
                            self.movePawn(squareClicked, [squareClicked[0] + card.moves[i][1], squareClicked[1] + card.moves[i][0]], card.name)
                            self.clicked = False
                            return True
                    elif sqToMove in dangerousSquares and self.board[squareClicked[0]][squareClicked[1]][:2] != self.board[sqToMove[1]][sqToMove[0]][:2]:
                        drawTransparentRect(screen, 'black', sqToMoveCoords[0], sqToMoveCoords[1], SQ_SIZE, SQ_SIZE, 64)
                except:
                    ...


    def movePawn(self, startSquare, endSquare, cardName: str) -> None:

        pawnName = self.board[startSquare[0]][startSquare[1]]
        self.board[startSquare[0]][startSquare[1]] = '--'
        contentOfSquareBefore = self.board[endSquare[0]][endSquare[1]]
        try:
            if self.board[endSquare[0]][endSquare[1]][1] != pawnName[1] and self.board[endSquare[0]][endSquare[1]][2] == 'M':
                self.endMessage = self.gameFinished(pawnName[:2])
        except:
            ...
        #game finished if master lands on opposing throne:
        if pawnName == 'p1M' and [endSquare[0], endSquare[1]] == self.p2Throne:
            self.endMessage = self.gameFinished(pawnName[:2])
        if pawnName == 'p2M' and [endSquare[0], endSquare[1]] == self.p1Throne:
            self.endMessage = self.gameFinished(pawnName[:2])
        self.board[endSquare[0]][endSquare[1]] = pawnName

        self.activePlayerIndex = (self.activePlayerIndex + 1) % 2
        
        self.moveLog.append({cardName+"_"+pawnName+"_"+contentOfSquareBefore: [startSquare, endSquare]})


    def undoMove(self) -> None:
        #Task: Add to movelog captures in order to respawn pawns when move that captures is undone

        lastMove = self.moveLog[-1][next(iter(self.moveLog[-1]))]
        nameOfCardToGive = list(self.moveLog[-2].keys())[0].split('_')[0]
        pawnToRespawn = list(self.moveLog[-1].keys())[0].split('_')[2]
        

        [startSquare, endSquare] = lastMove
        
        self.movePawn(endSquare, startSquare, "")
        self.moveLog = self.moveLog[:-2]
        self.playerTurn()
        if pawnToRespawn != '--':
            self.board[endSquare[0]][endSquare[1]] = pawnToRespawn
        """for card in self.players[self.activePlayerIndex].cards:
            print(card.name)"""
        cardIndex = self.players[self.activePlayerIndex].getCardIndexByName(nameOfCardToGive)

        #print("CardIndex: ", cardIndex)
        self.players[self.activePlayerIndex].cards[cardIndex].swapHeightWithWidth()
        for i in range(3):
            self.players[self.activePlayerIndex].cards[cardIndex].swapCoordinates()
            self.players[self.activePlayerIndex].cards[cardIndex].mirrorCoord(0)

        self.cardOut.swapHeightWithWidth()
        for i in range(3):
            self.cardOut.swapCoordinates()
            self.cardOut.mirrorCoord(0)

        cardToReturn = self.players[self.activePlayerIndex].cards[cardIndex]
        self.players[self.activePlayerIndex].cards[cardIndex] = self.cardOut
        self.cardOut = cardToReturn
        self.players[self.activePlayerIndex].cards[cardIndex].stPoint = self.cardOut.stPoint
        #change active status
        self.players[self.activePlayerIndex].cards[cardIndex].active = True
        self.cardOut.active = False

        if self.firstPlayer.userView:
            self.cardOut.stPoint = [(self.stW-CARD_HEIGHT+4*smallOffset)/2, self.stW + SQ_SIZE/2 + smallOffset]      
        else:
            self.cardOut.stPoint = [(self.stW-CARD_HEIGHT+4*smallOffset)/2 + BOARD_WIDTH + 2*bigOffset + CARD_HEIGHT,
                                    self.stW + BOARD_HEIGHT - SQ_SIZE/2 - 2*smallOffset- CARD_LENGTH + smallOffset]


    def getCardByName(self, cardName: str) -> Card:
        for card in self.cardsInGame:
            if card.name == cardName:
                return card


    def playerTurn(self, pTypes = [0, 0]) -> None:

        self.players[self.activePlayerIndex].plays = True
        isAI = pTypes[self.activePlayerIndex]
        if not isAI:
            for card in self.players[self.activePlayerIndex].cards:
                card.active = True
        self.players[(self.activePlayerIndex + 1) % 2].plays = False
        #self.activePlayerIndex
        for card in self.players[(self.activePlayerIndex + 1) % 2].cards:
            card.active = False


    def gameFinished(self, message: str) -> str:
        endMessage = f'Game over: {message} wins!'
        return endMessage
    

    def drawEndScreen(self, message: str) -> None:
        drawTransparentRect(screen, 'grey12', 0, 0, screen.get_width(), screen.get_height(), alpha=200)
        font = pygame.font.Font('freesansbold.ttf', 64)
        text = font.render(message, True, 'firebrick2')
        textRect = text.get_rect()
        textRect.center = (screen.get_width() // 2, screen.get_height() // 2)
        screen.blit(text, textRect)

        font = pygame.font.Font('freesansbold.ttf', 20)
        text = font.render('New game? (move mouse or press any key to continue)', True, 'firebrick2')
        textRect = text.get_rect()
        textRect.center = (screen.get_width() // 2, screen.get_height() // 2 + 45)
        screen.blit(text, textRect)


    def getPlayerPawnCoords(self, playerName) -> list[list: int]:
        coords = []
        for line in range(len(self.board)):
            for row in range(len(self.board[line])):
                if self.board[line][row][:2] == playerName:
                    coords.append([row, line])
        return coords

    def getPlayerMaster(self, playerName) -> list[int]:
        for line in range(len(self.board)):
            for row in range(len(self.board[line])):
                if self.board[line][row] == playerName + 'M':
                    return [row, line]

    def getPlayerValidMoves(self, player: Player, lookForChecks=True, returnList = False):
        validMoves = {}
        
        if lookForChecks:
            opponentsMoves = self.getPlayerValidMoves([x for x in self.players if not player == x][0], False)
            squaresInDanger = keepEndSquares(opponentsMoves)
        #squaresInDanger = self.getPlayerValidMoves([x for x in self.players if not player == x][0], False, True) #call for other player

        for card in player.cards:
            validMoves[card.name] = {}
            pawnsInGame = self.getPlayerPawnCoords(player.name)
            for pawnCoords in pawnsInGame:
                validMoves[card.name][str(pawnCoords)] = []
                for move in card.moves:
                    if (move[0] + pawnCoords[0]) >= 0 and (move[0] + pawnCoords[0]) < n and \
                        (move[1] + pawnCoords[1]) >= 0 and (move[1] + pawnCoords[1]) < n: #if move is whithin game board boundaries
                        if (not self.board[move[1] + pawnCoords[1]][move[0] + pawnCoords[0]][:2] == player.name) or not lookForChecks: #if there is no pawn of same color already there
                            if self.board[pawnCoords[1]][pawnCoords[0]][-1] == 'M' and lookForChecks:
                                # print("Move: ", move)
                                # print("Master's move: ", pawnCoords, ", ", [pawnCoords[0]+move[0],pawnCoords[1]+move[1]])
                                try:
                                    if self.board[move[1] + pawnCoords[1]][move[0] + pawnCoords[0]][2] == 'M':
                                        #print('will hit master')
                                        validMoves[card.name][str(pawnCoords)].append([move[0] + pawnCoords[0], move[1] + pawnCoords[1]])
                                    if [move[0] + pawnCoords[0], move[1] + pawnCoords[1]] in squaresInDanger:
                                        #print("conflict: ", move[0] + pawnCoords[0], move[1] + pawnCoords[1])
                                        pass
                                    else:
                                        #print("adding: ", pawnCoords, ", ", [pawnCoords[0]+move[0],pawnCoords[1]+move[1]])
                                        validMoves[card.name][str(pawnCoords)].append([move[0] + pawnCoords[0], move[1] + pawnCoords[1]])
                                
                                except:
                                    if [move[0] + pawnCoords[0], move[1] + pawnCoords[1]] in squaresInDanger:
                                        #print("conflict: ", move[0] + pawnCoords[0], move[1] + pawnCoords[1])
                                        pass
                                    else:
                                        #print("adding: ", pawnCoords, ", ", [pawnCoords[0]+move[0],pawnCoords[1]+move[1]])
                                        validMoves[card.name][str(pawnCoords)].append([move[0] + pawnCoords[0], move[1] + pawnCoords[1]])
                                
                            else:
                                validMoves[card.name][str(pawnCoords)].append([move[0] + pawnCoords[0], move[1] + pawnCoords[1]])
                validMoves[card.name][str(pawnCoords)] = list(k for k,_ in itertools.groupby(validMoves[card.name][str(pawnCoords)]))

        if not returnList: #Get rid of empty list instances like:  '[1,2]':[]
                for key, value in validMoves.items():
                    validMoves[key] = {k: v for k, v in value.items() if v}
                
                validMoves = {k: v for k, v in validMoves.items() if v}

        if lookForChecks:
            myThrone = getattr(self, f"{player.name}Throne")[::-1]
            # print("me: ", player.name)
            # print("myThrone: ", myThrone)
            myMaster = self.getPlayerMaster(player.name)
            # print("myMaster: ", myMaster)

            # print("valid moves: ", validMoves)
            # print("opponsntsMoves",opponentsMoves)
            # print("Squares in danger: ", squaresInDanger)


            #Make squares in danger per pawn. Now it's just end coordinates 

            myThroneInCheck: bool = myThrone in squaresInDanger
            myMasterInCheck: bool = myMaster in squaresInDanger

            # print("myThroneInCheck: ", myThroneInCheck)
            # print("myMasterInCheck: ", myMasterInCheck)

            myMovesEndsquares = keepEndSquares(validMoves)

            if myThroneInCheck:
                # print("1 keepMoves(opponentsMoves)", keepMoves(opponentsMoves))
                dangerousPawn = [ast.literal_eval(k) for k, v in keepMoves(opponentsMoves).items() if myThrone in v][0]
                #Throws error FIX
                # print(dangerousPawn)
                if self.board[dangerousPawn[1]][dangerousPawn[0]][-1] == 'M':
                    print("Throne done!")
                    return [] #If opposing master threatens throne its game over

            if myMasterInCheck:
                # print("2 keepMoves(opponentsMoves)", keepMoves(opponentsMoves))

                dangerousPawns = [ast.literal_eval(k) for k, v in keepMoves(opponentsMoves).items() if myMaster in v]
                # print("can move master: ", not str(myMaster) in keepMoves(validMoves))
                # print("can capture threatening piece: ",  not dangerousPawns[0] in myMovesEndsquares)
                # print("more than one piece threatening: ", len(dangerousPawns) > 1 )
                if not str(myMaster) in keepMoves(validMoves) and ((len(dangerousPawns) > 1 or not dangerousPawns[0] in myMovesEndsquares)):
                    print("Mate")
                    return []
                else: #Master in check but its salvageable
                    #Keep only moves that save
                    #print("Check")
                    # keep only master's moves and those that capture threatening piece
                    validMoves = keepSavingMoves(validMoves, myMaster, dangerousPawns)
                    #print(validMoves)
                #print()

        if returnList:
            validMoves = list(validMoves.values())
            tempList = []
            for i in range(len(validMoves)):
                for subList in list(validMoves[i].values()):
                    #print(subList)
                    tempList += subList
            tempList = [list(tupl) for tupl in {tuple(item) for item in tempList }] #drop duplicates
            validMoves = tempList

        return validMoves #format list: [[newCoordX, newCoordY], ...] keeps only end positions
                        #format dict: {card1Name: {'[pawnCoordX, pawnCoordY]': [newCoordX, newCoordY]], ... ,], '[otherPawnCoordX, otherPawnCoordY]'}}


# Helper functions
def keepMoves(movesByCards: dict) -> dict:
    combined = defaultdict(list)

    for card_moves in movesByCards.values():
        for pawn, moves in card_moves.items():
            combined[pawn].extend(moves)

    for pawn in combined:
        combined[pawn] = [list(x) for x in set(tuple(m) for m in combined[pawn])]

    combined = dict(combined)
    return combined


def keepEndSquares(movesByCards: dict) -> list:
    endSquares = []
    movesOnly = keepMoves(movesByCards)
    for startPosition in movesOnly:
        endSquares.extend(movesOnly[startPosition])
    return endSquares


def keepSavingMoves(validMovesPrior, masterCoords=None, threateningPawnsCoords: list=[]) -> dict:

    start_str = str(masterCoords) if masterCoords else None
    end_list = threateningPawnsCoords if len(threateningPawnsCoords) == 1 else []

    filteredMoves = {}

    for piece, moves in validMovesPrior.items():
        new_moves = {}
        for start, ends in moves.items():
            if start == start_str:
                new_moves[start] = ends
            elif any(end in ends for end in end_list):
                filtered_ends = [end for end in ends if end == threateningPawnsCoords[0]]
                if start in new_moves:
                    new_moves[start] += filtered_ends
                else:
                    new_moves[start] = filtered_ends
                
        if new_moves:
            filteredMoves[piece] = new_moves

    return filteredMoves