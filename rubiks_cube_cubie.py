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
            self.display_cube()

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
                [5, 28],  # UR
                [7, 19],  # UF
                [3, 10],  # UL
                [1, 37],  # UB
                [50, 34], # DR
                [46, 25], # DF
                [48, 16], # DL
                [52, 43], # DB
                [23, 30], # FR
                [21, 14], # FL
                [41, 12], # BL
                [39, 32], # BR
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

            print("".join(facelets))
            print(len(facelets))

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

def main():
    cube = Cube()
    cube.display_cube()
    cube.rotate("R U B F R B L")
    cube.display_cube()


if __name__ == "__main__":
    main()

