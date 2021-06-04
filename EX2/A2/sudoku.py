import sys
from collections import deque
from copy import deepcopy
from search import Problem,Node
from time import process_time
import numpy as np

m = np.mean
s = np.std

class sudokuSolver(Problem):

    def __init__(self,state, goal=None):
        super().__init__(state)

    def goal_test(self,state):
        total = sum(range(1,10))

        # Check sum of rows and columns
        for row in range(9):
            # print(sum(state[row]))
            if(len(state[row])!= 9 or sum(state[row]) != total):
                return False
            col_tot = 0
            for column in range(len(state[row])):
                col_tot = col_tot + state[column][row]
            # print(col_tot)
            if(col_tot != total):
                return False

        # Check sum of quadrant
        for column in range(0,9,3):
            for row in range(0,9,3):
                block_total = 0
                for block_row in range(0,3):
                    for block_column in range(0,3):
                        block_total += state[row + block_row][column + block_column]
                if (block_total != total):
                    return False

        return True

    # Find presence of zeros in the sudoku puzzle(r ->row, c->column)
    def getSpot(self,state):
        for r in range(9):
            for c in range(len(state[r])):
                if(state[r][c] == 0):
                    return r,c

    # Filters possible values for an empty space (function that returns numbers that can be possibly come in empty spaces(possible is the range from [1-9]))
    # and ensures they haven't already come in that particular used->(used can stand for row/column/quadrant))
    def filterValues(self,possible,used):
        options = [number for number in possible if number not in used]
        # print(options)
        return options
        
    # Filters possible values in a row
    def filterRow(self,state,row):
        possible = list(range(1,9+1))
        row_present = [number for number in state[row] if(number != 0)]
        options = self.filterValues(possible,row_present)
        return options

    # Filters possible values in a column
    def filterCol(self,state,options,column):
        col_present = [] 
        for column_index in range(9):
            if state[column_index][column] != 0:
                col_present.append(state[column_index][column])
        options = self.filterValues(options,col_present)
        return options

    #Filters possible values in a quadrant/block
    def filterQuad(self,state,options,row,column):
        quad_present = []
        row_start = (row//3)*3
        col_start = (column//3)*3

        for row_quad in range(0,3):
            for col_quad in range(0,3):
                quad_present.append(state[row_quad+row_start][col_quad+col_start])
        options = self.filterValues(options,quad_present)
        return options

    def actions(self, state):
        row,column = self.getSpot(state)
        # Removing invalid options for the given empty spot
        options = self.filterRow(state,row)
        options = self.filterCol(state,options,column)
        options = self.filterQuad(state,options,row,column)
        for option in options:
            yield [option, row, column]
    
    def result(self, state, action):
        option,row,column = action
        # print("the option is {}".format(option))
        new_state = deepcopy(state)
        new_state[row][column] = option
        # print("Adding {} to ({},{})".format(option,row+1,column+1))
        # self.displaySudoku(new_state)
        # print("The new state is {}".format(new_state))
        return new_state

    def displaySudoku(self,state):
        for i in range(9):
            for j in range(len(state[i])):
                print(state[i][j],end = " ")
            print()
        # print("-----------------------------------------------------------------------")

    def display(self,Node):
        # print(type(Node.state))
        for i in Node.state:
            # print(type(i[0]))
            print(*i)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# The below code snippets have been taken from the Problem class present in search.py(for my understanding) 
class ProblemAnalysis(Problem):

	def __init__(self, problem):
		self.problem = problem
		self.succs = self.goal_tests = self.states = 0
		self.found = None

	def actions(self, state):
		self.succs += 1
		return self.problem.actions(state)

	def result(self, state, action):
		self.states += 1
		return self.problem.result(state, action)

	def goal_test(self, state):
		self.goal_tests += 1
		result = self.problem.goal_test(state)
		if result:
			self.found = state
		return result

	def path_cost(self, c, state1, action, state2):
		return self.problem.path_cost(c, state1, action, state2)

	def value(self, state):
		return self.problem.value(state)

	def __getattr__(self, attr):
		return getattr(self.problem, attr)

	def __repr__(self):
		return '<{:4d}/{:4d}/{:4d}/{}>'.format(self.succs, self.goal_tests,self.states, str(self.found)[:4])

	def get_stats(self):
		return self.succs, self.goal_tests,self.states
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# The below set of code snippets have been taken from search.py (for my understanding)
class Search:
    
    def breadth_first_tree_search(self,problem):
        # FIFO queue
        frontier = deque([Node(problem.initial)])  

        while frontier:
            node = frontier.popleft()
            if problem.goal_test(node.state):
                return node
            frontier.extend(node.expand(problem))
        return None


    def depth_first_tree_search(self,problem):
        # Stack
        frontier = [Node(problem.initial)]
        # print(frontier)
        while frontier:
            node = frontier.pop()
            # print("The node states are {}".format(node.state))
            if problem.goal_test(node.state):
                return node
            frontier.extend(node.expand(problem))
            # print("the expanded node is {}".format(node.expand(problem)))
        return None

    def depth_limited_search(self,problem, limit=80):
        def recursive_dls(node, problem, limit):
            if problem.goal_test(node.state):
                return node
            elif limit == 0:
                return 'cutoff'
            else:
                cutoff_occurred = False
                for child in node.expand(problem):
                    result = recursive_dls(child, problem, limit - 1)
                    if result == 'cutoff':
                        cutoff_occurred = True
                    elif result is not None:
                        return result
                return 'cutoff' if cutoff_occurred else None

        # Body of depth_limited_search:
        return recursive_dls(Node(problem.initial), problem, limit)

    def iterative_deepening_search(self,problem):
        for depth in range(sys.maxsize):
            result = self.depth_limited_search(problem, depth)
            if result != 'cutoff':
                return result

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

def Solver (filename,choice,s):

    with open(filename, 'r') as file:
        count=1
        lines=[line.rstrip() for line in file]
        temp=[]
        for i in lines:
            temp.append(list(map(int, i)))

    nodes_expanded = []
    goal_tests = []
    nodes_generated = []
    time_taken = []

    if(choice == 1):
        print("Depth First Search (DFS)")
        print("~~~~~~~~~**********~~~~~~~~~~~")
    elif(choice == 2):
        print("Breadth First Search (BFS)")
        print("~~~~~~~~~**********~~~~~~~~~~~")
    elif(choice == 3):
        print("Depth Limited Search (DLS)")
        print("~~~~~~~~~**********~~~~~~~~~~~")
    elif(choice == 4):
        print("Iterative Deepening Search (IDS)")
        print("~~~~~~~~~**********~~~~~~~~~~~")

    for i in range(9,len(temp),9):
        board=temp[i-9:i]
        problem = sudokuSolver(board)
        p = ProblemAnalysis(problem)
        # print("Sudoku {} is \n".format(count))
        # problem.displaySudoku(board)
        # print()
        start = process_time()
        if(choice == 1):
            solution = s.depth_first_tree_search(p)
        elif(choice == 2):
            solution = s.breadth_first_tree_search(p)
        elif(choice == 3):
            solution = s.depth_limited_search(p)
        elif(choice == 4):
            solution = s.iterative_deepening_search(p)        
        stop = process_time()
        x,y,z = p.get_stats()
        nodes_expanded.append(x)
        goal_tests.append(y)
        nodes_generated.append(z)
        time_taken.append(stop - start)
        # print("The solution for Sudoku {} is \n".format(count))
        count+=1
        if solution: 
            pass
            print("Solved {}/50".format(count-1))
            # problem.display(solution)
        else:
            print ("No possible solutions")
        # print("----------------------------------------")
    print("The mean number of nodes expanded are {}\nThe mean number of goal tests are {}\nThe mean number of nodes generated are {}\nThe average time taken is {}".format(m(nodes_expanded),m(goal_tests),m(nodes_generated),m(time_taken)))
    print("----------------------------------------")

if __name__== "__main__":
    s = Search()

    Solver("easycases.txt",1,s)
    Solver("easycases.txt",2,s)
    Solver("easycases.txt",3,s)
    Solver("easycases.txt",4,s)
    Solver("hardcases.txt",1,s)
    Solver("hardcases.txt",2,s)
    Solver("hardcases.txt",3,s)
    Solver("hardcases.txt",4,s)


# Easy and Medium Sudokus
# Depth First Search
# ----------------------------------------
# The mean number of nodes expanded are 705.5454545454545
# The mean number of goal tests are 706.5454545454545
# The mean number of nodes generated are 715.9090909090909
# The average time taken is 0.06943686551515155
# Breadth First Search
# ----------------------------------------
# The mean number of nodes expanded are 6159.030303030303
# The mean number of goal tests are 6160.030303030303
# The mean number of nodes generated are 6173.272727272727
# The average time taken is 0.6419277233636363
# ----------------------------------------
# Depth Limited Search
# ----------------------------------------
# The mean number of nodes expanded are 880.9090909090909
# The mean number of goal tests are 881.9090909090909
# The mean number of nodes generated are 894.3939393939394
# The average time taken is 0.09091494651515197
# ----------------------------------------
# Iterative Deepening Search
# ----------------------------------------
# The mean number of nodes expanded are 127086.54545454546
# The mean number of goal tests are 133246.57575757575
# The mean number of nodes generated are 133214.0606060606
# The average time taken is 13.094667124696965

# Hard Cases
# Depth First Search
# ----------------------------------------
# The mean number of nodes expanded are 14806.12
# The mean number of goal tests are 14807.12
# The mean number of nodes generated are 14819.18
# The average time taken is 2.35143766292
# Breadth First Search
# ----------------------------------------
# The mean number of nodes expanded are 39246.68
# The mean number of goal tests are 39247.68
# The mean number of nodes generated are 39246.68
# The average time taken is 7.1195478979
# ----------------------------------------
# Depth Limited Search
# ----------------------------------------
# The mean number of nodes expanded are 24493.2
# The mean number of goal tests are 24494.2
# The mean number of nodes generated are 24506.14
# The average time taken is 4.076148927020003
# ----------------------------------------
# Iterative Deepening Search
# ----------------------------------------
# The mean number of nodes expanded are 1146896.46
# The mean number of goal tests are 1186144.14
# The mean number of nodes generated are 1186103.44
# The average time taken is 113.59817936758

