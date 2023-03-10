from collections import defaultdict
from math import gcd, sqrt
from typing import DefaultDict, List, Tuple
import sys 

IntPair = Tuple[int, int]
sys.setrecursionlimit(5000)
 
# contains all points and their obstacle data 
# [x, y, number of obstacle 1 possibilities (o1), o2, o3, o4] 
points={}

# stores incoming and outgoing edge relations corresponding to obstacles between points
pointsIN={}
pointsOUT={}

# does the same but in a different format
pointsIN2={}
pointsOUT2={}

# start and end point
source = ""
sink = ""

# counter for "imaginary" points
# when an obstacle can be built to multiple other points an imaginary point is made with the limited
# edge capacity, then edges are drawn to all destinations from there
# this allows the maxFlow algirithm to figure out how to distribute the availabe obstacles after the edges are constructed
x=1

# find slope between two points a and b
def normalized_slope(a: IntPair, b: IntPair) -> IntPair:  
    run = b[0] - a[0]
    rise = b[1] - a[1]
    
    # disregard same point in slope calculation 
    if (run == 0 and rise==0):
        return (0, 0)
    
    # Normalize by greatest common divisor.
    # math.gcd only works on positive numbers.
    gcd_ = gcd(abs(rise), abs(run))
    return (
        run // gcd_,
        rise // gcd_,
    )
 
# returns all points sharing the same x or y axis as point
def obstacle1(point: str) -> List[str]:
    destinations=[]
    pointCords = points[point][0:2]
    for i in points:
        try:
            iCords = points[i][0:2]
            #print(iCords,pointCords)
            
            if (iCords[0] == pointCords[0]) ^ (iCords[1] == pointCords[1]):
                destinations.append(i)

        except ValueError:
            print(i + "imaginary coordinate skipped")
            
    return destinations
    
# return furthest point
def obstacle2(point: str) -> List[str]:
    pointCords = points[point][0:2]
    maxDist = 0
    destination = point
    
    for i in points:
        iCords = points[i][0:2]
        dist = sqrt( (iCords[0]-pointCords[0])**2 + (iCords[1]-pointCords[1])**2)
        
        if (dist > maxDist):
            maxDist = dist
            destination = i
    
    # return in list format so every obstacle method returns the same type
    return [destination]

# return all points with at least one point inbetween our points
def obstacle3(point: str) -> List[str]:
    # You need at least 3 points to potentially have non-collinear points.
    # For [0, 2] points, all points are on the same line.
    if len(points) < 3:
        return []
 
    # Note that every line we find will have at least 2 points.
    # There will be at least one line because len(points) >= 3.
    # Therefore, it's safe to initialize to 0.
    destinations=[]
 
    a = tuple(points[point][0:2])
    # Fresh lines already have a, so default=1
    # points found are stored in a dictionary, each list of points sharing a line have the slope as key
    slope_bois: DefaultDict[IntPair, List[str]] = defaultdict(lambda: [])
 
    # for all points, append them to a list with the line leading to its' slope as key
    for b_index in points:
        b = tuple(points[b_index][0:2])
        slope_bois[normalized_slope(a, b)].append(b)
 
    # sort all slopes' points by distance to self
    for i in slope_bois:
        if i[0]<0:
            slope_bois[i] = sorted(slope_bois[i],key=lambda tup: tup[0], reverse=True)
        else:
            slope_bois[i] = sorted(slope_bois[i],key=lambda tup: tup[0], reverse=False)
        if i[1]<0:
            slope_bois[i] = sorted(slope_bois[i],key=lambda tup: tup[1], reverse=True)
        else:
            slope_bois[i] = sorted(slope_bois[i],key=lambda tup: tup[1], reverse=False)

    # add all points that satisfy criteria for obstacle 3 to destinations
    for i in slope_bois.values():
        if len(i)>2:         
            i = [str(j).replace(" ", "") for j in i]
            destinations.extend(i[2:])
 
    return destinations

def obstacle4(point: str) -> List[str]:
    return [list(points)[-1]]

def makeGraph(startpoint): 
    #print(startpoint)
    global x
    #get info on how many obstacles I can build and to where
    o1,o2,o3,o4=points[startpoint][2:6]
    targets = [[obstacle1(startpoint),o1],
               [obstacle2(startpoint),o2],
               [obstacle3(startpoint),o3],
               [obstacle4(startpoint),o4]]
    #print(targets)
    for i in targets: #for each obstacle type
        #print(i , i[0])
        if i[1]>0: #if I have obstacles to build
            if 0<len(i[0]): #and nodes to build them to
                if len(i[0])==1: #single target
                    #print(i[0][0])
                    # save outgoing edge
                    try:
                        pointsOUT[startpoint].append([i[0][0],0,i[1]])                         
                    except KeyError:
                        pointsOUT[startpoint] = [[i[0][0],0,i[1]]]
                    # save incoming edge for the target
                    try:
                        pointsIN[str(i[0][0])].append([startpoint,0,i[1]])
                    except KeyError:
                        pointsIN[str(i[0][0])] = [[startpoint,0,i[1]]]
                    
                    if not(str(i[0][0]) in pointsOUT):
                        makeGraph(str(i[0][0]))
                        
                else: #multi target
                    # make an imaginary point
                    try:
                        pointsOUT[startpoint].append(["(x{})".format(x),0,i[1]])
                            
                    except KeyError:
                        pointsOUT[startpoint] = [["(x{})".format(x),0,i[1]]]
                        
                    pointsIN["(x{})".format(x)] = [[startpoint,0,i[1]]]
                    
                    pointsOUT["(x{})".format(x)] = []
                    
                    # make edges from imaginary point to all targets
                    for j in i[0]:
                        pointsOUT["(x{})".format(x)].append([j,0,i[1]])
                        
                        try:
                            pointsIN[j].append(["(x{})".format(x),0,i[1]])
                        except KeyError:
                            pointsIN[j] = [["(x{})".format(x),0,i[1]]]
                    # increase imaginary point counter
                    x+=1
                    
                    # for all targets, if target has no outgoing edges, construct graph from target
                    for j in i[0]:
                        if not(j in pointsOUT):
                            makeGraph(j)
                

# Get input from terminal              
def inputGet():
    n = int(input())
    pp = {}
    for i in range(n):
        line = list(map(int, input().split()))
        pp["({},{})".format(line[0],line[1])] = line
    return pp


       
def ajacencyConversion(): 
    global pointsOUT2
    global pointsIN2
    
    #pain train choo-choo
    #gotta change the entire ajacency list to support double indexing by coords
    # this is needed to help identify edges leading into and out of self when edmondsKarp is running
    entries = {}
    for entry in list(pointsOUT):   #pointsOUT
        edges = {}
        for edge in pointsOUT[entry]:
            key, value = edge[0], edge[1:]
            try:
                edges[key][1] += value[1]
            except KeyError:
                edges[key] = value
        entries[entry] = edges
    pointsOUT2 = entries
    
    entries = {}
    for entry in list(pointsIN):   #pointsIN
        edges = {}
        for edge in pointsIN[entry]:
            key, value = edge[0], edge[1:]
            try:
                edges[key][1] += value[1]
            except KeyError:
                edges[key] = value
        entries[entry] = edges
    pointsIN2 = entries


queue = []
def enqueue(e):
    queue.append(e)

def dequeue():
    return queue.pop(0)

def solve(s):
    enqueue([s,True])
    
    visited = list(points)
    visited.extend(["(x{})".format(i+1) for i in range(x-1)])
    visited = [[visited[i]] for i in range(len(visited))]
    [visited[i].append(False) for i in range(len(visited))]
    visited = dict(visited)
    
    visited[s] = True
    
    prev = dict.fromkeys(visited, None)
    
    while bool(queue):
        node = dequeue()
        neighbours = []
        #print(node)
        try:
            if node[1]: #outgoing edge path
                
                #print(node, "<-", pointsOUT2[node])
                for i in list(pointsOUT2[node[0]]):
                    #print("::",pointsOUT2[node[0]][i])
                    if pointsOUT2[node[0]][i][1]>0:
                        
                        neighbours.append([i,True])
                        #cry about the syntax I don't care
            else:
                
                #print(node, "<-",pointsIN2[node])
                for i in list(pointsIN2[node[0]]):
                    #print("::",pointsIN2[node[0]][i])
                    if pointsIN2[node[0]][i][0]>0:
                        neighbours.append([i,False])
        except KeyError:
            pass
        
        for i in neighbours:
            if(not visited[i[0]]):
                enqueue(i)
                visited[i[0]] = True
                prev[i[0]] = node
    #print("result: ", prev)
    return prev

def reconstructPath(s, e, prev):
    path = []
    path.append([e])
    #print(e)
    e = prev[e]
    
    while e!=None:
        #print(e)
        path.append(e)
        try:
            e = prev[e[0]]
        except TypeError:
            e = None
    
    path.reverse()
    
    #print(path,prev)
    
    if list(path)[0][0] == s:
        return path
    return []

# breadth first search
def BFS(s, e):
    prev = solve(s)
    return reconstructPath(s, e, prev)

# edmonds karp solves max flow by using breadth first search for a possible path from source to sink
# path can be made on an edge with unused capacity, or in reverse direction by decreasing flow on edge (graph only has directed edges)
# once path is found maximise flow through it, then find a new path until no new paths can be made
def edmondsKarp(s,e):

    path = BFS(s,e)
    #print(path)
    #yes=True
    while bool(path):
        weights=[]
        first = True
        for i in path: #find all available capacity/invard flow
            if first:
                prev = i
                first = False
            else:
                if prev[1]: #path forward direction
                    edge = pointsOUT2[prev[0]][i[0]]
                    weights.append(edge[1])
                else:
                    edge = pointsIN2[i[0]][prev[0]]
                    weights.append(edge[0])
                prev = i
        
        flow = min(weights) #find minimum of it
        #print(weights, flow)
        
        first = True
        for i in path: #add it to path
            if first:
                prev = i
                first = False
            else:
                if prev[1]: #path forward direction
                    pointsOUT2[prev[0]][i[0]][0] += flow
                    pointsOUT2[prev[0]][i[0]][1] -= flow
                    
                    pointsIN2[i[0]][prev[0]][0] += flow
                    pointsIN2[i[0]][prev[0]][1] -= flow
                    
                else: # path reverse direction
                    pointsIN2[prev[0]][i[0]][0] -= flow
                    pointsIN2[prev[0]][i[0]][1] += flow
                    
                    pointsOUT2[i[0]][prev[0]][0] -= flow
                    pointsOUT2[i[0]][prev[0]][1] += flow
                    
                prev = i
        #yes=False
        path = BFS(s,e)
        #print(path)
    
    result = 0
    for edge in list(pointsIN2[e]):
        result += pointsIN2[e][edge][0]
    return result

points = inputGet()

source = list(points)[0] #will change later to avoid making list every time
sink = list(points)[-1] #will change later to avoid making list every time

# make directed graph corresponding to possible arrangements of obstacles
makeGraph(source)
# convert data structure for easier solve
ajacencyConversion()
# maximize flow, return max flow
print(edmondsKarp(source,sink))
