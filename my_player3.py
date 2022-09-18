#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 03:52:30 2022

@author: yohan
"""

from read import readInput
from write import writeOutput
import numpy as np
import os
class Board:
    def __init__(self):
        self.board = None
        self.previousBoard = None
        self.me = None
        self.oppPlayer = None
        self.gameMovesCount = None
        self.komi = 2.5
        self.depth = 3
        self.checkedLiberty = []
        
    def read_input(self):
        readArr = readInput(5, path = 'input.txt')
        self.me = readArr[0]
        self.oppPlayer = 1 if self.me == 2 else 2
        self.board = np.asarray(readArr[2])
        self.previousBoard = np.asarray(readArr[1])
        
    def write_output(self, coor):
        writeOutput(coor)
        
    def readGameMoves(self, path = 'gameMoveNumber.txt' ):
        if not np.any(self.previousBoard):
            if self.me == 1:
                self.gameMovesCount = 0
            else:
                self.gameMovesCount = 1
        elif os.path.isfile(path):
            f = open(path, 'r')
            self.gameMovesCount = int(f.read()) +1
            f.close()
            
    def writeGameMoves(self, path = 'gameMoveNumber.txt'):
        f = open(path, 'w+')
        f.write(str(self.gameMovesCount))
        f.close()
    def deleteGameMoves(self, path = 'gameMoveNumber.txt'):
        os.remove(path)
    
    def valid_move(self, i,j, oppPlayer, board1):
        if board1[i][j] != 0:
            return False
        if self.libertyCount(oppPlayer, i, j, board1) > 0:
            return True
        else:
            #print('g')
            coors = self.valid_coor(i,j)
            min_lib = 4
            for coor in coors:
                self.checkedLiberty = []
                if board1[coor[0],coor[1]] == oppPlayer:
                    min_lib = min(min_lib, self.libertyCount(1 if oppPlayer == 2 else 2, coor[0], coor[1], board1))
            return True if min_lib == 1 else False
    
    def valid_coor(self, m, n):
        validCoor = []
        validCoor.append((m+1,n)) if m+1 <= 4 else True
        validCoor.append((m-1,n)) if m-1 >= 0 else True
        validCoor.append((m,n+1)) if n+1 <= 4 else True
        validCoor.append((m,n-1)) if n-1 >= 0 else True
        return validCoor
    
    def libertyCount(self, oppPlayer, m, n, board1):
        self.checkedLiberty.append((m,n))
        count = 0
        validCoor = self.valid_coor(m, n)
        for coor in validCoor:
            if coor not in self.checkedLiberty:
                if board1[coor[0],coor[1]] != oppPlayer:
                    if board1[coor[0], coor[1]] != 0:
                        count += self.libertyCount(oppPlayer, coor[0], coor[1], board1)
                    else:
                        count += 1
                        self.checkedLiberty.append((coor[0],coor[1]))
            #print(str(coor) + " " + str(count))
        return count
    # def libertyCount(self, color, m, n, arr):
    #     self.checkedLiberty.append((m,n))
    #     count = 0
    #     validCoor = self.valid_coor(m, n)
    #     for coor in validCoor:
    #         if coor not in self.checkedLiberty:
    #             if arr[coor[0],coor[1]] != color:
    #                 if arr[coor[0], coor[1]] != 0:
    #                     count += self.libertyCount(color, coor[0], coor[1], arr)
    #                 else:
    #                     count += 1
    #                     self.checkedLiberty.append((coor[0],coor[1]))
    #         #print(str(coor) + " " + str(count))
    #     return count
    def libertyCountEntireBoard(self, board1):
        queue = []
        visited = []
        liberty = np.zeros((5,5))
        liberty.fill(-1)
        libertyMe = 0
        libertyOpp = 0
        for i in range(5):
            for j in range(5):
                if liberty[i][j] == -1 and board1[i][j] != 0:
                    visited = []
                    queue.append((i,j))
                    count = 0
                    countedEmptySpace = []
                    visited.append((i,j))
                    while queue:
                        coor = queue.pop()
                        #print(coor)
                        neighbour = self.valid_coor(coor[0],coor[1])
                        for k in neighbour:
                            if k not in visited:
                                if board1[k[0],k[1]] == 0:
                                    if (k[0],k[1]) not in countedEmptySpace:
                                        count+=1
                                        countedEmptySpace.append((k[0],k[1]))
                                elif board1[k[0],k[1]] == board1[i][j]:
                                    queue.append((k[0],k[1]))
                                    visited.append((k[0],k[1]))
                    
                    for p in visited:
                        liberty[p[0],p[1]] = count
                        if board1[p[0],p[1]] == self.me:
                            libertyMe+=count
                        elif board1[p[0],p[1]] == self.oppPlayer:
                            libertyOpp += count
        return liberty, libertyMe, libertyOpp
    
    def countPieces(self, board1):
        countMine = 0
        countOpp = 0
        countEmpty = 0
        for i in range(5):
            for j in range(5):
                if board1[i][j] == self.me:
                    countMine+=1
                elif board1[i][j] == self.oppPlayer:
                    countOpp += 1 
                else:
                    countEmpty += 1
        return countMine, countOpp, countEmpty
             
        
    def koCheck(self, old_arr, new_arr):
        rem_ele = [(i,j) for i in range(len(old_arr)) for j in range(len(new_arr)) if new_arr[i][j] - old_arr[i][j] < 0]
        att_ele = [(i,j) for i in range(len(old_arr)) for j in range(len(new_arr)) if new_arr[i][j] - old_arr[i][j] > 0]
        return rem_ele, att_ele
    
    def deletePieces(self, liberty, board1):
        deletedPieces = []
        for i in range(5):
            for j in range(5):
                if liberty[i][j] == 0:
                    deletedPieces.append((i,j,board1[i][j]))
                    board1[i][j] = 0
        return deletedPieces
        
        
    def restorePieces(self, liberty, deletedPieces, board1):
        for delPieces in deletedPieces:
            board1[delPieces[0],delPieces[1]] = delPieces[2]
    
    def endGameStatus(self, passCount, board1):
        if self.gameMovesCount == 24:
            score, oppPlayerScore, empty = self.countPieces(board1)
            if passCount == 2 and empty > 5:
                return 'early'
            if self.me == 1:
                if score > oppPlayerScore + self.komi:
                    return 'win'
                elif score < oppPlayerScore + self.komi:
                    return 'lose'
                else:
                    return 'draw'
            elif self.me == 2:
                if score + self.komi > oppPlayerScore:
                    return 'win'
                elif score + self.komi < oppPlayerScore:
                    return 'lose'
                else:
                    return 'draw'
    
class alphaBeta:
    def move(self, board):
        rem_ele, att_ele = board.koCheck(board.previousBoard, board.board)
        board1 = np.copy(board.board)
        m, coor0, coor1, board2 = self.maxState(np.NINF, np.Inf, board, (rem_ele), att_ele, None, None, 0, False, board1)
        coor = (coor0,coor1)
        #print(board2==board1)
        return coor
    
    def minState(self, alpha, beta, board, rem_ele_ind, att_ele_ind, p, q, passCount, flag, board1):
        board.depth -= 1
        min_v = np.Inf
        

        x = None
        y = None
    
        if flag:
            result = board.endGameStatus(passCount, board1)
            if result == 'win':
                board.depth += 1
                return 100, 0, 0, board1
            elif result == 'lose':
                board.depth += 1
                return -100, 0, 0, board1
            elif result == 'draw':
                board.depth += 1
                return 0, 0, 0, board1
            elif result == 'early':
                board.depth += 1
                return -100, 0, 0, board1
        
        if board.depth == 0:
            board.depth += 1
            return self.heuristic(board, p, q, rem_ele_ind, board1), 0, 0, board1
    
        for i in range(0, 5):
            for j in range(0, 5):
                if i < 6:
                    board.checkedLiberty = []
                    if board.valid_move(i,j,board.me, board1):
                        if (i, j) in rem_ele_ind:
                            if att_ele_ind in board.valid_coor(i,j):
                                if board.libertycount(board.oppPlayer, att_ele_ind[0], att_ele_ind[1], board1) == 1:
                                    break
                        board1[i][j] = board.oppPlayer
                        liberty,k,l = board.libertyCountEntireBoard(board1)
                        deletedPieces = board.deletePieces(liberty, board1)
                        if len(deletedPieces) > 0:
                            att_ele_ind_new = (i,j)
                        else:
                            att_ele_ind_new = None
                        m, max_i, max_j, board1 = self.maxState(alpha, beta, board, deletedPieces, att_ele_ind_new, i, j, passCount, True, board1)
                        if m < min_v:
                            min_v = m
                            x = i
                            y = j
                        board1[i][j] = 0
                        board.restorePieces(liberty, deletedPieces, board1)
                        if min_v <= alpha:
                            board.depth += 1
                            return min_v, x, y, board1
                        if min_v < beta:
                            beta = min_v
        passCount += 1
        m, max_i, max_j, board1 = self.maxState(alpha, beta, board, [], None, 'PASS', 'PASS', passCount, True, board1)
        if board.depth != 1:
            m += self.heuristic(board, i, j, deletedPieces,board1)
        if m < min_v:
            min_v = m
            x = 'PASS'
            y = 'PASS'
        if min_v <= alpha:
            board.depth += 1
            return min_v, x, y, board1
        if min_v < beta:
            beta = min_v
        passCount -= 1
                    
        board.depth += 1
        return min_v, x, y, board1
        
    def maxState(self, alpha, beta, board, rem_ele_ind, att_ele_ind, p, q, passCount, flag, board1):
        board.depth -= 1
        max_v = np.NINF

        x = None
        y = None
    
        if flag:
            result = board.endGameStatus(passCount, board1)
            if result == 'win':
                board.depth += 1
                return 100, 0, 0, board1
            elif result == 'lose':
                board.depth += 1
                return -100, 0, 0, board1
            elif result == 'draw':
                board.depth += 1
                return 80, 0, 0, board1
            elif result == 'early':
                board.depth += 1
                return -100, 0, 0, board1
    
        if board.depth == 0:
            board.depth += 1
            return self.heuristic(board, p, q, rem_ele_ind,board1), 0, 0, board1
    
        for i in range(0, 5):
            for j in range(0, 5):
                if i < 6:
                    board.checkedLiberty = []
                    if board.valid_move(i,j,board.oppPlayer, board1):
                        if (i, j) in rem_ele_ind:
                            if att_ele_ind in board.valid_coor(i,j):
                                if board.libertycount(board.me, att_ele_ind[0], att_ele_ind[1], board1) == 1:
                                    break
                        board1[i][j] = board.me
                        liberty,k,l = board.libertyCountEntireBoard(board1)
                        deletedPieces = board.deletePieces(liberty, board1)
                        if len(deletedPieces) > 0:
                            att_ele_ind_new = (i,j)
                        else:
                            att_ele_ind_new = None
                        
                        m, min_i, min_j, board1 = self.minState(alpha, beta, board, deletedPieces, att_ele_ind_new, i, j, passCount, True, board1)
                        if board.depth != 1:
                            m += self.heuristic(board, i, j, deletedPieces,board1)
                        if m > max_v:
                            max_v = m
                            x = i
                            y = j
                        board1[i][j] = 0
                        board.restorePieces(liberty, deletedPieces, board1)
                        if max_v >= beta:
                            board.depth += 1
                            return max_v, x, y, board1
                        if max_v > alpha:
                            alpha = max_v
        passCount += 1
        m, min_i, min_j, board1 = self.minState(alpha, beta, board, [], None, 'PASS', 'PASS', passCount, True, board1)
        if m > max_v:
            max_v = m
            x = 'PASS'
            y = 'PASS'
        if max_v >= beta:
            board.depth += 1
            return max_v, x, y, board1
        if max_v > alpha:
            alpha = max_v
        passCount -= 1
                        
        board.depth += 1
        return max_v, x, y, board1
        
    def heuristic(self, board, i, j, deletedPieces, board1):
        countMine, countOpp, empty = board.countPieces(board1)
        liberty, libertyMe, libertyOpp = board.libertyCountEntireBoard(board1)
        if i == 0 or i == 4 or j ==0 or j == 4:
            edge = 0.3
        else:
            edge = 0
        if board.me == 1:
            #x = ((countMine - (countOpp))*(board.gameMovesCount)/25 + (libertyMe - libertyOpp) - ((board.gameMovesCount)/25)*edge) + len(deletedPieces)*10
            #print(x)
            #BEST
            x = (countMine - 2.5 - countOpp) *(board.gameMovesCount)/25 + (libertyMe - libertyOpp) *(board.gameMovesCount)/25 - ((24-board.gameMovesCount)/25)*edge + len(deletedPieces)*10
            #x = (countMine - 2.5 - countOpp) + (libertyMe - libertyOpp) - ((24-board.gameMovesCount)/25)*edge 

            
        else:
            ##x = (countMine + 2.5 - countOpp) *(board.gameMovesCount)/25 + (libertyMe - libertyOpp) *(board.gameMovesCount)/25 - ((24-board.gameMovesCount)/25)*edge 
            ##x = ((countMine - (countOpp))*(24-board.gameMovesCount)/25 + (libertyMe - libertyOpp) - ((24-board.gameMovesCount)/25)*edge) + len(deletedPieces)*10
            #BEST
            #Bestx = (countMine + 2.5 - countOpp) + (libertyMe - libertyOpp) - ((24-board.gameMovesCount)/25)*edge + len(deletedPieces)*10
            x = (countMine + 2.5 - countOpp) + (libertyMe - libertyOpp) - ((24-board.gameMovesCount)/25)*edge + len(deletedPieces)*10
            #print(x)
        return x
    
    
def main():
    board = Board()
    board.read_input()
    board.readGameMoves()
    ab = alphaBeta()
    board.gameMovesCount += 1
    coor = ab.move(board)
    board.write_output(coor)
    if board.gameMovesCount == 24:
        board.deleteGameMoves()
    else:
        board.writeGameMoves()
    
    
    
if __name__ == '__main__':
    main()