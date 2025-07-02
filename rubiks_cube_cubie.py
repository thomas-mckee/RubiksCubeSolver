from cubie_move_maps import MOVES

class Cube:
    def __init__(self):
        self.corners = [(i, 0) for i in range(8)]   # (piece, orientation)
        self.edges = [(i, 0) for i in range (12)]   # (piece, flip)
        self.facelet = "UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD"

    def copy(self):
        new_cube = Cube()
        new_cube.corners = list(self.corners)
        new_cube.edges = list(self.edges)
        return new_cube
    
    def rotate(self, moves):
        for move in moves.split(" "):
            if move:
                move_def = MOVES[move]
                self.apply_corner_move(move_def["corners"], move_def.get("corner_orient", {}))
                self.apply_edge_move(move_def["edges"], move_def.get("edge_flip", {}))

    def apply_corner_move(self, perm, twists):
        old = self.corners.copy()
        for i, j in perm:
            piece, orient = old[j]
            twist = twists.get(j, 0)
            self.corners[i] = (piece, (orient + twist) % 3)
    
    def apply_edge_move(self, perm, flips):
        old = self.edges.copy()
        for i, j in perm:
            piece, flip = old[j]
            extra = flips.get(j, 0)
            self.edges[i] = (piece, (flip + extra) % 2)

    def is_solved(self):
        return all(p == i and o == 0 for i, (p, o) in enumerate(self.corners)) and all(p == i and f == 0 for i, (p, f) in enumerate(self.edges))
    
    def display_cube(self):
        """Prints the cube in 2D net layout to the console with color emojis."""
        def cubie_to_facelets(cubie):
            facelets = [''] * 54

            # Corner facelet positions (standard layout)
            corner_facelet_pos = [
                [8,  27,  20],  # URF
                [6,  18,  11],  # UFL
                [0,   9,  38],  # ULB
                [2,  36,  29],  # UBR
                [47, 26,  33],  # DFR
                [45, 17,  24],  # DLF
                [51, 44, 15],  # DBL
                [53, 35,  42],  # DRB
            ]

            # These are the colors of the corner cubies in their default position
            corner_colors = [
                ['U', 'R', 'F'],
                ['U', 'F', 'L'],
                ['U', 'L', 'B'],
                ['U', 'B', 'R'],
                ['D', 'F', 'R'],
                ['D', 'L', 'F'],
                ['D', 'B', 'L'],
                ['D', 'R', 'B'],
            ]

            for i in range(8):
                cubie_id, ori = cubie.corners[i]
                for j in range(3):
                    facelet_index = corner_facelet_pos[i][j]
                    color = corner_colors[cubie_id][(j - ori) % 3]
                    facelets[facelet_index] = color

            # Edge facelet positions
            edge_facelet_pos = [
                [5, 28],  # UR 0
                [7, 19],  # UF 1
                [3, 10],  # UL 2
                [1, 37],  # UB 3
                [50, 34], # DR 4
                [46, 25], # DF 5
                [48, 16], # DL 6
                [52, 43], # DB 7
                [23, 30], # FR 8
                [21, 14], # FL 9
                [41, 12], # BL 10
                [39, 32], # BR 11
            ]

            edge_colors = [
                ['U', 'R'],
                ['U', 'F'],
                ['U', 'L'],
                ['U', 'B'],
                ['D', 'R'],
                ['D', 'F'],
                ['D', 'L'],
                ['D', 'B'],
                ['F', 'R'],
                ['F', 'L'],
                ['B', 'L'],
                ['B', 'R'],
            ]

            for i in range(12):
                cubie_id, flip = cubie.edges[i]
                for j in range(2):
                    facelet_index = edge_facelet_pos[i][j]
                    color = edge_colors[cubie_id][(j - flip) % 2]
                    facelets[facelet_index] = color

            # Center facelets are fixed
            center_indices = [4, 13, 22, 31, 40, 49]
            center_colors = ['U', 'L', 'F', 'R', 'B', 'D']
            for idx, col in zip(center_indices, center_colors):
                facelets[idx] = col

            return ''.join(facelets)
        
        self.facelet = cubie_to_facelets(self)
        s = self.facelet

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

class Thistlethwaite_Solver:
    def __init__(self, cube):
        self.MOVES_G0 = MOVES#["U", "D", "F", "B", "L", "R"]
        self.MOVES_G1 = ["U", "D", "F2", "B2", "L", "L'", "L2", "R", "R'", "R2"]
        self.MOVES_G2 = ["U2", "D2", "F2", "B2", "L", "R"]
        self.MOVES_G3 = ["U2", "D2", "L2", "R2", "F2", "B2"]
        self.cube = cube.copy()
        self.solution = []
        self.g3_corner_table = self.generate_g3_corner_table()
    
    def in_g1(self, cube):
        return all(f == 0 for _, f in cube.edges)  

    def in_g2(self, cube):
        return (self.in_g1(cube) and all(o == 0 for _, o in cube.corners) and self.check_E_slice(cube))

    def in_g3(self, cube):
        return (
            self.in_g2(cube) and
            self.corner_permutation_key(cube) in self.g3_corner_table and
            self.check_UD_edges(cube)
        )


    def is_solved(self, cube):
        return cube.is_solved()
    
    def check_E_slice(self, cube):
        e_slice_ids = [8, 9, 10, 11]
        return all(cube.edges[i][0] in e_slice_ids for i in range(8, 12))
    
    def check_UD_edges(self, cube):
        UD_EDGES = [0,1,2,3,4,5,6,7]
        # Check current edges in U and D positions are U and D edges
        for i in UD_EDGES:
            if cube.edges[i][0] not in UD_EDGES:
                return False
        return True
    
    def generate_g3_corner_table(self):
        from collections import deque

        visited = set()
        queue = deque()

        # Start from solved cube
        solved = Cube()
        start_key = self.corner_permutation_key(solved)
        visited.add(start_key)
        queue.append(solved)

        while queue:
            cube = queue.popleft()
            for move in self.MOVES_G3:
                new_cube = cube.copy()
                new_cube.rotate(move)
                key = self.corner_permutation_key(new_cube)
                if key not in visited:
                    visited.add(key)
                    queue.append(new_cube)

        return visited
    
    def corner_permutation_key(self, cube):
        return tuple(p for (p, _) in cube.corners)

    
    def cube_key(self, cube):
        # Could be corners + edges for uniqueness
        return str(cube.corners) + str(cube.edges)

    def dfs(self, cube, goal_test, move_set, solution, depth_remaining, visited):
        if goal_test(cube):
            return solution
        if depth_remaining == 0:
            return None

        for move in move_set:
            next_cube = cube.copy()
            next_cube.rotate(move)
            key = self.cube_key(next_cube)

            if key not in visited:
                visited.add(key)
                result = self.dfs(next_cube, goal_test, move_set, solution + [move], depth_remaining - 1, visited)
                if result is not None:
                    return result
        return None


    def iddfs(self, goal_test, move_set, max_depth=10):
        for depth in range(max_depth + 1):
            visited = set()
            print(f"Trying depth {depth}...")
            result = self.dfs(self.cube.copy(), goal_test, move_set, [], depth, visited)
            if result is not None:
                return result
        return []  # No solution found within depth

    
    def bfs(self, goal_test, move_set):
        from collections import deque
        visited = set()
        queue = deque()
        queue.append((self.cube.copy(), []))
        visited.add(self.cube_key(self.cube))

        while queue:
            cube, path = queue.popleft()
            if goal_test(cube):
                return path

            for move in move_set:
                next_cube = cube.copy()
                next_cube.rotate(move)
                key = self.cube_key(next_cube)
                if key not in visited:
                    visited.add(key)
                    queue.append((next_cube, path + [move]))

        return []  # Should not reach here if implemented correctly



    def solve(self, use_dfs=False, max_depth=2):
        for phase in range(4):
            moveset = [self.MOVES_G0, self.MOVES_G1, self.MOVES_G2, self.MOVES_G3][phase]
            goal_test = [self.in_g1, self.in_g2, self.in_g3, self.is_solved][phase]

            if use_dfs:
                phase_solution = self.iddfs(goal_test, moveset, max_depth)
            else:
                phase_solution = self.bfs(goal_test, moveset)

            if not phase_solution:
                print(f"Phase G{phase+1} failed to solve.")
                break
            
            self.solution.extend(phase_solution)
            self.cube.rotate(" ".join(phase_solution))
            print(f"G{phase+1} complete ({len(phase_solution)} moves): {' '.join(phase_solution)}")
            self.cube.display_cube()



def main():
    cube = Cube()
    cube.rotate("U2 B2 R' L' B2 L' U F R2 U2 L2 F R' F U D2 L F U' L R F2 L' R' B R2 U F R2 L2")
    cube.display_cube()

    solver = Thistlethwaite_Solver(cube)
    solver.solve()
    print("Solution:", solver.solution)

    



if __name__ == "__main__":
    main()

