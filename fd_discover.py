# coding: utf-8

from __future__ import print_function
import numpy as np
import csv
import time
from datetime import datetime
from collections import defaultdict
t1 = datetime.now()

partitions = {}
def getFrozenSetFromOne(x):
    return frozenset([x,])

def merge_partition(ps1, ps2):
    s = []
    iRow2p = {}
    for i, p1 in enumerate(ps1):
        for iRow in p1:
            iRow2p[iRow] = i
    for p2 in ps2:
        tmp = defaultdict(list)
        for iRow in p2:
            tmp[iRow2p[iRow]].append(iRow)
        s += tmp.values()
    return s

def get_partition(attributes):
    if attributes in partitions:
        return partitions[attributes]

    if len(attributes) == 0:
        partitions[attributes] = []
    elif len(attributes) == 1:
        iAttr = tuple(attributes)[0]
        d = defaultdict(list)
        for index, row in enumerate(table):
            d[row[iAttr]].append(index)
        partitions[attributes] = d.values()
    else:
        attr_tuple = tuple(attributes)
        ps1 = get_partition(frozenset(attr_tuple[0:-1]))
        ps2 = get_partition(frozenset(attr_tuple[0:-2] + attr_tuple[-1:]))
        partitions[attributes] = merge_partition(ps1, ps2)

    return partitions[attributes]

def isValid(X, E):
    '''
    test if X\{E} -> E is valid
    X is a set of number, E is a number
    '''
    return len(get_partition(X - {E})) == len(get_partition(X))

def compute_dependencies(L): # L is a set of tuple of number
    L_new = L.copy()
    for X in L:
        Xs = frozenset(X)
        RHS[X] = R
        for E in Xs:
            RHS[X] = RHS[X] & RHS[Xs - {E}]
        for E in RHS[X] & Xs:
            if isValid(Xs, E):
                fds.append((Xs - {E}, E))
                RHS[X] -= getFrozenSetFromOne(E)
                RHS[X] = RHS[X] & Xs
        if len(RHS[X]) == 0:
            L_new.remove(X)

    return L_new

def generate_next_level(L):
    # list comprehension?
    Ln = set([])
    for l1 in L:
        for l2 in L:
            if l1 != l2 and len(l1 - l2) == 1:
                Ln.add(l1 | l2)
    return Ln

def mycmp(fd1, fd2):
    left1 = sorted(list(fd1[0]))
    left2 = sorted(list(fd2[0]))
    if left1 < left2 or (fd1[0] == fd2[0] and fd1[1] < fd2[1]):
        return -1
    elif left1 > left2 or (fd1[0] == fd2[0] and fd1[1] > fd2[1]):
        return 1
    else:
        return 0

def output_fd(fds):
    with open(output_filename, 'w') as f:
        fds_sorted = sorted(fds, cmp=mycmp)
        for fd in fds_sorted:
            str = ''
            for l in sorted(list(fd[0])):
                str += '%d ' % (l+1)
            str += '-> %d\n' % (fd[1]+1)
            f.write(str)

# get data
input_filename = 'data.txt'
output_filename = 'outputp.txt'
with open(input_filename, 'rb') as f:
    reader = csv.reader(f)
    table = map(tuple, reader)

maxL = len(table[0])
R = frozenset(range(maxL))
RHS = {frozenset([]): R}
fds = []

def main():
    L = frozenset(map(getFrozenSetFromOne, R))
    L = compute_dependencies(L)
    for i in range(1, maxL):
        L = compute_dependencies(generate_next_level(L))
        print('level: %d, time used: %s' %(i+1, datetime.now() - t1))

    output_fd(fds)

    print('time used: %s' %(datetime.now() - t1))

main()
