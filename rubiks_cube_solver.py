from move_maps import MOVES
from timeit import default_timer
import random
import matplotlib.pyplot as plt

class Cube:
    def __init__(self, state=None, is_if=False):
        if state:
            self.state = list(state)
        else:
            self.state = list('UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD')
                            
    def rotate(self, moves):
        # Iterate over all moves in chain
        for move in moves.split(" "):
            if move != '':
                move_dict = MOVES[move.upper()]
                old_state = self.state.copy()
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
            'X': '⬛',
            'o': '🟫',
            'x': '🟪',
            'y': '🔳'
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

def g0_mask_cube(if_cube, mask):
    state = []
    for i in if_cube.state:
        if i in mask:
            state.append('o')
        else:
            state.append("X")
    cube = Cube("".join(state))
    return cube

def g1_mask_cube(if_cube, co_pieces, eo_ud_pieces, eo_e_pieces):
    state = []
    for i in if_cube.state:
        if i in co_pieces or i in eo_ud_pieces:
            state.append("x")
        elif i in eo_e_pieces:
            state.append("y")
        else:
            state.append("X")
    cube = Cube("".join(state))
    return cube

def g2_corner_mask(if_cube, corners):
    state = []
    for i in if_cube.state:
        if i in corners:
            state.append(ifcube_idx_to_fcube_face(i))
        else:
            state.append("X")
    cube = Cube("".join(state))
    return cube

def g2_mask_cube(if_cube):
    # Map each face to its starting index
    face_base = {'U': 0, 'L': 9, 'F': 18, 'R': 27, 'B': 36, 'D': 45}

    # Define corner permutation positions (face-relative)
    cp_facelets = [0, 2, 6, 8]  # edges of the face (not centers)
    cp_faces = ['U', 'D', 'F', 'B', 'L', 'R']
    cp_pieces = [face_base[f] + i for f in cp_faces for i in cp_facelets]

    # Define edge permutation positions on F/B/L/R faces only
    ep_facelets = [1, 3, 5, 7]  # side edge stickers
    ep_faces = ['F', 'B', 'L', 'R']
    ep_pieces = [face_base[f] + i for f in ep_faces for i in ep_facelets]

    # Function to simplify opposite face color collapse
    def collapse_face(f):
        return {'B': 'F', 'L': 'R'}.get(f, f)

    # Create the masked state
    masked = []
    for idx in if_cube.state:
        face = "ULFRBD"[idx // 9]  # get face from index
        if idx in cp_pieces:
            masked.append(face)
        elif idx in ep_pieces:
            masked.append(collapse_face(face))
        else:
            masked.append("X")
    return Cube(masked)

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
        #print(f"Depth {i} - States {len(pruning_table)}")
    return pruning_table

def solve_dfs_with_pruning(solver, cube, solution, depth_remaining):
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
        result = solve_dfs_with_pruning(solver, new_cube, solution, depth_remaining - 1)
        if result is not None:
            return result
        solution.pop()
    return None

def solve_iidfs_pruning(solver, cube, depth_limit):
    for depth in range(1, depth_limit + 1):
        solution = []
        result = solve_dfs_with_pruning(solver, cube.copy(), solution, depth)
        if result is not None:
            return result
    return None

def fb_is_solved(cube):
    fb_pieces = [12,13,14,15,16,17,21,24,41,44,45,48,51]
    return all(cube.state[i] == cube.index_facelet_cube(i) for i in fb_pieces)

def g0_is_solved(cube):
    eo_pieces = [1,3,5,7,21,23,39,41,46,48,50,52]
    return all(cube.state[i] == 'o' for i in eo_pieces)

def g1_is_solved(cube):
    co_pieces = [0, 2, 6, 8, 45, 47, 51, 53]
    eo_ud_pieces = [1, 3, 5, 7, 46, 48, 50, 52]
    eo_e_pieces = [21, 23, 39, 41]

    return (
        all(cube.state[i] == 'x' for i in co_pieces + eo_ud_pieces)
        and all(cube.state[j] == 'y' for j in eo_e_pieces)
    )

def g3_is_solved(cube):
    solved_cube = 'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD'
    return "".join(cube.state) == solved_cube

def get_random_scramble(moveset, k=20):
    scramble = []
    last_move = moveset[0]

    for _ in range(k):
        while True:
            move = random.choice(moveset)
            if move[0] != last_move[0]:
                scramble.append(move)
                last_move = move
                break
    return " ".join(scramble)

g0_moves = ["U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "L", "L'", "L2", "R", "R'", "R2"]
g1_moves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F2", "B2"]
g2_moves = ["U", "D", "L2", "R2", "F2", "B2"]
g3_moves = ["U2", "D2", "L2", "R2", "F2", "B2"]

g0_depth = 9
g1_depth = 8
g2_depth = 8
g3_depth = 8

# Precompute solved reference cube
solved_if_cube = Cube([i for i in range(54)])
solved_cube = Cube()

# G0 pruning table (EO)
eo_pieces = [1,3,5,7,21,23,39,41,46,48,50,52]
g0_masked_cube = g0_mask_cube(solved_if_cube, eo_pieces)
g0_table = gen_pruning_table(["".join(g0_masked_cube.state)], g0_depth, g0_moves)

# G1 pruning table (CO + EO split)
co_pieces = [0,2,6,8,45,47,51,53]
eo_ud_pieces = [1,3,5,7,46,48,50,52]
eo_e_pieces = [21,23,39,41]
g1_masked_cube = g1_mask_cube(solved_if_cube, co_pieces, eo_ud_pieces, eo_e_pieces)
g1_table = gen_pruning_table(["".join(g1_masked_cube.state)], g1_depth, g1_moves)

# G2 pruning table
g2_masked_cube = g2_mask_cube(solved_if_cube)
g2_solved_states = list(gen_pruning_table(["".join(g2_masked_cube.state)], 10, [
    "U2", "D2", "F2", "B2", "L2", "R2"
]).keys())
g2_table = gen_pruning_table(g2_solved_states, g2_depth, g2_moves)

# G3 pruning table
g3_table = gen_pruning_table(["".join(solved_cube.state)], g3_depth, g3_moves)

def thistlethwaite(g0_table, g1_table, g2_table, g2_solved_states, g3_table):

    scramble = get_random_scramble(g0_moves, 25)

    cube = Cube()
    cube.rotate(scramble)

    g0_masked_cube = g0_mask_cube(solved_if_cube, [1,3,5,7,21,23,39,41,46,48,50,52])
    g0_masked_cube.rotate(scramble)

    g0_solver = Solver(g0_is_solved, g0_moves, g0_table, g0_depth)
    t1 = default_timer()
    g1_solution = solve_iidfs_pruning(g0_solver, g0_masked_cube, 14)

    if not g1_solution:
        return (0, 0)

    cube.rotate(str(g1_solution))

    g1_masked_cube = g1_mask_cube(solved_if_cube,
                                  [0,2,6,8,45,47,51,53],
                                  [1,3,5,7,46,48,50,52],
                                  [21,23,39,41])
    g1_masked_cube.rotate(scramble + " " + str(g1_solution))

    g1_solver = Solver(g1_is_solved, g1_moves, g1_table, g1_depth)
    g2_solution = solve_iidfs_pruning(g1_solver, g1_masked_cube, 14)

    if not g2_solution:
        return (0, 0)

    cube.rotate(str(g2_solution))

    g2_masked_cube = g2_mask_cube(solved_if_cube)
    g2_masked_cube.rotate(scramble + " " + str(g1_solution) + " " + str(g2_solution))

    def g2_is_solved(cube):
        return "".join(cube.state) in g2_solved_states

    g2_solver = Solver(g2_is_solved, g2_moves, g2_table, g2_depth)
    g3_solution = solve_iidfs_pruning(g2_solver, g2_masked_cube, 18)

    if not g3_solution:
        return (0, 0)

    cube.rotate(str(g3_solution))

    g3_solver = Solver(g3_is_solved, g3_moves, g3_table, g3_depth)
    g4_solution = solve_iidfs_pruning(g3_solver, cube, 17)
    t2 = default_timer()

    if not g4_solution:
        return (0, 0)

    cube.rotate(str(g4_solution))

    full_solution = str(g1_solution) + " " + str(g2_solution) + " " + str(g3_solution) + " " + str(g4_solution)
    print("\nSolver found solution: ", full_solution, "["+str(len(full_solution.split(" ")))+"]")
    print(f"Total Time: {t2 - t1}s")
    return ((t2 - t1) * 1000, len(full_solution.split(" ")))

# def thistlethwaite():
# ### G0 -> G1 ###
#     g0_moves = ["U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2", "L", "L'", "L2", "R", "R'", "R2"]

#     g0_pruning_depth = 7

#     scramble = get_random_scramble(g0_moves)

#     cube = Cube()
    
#     #print("SCRAMBLE")
#     #print(scramble)
#     cube.rotate(scramble)
#     #cube.display_cube()
    

#     if_state = []
#     for i in range(54):
#         if_state.append(i)
#     solved_if_cube = Cube(if_state)

#     eo_pieces = [1,3,5,7,21,23,39,41,46,48,50,52]
#     g0_masked_cube = g0_mask_cube(solved_if_cube, eo_pieces)

#     g0_pruning_table = gen_pruning_table(["".join(g0_masked_cube.state)], g0_pruning_depth, g0_moves)

#     g0_masked_cube.rotate(scramble)

#     g0_solver = Solver(g0_is_solved, g0_moves, g0_pruning_table, g0_pruning_depth)

#     t1 = default_timer()
#     g1_solution = solve_iidfs_pruning(g0_solver, g0_masked_cube, 10)

#     if g1_solution:
#         #print("Reduce to G1:")
#         #print(g1_solution)
#         cube.rotate(str(g1_solution))
#         #cube.display_cube()
#     else:
#         print("No solution found.")
#         return (0, 0)

#     # ### G1 -> G2 ###
#     g1_moves = ["U", "U'", "U2", "D", "D'", "D2", "L", "L'", "L2", "R", "R'", "R2", "F2", "B2"]
#     g1_pruning_depth = 5

#     co_pieces = [0,2,6,8,45,47,51,53]
#     eo_ud_pieces = [1,3,5,7,46,48,50,52]
#     eo_e_pieces = [21,23,39,41]

#     g1_masked_cube = g1_mask_cube(solved_if_cube, co_pieces, eo_ud_pieces, eo_e_pieces)

#     g1_pruning_table = gen_pruning_table(["".join(g1_masked_cube.state)], g1_pruning_depth, g1_moves)

#     g1_masked_cube.rotate((scramble + " " + str(g1_solution)).rstrip())

#     g1_solver = Solver(g1_is_solved, g1_moves, g1_pruning_table, g1_pruning_depth)

#     g2_solution = solve_iidfs_pruning(g1_solver, g1_masked_cube, 10)

#     if g2_solution:
#         #print("Reduce to G2:")
#         #print(g2_solution)
#         cube.rotate(str(g2_solution))
#         #cube.display_cube()
#     else:
#         print("No solution found.")
#         return (0, 0)


#     ### G2 -> G3 ###
#     g2_moves = ["U", "D", "L2", "R2", "F2", "B2"]
#     g2_pruning_depth = 5

#     corners = [0,2,6,8,9,11,15,17,18,20,24,26,27,29,33,35,36,38,42,44,45,47,51,53]

#     #g2_corner_table = gen_pruning_table(["".join(g2_corner_mask(solved_if_cube, corners).state)], 10, ["U2", "D2", "F2", "B2", "L2", "R2"])
#     g2_masked_cube = g2_mask_cube(solved_if_cube)

#     solved_states_viewed_in_g2 = list(gen_pruning_table(["".join(g2_masked_cube.state)], 10, ["U2", "D2", "F2", "B2", "L2", "R2"]).keys())
#     g2_pruning_table = gen_pruning_table(solved_states_viewed_in_g2, g2_pruning_depth, g2_moves)
#     g2_masked_cube.rotate((scramble + " " + str(g1_solution) + " " + str(g2_solution)).rstrip())

#     def g2_is_solved(cube):
#         state = "".join(cube.state)
#         return state in solved_states_viewed_in_g2


#     g2_solver = Solver(g2_is_solved, g2_moves, g2_pruning_table, g2_pruning_depth)

#     g3_solution = solve_iidfs_pruning(g2_solver, g2_masked_cube, 14)

#     if g3_solution:
#         #print("Reduce to G3:")
#         #print(g3_solution)
#         cube.rotate(str(g3_solution))
#         #cube.display_cube()
#     else:
#         print("No solution found.")
#         return (0, 0)

#     ### G3 -> G4 ###
#     solved_cube = Cube()

#     g3_moves = ["U2", "D2", "L2", "R2", "F2", "B2"]
#     g3_pruning_depth = 6

#     g3_pruning_table = gen_pruning_table(["".join(solved_cube.state)], g3_pruning_depth, g3_moves)

#     g3_solver = Solver(g3_is_solved, g3_moves, g3_pruning_table, g3_pruning_depth)

#     g4_solution = solve_iidfs_pruning(g3_solver, cube, 14)
#     t2 = default_timer()
    
#     if g4_solution:
#         #print("Reduce to solved:")
#         #print(g4_solution)
#         cube.rotate(str(g4_solution))
#         #cube.display_cube()
#     else:
#         print("No solution found.")
#         return (0, 0)

#     full_solution = str(g1_solution) + " " + str(g2_solution) + " " + str(g3_solution) + " " + str(g4_solution)
#     print("\nSolver found solution: ", full_solution, "["+str(len(full_solution.split(" ")))+"]")
#     print(f"Total Time: {t2 - t1}s")

#     return ((t2 - t1) * 1000, len(full_solution.split(" ")))

def simulate_solves(num_solves):
    times = []
    num_moves = []
    num_solved = 0

    for i in range(num_solves):
        if i % 100 == 0:
            print(f"{i}/{num_solves}")
        time, moves = thistlethwaite(g0_table, g1_table, g2_table, g2_solved_states, g3_table)
        if moves:
            num_solved += 1
        times.append(time)
        num_moves.append(moves)

    print(f"{num_solved*100/num_solves}% solved")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.hist(times, bins=15, color='skyblue', edgecolor='black')
    ax1.set_title("Distribution of Solve Times")
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Frequency")

    ax2.hist(num_moves, bins=15, color='salmon', edgecolor='black')
    ax2.set_title("Distribution of Move Counts")
    ax2.set_xlabel("Number of Moves")
    ax2.set_ylabel("Frequency")

    plt.tight_layout()
    plt.show()


def main():
    simulate_solves(10000)

if __name__ == "__main__":
    main()

