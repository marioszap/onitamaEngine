import ast
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
        print(movesScored)

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

class node(): #nodes represnt game states that occur after players' moves
    def __init__(self, gameState: GameState, evaluation=0, children = []):
        self.gameState = gameState
        self.children = children
        self.eval = evaluation
        self.minmaxIndex = toAbsOne(self.gameState.activePlayerIndex)

        validMoves = self.gameSate.getPlayerValidMoves(self.gameSate.firstPlayer)
        
        for cardName in validMoves:
            print("\n",cardName, ': ', validMoves[cardName])
            for move in validMoves[cardName]:
                endCoords = validMoves[cardName][move]
                print("start coord: ", ast.literal_eval(move), end=', ')
                for endCoord in endCoords:
                    print("end coord: ",endCoord)


    def evaluate(self, move: list[list: int]): #move: [[startingX, startingY], [endingX, endingY]]
        squareToGo = self.gs.board[move[1][1]][move[1][0]]
        
        if len(squareToGo) == 3: #isPlayer's pawn
            score = 10
        return score


    def spawnChildren(self):
        state = self.gameState
        state.getPlayerValidMoves(state.players[self.activePlayerIdx])


    def checkIfGameOver(self, move: list[list: int]):

        currSquare = self.gs.board[move[0][1]][move[0][0]]
        squareToGo = self.gs.board[move[1][1]][move[1][0]]

        currPlayerName = currSquare[:2]

        if currPlayerName == 'p1':
            targetThrone = self.gs.p2Throne
        elif currPlayerName == 'p2':
            targetThrone = self.gs.p1Throne
        
        if len(squareToGo) == 3: #isPlayer's pawn
            if squareToGo[2] == 'M': #isMaster
                return True
        if currSquare[2] =='M':
            if squareToGo[1] == targetThrone[0] and squareToGo[0] == targetThrone[1]:
                return True
        return False


    def minmax(self, depth: int, alpha: int, beta: int): 
        
        if depth == 0: #chldren List == empty => ending position 
            return self.evaluate() + (self.checkIfGameOver() * 1000) #if game over +1000
        if self.checkIfGameOver():
            return self.evaluate() + 1000
        
        maxEval = -math.inf * self.minmaxIndex
        for child in self.children:

            evaluation = child.minmax(depth-1, alpha, beta, -1 * self.minmaxIndex)
            maxEval = self.minmaxIndex * max(self.minmaxIndex * maxEval, self.minmaxIndex * evaluation)
        
            #alpha beta pruning
            if self.minmaxIndex == 1: #if maximizing player
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            elif self.minmaxIndex == -1:
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
        
        print(maxEval)
        return maxEval

if __name__ == '__main__':

    ch1 = node(1, 1)
    ch2 = node(1, -2)
    p = node(-1, 0, [ch1, ch2])
    p.minmax(1, -math.inf, math.inf, -1)
