import time 
import sys 
import queue
import tracemalloc 
import heapq 

sys.setrecursionlimit(999999)

def getPos(board: list[str], weights: list[int]) -> tuple[(int, int), list[(int, int, int)], list[(int, int)]]: 
    playerPos, stones, stoneGoalPos = None, [], [] 
    for i, row in enumerate(board): 
        for j, char in enumerate(row): 
            if char == '@': 
                playerPos = (i, j)
            elif char == '+': 
                playerPos = (i, j)
                stoneGoalPos.append((i, j))
            elif char == '$' or char == '*': 
                stones.append((i, j, weights.pop()))
                if char == '*':
                    stoneGoalPos.append((i, j))
            elif char == '.': 
                stoneGoalPos.append((i, j))
    return playerPos, tuple(stones), tuple(stoneGoalPos)

def initGame(): 
    weights = list(map(int, sys.stdin.readline().split()))[::-1] # Lấy trọng số của các tảng đá 
    board = [] # Bản đồ của trò chơi

    # Lấy input đến khi kết thúc file  
    while True: 
        try: 
            line = sys.stdin.readline()
            if not line:
                break
            board.append(line)
        except EOFError:
            break 

    # Lấy tọa độ của các tảng đá, người chơi 
    playerPos, stones, stoneGoalPos = getPos(board, weights)
    return board, playerPos, stones, stoneGoalPos

def isGoal(stones, stoneGoalPos): 
    stonePos = [(stone[0], stone[1]) for stone in stones]
    return tuple(sorted(stonePos)) == stoneGoalPos

def isValid(playerPos, stonePos, action: tuple[int, int, chr]): 
    x = playerPos[0] + action[0] + action[0] * action[-1].isupper()
    y = playerPos[1] + action[1] + action[1] * action[-1].isupper() 
    return board[x][y] != '#' and (x, y) not in stonePos

def isFailed(stones):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [[0,1,2,3,4,5,6,7,8],
                    [2,5,8,1,4,7,0,3,6],
                    [0,1,2,3,4,5,6,7,8][::-1],
                    [2,5,8,1,4,7,0,3,6][::-1]]
    flipPattern = [[2,1,0,5,4,3,8,7,6],
                    [0,3,6,1,4,7,2,5,8],
                    [2,1,0,5,4,3,8,7,6][::-1],
                    [0,3,6,1,4,7,2,5,8][::-1]]
    allPattern = rotatePattern + flipPattern

    posBox = [(stone[0], stone[1]) for stone in stones]

    for box in posBox:
        if box not in stoneGoalPos:
            curBoard = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1), 
                    (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1), 
                    (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [curBoard[i] for i in pattern]
                if board[newBoard[1][0]][newBoard[1][1]] == '#' and board[newBoard[5][0]][newBoard[5][1]] == '#': 
                    return True
                if newBoard[1] in posBox and board[newBoard[2][0]][newBoard[2][1]] == '#' and board[newBoard[5][0]][newBoard[5][1]] == '#': 
                    return True
                elif newBoard[1] in posBox and board[newBoard[2][0]][newBoard[2][1]] == '#' and newBoard[5] in posBox: 
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: 
                    return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and board[newBoard[2][0]][newBoard[2][1]] == '#' and board[newBoard[3][0]][newBoard[3][1]] == '#' and board[newBoard[8][0]][board[8][1]] == '#': 
                    return True
    return False

def getActions(playerPos, stones): 
    actions = [[-1,0,'u','U'],[1,0,'d','D'],[0,-1,'l','L'],[0,1,'r','R']]
    stonePos = [(stone[0], stone[1]) for stone in stones]
    validActions = []
    for action in actions:
        x1, y1 = playerPos[0] + action[0], playerPos[1] + action[1]
        if (x1, y1) in stonePos: # đẩy tảng đá
            action.pop(2) 
        else:
            action.pop(3) 
        if isValid(playerPos, stonePos, action):
            validActions.append(action)
        else: 
            continue     
    return validActions

def updateGame(playerPos, stones, action): 
    xPlayer, yPlayer = playerPos[0] + action[0], playerPos[1] + action[1]
    stones = list(stones)
    w = 0
    if action[-1].isupper():
        for i, (x, y, w) in enumerate(stones): 
            if (x, y) == (xPlayer, yPlayer):
                stones.pop(i)
                stones.append((xPlayer + action[0], yPlayer + action[1], w))
                break 
    return (xPlayer, yPlayer), tuple(stones), w + 1 

def calculateHeuristic(stones, stoneGoalPos, playerPos): 
    distance = 0 

    for pos1 in stoneGoalPos: 
        minDist = 10 ** 9
        for pos2 in stones: 
            curDist = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
            curDist *= pos2[-1]
            curDist += abs(playerPos[0] - pos2[0]) + abs(playerPos[1] - pos2[1])
            if curDist < minDist: 
                minDist = curDist
        distance += minDist 

    return distance 
    

def BFS(playerPos, stones, stoneGoalPos): 
    frontier = queue.Queue()
    closedSet = set()
    numNodes = 1 
    # Mỗi phần tử trong hàng đợi sẽ là 1 trạng thái (Vị trí người chơi, tọa độ các viên đá, Các move đã thực thi, Tổng weight đã thực thi)
    frontier.put((playerPos, stones, "", 0))
    while not frontier.empty(): 
        playerPos, stones, actions, totalWeight = frontier.get()
        if isGoal(stones, stoneGoalPos): 
            return actions, totalWeight - len(actions), numNodes
        
        if (playerPos, stones) in closedSet:
            continue

        closedSet.add((playerPos, stones))

        for action in getActions(playerPos, stones):
            nextPlayerPos, nextStones, weight = updateGame(playerPos, stones, action)
            if isFailed(nextStones): 
                continue
            numNodes += 1 
            frontier.put((nextPlayerPos, nextStones, actions + action[-1], totalWeight + weight))

def DFS(playerPos, stones, stoneGoalPos): 
    stack = []
    closedSet = set()
    numNodes = 1 
    # Mỗi phần tử trong hàng đợi sẽ là 1 trạng thái (Vị trí người chơi, tọa độ các viên đá, Các move đã thực thi, Tổng weight đã thực thi)
    stack.append((playerPos, stones, "", 0))
    while stack: 
        playerPos, stones, actions, totalWeight = stack.pop()

        if isGoal(stones, stoneGoalPos): 
            return actions, totalWeight - len(actions), numNodes
        
        if (playerPos, stones) in closedSet:
            continue

        if len(actions) >= 1500: # heuristic cho DFS  
            continue

        closedSet.add((playerPos, stones))

        for action in getActions(playerPos, stones):
            nextPlayerPos, nextStones, weight = updateGame(playerPos, stones, action)
            if isFailed(nextStones): 
                continue
            numNodes += 1 
            stack.append((nextPlayerPos, nextStones, actions + action[-1], totalWeight + weight))

def UCS(playerPos, stones, stoneGoalPos):
    frontier = []
    heapq.heappush(frontier, (0, playerPos, stones, ""))
    closedSet = set()
    numNodes = 1 

    while frontier:
        totalWeight, playerPos, stones, actions = heapq.heappop(frontier)
        
        if isGoal(stones, stoneGoalPos): 
            return actions, totalWeight - len(actions), numNodes
    
        if (playerPos, stones) in closedSet:
            continue
    
        closedSet.add((playerPos, stones))

        for action in getActions(playerPos, stones): 
            nextPlayerPos, nextStones, weight = updateGame(playerPos, stones, action)
            if isFailed(nextStones): 
                continue
            numNodes += 1 
            heapq.heappush(frontier, (totalWeight + weight, nextPlayerPos, nextStones, actions + action[-1]))

def AStar(playerPos, stones, stoneGoalPos): 
    frontier = []
    heapq.heappush(frontier, (0, playerPos, stones, "", 0))
    closedSet = set()
    numNodes = 1 

    while frontier:
        totalWeightHeuristic, playerPos, stones, actions, totalWeight = heapq.heappop(frontier)
        
        if isGoal(stones, stoneGoalPos): 
            return actions, totalWeight - len(actions), numNodes
    
        if (playerPos, stones) in closedSet:
            continue
    
        closedSet.add((playerPos, stones))

        for action in getActions(playerPos, stones): 
            nextPlayerPos, nextStones, weight = updateGame(playerPos, stones, action)
            if isFailed(nextStones): 
                continue
            heuristic = calculateHeuristic(stones, stoneGoalPos, playerPos)
            numNodes += 1 
            heapq.heappush(frontier, (totalWeightHeuristic + weight + heuristic, nextPlayerPos, nextStones, actions + action[-1], totalWeight + weight))



if __name__ == '__main__':
    board, playerPos, stones, stoneGoalPos = initGame()
    print("BFS")
    time_start = time.time()
    tracemalloc.start()
    actions, totalWeight, numNodes = BFS(playerPos, stones, stoneGoalPos)
    timer = (time.time() - time_start) * 1000 
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_in_MB = peak / (1024 * 1024)  
    print(f"Steps: {len(actions)}, Weight: {totalWeight}, Node: {numNodes}, Time (ms): {timer:.2f}, Memory (MB): {memory_in_MB:.2f}")
    print(actions)

    print("DFS")
    time_start = time.time()
    tracemalloc.start()
    actions, totalWeight, numNodes = DFS(playerPos, stones, stoneGoalPos)
    timer = (time.time() - time_start) * 1000 
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_in_MB = peak / (1024 * 1024)  
    print(f"Steps: {len(actions)}, Weight: {totalWeight}, Node: {numNodes}, Time (ms): {timer:.2f}, Memory (MB): {memory_in_MB:.2f}")
    print(actions)

    print("UCS")
    time_start = time.time()
    tracemalloc.start()
    actions, totalWeight, numNodes = UCS(playerPos, stones, stoneGoalPos)
    timer = (time.time() - time_start) * 1000 
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_in_MB = peak / (1024 * 1024)  
    print(f"Steps: {len(actions)}, Weight: {totalWeight}, Node: {numNodes}, Time (ms): {timer:.2f}, Memory (MB): {memory_in_MB:.2f}")
    print(actions)

    print("A*")
    time_start = time.time()
    tracemalloc.start()
    actions, totalWeight, numNodes = AStar(playerPos, stones, stoneGoalPos)
    timer = (time.time() - time_start) * 1000 
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_in_MB = peak / (1024 * 1024)  
    print(f"Steps: {len(actions)}, Weight: {totalWeight}, Node: {numNodes}, Time (ms): {timer:.2f}, Memory (MB): {memory_in_MB:.2f}")
    print(actions)

    