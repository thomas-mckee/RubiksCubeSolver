from move_maps import MOVES

class Cube:
    def __init__(self, state=None):
        if state:
            self.state = list(state)
        else:
            self.state = list('UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD')
                            
    def rotate(self, moves):
        """Rotates the cube facelet based on move(s)"""
        # Iterate over all moves in chain
        for move in moves.split(" "):
            # Get move dictionary
            move_dict = MOVES[move.upper()]
            
            # Save old cube state
            old_state = self.state.copy()

            # Update cube with each move
            for src, dst in move_dict.items():
                self.state[dst] = old_state[src]

    def is_solved(self, correct_cube):
        return all(self.state[i] == self.state[i - i % 3] for i in range(54))

    def copy(self):
        return Cube(self.state)
    
    def print_cube(self):
        correct = 'BUFUULUDLDRRDLLDBRBRUDFBDDDBFULRRLFFLFRBBFULLFBFUDRBUR'
        print("".join(self.state))
        print(correct == "".join(self.state))
        

    def display_cube(self):
        """Prints the cube in 2D net layout to the console with color emojis."""
        s = self.state  

        color_map = {
            'D': '🟨',  
            'U': '⬜',  
            'R': '🟥',  
            'L': '🟧',  
            'B': '🟦',  
            'F': '🟩',  
        }

        def face(rows):
            return [''.join(color_map[s[i]] for i in row) for row in rows]

        U = face([[0,1,2],[3,4,5],[6,7,8]])
        L = face([[9,10,11],[12,13,14],[15,16,17]])
        F = face([[18,19,20],[21,22,23],[24,25,26]])
        R = face([[27,28,29],[30,31,32],[33,34,35]])
        B = face([[36,37,38],[39,40,41],[42,43,44]])
        D = face([[45,46,47],[48,49,50],[51,52,53]])

        # Top face
        print("      " + U[0])
        print("      " + U[1])
        print("      " + U[2])

        # Middle row (L, F, R, B)
        for l, f, r, b in zip(L, F, R, B):
            print(l + f + r + b)

        # Bottom face
        print("      " + D[0])
        print("      " + D[1])
        print("      " + D[2])
        print()


def custom_solution(solver, cube):
    solved_cube = solver[0]
    solved_pieces = solver[1]
    for pos in solved_pieces:
        if cube.state[pos] != solved_cube.state[pos]:
            return False
    return True

MOVES_LIST = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2"]

def solve_dfs(solver, cube, solution, depth_remaining):
    if custom_solution(solver, cube):
        return solution.strip()
    if depth_remaining == 0:
        return None
    for move in MOVES_LIST:
        new_cube = cube.copy()
        new_cube.rotate(move)
        result = solve_dfs(solver, new_cube, solution + " " + move, depth_remaining - 1)
        if result is not None:
            return result
    return None

def solve_iidfs(solver, cube, depth_limit):
    for depth in range(depth_limit+1):
        solution = solve_dfs(solver, cube, "", depth)
        if solution != None:
            return solution
    return None

def main():
    cube = Cube()
    scramble = "R2 B L' F R"
    cube.rotate(scramble)
    cube.display_cube()

    solved_cube = Cube("UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD")
    solved_pieces = [12, 13, 14, 15, 16, 17, 21, 24, 41, 44, 45, 48, 51]
    solver = (solved_cube, solved_pieces)

    solution = solve_iidfs(solver, cube, 5)

    if solution:
        print("Solution found:" + solution)
        cube.rotate(solution)
        cube.display_cube()
    else:
        print("No solution found within depth limit.")

if __name__ == "__main__":
    main()

