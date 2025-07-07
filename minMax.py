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


    def generateKeyFromPrevious(self, gameState:GameState, previousKey, move, cardUsedName, cardGottenName, pawnCaptured):
        #move = [[row, col], [row, col]]
        board = gameState.board
        activePlayerName = gameState.players[gameState.activePlayerIndex].name
        inactivePlayerName = gameState.players[(gameState.activePlayerIndex + 1) % 2].name
        pawnName = board[move[1][1]][move[1][0]]
        
        key = previousKey ^ self.squareIds[str([move[0][0], move[0][1]])][pawnName]
        key ^= self.squareIds[str([move[1][0], move[1][1]])][pawnName]
        if not pawnCaptured is None:
            key ^= self.squareIds[str([move[1][0], move[1][1]])][pawnCaptured]
        key ^= self.cardOwnerShip[inactivePlayerName][cardUsedName]
        key ^= self.cardOwnerShip[inactivePlayerName][cardGottenName]
        key ^= self.sideToMove[inactivePlayerName]
        key ^= self.sideToMove[activePlayerName]
        return key



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
            elif board[row][column] == "p1M":
                score -= 1000
            elif board[row][column] == "p2M":
                score += 1000
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
            print('Here')
            negaMaxIncrementalZobrist(gameState, MAX_DEPTH, turnSign, -math.inf * alpha_beta, math.inf * alpha_beta, zobrist, MAX_DEPTH=MAX_DEPTH)
        elif algorithm == "MinMax":
            minmaxZobrist(gameState, MAX_DEPTH, -math.inf * alpha_beta, math.inf * alpha_beta, zobrist, MAX_DEPTH)
    else:
        if ordering:
            if algorithm == "MinMax":
                minmaxMoveOrderingLMR(gameState, MAX_DEPTH, -math.inf * alpha_beta, math.inf * alpha_beta, MAX_DEPTH)
            elif algorithm == "NegaMax":
                turnSign = toAbsOne(gameState.activePlayerIndex)
                negaMaxMoveOrderingLMR(gameState, MAX_DEPTH, turnSign, -math.inf * alpha_beta, math.inf * alpha_beta, MAX_DEPTH)
        else:
            if algorithm == "MinMax":
                minmax(gameState, MAX_DEPTH, -math.inf * alpha_beta, math.inf * alpha_beta, MAX_DEPTH)
            elif algorithm == "NegaMax":
                turnSign = toAbsOne(gameState.activePlayerIndex)
                negaMax(gameState, MAX_DEPTH, turnSign, -math.inf * alpha_beta, math.inf * alpha_beta, MAX_DEPTH)

    return nextMove


def minmax(gameState: GameState, depth: int, alpha: int, beta: int, MAX_DEPTH: int = None, _state={'last': None}) -> int:
    global nextMove
    
    if depth == 0:
        return evaluate(gameState)

    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']
    
    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if gameState.activePlayerIndex == 1: #max

        if validMoves == 'Mate':
            return -1000
        
        maxScore = float('-inf')
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
        
        minScore = float('inf')
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

    if depth == 0:
        return evaluate(gameState)

    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']

    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if validMoves == 'Mate':
        return 1000 if gameState.activePlayerIndex == 0 else -1000

    moveList = []

    # Build list of all possible moves with a quick evaluation for ordering
    if depth > 0:
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
        maxScore = float('-inf')
        for moveScore, cardName, startCoords, endCoords in moveList:
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
            gameState.cardOut = player.sendCard(card, gameState.cardOut)

            score = minmaxMoveOrdering(gameState, depth - 1, alpha, beta, MAX_DEPTH, _state)
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
        minScore = float('inf')
        for moveScore, cardName, startCoords, endCoords in moveList:
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
            gameState.cardOut = player.sendCard(card, gameState.cardOut)

            score = minmaxMoveOrdering(gameState, depth - 1, alpha, beta, MAX_DEPTH, _state)
            gameState.undoMove()

            if score < minScore:
                minScore = score
                if depth == MAX_DEPTH:
                    nextMove = {cardName: [startCoords, endCoords]}
            beta = min(beta, score)
            if beta <= alpha:
                break  # alpha cut-off
        return minScore

def minmaxMoveOrderingLMR(gameState: GameState, depth: int, alpha: int, beta: int, MAX_DEPTH: int = None, _state={'last': None}) -> int:
    global nextMove

    if depth <= 0:
        return evaluate(gameState)

    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']

    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if validMoves == 'Mate':
        return 1000 if gameState.activePlayerIndex == 0 else -1000

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
        for index, (moveScore, cardName, startCoords, endCoords) in enumerate(moveList):
            R = 0
            if index > len(moveList) / 2:
                R = 1
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
            gameState.cardOut = player.sendCard(card, gameState.cardOut)

            score = minmaxMoveOrderingLMR(gameState, depth - 1 - R, alpha, beta, MAX_DEPTH, _state)
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
        for index, (moveScore, cardName, startCoords, endCoords) in enumerate(moveList):
            R = 0
            if index > len(moveList) / 2:
                R = 1
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
            gameState.cardOut = player.sendCard(card, gameState.cardOut)

            score = minmaxMoveOrderingLMR(gameState, depth - 1 - R, alpha, beta, MAX_DEPTH, _state)
            gameState.undoMove()

            if score < minScore:
                minScore = score
                if depth == MAX_DEPTH:
                    nextMove = {cardName: [startCoords, endCoords]}
            beta = min(beta, score)
            if beta <= alpha:
                break  # alpha cut-off
        return minScore


def minmaxZobrist(gameState: GameState, depth: int, alpha: int, beta: int, zobrist: ZobristHashing, MAX_DEPTH: int = None, previousMoveData = None, _state={'last': None}) -> int:
    global nextMove
    
    if depth == 0:
        return evaluate(gameState)

    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']
    
    global transpositionTable
    global nextMove
    global zobristHashesFound

    currentHash = zobrist.generateKey(gameState)

    if previousMoveData is None:
        currentHash = zobrist.generateKey(gameState)
    else:
        currentHash = zobrist.generateKeyFromPrevious(gameState, previousMoveData[0], previousMoveData[1], previousMoveData[3], previousMoveData[2], previousMoveData[4])

    if currentHash in transpositionTable:
        entry = transpositionTable[currentHash]
        zobristHashesFound += 1
        if entry['depth'] >= depth:
            return entry['score']


    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if gameState.activePlayerIndex == 1: #max

        if validMoves == 'Mate':
            return -1000
        
        maxScore = float('-inf')
        for cardName in validMoves:
            card = gameState.getCardByName(cardName)
            for move in validMoves[cardName]:
                startCoords = ast.literal_eval(move)
                for endCoords in validMoves[cardName][move]:
                    pawnCaptured = gameState.board[endCoords[1]][endCoords[0]] if gameState.board[endCoords[1]][endCoords[0]] != '--' else None
                    cardGivenName = cardName.split("_")[0]
                    cardGottenName = gameState.cardOut.name
                    gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                    gameState.cardOut = player.sendCard(card, gameState.cardOut)

                    score = minmaxZobrist(gameState, depth-1, alpha, beta, zobrist, [currentHash, [startCoords, endCoords], cardGottenName, cardGivenName, pawnCaptured])
                    gameState.undoMove()
                    if score > maxScore:
                        maxScore = score
                        if depth == MAX_DEPTH:
                            nextMove = {cardName: [startCoords, endCoords]}
                    if not math.isnan(alpha):        
                        alpha = max(alpha, score)
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

    else:

        if validMoves == "Mate":
            return 1000
        
        minScore = float('inf')
        for cardName in validMoves:
            card = gameState.getCardByName(cardName)
            for move in validMoves[cardName]:
                startCoords = ast.literal_eval(move)
                for endCoords in validMoves[cardName][move]:
                    pawnCaptured = gameState.board[endCoords[1]][endCoords[0]] if gameState.board[endCoords[1]][endCoords[0]] != '--' else None
                    cardGivenName = cardName.split("_")[0]
                    cardGottenName = gameState.cardOut.name
                    gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                    gameState.cardOut = player.sendCard(card, gameState.cardOut)
                    score = minmaxZobrist(gameState, depth-1, alpha, beta, zobrist, [currentHash, [startCoords, endCoords], cardGottenName, cardGivenName, pawnCaptured])
                    gameState.undoMove()
                    if score < minScore:
                        minScore = score
                        if depth == MAX_DEPTH:
                            nextMove = {cardName: [startCoords, endCoords]}
                    if not math.isnan(alpha):        
                        beta = min(beta, score)
                        if beta <= alpha:
                            transpositionTable[currentHash] = {
                                'score': minScore,
                                'depth': depth,
                            }
                            return minScore

        transpositionTable[currentHash] = {
                'score': minScore,
                'depth': depth,
            }


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




def negaMaxMoveOrdering(gameState: GameState, depth: int, turnSign: int, alpha: int, beta: int, MAX_DEPTH: int = None, _state={'last': None}) -> int:
    if depth == 0:
        return turnSign * evaluate(gameState)
    
    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']
    
    global nextMove

    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if validMoves == 'Mate':
        return 1000 if gameState.activePlayerIndex == 0 else -1000


    moveList = []
    if depth > 0:
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
    

    maxScore = -1000

    for moveScore, cardName, startCoords, endCoords in moveList:
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
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


def negaMaxMoveOrderingLMR(gameState: GameState, depth: int, turnSign: int, alpha: int, beta: int, MAX_DEPTH: int = None, _state={'last': None}) -> int:
    if depth == 0:
        return turnSign * evaluate(gameState)
    
    if MAX_DEPTH is None:
        MAX_DEPTH = _state['last']
    
    global nextMove

    player = gameState.players[gameState.activePlayerIndex]
    validMoves = gameState.getPlayerValidMoves(player)

    if validMoves == 'Mate':
        return 1000 if gameState.activePlayerIndex == 0 else -1000


    moveList = []
    if depth > 0:
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
    

    maxScore = -1000

    for index, (moveScore, cardName, startCoords, endCoords) in enumerate(moveList):
            R = 0
            if index > len(moveList) / 2:
                R = 1
            card = gameState.getCardByName(cardName)
            gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
            gameState.cardOut = player.sendCard(card, gameState.cardOut)

            score = -negaMax(gameState, depth - 1 - R, -turnSign, -beta, -alpha)
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


def negaMaxZobrist(gameState: GameState, depth: int, turnSign: int, alpha: int, beta: int, zobrist: ZobristHashing, MAX_DEPTH: int = None,  _state={'last': None}) -> int:
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

                if score > maxScore:
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



def negaMaxIncrementalZobrist(gameState: GameState, depth: int, turnSign: int, alpha: int, beta: int, zobrist: ZobristHashing, previousMoveData = None, MAX_DEPTH: int = None,  _state={'last': None}) -> int:
    if depth == 0:
        return turnSign * evaluate(gameState)
    
    global transpositionTable
    global nextMove
    global zobristHashesFound

    if previousMoveData is None:
        currentHash = zobrist.generateKey(gameState)
    else:
        currentHash = zobrist.generateKeyFromPrevious(gameState, previousMoveData[0], previousMoveData[1], previousMoveData[3], previousMoveData[2], previousMoveData[4])

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


    maxScore = -1000

    for cardName in validMoves:
        card = gameState.getCardByName(cardName.split("_")[0])
        
        for move in validMoves[cardName]:
            startCoords = ast.literal_eval(move)
            for endCoords in validMoves[cardName][move]:
                pawnCaptured = gameState.board[endCoords[1]][endCoords[0]] if gameState.board[endCoords[1]][endCoords[0]] != '--' else None
                gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName.split("_")[0])
                cardGivenName = cardName.split("_")[0]
                cardGottenName = gameState.cardOut.name
                gameState.cardOut = player.sendCard(card, gameState.cardOut)

                score = -negaMaxIncrementalZobrist(gameState, depth - 1, -turnSign, -beta, -alpha, zobrist, [currentHash, [startCoords, endCoords], cardGottenName, cardGivenName, pawnCaptured])
                gameState.undoMove()

                if score > maxScore:
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
