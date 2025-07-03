from move_maps import MOVES
from timeit import default_timer

class Cube:
    def __init__(self, state=None, is_if=False):
        if state:
            self.state = list(state)
        else:
            self.state = list('UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD')
                            
    def rotate(self, moves):
        # Iterate over all moves in chain
        for move in moves.split(" "):
            # Get move dictionary
            move_dict = MOVES[move.upper()]
            
            # Save old cube state
            old_state = self.state.copy()

            # Update cube with each move
            for src, dst in move_dict.items():
                self.state[dst] = old_state[src]

    def is_solved(self, solver=None):
        """
        Checks if the cube is in a solved state.

        If no solver is provided, it checks whether each face of the cube 
        consists of a uniform color (standard solved state).

        If a solver is provided, it uses the custom reference cube state and 
        specific piece positions to determine whether the cube is solved 
        according to those conditions.

        Args:
            solver (tuple, optional): A tuple of (solved_cube, solved_pieces), 
                where `solved_cube` is a Cube object representing the solved state, 
                and `solved_pieces` is a list of indices to check against.

        Returns:
            bool: True if the cube is solved according to the specified criteria, 
                  False otherwise.
        """
        if solver:
            solved_cube = solver[0]
            solved_pieces = solver[1]
            for pos in solved_pieces:
                if self.state[pos] != solved_cube.state[pos]:
                    return False
            return True
        else:
            return all(self.state[i] == self.state[i - i % 3] for i in range(54))
        
    def index_facelet_cube(self, idx):
        return "ULFRBD"[idx // 9]
    
    def get_mask(self, mask):
        masked_state = "".join(self.state[i] if i in mask else "X" for i in range(54))
        return Cube(masked_state)
    
    def copy(self):
        return Cube(self.state)
    
    def print_cube(self):
        print("".join(self.state))
        

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
            'X': '⬛'  
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

class Solver:
    def __init__(self, is_solved_fn, moves, pruning_table, pruning_depth):
        self.is_solved_fn = is_solved_fn
        self.moves = moves
        self.pruning_table = pruning_table
        self.pruning_depth = pruning_depth

    def is_solved(self, cube):
        return self.is_solved_fn(cube)


def solve_dfs(solver, cube, solution, depth_remaining):
    if solver.is_solved(cube): 
        return solution.strip()
    if depth_remaining == 0:
        return None

    for move in solver.moves:
        new_cube = cube.copy()
        new_cube.rotate(move)
        result = solve_dfs(
            solver, 
            new_cube,
            solution + " " + move, 
            depth_remaining - 1
        )
        if result is not None:
            return result 

    return None 


def solve_iidfs(solver, cube, depth_limit):
    for depth in range(depth_limit+1):
        solution = solve_dfs(solver, cube, "", depth)
        if solution is not None:
            return solution
    return None

def ifcube_idx_to_fcube_face(idx):
    return "ULFRBD"[idx // 9]


def mask_cube(if_cube, mask):
    state = []
    for i in if_cube.state:
        if i in mask:
            state.append(ifcube_idx_to_fcube_face(i))
        else:
            state.append("X")
    cube = Cube("".join(state))
    return cube

def gen_pruning_table(solved_states, depth, moveset):
    pruning_table = {}
    previous_frontier = solved_states[:]

    for state in solved_states:
        pruning_table[state] = 0

    for i in range(1, depth + 1):
        frontier = []
        for state in previous_frontier:
            for move in moveset:
                cube = Cube(state)
                cube.rotate(move)
                new_state = "".join(cube.state)
                if new_state not in pruning_table:
                    pruning_table[new_state] = i
                    frontier.append(new_state)
        previous_frontier = frontier
        print(f"Depth {i} - States {len(pruning_table)}")
    return pruning_table



def solve_dfs_with_pruning(solver, cube, solution, depth_remaining, mask):
    # Check if the cube is solved (mask for FB)
    if solver.is_solved(cube):
        return " ".join(solution)
    if depth_remaining == 0:
        return None

    # Mask the cube for pruning table lookup
    lower_bound = solver.pruning_table.get("".join(cube.state), solver.pruning_depth + 1)
    if lower_bound > depth_remaining:
        return None

    for move in solver.moves:
        if solution and move[0] == solution[-1][0]:
            continue  # Skip same-face moves
        new_cube = cube.copy()
        new_cube.rotate(move)
        solution.append(move)
        result = solve_dfs_with_pruning(solver, new_cube, solution, depth_remaining - 1, mask)
        if result is not None:
            return result
        solution.pop()
    return None

def solve_iidfs_pruning(solver, cube, depth_limit, mask):
    for depth in range(1, depth_limit + 1):
        solution = []
        result = solve_dfs_with_pruning(solver, cube.copy(), solution, depth, mask)
        if result is not None:
            return result
    return None





def fb_is_solved(cube):
    fb_pieces = [12,13,14,15,16,17,21,24,41,44,45,48,51]
    return all(cube.state[i] == cube.index_facelet_cube(i) for i in fb_pieces)

def main():
    mu_moves = ["M", "M'", "M2", "U", "U'", "U2"]
    htm_moves = ["U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "L", "L'", "L2", "R", "R'", "R2"]
    htmrwm_moves = ["U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "r", "r'", "r2", "R", "R'", "R2", "M", "M'", "M2"]
    fb_pruning_depth = 5
    

    cube = Cube()
    scramble = "U2 F2 D' F B2 L2 U' L' U' L2 B F' D2 F2 U' B2 L' F' D U' L' B2 L2 F B' D U' F' U2 D'"
    cube.rotate(scramble)
    cube.display_cube()

    if_state = []

    for i in range(54):
        if_state.append(i)
    if_cube = Cube(if_state)

    fb_pieces = [12,13,14,15,16,17,21,24,41,44,45,48,51]
    masked_cube = mask_cube(if_cube, fb_pieces)
    masked_cube.display_cube()

    fb_pruning_table = gen_pruning_table(["".join(masked_cube.state)], fb_pruning_depth, htm_moves)

    masked_cube.rotate(scramble)
    masked_cube.display_cube()

    fb_solver = Solver(fb_is_solved, htm_moves, fb_pruning_table, fb_pruning_depth)

    t1 = default_timer()
    solution = solve_iidfs_pruning(fb_solver, masked_cube, 10, fb_pieces)
    t2 = default_timer()


    if solution:
        print("Solution:", solution)
        masked_cube.rotate(solution)
        masked_cube.display_cube()
    else:
        print("No solution found.")

    print(f"Time Elapsed: {t2 - t1}s")

if __name__ == "__main__":
    main()

