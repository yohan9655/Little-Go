#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 15:50:29 2022

@author: yohan
"""
from read import readInput
from write import writeOutput
import numpy as np
import pickle
import os
import argparse
import json
import random

class Q_agent:
    def __init__(self, alpha = 0.7, gamma = 0.9, win = 1, draw = 0, lose = -1, train=False):
        self.alpha = alpha
        self.gamma = gamma
        self.win = win
        self.draw = draw
        self.lose = lose
        self.QVal = {}
        self.initial_value = 0
        self.states_used = []
        self.trainFlag = train
        self.color = None
        self.oppPlayer = None
        self.checkedLiberty = []
        
        
    def read_input(self):
        readArr = readInput(5, path = 'input.txt')
        self.color = readArr[0]
        self.oppPlayer = 1 if self.color == 2 else 2
        return np.asarray(readArr[1]), np.asarray(readArr[2])
    
    def write_output(self, coor):
        writeOutput(coor, path = 'output.txt')
        
        
    def read_QValues(self, path):
        if os.path.isfile(path):
            with open(path, 'rb') as handle:
                self.QVal = pickle.load(handle)
            handle.close()
        else:
            self.QVal = {}
    def read_statesUsed(self, path):
        if self.trainFlag == True:
            if os.path.isfile(path):
                with open(path, 'rb') as handle:
                    self.states_used = pickle.load(handle)
                handle.close()
                    
    def write_QValues(self, path, end):
        with open(path, 'wb') as handle:
            pickle.dump(self.QVal, handle, protocol=4)
        handle.close()

        with open(path[:-6]+'json', 'w') as handle:
            handle.write(json.dumps(str(self.QVal)))
        handle.close()
    def write_statesUsed(self, path):
        if self.trainFlag == True:
            #print('States -> ')
            #print(self.states_used)
            with open(path, 'wb') as handle:
                pickle.dump(self.states_used, handle, protocol=4)
            handle.close()
            
    def delete_StateUsed(self, path):
        os.remove(path)
        
    def get_next_move(self, q_value):
        q_value+=1

        
    # def learn_from_game(self, end):
    #     if end == 'win':
    #         reward = self.win
    #     elif end == 'lose':
    #         reward = self.lose
    #     else:
    #         reward = self.draw
    #     self.states_used.reverse()
    #     max_q_value = -1.0
    #     for hist in self.states_used:
    #         state, move_rel, move_abs  = hist
    #         q = self.QVal[state]
    #         if max_q_value < 0:
    #             q[move_rel[0]][move_rel[1]] = reward
    #         else:
    #             q[move_rel[0]][move_rel[1]] = q[move_rel[0]][move_rel[1]] * (1 - self.alpha) + self.alpha * self.gamma * max_q_value
    #         max_q_value = np.max(q)
    #     self.states_used = []
    def learn_from_game(self, end):
        try:
            if end == 'win':
                reward = self.win
            elif end == 'lose':
                reward = self.lose
            else:
                reward = self.draw
            self.states_used.reverse()
            max_q_value = -1.0
            for hist in self.states_used:
                state, move  = hist
                if state not in self.QVal:
                    rot1 = tuple(map(tuple, np.rot90(np.asarray(state), 1)))
                    if rot1 not in self.QVal:
                        rot2 = tuple(map(tuple,np.rot90(np.asarray(state), 2)))
                        if rot2 not in self.QVal:
                            rot3 = tuple(map(tuple,np.rot90(np.asarray(state), 3)))
                            if rot3 not in self.QVal:
                                flip0 = tuple(map(tuple, np.flip(np.asarray(state))))
                                if flip0 not in self.QVal:
                                    flip1 = tuple(map(tuple, np.flip(np.asarray(state),1)))
                                    self.QVal[flip1][0:-1] = np.flip(self.QVal[flip1][0:-1],1)
                                    self.QVal[state] = self.QVal[flip1]
                                    del self.QVal[flip1]
                                else:
                                    self.QVal[flip0][0:-1] = np.flip(self.QVal[flip0][0:-1])
                                    self.QVal[state] = self.QVal[flip0]
                                    del self.QVal[flip0]
                            else:
                                self.QVal[rot3][0:-1] = np.rot90(self.QVal[rot3][0:-1],1)
                                self.QVal[state] = self.QVal[rot3]
                                del self.QVal[rot3]
                        else:
                            self.QVal[rot2][0:-1] = np.rot90(self.QVal[rot2][0:-1],2)
                            self.QVal[state] = self.QVal[rot2]
                            del self.QVal[rot2]
                    else:
                        self.QVal[rot1][0:-1] = np.rot90(self.QVal[rot1][0:-1],3)
                        self.QVal[state] = self.QVal[rot1]
                        del self.QVal[rot1]
                q = self.QVal[state]
                if max_q_value < 0:
                    if move == 'PASS':
                        q[5][0] = reward
                    else:
                        q[move[0]][move[1]] = reward
                else:
                    if move == 'PASS':
                        q[5][0] = q[5][0] * (1 - self.alpha) + self.alpha * self.gamma * max_q_value
                    else:
                        q[move[0]][move[1]] = q[move[0]][move[1]] * (1 - self.alpha) + self.alpha * self.gamma * max_q_value
                max_q_value = np.max(q)
            self.states_used = []
        except Exception as e: 
            f = open('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/log.txt', 'a+')
            f.write(e)
            f.close()  
        
    
    def valid_move(self, i,j, arr):
        if arr[i][j] != 0:
            return False
        if self.libertyCount(self.oppPlayer, i, j,arr) > 0:
            return True
        else:
            print('g')
            coors = self.valid_coor(i,j)
            min_lib = 4
            for coor in coors:
                self.checkedLiberty = []
                if arr[coor[0],coor[1]] != self.color:
                    min_lib = min(min_lib, self.libertyCount(self.color, coor[0], coor[1], arr))
            return True if min_lib == 1 else False

    def valid_coor(self, m, n):
        validCoor = []
        validCoor.append((m+1,n)) if m+1 <= 4 else True
        validCoor.append((m-1,n)) if m-1 >= 0 else True
        validCoor.append((m,n+1)) if n+1 <= 4 else True
        validCoor.append((m,n-1)) if n-1 >= 0 else True
        return validCoor
    def libertyCount(self, color, m, n, arr):
        self.checkedLiberty.append((m,n))
        count = 0
        validCoor = self.valid_coor(m, n)
        for coor in validCoor:
            if coor not in self.checkedLiberty:
                if arr[coor[0],coor[1]] != color:
                    if arr[coor[0], coor[1]] != 0:
                        count += self.libertyCount(color, coor[0], coor[1], arr)
                    else:
                        count += 1
                        self.checkedLiberty.append((coor[0],coor[1]))
            #print(str(coor) + " " + str(count))
        return count
                
        
    def koCheck(self, old_arr, new_arr):
        rem_ele = [(i,j) for i in range(len(old_arr)) for j in range(len(new_arr)) if new_arr[i][j] - old_arr[i][j] < 0]
        att_ele = [(i,j) for i in range(len(old_arr)) for j in range(len(new_arr)) if new_arr[i][j] - old_arr[i][j] > 0]

        return rem_ele, att_ele
    
    # def get_Q_values(self, arr):
    #     if arr not in self.QVal:
    #         zero = np.zeros((4,3))
    #         zero.fill(0)
    #         zero[3,1:].fill(np.NINF)
    #         self.QVal[arr] = zero
    #         return zero
    #     else:
    #         return self.QVal[arr]
    def get_Q_values(self, arr):
        try:
            if arr not in self.QVal:
                rot1 = tuple(map(tuple, np.rot90(np.asarray(arr), 1)))
                if rot1 not in self.QVal:
                    rot2 = tuple(map(tuple,np.rot90(np.asarray(arr), 2)))
                    if rot2 not in self.QVal:
                        rot3 = tuple(map(tuple,np.rot90(np.asarray(arr), 3)))
                        if rot3 not in self.QVal:
                            flip0 = tuple(map(tuple, np.flip(np.asarray(arr))))
                            if flip0 not in self.QVal:
                                flip1 = tuple(map(tuple, np.flip(np.asarray(arr),1)))
                                if flip1 not in self.QVal:
                                    zero = np.zeros((6,5))
                                    #zero.fill(0.5)
                                    zero[5,1:].fill(np.NINF)
                                    self.QVal[arr] = zero
                                    return zero
                                else:
                                    self.QVal[flip1][0:-1] = np.flip(self.QVal[flip1][0:-1],1)
                                    self.QVal[arr] = self.QVal[flip1]
                                    del self.QVal[flip1]
                                    return self.QVal[arr]
                            else:
                                self.QVal[flip0][0:-1] = np.flip(self.QVal[flip0][0:-1])
                                self.QVal[arr] = self.QVal[flip0]
                                del self.QVal[flip0]
                                return self.QVal[arr]
                        else:
                            self.QVal[rot3][0:-1] = np.rot90(self.QVal[rot3][0:-1],1)
                            self.QVal[arr] = self.QVal[rot3]
                            del self.QVal[rot3]
                            return self.QVal[arr]
                    else:
                        self.QVal[rot2][0:-1] = np.rot90(self.QVal[rot2][0:-1],2)
                        self.QVal[arr] = self.QVal[rot2]
                        del self.QVal[rot2]
                        return self.QVal[arr]
                else:
                    self.QVal[rot1][0:-1] = np.rot90(self.QVal[rot1][0:-1],3)
                    self.QVal[arr] = self.QVal[rot1]
                    del self.QVal[rot1]
                    return self.QVal[arr]
            else:
                return self.QVal[arr]
        except Exception as e: 
            f = open('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/log.txt', 'a+')
            f.write(e)
            f.close()  
    def get_best_mov(self, arr, rem_ele_ind, att_ele_ind):
        try:
            maxVal = np.NINF
            maxVal_state = []
            maxVal_Index = None
            stateTuple = tuple(map(tuple,arr))
            q_values = self.get_Q_values(stateTuple)
            while(True):
                #print(q_values)
                max_value_index = np.unravel_index(np.argmax(q_values), q_values.shape)
                if q_values[max_value_index[0], max_value_index[1]] == np.NINF:
                    break
                self.checkedLiberty = []
                if max_value_index[0] > 4:
                    if maxVal < q_values[max_value_index[0], max_value_index[1]]:
                        maxVal = q_values[max_value_index[0], max_value_index[1]]
                        maxVal_Index = 'PASS'
                        maxVal_state = stateTuple
                    break
                elif self.valid_move(max_value_index[0], max_value_index[1], arr):
                    if (max_value_index[0], max_value_index[1]) == rem_ele_ind:
                        if self.libertyCount(self.color, att_ele_ind[0], att_ele_ind[1]) > 1:
                            if maxVal < q_values[max_value_index[0], max_value_index[1]] or (maxVal == q_values[max_value_index[0], max_value_index[1]] and maxVal_Index == 'PASS'):
                                maxVal = q_values[max_value_index[0], max_value_index[1]]
                                maxVal_Index = (max_value_index[0], max_value_index[1])
                                maxVal_state = stateTuple
                            break
                        else:
                            q_values[max_value_index[0]][max_value_index[1]] = np.NINF
                    else:
                        if maxVal < q_values[max_value_index[0], max_value_index[1]] or (maxVal == q_values[max_value_index[0], max_value_index[1]] and maxVal_Index == 'PASS'):
                            maxVal = q_values[max_value_index[0], max_value_index[1]]
                            maxVal_Index = (max_value_index[0], max_value_index[1])
                            maxVal_state = stateTuple
                        break
                else:
                    q_values[max_value_index[0]][max_value_index[1]] = np.NINF
            self.states_used.append((maxVal_state, maxVal_Index))
            print(maxVal_Index)
            if maxVal_Index != 'PASS':
                return maxVal_Index                   
            else:
                return 'PASS','PASS'
            # self.states_used.append((maxVal_state, maxVal_Index_relative, maxVal_Index_absolute))
            # print(maxVal_Index_absolute)
            # if maxVal_Index_absolute != 'PASS':
            #     return maxVal_Index_absolute
            # else:
            #     return 'PASS','PASS'
        except Exception as e: 
            f = open('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/log.txt', 'a+')
            f.write(e)
            f.close()  
        
        
    def move(self, new_arr, old_arr):
        rem_ele, att_ele = self.koCheck(old_arr, new_arr)
        i, j = self.get_best_mov(new_arr, rem_ele, att_ele)
        return i,j    
    
        

def main(args):
    Q = Q_agent(train=args.train)
    Q.read_QValues('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/myPlayerQValue.pickle')
    Q.read_statesUsed('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/state_used.pickle')
    if args.end == None and args.train == True:
        print('Here!')
        old_arr, new_arr = Q.read_input()
        i, j = Q.move(new_arr, old_arr)
        Q.write_output((i,j))
        Q.write_statesUsed('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/state_used.pickle')
        Q.write_QValues('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/myPlayerQValue.pickle', args.end)
    elif args.end != None and args.train == True:
        print('Here!!')
        Q.learn_from_game(args.end)
        Q.write_QValues('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/myPlayerQValue.pickle', args.end)
        Q.delete_StateUsed('/Users/yohan/Desktop/Classes/CSCI 561 Foundations of Artificial Intelligence/Homework/Homework 2/myplayer_play5/OppPlayerQAgent/state_used.pickle')
    elif args.train == False:
        old_arr, new_arr = Q.read_input()
        i, j = Q.move(new_arr, old_arr)
        Q.write_output((i,j))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--end", help = "If game ended pass parameter win or lose or draw", default=None)
    parser.add_argument("-t", "--train", help = "If game ended pass parameter win or lose or draw", default=False, type=bool)
    args = parser.parse_args()
    #print(args.end)
    main(args)
    
# path = 'myPlayerQValue.json'
# if os.path.isfile(path):
#     with open(path, 'r') as handle:
#         Q.QVal = json.load(handle)
#     handle.close()
     