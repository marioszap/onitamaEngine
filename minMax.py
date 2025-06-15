import ast
import json
from engine import *
import numpy as np
import math
from itertools import islice
import pprint
import random


def toAbsOne(index) -> int:
    return int(np.sign([index-0.5])) #if pIdx = 1 => sign(0.5) = 1, if pIdx = 0 => sign(-0.5) = -1


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

        

        # self.validMoves = self.gameState.getPlayerValidMoves(self.gameState.players[self.gameState.activePlayerIndex])  
        
        """for cardName in self.validMoves:
            print("\n",cardName, ': ', self.validMoves[cardName])
            for move in self.validMoves[cardName]:
                endCoords = self.validMoves[cardName][move]
                print("start coord: ", ast.literal_eval(move), end=', ')
                for endCoord in endCoords:
                    print("end coord: ", endCoord)#"""


class ZobristHashing():
    def __init__(self, gameState: GameState):
        self.squareIds = {}
        self.cardHashes = {}
        self.cardOwnerShip = {"p1": {}, "p2": {}}
        self.playerHashes = {"p1": random.getrandbits(64), "p2": random.getrandbits(64)}
        self.sideToMove = {"p1": random.getrandbits(64), "p2": random.getrandbits(64)}

        for row in range(len(gameState.board)):
            for col in range(len(gameState.board[row])):
                self.squareIds[str([row, col])] = {'M': random.getrandbits(64), 'S': random.getrandbits(64)}
        
        for card in gameState.cardsInGame:
            self.cardHashes[card.name] = random.getrandbits(64)

        for player in gameState.players:
            for card in player.cards:
                self.cardOwnerShip[player.name][card.name] = self.cardHashes[card.name] ^ self.playerHashes[player.name]

        self.TranspositionTable = {}

    def generateKey(self, gameState: GameState):
        key = 0
        board = gameState.board
        activePlayerName = gameState.players[gameState.activePlayerIndex].name

        for player in gameState.players:
            for card in player.cards:
                key ^= self.cardHashes[player.name][card.name]
        
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] != '--':
                    key ^= self.squareIds[str([row, col])][board[row][col][2]]

        key ^= self.sideToMove[activePlayerName]
        return key




def evaluate(gameState:GameState): #move: [[startingX, startingY], [endingX, endingY]]
    board = gameState.board
    score = 0
    for row in range(len(board)):
        for column in range(len(board[row])):
            if board[row][column] == "p1M" and gameState.p2Throne == [row, column]:
                return -1000
            elif board[row][column] == "p2M" and gameState.p1Throne == [row, column]:
                return 1000
            elif board[row][column][1] == '1':
                score -= 10
            elif board[row][column][1] == '2':
                score += 10
    return score


def startMinMax(gameState: GameState, MAX_DEPTH: int):
    global nextMove
    minmax(gameState, MAX_DEPTH, MAX_DEPTH, -math.inf, math.inf)
    return nextMove


def minmax(gameState: GameState, depth: int, MAX_DEPTH: int, alpha: float, beta: float):
    if depth == 0:
        return evaluate(gameState)
    global nextMove
    
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
                    gameState.cardOut = player.sendCard(card, gameState.cardOut)

                    gameState.movePawn(startCoords[::-1], endCoords[::-1], cardName)
                    score = minmax(gameState, depth-1, MAX_DEPTH, alpha, beta)
                    gameState.undoMove()
                    if score >= maxScore:
                        maxScore = score
                        if depth == MAX_DEPTH:
                            print("Next added", {cardName: [startCoords, endCoords]})
                            nextMove = {cardName: [startCoords, endCoords]}
                            
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
                    score = minmax(gameState, depth-1, MAX_DEPTH, alpha, beta)
                    gameState.undoMove()
                    if score <= minScore:
                        minScore = score

                        if depth == MAX_DEPTH:
                            print("Next added", {cardName: [startCoords, endCoords]})

                            nextMove = {cardName: [startCoords, endCoords]}

                    beta = min(beta, score)
                    if beta <= alpha:
                        return minScore

        return minScore


"""if __name__ == '__main__':

    ch1 = node(1, 1)
    ch2 = node(1, -2)
    p = node(-1, 0, [ch1, ch2])
    p.minmax(1, -math.inf, math.inf)"""
