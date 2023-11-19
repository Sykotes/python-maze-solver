from sys import argv


class Node():
    def __init__(self, state, parent, action, heuristic):
        self.state = state
        self.parent = parent
        self.action = action
        self.heuristic = heuristic

class DFSFronteir():
    def __init__(self):
        self.fronteir = []


    def add(self, node):
        self.fronteir.append(node)

    
    def contains_state(self, state):
        return any(node.state == state for node in self.fronteir)
    

    def empty(self):
        return len(self.fronteir) == 0


    def remove(self):
        if self.empty():
            raise Exception("empty fronteir")
        else:
            node = self.fronteir.pop(-1)
            return node


class BFSFronteir(DFSFronteir):
    def remove(self):
        if self.empty():
            raise Exception("empty fronteir")
        else:
            node = self.fronteir.pop(0)
            return node


class GBFSFronteir(DFSFronteir):
    def add(self, node):
        self.fronteir.append(node)
        self.fronteir = sorted(self.fronteir, key=lambda x: x.heuristic)


    def remove(self):
        if self.empty():
            raise Exception("empty fronteir")
        else:
            node = self.fronteir.pop(0)
            return node



class Maze():
    def __init__(self, filename, fronteir_type):
        self.fronteir_type = fronteir_type

        with open(filename) as file:
            content = file.read()

        if content.count("A") != 1:
            raise Exception("maze must have one start point: A")
        if content.count("B") != 1:
            raise Exception("maze must have one end point: B")

        content = content.splitlines()
        self.height = len(content)
        self.width = max(len(line) for line in content)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if content[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif content[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif content[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)

                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.path_length = 0

        self.solution = None


    def print_maze(self):
        solution = self.solution[1] if self.solution is not None else None
        self.places_to_explor = 0
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
                    print("x", end="")
                    self.path_length += 1
                else: 
                    print(" ", end="")
                    self.places_to_explor += 1
            print()
        print(f"\nEmpty path spaces: {self.places_to_explor}")


    def neighbors(self, state):
        row, col = state

        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1)),
        ]

        result = []
        for action, (r, c) in candidates:
            try:
                if not self.walls[r][c]:
                    result.append((action, (r, c)))
            except IndexError:
                continue
        return result


    def solve(self):
        self.num_explored = 0

        start = Node(state=self.start, parent=None, action=None, heuristic=0)
        if self.fronteir_type == "dfs":
            fronteir = DFSFronteir()
        elif self.fronteir_type == "bfs":
            fronteir = BFSFronteir()
        elif self.fronteir_type == "gbfs":
            fronteir = GBFSFronteir()
        else:
            raise Exception("No fronteir type specified")
        fronteir.add(start)

        self.explored = set()

        while True:
            node = fronteir.remove()
            self.num_explored += 1

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

                self.print_maze()
                print(f"Explored path: {self.num_explored}")
                print(f"Length of taken path: {self.path_length}")
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not fronteir.contains_state(state) and state not in self.explored:
                    heuristic = self.heuristic(state)
                    child = Node(state=state, parent=node, action=action, heuristic=heuristic)
                    fronteir.add(child)


    def heuristic(self, state):
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])




if __name__ == "__main__":
    maze = Maze(filename=f"mazes/{argv[1]}.txt", fronteir_type=argv[2])
    maze.solve()
