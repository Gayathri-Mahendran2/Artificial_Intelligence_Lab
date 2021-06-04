import sys
from collections import deque
import math
from utils import *
import time
import random as rand

class Point: 
	def __init__(self, x, y): 
		self.x = x 
		self.y = y 
def onSegment(p, q, r): 
	if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
		(q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))): 
		return True
	return False
def Left_index(points):      
    minn = 0
    for i in range(1,len(points)): 
        if points[i].x < points[minn].x: 
            minn = i 
        elif points[i].x == points[minn].x: 
            if points[i].y > points[minn].y: 
                minn = i 
    return minn 

def orientation(p, q, r): 
	# 0 : Colinear points 
	# 1 : Clockwise points 
	# 2 : Counterclockwise 
	val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y)) 
	if (val > 0): 
		# Clockwise orientation 
		return 1
	elif (val < 0): 
		# Counterclockwise orientation 
		return 2
	else: 
		# Colinear orientation 
		return 0


def convexHull(points, n): 
    # There must be at least 3 points 
    if n < 3: 
        return
    # Find the leftmost point 
    l = Left_index(points) 
    hull = [] 
    p = l 
    q = 0
    while(True): 
        # Add current point to result 
        hull.append(p) 
        q = (p + 1) % n 
        for i in range(n): 
            if(orientation(points[p],points[i], points[q]) == 2): 
                q = i 
        p = q 
        # While we don't come to first point 
        if(p == l): 
            break
    temp_ptr=points[hull[0]]
    edges=[]
    vertices=[]
    for i in range(len(hull)):
        vertices.append(points[hull[i]])
    for i in range(len(hull)-1):
        temp=[points[hull[i]],points[hull[i+1]]]
        edges.append(temp)
    edges.append([points[hull[0]],points[hull[len(hull)-1]]])
    return vertices,edges


# the line segment 'p1q1' and 'p2q2' intersect. 
def doIntersect(p1,q1,p2,q2):
	o1 = orientation(p1, q1, p2) 
	o2 = orientation(p1, q1, q2) 
	o3 = orientation(p2, q2, p1) 
	o4 = orientation(p2, q2, q1) 
	# General case 
	if ((o1 != o2) and (o3 != o4)): 
		return True
	# Special Cases 
	# p1 , q1 and p2 are colinear and p2 lies on segment p1q1 
	if ((o1 == 0) and onSegment(p1, p2, q1)): 
		return True
	# p1 , q1 and q2 are colinear and q2 lies on segment p1q1 
	if ((o2 == 0) and onSegment(p1, q2, q1)): 
		return True
	# p2 , q2 and p1 are colinear and p1 lies on segment p2q2 
	if ((o3 == 0) and onSegment(p2, p1, q2)): 
		return True
	# p2 , q2 and q1 are colinear and q1 lies on segment p2q2 
	if ((o4 == 0) and onSegment(p2, q1, q2)): 
		return True
	# If none of the cases 
	return False

def duplicate(temp,points,polygon):
    temp_p=(temp.x,temp.y)
    for poly in points:
        for vertex in poly:
            temp_r=(vertex.x,vertex.y)
            if(temp_p==temp_r):
                return True
    for poly in polygon:
        temp_r=(poly.x,poly.y)
        if(temp_p==temp_r):
            return True
    return False

class Problem:
    polygon_vertices=[]
    polygon_edges=[]
    polygon_coord=[]
    def __init__(self, initial, goal,vertices,edges,polygons):
        self.initial = initial
        self.goal = goal
        self.polygon_vertices=vertices
        self.polygon_edges=edges
        self.polygon_coord=polygons
        self.nodes_generated=0
        self.nodes_expanded=0

    def find_polygon(self,state):
        for i in self.polygon_coord:
            if state in i:
                return i
        return None

    def actions(self, state):
        possible_points=[]
        self.inc_nodes_exp(1)
        #to append the vertices connected as a edge to the state
        #converting to point
        state_point=Point(state[0],state[1])
        for edges in self.polygon_edges:
            if state in edges:
                for point in edges:
                    if(point!=state):
                        possible_points.append(point)
        #find the polygon it belongs to
        polygon=self.find_polygon(state)
        #to check if the selected point and the state when form a line segment intersect or not
        for vertex in self.polygon_vertices:
            if(vertex==state):
                continue
            if(state!=self.initial and vertex in polygon):
                continue
            #converting to point
            check=[]
            check_point=Point(vertex[0],vertex[1])
            for edge in self.polygon_edges:
                #print("selected edge: ",edge)
                if(state not in edge and vertex not in edge):#don't consider this edge as it will alwys intersect with a line(state and vertex)
                    lineseg_point1=Point(edge[0][0],edge[0][1])
                    lineseg_point2=Point(edge[1][0],edge[1][1])
                    check.append(doIntersect(state_point,check_point,lineseg_point1,lineseg_point2))
            if(vertex not in possible_points and vertex!=state and True not in check and check!=[]):
                possible_points.append(vertex)
        
        #to check if any of the points 
        #print("Possible points: ",possible_points)
        return possible_points

    def h(self,node):
        x1,y1=node.state[0],node.state[1]
        x2,y2=self.goal[0],self.goal[1]
        temp_dist1=abs(x2-x1)**2
        temp_dist2=abs(y2-y1)**2
        dist=temp_dist2+temp_dist1
        dist=math.sqrt(dist)
        return dist

    def result(self, state, action):
        self.inc_nodes_gen(1)
        new_state=(action[0],action[1])
        return new_state

    def goal_test(self, state):
        if(state[0]==self.goal[0] and state[1]==self.goal[1]):
            return True
        else:
            return False

    def path_cost(self, c, state1, action, state2):
        x1,y1=state1[0],state1[1]
        x2,y2=state2[0],state2[1]
        temp_dist1=abs(x2-x1)**2
        temp_dist2=abs(y2-y1)**2
        dist=temp_dist2+temp_dist1
        dist=math.sqrt(dist)
        return c+dist


    def value(self, state):
        raise NotImplementedError

    def inc_nodes_gen(self,val):
        self.nodes_generated=self.nodes_generated+val
    def inc_nodes_exp(self,val):
        self.nodes_expanded=self.nodes_expanded+val


#########


class Node:

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        #problem.inc_nodes_exp(1)
        #problem.inc_nodes_gen(len(problem.actions(self.state)))
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self, action, problem.path_cost(self.path_cost, self.state, action, next_state))
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

     """We want for a queue of nodes in breadth_first_graph_search or
     astar_search to have no duplicated states, so we treat nodes
     with the same state as equal. [Problem: this may not be what you
     want in other contexts.]"""

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        """ We use the hash value of the state
        stored in the node instead of the node
        object itself to quickly search a node
        with the same state in a Hash Table
        return hash(self.state)"""


#########

def breadth_first_graph_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = deque([node])
    explored = set()
    while frontier:
        node = frontier.popleft()
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return child
                frontier.append(child)
    return None

def best_first_graph_search(problem, f, display=False):
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            if display:
                print(len(explored), "paths have been expanded and", len(frontier), "paths remain in the frontier")
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None

##########
# Informed (Heuristic) Search

def greedy_best_first_graph_search(problem, h=None, display=False):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n:h(n), display)


# Greedy best-first search is accomplished by specifying f(n) = h(n).


def astar_search(problem, h=None, display=False):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n), display)


##########
def generate_graph():
    points=[]
    for i in range(1,5):
        for j in range(1,5):
            polygon_size=rand.randint(0,100)%6+3
            polygon=[]
            k=0
            while(k<polygon_size):
                upper1=(i+1)*10-1
                lower1=(i)*10
                upper2=(j+1)*10-1
                lower2=(j)*10
                x1,y1=rand.randint(lower1,upper1),rand.randint(lower2,upper2)
                temp=Point(x1,y1)
                if(duplicate(temp,points,polygon)==False):
                        polygon.append(temp)
                        k=k+1
            points.append(polygon)
    start_state=(rand.randint(0,9),rand.randint(0,9))
    goal_state=(rand.randint(51,60),rand.randint(51,60))
    #plt.plot(start_state[0],start_state[1],"bo")
    #plt.plot(goal_state[0],goal_state[1],"bo")
    polygon_coord=[]
    polygon_edges=[]
    polygon_vertex=[]
    for p1 in points:
        coord=[]
        x_val=[]
        y_val=[]
        vertices,edges=convexHull(p1,len(p1))
        for i in vertices:
            #plt.plot(i.x,i.y,"ro")
            coord.append((i.x,i.y))
            polygon_vertex.append((i.x,i.y))
        polygon_coord.append(coord)
        
        for j in edges:
            x_val.append(j[0].x)
            x_val.append(j[1].x)
            y_val.append(j[0].y)
            y_val.append(j[1].y)
            polygon_edges.append([(j[0].x,j[0].y),(j[1].x,j[1].y)])
        #plt.plot(x_val,y_val)
    #plt.axis([0,50,0,50])
    #plt.show()
    polygon_vertex.append(goal_state)
    #print("Start State: ",start_state_coord)
    #print("Goal State: ",goal_state_coord)
    #print("All vertices: ",polygon_vertex)
    #print("All coordinates: ",polygon_coord)
    #print("All edges: ",polygon_edges)
    return polygon_coord,polygon_edges,polygon_vertex,start_state,goal_state

avg_time=0
avg_nodes_gen=0
avg_nodes_exp=0
avg_cost=0
print("BFS Analysis")
for times in range(0,100):
    #print("Graph ",(times+1))
    polygon_coord,polygon_edges,polygon_vertex,start_state,goal_state=generate_graph()
    #print("Defined states")
    distance_obj=Problem(start_state,goal_state,polygon_vertex,polygon_edges,polygon_coord)
    #print("Distance object initialized")
    start_time=time.time()
    solved=breadth_first_graph_search(distance_obj)
    end_time=time.time()
    search_time=end_time-start_time
    #path=solved.path()
    avg_time=avg_time+search_time
    avg_nodes_gen=avg_nodes_gen+distance_obj.nodes_generated
    avg_nodes_exp=avg_nodes_exp+distance_obj.nodes_expanded
    avg_cost=avg_cost+solved.path_cost
    #print("Time: ",search_time,"Cost: ",solved.path_cost)
print("Average Time Taken: ",avg_time/100)
print("Average Nodes Generated: ",avg_nodes_gen/100)
print("Average Nodes Expanded: ",avg_nodes_exp/100)
print("Average Cost: ",avg_cost/100)

avg_time=0
avg_nodes_gen=0
avg_nodes_exp=0
avg_cost=0
print("Greedy Search Analysis")
for times in range(0,100):
    #print("Graph ",(times+1))
    polygon_coord,polygon_edges,polygon_vertex,start_state,goal_state=generate_graph()
    #print("Defined states")
    distance_obj=Problem(start_state,goal_state,polygon_vertex,polygon_edges,polygon_coord)
    #print("Distance object initialized")
    start_time=time.time()
    solved=greedy_best_first_graph_search(distance_obj)
    end_time=time.time()
    search_time=end_time-start_time
    #path=solved.path()
    avg_time=avg_time+search_time
    avg_nodes_gen=avg_nodes_gen+distance_obj.nodes_generated
    avg_nodes_exp=avg_nodes_exp+distance_obj.nodes_expanded
    avg_cost=avg_cost+solved.path_cost
    #print("Time: ",search_time,"Cost: ",solved.path_cost)
print("Average Time Taken: ",avg_time/100)
print("Average Nodes Generated: ",avg_nodes_gen/100)
print("Average Nodes Expanded: ",avg_nodes_exp/100)
print("Average Cost: ",avg_cost/100)

avg_time=0
avg_nodes_gen=0
avg_nodes_exp=0
avg_cost=0
print("A* Search Analysis")
for times in range(0,100):
    #print("Graph ",(times+1))
    polygon_coord,polygon_edges,polygon_vertex,start_state,goal_state=generate_graph()
    #print("Defined states")
    distance_obj=Problem(start_state,goal_state,polygon_vertex,polygon_edges,polygon_coord)
    #print("Distance object initialized")
    start_time=time.time()
    solved=astar_search(distance_obj)
    end_time=time.time()
    search_time=end_time-start_time
    #path=solved.path()
    avg_time=avg_time+search_time
    avg_nodes_gen=avg_nodes_gen+distance_obj.nodes_generated
    avg_nodes_exp=avg_nodes_exp+distance_obj.nodes_expanded
    avg_cost=avg_cost+solved.path_cost
    #print("Time: ",search_time,"Cost: ",solved.path_cost/100)
print("Average Time Taken: ",avg_time/100)
print("Average Nodes Generated: ",avg_nodes_gen/100)
print("Average Nodes Expanded: ",avg_nodes_exp/100)
print("Average Cost: ",avg_cost/100)

