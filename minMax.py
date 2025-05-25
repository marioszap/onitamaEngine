import ast
import json
from engine import *
import numpy as np
import math

class minMax():
    def __init__(self, state: GameState) -> None:
        self.gs = state

    def scoreEachMove(self, moves: dict, playerIdx: int, currPlayerName: str):#, depth: int):
        gameOver = False
        """if depth == 0 or gameOver:
            return evaluation"""
        if currPlayerName == 'p1':
            targetThrone = self.gs.p2Throne
        else:
            targetThrone = self.gs.p1Throne
        
        movesScored = moves
        playerIdx = int(np.sign([playerIdx-0.5])) #if pIdx = 1 => sign(0.5) = 1, if pIdx = 0 => sign(-0.5) = -1
        bestEval = playerIdx * math.inf
        evaluation = bestEval
        for cardName in moves:
            for i in range(len(moves[cardName])):
                score = 0
                currCoord: list[int] = moves[cardName][i][0]
                newCoord: list[int] = moves[cardName][i][1]
                squareToGo = self.gs.board[newCoord[1]][newCoord[0]]
                currSquare = self.gs.board[currCoord[1]][currCoord[0]]
                if len(squareToGo) == 3: #isPlayer
                    if squareToGo[0:2] != currPlayerName: #Different color
                        if squareToGo[2] == 'M': #isMaster
                            score += 10000
                            gameOver = True
                            break
                        else:                   #isStudent
                            score += 10
                if currSquare[2] =='M':
                    if newCoord[0] == targetThrone[1] and newCoord[1] == targetThrone[0]:
                        score += 10000
                        gameOver = True
                        break
                    elif math.sqrt((newCoord[1] - targetThrone[0])**2 + (newCoord[0] - targetThrone[1])**2) < \
                        math.sqrt((currCoord[1] - targetThrone[0])**2 + (currCoord[0] - targetThrone[1])**2): #is closer to enemy throne than currSquare
                        score += 1
                movesScored[cardName][i] = {'score': score, 'move': moves[cardName][i]}
        #print(movesScored)

    def minMaxPlayNextMove(self, activePlayer: Player, predictMovesAhead: int):
        score: int = 0
        validMoves = self.gs.getPlayerValidMoves(activePlayer.name)
        self.scoreEachMove(validMoves, self.gs.activePlayerIndex, 'p1')


    """def minimax(self, position, depth, maximizingPlayer):
        if depth == 0 or gameOver:
            return evaluation

        if maximizingPlayer:
            maxEval = -math.inf
            for nextPosition in nextPositions:
                evaluation = minimax(nextPosition, depth-1, False)
                maxEval = max(maxEval, evaluation)
            return maxEval
        else:
            minEval = math.inf
            for nextPosition in nextPositions:
                evaluation = minimax(nextPosition, depth-1, True)
                minEval = min(minEval, evaluation)
            return minEval"""

#minmax = minMax()
#minmax.scoreEachMove({}, 0, GameState)


def toAbsOne(index) -> int:
    return int(np.sign([index-0.5])) #if pIdx = 1 => sign(0.5) = 1, if pIdx = 0 => sign(-0.5) = -1


def setupMinMaxTree(game: GameState):
    
    ...

def cardRarity(cardsInGame: list[Card]) -> None:
    movesInGame = []
    allCards = open('cardsMoves.json')
    allCards = json.load(allCards)
    for card in cardsInGame:
        print(f"for {card.name}", allCards[card.name])
        movesInGame += allCards[card.name]
    numAppearencesOfMoves = 0
    print("movesInGame: ", movesInGame)
    for card in cardsInGame:
        for move in allCards[card.name]:
            for moveInGame in movesInGame:
                if move == moveInGame:
                    numAppearencesOfMoves += 1 - (move[1]/10 * (move[1] > 0))
        card.rarity = len(allCards[card.name]) / numAppearencesOfMoves
        print(card.name, ": len: ", len(allCards[card.name]), '/', numAppearencesOfMoves, ' = ', card.rarity)
        numAppearencesOfMoves = 0



class node(): #nodes represnt game states that occur after players' moves
    def __init__(self, gameState: GameState, isRoot = False, isLeaf = False):
        self.gameState = gameState
        self.children: list[dict] = []
        self.eval = 0
        self.minmaxPlayerIndex = toAbsOne(self.gameState.activePlayerIndex)
        self.isRoot = isRoot #First node to be created should be root
        if isRoot:
            self.childrenScores = []

        self.validMoves = self.gameState.getPlayerValidMoves(self.gameState.players[self.gameState.activePlayerIndex])  
        
        """for cardName in self.validMoves:
            print("\n",cardName, ': ', self.validMoves[cardName])
            for move in self.validMoves[cardName]:
                endCoords = self.validMoves[cardName][move]
                print("start coord: ", ast.literal_eval(move), end=', ')
                for endCoord in endCoords:
                    print("end coord: ", endCoord)#"""
        if not isLeaf:
            for cardName in self.validMoves:
                for move in self.validMoves[cardName]:
                    endCoords = self.validMoves[cardName][move]
                    startCoord = ast.literal_eval(move)
                    for endCoord in endCoords:
                        self.children.append({cardName : [startCoord, endCoord]})



    def evaluate(self) -> float: #move: [[startingX, startingY], [endingX, endingY]]
        board = self.gameState.board
        score = 0
        for row in board:
            for square in row:
                if square[1] == '1':
                    score -= 10
                elif square[1] == '2':
                    score += 10
        return score


    def checkIfGameOver(self):
        #If I don't have a master or the opposing master is sitting on my throne
        if self.gameState.endMessage:
            return True
        return False


    def determineAndReturnBestMove(self) -> dict:
        if self.isRoot:
            if self.minmaxPlayerIndex == 1:
                min_index = self.childrenScores.index(max(self.childrenScores))
                childToMove = self.children[min_index]
            else:
                max_index = self.childrenScores.index(min(self.childrenScores))
                childToMove = self.children[max_index]
        return childToMove



    def minmax(self, depth: int, alpha: int, beta: int): 
        print()

        print("Depth: ", depth)
        if depth == 0: #chldren List == empty => tree leaf 
            evaluation =  self.evaluate() + (self.checkIfGameOver() * (-1000)) #if game over -1000
            print("--MoveLog: ", self.gameState.moveLog)
            self.gameState.undoMove()
            #print("Execution should be in here!")
            return evaluation
        if self.checkIfGameOver():
            evaluation =  self.evaluate() - 1000
            print("--MoveLog: ", self.gameState.moveLog)
            self.gameState.undoMove()
            return evaluation
        #print("No depth == 0 or gameOver")
        maxEval = -math.inf * self.minmaxPlayerIndex
        #print("Children: ")
        #print(self.children)
        for child in self.children:
            #1. Make move game.movePawn()_____
            #2. give card  player.sendCard()  |
            #3. recieve cardout __|           |
            #4. activePlayerIndex change______|

            #Methods to handle making move and create next node#########################################
            cardName = list(child.keys())[0]                                                           #
            startCoords, endCoords = child[cardName]            
            player = self.gameState.players[self.gameState.activePlayerIndex]
        
            #print("Child: ", child)
            #print("cards in player hand: ")
            #for card in player.cards:
            #    print("\t", card.name)
            #print("cardName: ", cardName)
            #print("card out before sending card: ", self.gameState.cardOut.name)
            self.gameState.cardOut = player.sendCard(player.cards[player.getCardIndexByName(cardName)], self.gameState.cardOut) #
            #print("card out after sending card: ", self.gameState.cardOut.name)
            self.gameState.movePawn(startCoords, endCoords, cardName)
            if depth == 1:                                  #
                childNode = node(gameState=self.gameState, isLeaf=True)                                                 #
                
            childNode = node(gameState=self.gameState)                                                 #
            
            #Are not part of the algorithm #############################################################


            evaluation = childNode.minmax(depth-1, alpha, beta)
            print("depth: ", depth)
            maxEval = self.minmaxPlayerIndex * max(self.minmaxPlayerIndex * maxEval, self.minmaxPlayerIndex * evaluation)
            if self.isRoot:
                self.childrenScores.append(maxEval)
                return
            #alpha beta pruning
            if self.minmaxPlayerIndex == 1: #if maximizing player
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            elif self.minmaxPlayerIndex == -1:
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
        
        #print(maxEval)
        print("--MoveLog: ", self.gameState.moveLog)
        self.gameState.undoMove()
        return maxEval

"""if __name__ == '__main__':

    ch1 = node(1, 1)
    ch2 = node(1, -2)
    p = node(-1, 0, [ch1, ch2])
    p.minmax(1, -math.inf, math.inf)"""
