import ast
import json
from engine import *
import numpy as np
import math
import random

global transpositionTable
transpositionTable = {}
global zobristHashesFound
zobristHashesFound = 0

def toAbsOne(index) -> int:
    return int(np.sign([index-0.5])) #if pIdx = 1 => sign(0.5) = 1, if pIdx = 0 => sign(-0.5) = -1

class ZobristHashing():
    def __init__(self, gameState: GameState):
        self.squareIds = {}
        self.cardHashes = {}
        self.cardOwnerShip = {"p1": {}, "p2": {}}
        self.playerHashes = {"p1": random.getrandbits(64), "p2": random.getrandbits(64)}
        self.sideToMove = {"p1": random.getrandbits(64), "p2": random.getrandbits(64)}

        for row in range(len(gameState.board)):
            for col in range(len(gameState.board[row])):
                self.squareIds[str([row, col])] = {'p1M': random.getrandbits(64), 'p1S': random.getrandbits(64), 'p2M': random.getrandbits(64), 'p2S': random.getrandbits(64)}
        
        for card in gameState.cardsInGame:
            self.cardHashes[card.name] = random.getrandbits(64)

        for player in gameState.players:
            for card in gameState.cardsInGame:
                self.cardOwnerShip[player.name][card.name] = self.cardHashes[card.name] ^ self.playerHashes[player.name]

    def generateKey(self, gameState: GameState):
        key = 0
        board = gameState.board
        activePlayerName = gameState.players[gameState.activePlayerIndex].name

        for player in gameState.players:
            for card in player.cards:
                key ^= self.cardOwnerShip[player.name][card.name]
        
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] != '--':
                    key ^= self.squareIds[str([row, col])][board[row][col]]

        key ^= self.sideToMove[activePlayerName]
        return key


    def generateKeyFromPrevious(self, gameState:GameState, previousKey, move, cardUsedName, cardGottenName):
        #move = [[row, col], [row, col]]
        board = gameState.board
        pawnName = board[move[1][0]][move[1][1]]
        key = previousKey ^ self.squareIds[str([move[0][0], move[0][1]])][pawnName]
        key ^= self.squareIds[str([move[1][0], move[1][1]])][pawnName]
        key ^= self.cardOwnerShip[gameState.players[(gameState.activePlayerIndex + 1) % 2].name][cardUsedName]
        key ^= self.cardOwnerShip[gameState.players[(gameState.activePlayerIndex + 1) % 2].name][cardGottenName]
        return key


def reorderMoves(gameState: GameState, validMoves: dict) -> dict:
    movesWithScores = {}
    cardCounter = {}
    #pprint(validMoves)
    for cardName in validMoves:
        cardCounter[cardName] = 1
    
    board = gameState.board
    player = gameState.players[gameState.activePlayerIndex]
    opponentsThrone = gameState.p2Throne if player.name == 'p1' else gameState.p1Throne

    for cardName in validMoves:
        for startCoord in validMoves[cardName]:
            for endCoords in validMoves[cardName][startCoord]:
                startCoords = ast.literal_eval(startCoord)
                gameState.cardOut = player.sendCard(gameState.getCardByName(cardName), gameState.cardOut)
                gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                newValidMoves = gameState.getPlayerValidMoves(player)
                gameState.undoMove()

                score = 0
                for newCardName in newValidMoves:
                    score += len(newValidMoves[newCardName])
                    for newStartCoords in newValidMoves[newCardName]:
                        for newEndCoords in newValidMoves[newCardName][newStartCoords]:
                            if len(board[newEndCoords[1]][newEndCoords[0]]) == 3:
                                score += 2
                                if board[newEndCoords[1]][newEndCoords[0]][2] == 'M':
                                    score += 10
                            if newEndCoords[::-1] == opponentsThrone:
                                score += 1000
                movesWithScores[cardName + '_' + str(cardCounter[cardName])] = {'move': {startCoord: endCoords}, 'score': score}
                cardCounter[cardName] += 1

    sortedMovesWithScores = dict(sorted(movesWithScores.items(), key=lambda item: item[1]['score'], reverse=True))
    #print(sortedMovesWithScores)
    strippedSortedMoves = { k: {move_key: [move_val]} for k, v in sortedMovesWithScores.items() for move_key, move_val in v['move'].items() }
    #print(strippedSortedMoves)
    return strippedSortedMoves


def evaluate(gameState: GameState): #move: [[startingX, startingY], [endingX, endingY]]
    board = gameState.board
    score = 0
    for row in range(len(board)):
        for column in range(len(board[row])):
            if board[row][column] == "p1M" and gameState.p2Throne == [row, column]:
                return -1000
            elif board[row][column] == "p2M" and gameState.p1Throne == [row, column]:
                return +1000
            elif board[row][column][1] == '1':
                score -= 10
            elif board[row][column][1] == '2':
                score += 10
            
    return score


"""def evaluateFullFledged(gameState: GameState):
    score = evaluate(gameState)

    score -= sum(distanceFromCenter(p) for p in position.my_pieces) * 5
    score += 10 * (5 - manhattan_distance(position.my_master_pos, position.their_temple))

    # Mobility
    my_moves = len(generate_legal_moves(position, maximizing=True))
    their_moves = len(generate_legal_moves(position, maximizing=False))
    score += 5 * (my_moves - their_moves)"""

def findNextMove(gameState: GameState, MAX_DEPTH: int, zobrist: ZobristHashing, algorithm: str = 'NegaMax', ordering: bool = True, alpha_beta: bool = True):
    global nextMove
    if not zobrist is None: #Using transposition tables
        
        if algorithm == "NegaMax":
            turnSign = toAbsOne(gameState.activePlayerIndex)
            negaMaxZobrist(gameState, MAX_DEPTH, turnSign, -math.inf * alpha_beta, math.inf * alpha_beta, zobrist, MAX_DEPTH, ordering)
    
    else:
        if algorithm == "MinMax":
            print('In minmax')
            minmaxMoveOrdering(gameState, MAX_DEPTH, -math.inf * alpha_beta, math.inf * alpha_beta, MAX_DEPTH)
        elif algorithm == "NegaMax":
            print('in Negamax')
            turnSign = toAbsOne(gameState.activePlayerIndex)
            negaMax(gameState, MAX_DEPTH, turnSign, -math.inf * alpha_beta, math.inf * alpha_beta, MAX_DEPTH)
    return nextMove


def minmax(gameState: GameState, depth: int, alpha: int, beta: int, MAX_DEPTH: int = None, _state={'last': None}) -> int:
    global nextMove
    
    if depth == 1:
        return evaluate(gameState)

    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']
    
    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if gameState.activePlayerIndex == 1: #max

        if validMoves == 'Mate':
            return -1000
        
        maxScore = -1000
        for cardName in validMoves:
            card = gameState.getCardByName(cardName)
            for move in validMoves[cardName]:
                startCoords = ast.literal_eval(move)
                for endCoords in validMoves[cardName][move]:

                    gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                    gameState.cardOut = player.sendCard(card, gameState.cardOut)

                    score = minmax(gameState, depth-1, alpha, beta)
                    gameState.undoMove()
                    if score > maxScore:
                        maxScore = score
                        if depth == MAX_DEPTH:
                            nextMove = {cardName: [startCoords, endCoords]}
                    if not math.isnan(alpha):        
                        alpha = max(alpha, score)
                        if beta <= alpha:
                            return maxScore
        return maxScore

    else:

        if validMoves == "Mate":
            return 1000
        
        minScore = 1000
        for cardName in validMoves:
            card = gameState.getCardByName(cardName)
            for move in validMoves[cardName]:
                startCoords = ast.literal_eval(move)
                for endCoords in validMoves[cardName][move]:
                    gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                    gameState.cardOut = player.sendCard(card, gameState.cardOut)
                    score = minmax(gameState, depth-1, alpha, beta)
                    gameState.undoMove()
                    if score < minScore:
                        minScore = score
                        if depth == MAX_DEPTH:
                            nextMove = {cardName: [startCoords, endCoords]}
                    if not math.isnan(alpha):        
                        beta = min(beta, score)
                        if beta <= alpha:
                            return minScore

        return minScore


def minmaxMoveOrdering(gameState: GameState, depth: int, alpha: int, beta: int, MAX_DEPTH: int = None, _state={'last': None}) -> int:
    global nextMove

    if depth == 1:
        return evaluate(gameState)

    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']

    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if validMoves == 'Mate':
        return -1000 if gameState.activePlayerIndex == 0 else 1000

    moveList = []

    # Build list of all possible moves with a quick evaluation for ordering
    for cardName in validMoves:
        card = gameState.getCardByName(cardName)
        for move in validMoves[cardName]:
            startCoords = ast.literal_eval(move)
            for endCoords in validMoves[cardName][move]:
                # Apply the move temporarily
                gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                gameState.cardOut = player.sendCard(card, gameState.cardOut)

                # Evaluate the resulting state (lightweight!)
                moveScore = evaluate(gameState)

                # Save move details + score
                moveList.append((moveScore, cardName, startCoords, endCoords))

                # Undo to prepare for next
                gameState.undoMove()

    # Reorder move list to favor pruning
    reverse = (gameState.activePlayerIndex == 1)  # Max player: sort high to low
    moveList.sort(reverse=reverse, key=lambda x: x[0])

    # Apply reordered moves
    if gameState.activePlayerIndex == 1:  # Maximizing
        maxScore = -1000
        for moveScore, cardName, startCoords, endCoords in moveList:
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
            gameState.cardOut = player.sendCard(card, gameState.cardOut)

            score = minmax(gameState, depth - 1, alpha, beta, MAX_DEPTH, _state)
            gameState.undoMove()

            if score > maxScore:
                maxScore = score
                if depth == MAX_DEPTH:
                    nextMove = {cardName: [startCoords, endCoords]}
            alpha = max(alpha, score)
            if beta <= alpha:
                break  # beta cut-off
        return maxScore

    else:  # Minimizing
        minScore = 1000
        for moveScore, cardName, startCoords, endCoords in moveList:
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
            gameState.cardOut = player.sendCard(card, gameState.cardOut)

            score = minmax(gameState, depth - 1, alpha, beta, MAX_DEPTH, _state)
            gameState.undoMove()

            if score < minScore:
                minScore = score
                if depth == MAX_DEPTH:
                    nextMove = {cardName: [startCoords, endCoords]}
            beta = min(beta, score)
            if beta <= alpha:
                break  # alpha cut-off
        return minScore



def negaMax(gameState: GameState, depth: int, turnSign: int, alpha: int, beta: int, MAX_DEPTH: int = None, _state={'last': None}) -> int:
    if depth == 0:
        return turnSign * evaluate(gameState)
    
    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']
    
    global nextMove

    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if validMoves == 'Mate':
        return -1000

    maxScore = -1000

    for cardName in validMoves:
        card = gameState.getCardByName(cardName.split("_")[0])
        
        for move in validMoves[cardName]:
            startCoords = ast.literal_eval(move)
            for endCoords in validMoves[cardName][move]:
                gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName.split("_")[0])
                gameState.cardOut = player.sendCard(card, gameState.cardOut)

                score = -negaMax(gameState, depth - 1, -turnSign, -beta, -alpha)
                gameState.undoMove()

                if score > maxScore:
                    maxScore = score
                    if depth == MAX_DEPTH:
                        nextMove = {cardName: [startCoords, endCoords]}
                if not math.isnan(alpha):        
                    if maxScore > alpha:
                        alpha = maxScore
                    if beta <= alpha:
                        return maxScore

    return maxScore


def negaMaxZobrist(gameState: GameState, depth: int, turnSign: int, alpha: int, beta: int, zobrist: ZobristHashing, MAX_DEPTH: int = None, moveOrdering = True,  _state={'last': None}) -> int:
    if depth == 0:
        return turnSign * evaluate(gameState)
    
    global transpositionTable
    global nextMove
    global zobristHashesFound

    currentHash = zobrist.generateKey(gameState)
    
    if currentHash in transpositionTable:
        entry = transpositionTable[currentHash]
        zobristHashesFound += 1
        if entry['depth'] >= depth:
            return entry['score']


    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']
    

    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)
    if validMoves == 'Mate':
        return -1000

    if moveOrdering and not isinstance(validMoves, str):
        validMoves = reorderMoves(gameState, validMoves)

    maxScore = -1000

    for cardName in validMoves:
        card = gameState.getCardByName(cardName.split("_")[0])
        
        for move in validMoves[cardName]:
            startCoords = ast.literal_eval(move)
            for endCoords in validMoves[cardName][move]:
                gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName.split("_")[0])
                cardGivenName = cardName.split("_")[0]
                cardGottenName = gameState.cardOut.name
                gameState.cardOut = player.sendCard(card, gameState.cardOut)

                score = -negaMaxZobrist(gameState, depth - 1, -turnSign, -beta, -alpha, zobrist)
                gameState.undoMove()

                if score >= maxScore:
                    maxScore = score
                    
                    if depth == MAX_DEPTH:
                        nextMove = {cardName.split("_")[0]: [startCoords, endCoords]}
                
                if not math.isnan(alpha):        
                    if maxScore > alpha:
                        alpha = maxScore
                    if beta <= alpha:
                        transpositionTable[currentHash] = {
                            'score': maxScore,
                            'depth': depth,
                        }
                        return maxScore
    
    transpositionTable[currentHash] = {
        'score': maxScore,
        'depth': depth,
    }

    return maxScore
