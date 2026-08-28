import sys
import time
import heapq


class Node():
    def __init__(self, state, parent, action, depth=0):     #depth = 0 as solve_dfs doesnt pass it
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth


class StackFrontier():      #StackFronteir is a Last In First Out for DFS algorithm
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():

    def __init__(self, filename):

        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        self.originalContents = contents # Keep track of the original contents of the maze

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None


    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def print_results(self):
        if self.solution is None:       #print results if no solution is found
            print("No solution")
            print("Path cost:N/A")
            print("Path length: N/A")
        else:
            actions, cells = self.solution       #print results if solution is found
            print("-".join(actions))
            counter = 0             # Count the number of actions
            for action in actions:
                counter += 1
            print("path cost: ", counter)
            print("path length: ", len(actions))
        
        print("states explored: ", self.num_explored)
        print("original maze:")
        print(self.originalContents.rstrip())
        print("path:")
        self.print()
        print("Time: ",f"{self.time_end - self.time_start:.6f}" " seconds")
        print("Max frontier size: ", self.max_frontier_size)


    def neighbors(self, state):
        row, col = state
        candidates = [
            ("U", (row - 1, col)),
            ("D", (row + 1, col)),
            ("L", (row, col - 1)),
            ("R", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result


    def solve_dfs(self):
        """Finds a solution to maze, if one exists."""

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                self.solution = None
                return False


            if len(frontier.frontier) > self.max_frontier_size:     # Update max frontier size if new frontier is larger
                self.max_frontier_size = len(frontier.frontier)

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return True

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)


    def solve_ids(self):
        limit = 0

        # Keep looping until solution found
        while True:
            result = self.depth_limited_dfs(limit)
            if result == "found":
                return True
            if result == "failure":     #no node exists
                self.solution = None
                return False
            limit +=1        # result == "cutoff"then increase limit and try again

    
    def is_on_path(self, node, state):     
    # Walk back through parent pointers to check if `state` is an ancestor
        current = node
        while current is not None:
            if current.state == state:
                return True
            current = current.parent
        return False


    def depth_limited_dfs(self, limit):
        cutoff_occured = False
        frontier = StackFrontier()
        frontier.add(Node(state=self.start, parent=None, action=None, depth=0))  # no depth!

        while not frontier.empty():
            node =  frontier.remove()
            self.num_explored +=1

            if len(frontier.frontier) > self.max_frontier_size:
                 self.max_frontier_size = len(frontier.frontier)

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return "found"

            if node.depth == limit:
                cutoff_occured = True       #wall hit dont expand
            else:
                for action, state in self.neighbors(node.state):
                    if not frontier.contains_state(state) and not self.is_on_path(node, state):
                        child = Node(state=state, parent=node, action=action, depth=node.depth+1)
                        frontier.add(child)

        if cutoff_occured:
            return "cutoff"
        else:
            return "failure"


    def heuristic(self, state):
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])


    def solve_Astar(self):
        counter = 0
        heap = []
        start = Node(state=self.start, parent = None,  action=None, depth = 0)
        h = self.heuristic(self.start)
        heapq.heappush(heap, (h, counter, start))   # f = g + h, g=0 so f=h

        self.explored = set()


        while heap:
            if len(heap) > self.max_frontier_size:
                self.max_frontier_size = len(heap)

            f,_, node = heapq.heappop(heap)
            if node.state in self.explored:
                continue
            self.num_explored +=1
    
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return True

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if state not in self.explored:
                    g = node.depth + 1
                    h = self.heuristic(state)
                    child = Node(state=state, parent=node, action=action, depth=g)
                    counter+=1
                    heapq.heappush(heap, (g+h,  counter, child))

        self.solution = None
        return False


    def solve_IDAstar(self):
        threshold = self.heuristic(self.start)
        start = Node(state=self.start, parent=None,action=None, depth=0)

        while True:
            result = self.dfs_threshold(start, threshold)
            if result == "found":
                return True
            if result == float('inf'):
                self.solution = None
                return False
            threshold = result      #next threshold - min f that exceeded

    def dfs_threshold(self, node, threshold):
        f = node.depth + self.heuristic(node.state)

        if f > threshold:
            return f

        self.num_explored += 1

        if node.depth > self.max_frontier_size:
            self.max_frontier_size = node.depth


        if node.state == self.goal:
            actions = []
            cells = []
            n = node

            while n.parent is not None:
                actions.append(n.action)
                cells.append(n.state)
                n = n.parent
            actions.reverse()
            cells.reverse()
            self.solution = (actions, cells)
            return "found"

        min_exceeded = float('inf')
        for action, state in self.neighbors(node.state):
            if self.is_on_path(node, state) is True:        # skip this neighbour coz it's on the current path, so moving there would loop
                continue
            child = Node(state=state, parent=node, action=action, depth=node.depth +1)
            result = self.dfs_threshold(child, threshold)
            if result == "found":
                return "found"
            if result < min_exceeded:
                min_exceeded = result

        return min_exceeded



    def solve(self, strategy ="dfs"):       #default strategy is dfs 

        # Keep track of number of states explored
        self.num_explored = 0
        self.max_frontier_size = 0
        self.explored = set()
        self.solution = None
        self.time_start = time.perf_counter()


        found = None                     

        if strategy == "dfs":
            found = self.solve_dfs()
        elif strategy == "ids":
            found = self.solve_ids()
        elif strategy == "A*":
            found = self.solve_Astar()
        elif strategy == "IDA*":
            found = self.solve_IDAstar()
        else:
            raise ValueError(f"Unknown strategy '{strategy}'. Expected 'dfs', 'ids', 'A*', or 'IDA*'.")

        self.time_end = time.perf_counter()


        return found                      

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python maze.py maze.txt [strategy]")
    m = Maze(sys.argv[1])
    strategy = sys.argv[2] if len(sys.argv) == 3 else "dfs"
    print("Solving...")
    m.solve(strategy)
    m.print_results()

    maze_name = sys.argv[1].split(".")[0]
    m.output_image(f"{maze_name}_{strategy}.png", show_explored=True)




