import random, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import math
import sys

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
        self.board[self.p1Throne[0]][self.p1Throne[1]] = "p1M"
        self.board[self.p2Throne[0]][self.p2Throne[1]] = "p2M"
        self.clicked = False
        self.clickArea = pygame.Rect(stW, stH, BOARD_HEIGHT, BOARD_HEIGHT)
        self.stW = stW
        self.stH = stH
        self.players = [None] * 2
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

        self.cardOut.swapCoordinates()
        self.cardOut.swapHeightWithWidth()


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


    def highlightSquares(self, screen, card, playerName: str) -> bool:
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
            for i in range(len(card.moves)):
                try:
                    sqToMove = [(squareClicked[1] + card.moves[i][0]), (squareClicked[0] + card.moves[i][1])]
                    sqToMoveCoords = [(squareClicked[1] + card.moves[i][0]) * SQ_SIZE + self.stW, (squareClicked[0] + card.moves[i][1]) * SQ_SIZE + self.stH]
                    if self.clickArea.collidepoint((sqToMoveCoords[0], sqToMoveCoords[1])) \
                    and self.board[squareClicked[0]][squareClicked[1]][:2] != self.board[sqToMove[1]][sqToMove[0]][:2]:
                        drawTransparentRect(screen, sqHighlightColor, sqToMoveCoords[0], sqToMoveCoords[1], SQ_SIZE, SQ_SIZE, 64)
                        if pygame.Rect(sqToMoveCoords[0], sqToMoveCoords[1], SQ_SIZE, SQ_SIZE).collidepoint(mousePosition) and pygame.mouse.get_pressed()[0]:
                            self.movePawn(squareClicked, [squareClicked[0] + card.moves[i][1], squareClicked[1] + card.moves[i][0]])
                            self.clicked = False
                            return True
                except:
                    ...


    def movePawn(self, startSquare, endSquare) -> None:
        pawnName = self.board[startSquare[0]][startSquare[1]]
        self.board[startSquare[0]][startSquare[1]] = '--'
        try:
            if self.board[endSquare[0]][endSquare[1]][1] != pawnName[1] and self.board[endSquare[0]][endSquare[1]][2] == 'M':
                self.endMessage = self.gameFinished(pawnName[:2])
        except:
            ...

        if pawnName == 'p1M' and [endSquare[0], endSquare[1]] == self.p2Throne:
            self.endMessage = self.gameFinished(pawnName[:2])
        if pawnName == 'p2M' and [endSquare[0], endSquare[1]] == self.p1Throne:
            self.endMessage = self.gameFinished(pawnName[:2])
        self.board[endSquare[0]][endSquare[1]] = pawnName


    def playerTurn(self, playerToPlayIndex: int) -> None:
        self.players[playerToPlayIndex].plays = True
        for card in self.players[playerToPlayIndex].cards:
            card.active = True
        self.players[(playerToPlayIndex + 1) % 2].plays = False
        for card in self.players[(playerToPlayIndex + 1) % 2].cards:
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


    def getPlayerPawnCoords(self, playerName):
        coords = []
        for line in range(len(self.board)):
            for row in range(len(self.board[line])):
                if self.board[line][row][:2] == playerName:
                    coords.append([line, row])
        return coords
    
    def getPlayerValidMoves(self, playerName):
        for player in self.players:
            if player.name == playerName:
                for card in player.cards:
                    print(card.name)
                    print(card.moves)
        