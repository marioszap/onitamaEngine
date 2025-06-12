import ast
import json
from engine import *
import numpy as np
import math
from itertools import islice
import pprint


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
    def __init__(self, gameState: GameState, isRoot = False, isLeaf = False, isRootsChild = False):
        self.gameState = gameState
        self.children: list[dict] = []
        self.eval = 0
        self.minmaxPlayerIndex = toAbsOne(self.gameState.activePlayerIndex)
        self.isRoot = isRoot #First node to be created should be root
        

        self.validMoves = self.gameState.getPlayerValidMoves(self.gameState.players[self.gameState.activePlayerIndex])  
        if self.isRoot:
            self.move = []
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
        else:
            self.children = None


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


    def randomMove(self) -> list[list: int]:
        validMoves = self.gameState.getPlayerValidMoves(self.gameState.players[self.gameState.activePlayerIndex])
        print(validMoves)
        randomCardName = random.choice(list(validMoves))
        randomMove = random.choice(list(validMoves[randomCardName]))
        print(validMoves[randomCardName])
        print(type(ast.literal_eval(randomMove)), random.choice(validMoves[randomCardName][randomMove]))
        return [ast.literal_eval(randomMove), random.choice(validMoves[randomCardName][randomMove])]


    def determineAndReturnBestMove(self) -> dict:
        if self.isRoot:
            if self.minmaxPlayerIndex == 1:
                best_score = max(move['score'] for move in self.children)
            else:
                best_score = min(move['score'] for move in self.children)
            print("Children: ", self.children)
            print("Best score: ", best_score, "player minmaxIdx: ", self.minmaxPlayerIndex)
            best_moves = [move for move in self.children if move['score'] == best_score]
            return random.choice(best_moves)
        



    def minmax(self, depth: int, alpha: int, beta: int): 
        #print()

        
        if depth == 0:  #tree leaf
            evaluation =  self.evaluate() + ((self.children == []) * -1000 * self.minmaxPlayerIndex) #if game over -1000
            self.gameState.undoMove()
            #print("Evaluation: ", evaluation)
            return evaluation
        elif self.children == []: #chldren List == empty => no available moves 
            evaluation =  self.evaluate() - 1000 * self.minmaxPlayerIndex
            #print("Evaluation: ", evaluation)
            
            self.gameState.undoMove()
            return evaluation

        maxEval = -math.inf * self.minmaxPlayerIndex
        
        for i in range(len(self.children)):
            #1. Make move game.movePawn()_____
            #2. give card  player.sendCard()  |
            #3. recieve cardout __|           |
            #4. activePlayerIndex change______|

            #print("Child: ", self.children[i])
            #Methods to handle making move and create next node#########################################
            cardName = list(self.children[i].keys())[0]                                                           #
            startCoords, endCoords = self.children[i][cardName]            
            player = self.gameState.players[self.gameState.activePlayerIndex]
        
            self.gameState.cardOut = player.sendCard(player.cards[player.getCardIndexByName(cardName)], self.gameState.cardOut) #

            self.gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)

            if depth == 1:                                  #
                childNode = node(gameState=self.gameState, isLeaf=True)
            elif self.isRoot:
                childNode = node(gameState=self.gameState, isRootsChild=True)
            else:                                            #
                childNode = node(gameState=self.gameState)
            
            #Are not part of the algorithm #############################################################


            evaluation = childNode.minmax(depth-1, alpha, beta)
            #print("depth: ", depth)
            maxEval = self.minmaxPlayerIndex * max(self.minmaxPlayerIndex * maxEval, self.minmaxPlayerIndex * evaluation)
            if maxEval != 0:
                print("child: ", self.children[i])
                if self.minmaxPlayerIndex > 0:
                    print("Depth: ", depth)
                    print("Maximizing Player: ", self.minmaxPlayerIndex, end=" ")
                else:
                    print("Depth: ", depth)
                    print('Minimizing Player: ', self.minmaxPlayerIndex, end=" ")
                print("Between: ", self.minmaxPlayerIndex * self.minmaxPlayerIndex * maxEval, " and ", self.minmaxPlayerIndex *self.minmaxPlayerIndex * evaluation)
                print("Chose: ", maxEval)
                print()
            self.children[i]["score"] = maxEval
            
                
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

        self.gameState.undoMove()
        return maxEval

def evaluate(gameState:GameState): #move: [[startingX, startingY], [endingX, endingY]]
    board = gameState.board
    score = 0
    for row in board:
        for square in row:
            if square[1] == '1':
                score -= 10
            elif square[1] == '2':
                score += 10
    return score


def startMinMax(gameState: GameState, MAX_DEPTH):
    global nextMove
    minmax2(gameState, MAX_DEPTH, MAX_DEPTH)
    return nextMove


def minmax2(gameState: GameState, depth: int, MAX_DEPTH):
    if depth == 0:
        print("Eval: ", evaluate(gameState))
        return evaluate(gameState)
    global nextMove
    
    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if gameState.activePlayerIndex == 1: #max
        maxScore = -1000
        for cardName in validMoves:
            card = gameState.getCardByName(cardName)
            for move in validMoves[cardName]:
                startCoords = ast.literal_eval(move)
                for endCoords in validMoves[cardName][move]:
                    gameState.cardOut = player.sendCard(card, gameState.cardOut)

                    gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                    score = minmax2(gameState, depth-1, MAX_DEPTH)
                    print("depth: ", depth, "score: ", score, "maxScore: ", maxScore)
                    if score >= maxScore:
                        maxScore = score
                        print("In here")
                        if depth == MAX_DEPTH:
                            print("Next added", {cardName: [startCoords, endCoords]})
                            nextMove = {cardName: [startCoords, endCoords]}
                    gameState.undoMove()
        return maxScore

    else:
        minScore = 1000
        for cardName in validMoves:
            card = gameState.getCardByName(cardName)
            for move in validMoves[cardName]:
                startCoords = ast.literal_eval(move)
                for endCoords in validMoves[cardName][move]:
                    gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                    gameState.cardOut = player.sendCard(card, gameState.cardOut)
                    score = minmax2(gameState, depth-1, MAX_DEPTH)
                    print("depth: ", depth, "score: ", score, "maxScore: ", minScore)

                    if score <= minScore:
                        minScore = score
                        print("In here")

                        if depth == MAX_DEPTH:
                            print("Next added", {cardName: [startCoords, endCoords]})

                            nextMove = {cardName: [startCoords, endCoords]}
                    gameState.undoMove()
        return minScore

"""if __name__ == '__main__':

    ch1 = node(1, 1)
    ch2 = node(1, -2)
    p = node(-1, 0, [ch1, ch2])
    p.minmax(1, -math.inf, math.inf)"""
