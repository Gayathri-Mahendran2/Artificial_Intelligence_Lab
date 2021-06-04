import numpy as np

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def clauseCheck(c, model):
    c_value = True
    valid_lit = intersection(c.keys(),model.keys())
    if(len(valid_lit)==0):     #returns 2 if there is no literal in model that matches with literal in clause
        return(2)
    for lit, value in model.items():
        if(lit in valid_lit and value == c[lit]):
            c_value = True
            break
        else:
            c_value = False
    if(c_value==False and len(valid_lit) != len(c.keys())):    #returns 3 if only one literal is false
        return(3)
    return(c_value)


def sentenceCheck(s, model):
    true_count = 0
    for i in s:
        c_value = clauseCheck(i, model)
        if(c_value == False):
            return(False)
        if(c_value==True):
            true_count += 1
    if(true_count == len(s)):
        return(True)
    return(2)


def findPureSymbol(s, symbols, model):
    pure_s = None
    pure_v = None
    positive_symbols = set()
    negative_symbols = set()
    for i in symbols:
        for j in s:
            if(i in j):
                if(j[i]==0):
                    negative_symbols.add(i)
                else:
                    positive_symbols.add(i)
    for i in symbols:
        if(i in positive_symbols and i in negative_symbols):
            positive_symbols.remove(i)
            negative_symbols.remove(i)

    if(len(positive_symbols)>0):
        pure_s,pure_v = list(positive_symbols)[0],1
    if(len(negative_symbols)>0):
        pure_s,pure_v = list(negative_symbols)[0],1

    return(pure_s, pure_v)


def findUnitClause(s, model):
    unit_s = None
    unit_v = None
    for i in s:
        intersec = intersection(i.keys(),model.keys())
        if((len(intersec) == len(i.keys())-1) and clauseCheck(i, model) == 3):
            unit_s = list(np.setdiff1d(list(i.keys()),list(model.keys())))[0]
            unit_v = i[unit_s]
            break
    return(unit_s, unit_v)



def DPLL(clauses, symbols, model, result) :
    if(sentenceCheck(clauses, model)==True):
        result.append(model)
        return(True)
    elif(sentenceCheck(clauses, model)==False):
        return(False)
    P,value = findPureSymbol(clauses, symbols, model)
    if(P != None):
        new = dict(model)
        new[P] = value
        return DPLL(clauses, [i for i in symbols if i!=P], new, result)
    P,value = findUnitClause(clauses, model)
    if(P != None):
        new = dict(model)
        new[P] = value
        return DPLL(clauses, [i for i in symbols if i!=P], new, result)

    P = symbols[0]
    rest = symbols[1:]

    new1 = dict(model)
    new1[P] = 1

    new2 = dict(model)
    new2[P] = 0

    return(DPLL(clauses, rest, new1, result) or DPLL(clauses, rest, new2, result))


def clause_ip(symbols):
    ip = input().split(":")
    if((ip[0] not in symbols) or (int(ip[1]) not in [0,1])):
        print("invalid literal! Try again")
        ip = clause_ip(symbols)
    return(ip)


def DPLL_SATISFIABLE():
    result =[]
    clauses = []
    symbols = input("Enter number of symbols: ").split(" ")
    n_S = len(symbols)
    n_O = int((input("Enter CNF order : ")))
    n_C = int(input("Enter no of clauses : "))
    for i in range(n_C):
        print("Clause {}".format(i+1))
        clause_dict = {}
        for j in range(n_O):
            ip = clause_ip(symbols)
            clause_dict[ip[0]] = int(ip[1])
        clauses.append(clause_dict)
    sat = DPLL(clauses, symbols, {}, result)
    return(sat,result)


sat_op = DPLL_SATISFIABLE()

print("\nIs it satisfiable : ",sat_op[0])
print("Model : ",sat_op[1])


'''

Output:

case 1: not a model

Enter number of symbols : a b c
Enter CNF order : 2
Enter no of clauses : 5

Clause 1 :
a:1 b:1
Clause 2 :
b:0 c:0
Clause 3 :
c:1 a:0
Clause 4 :
a:0 b:1
Clause 5 :
a:1 b:0

Is it satisfiable :  False
Model :  []

************************************************
case 1: model

Enter number of symbols : a b c d
Enter CNF order : 3
Enter no of clauses : 5

Clause 1 :
a:0 b:1 c:1
Clause 2 :
a:0 b:0 c:1
Clause 3 :
a:1 c:1 d:1
Clause 4 :
b:0 c:0 d:1
Clause 5 :
a:0 b:0 c:1

Is it satisfiable :  True
Model :  [{'d': 1, 'a': 1, 'b': 1, 'c': 1}]


************************************************

'''
