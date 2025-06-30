MOVES = {
    'U': {
        "corners": [(0, 3), (3, 2), (2, 1), (1, 0)],   
        "corner_orient": {},
        "edges": [(1, 0), (2, 1), (3, 2), (0, 3)],  # (dst, src)
        "edge_flip": {}
    },
    'D': {
        "corners": [(4, 5), (5, 6), (6, 7), (7, 4)],
        "corner_orient": {},
        "edges": [(4, 5), (5, 6), (6, 7), (7, 4)],
        "edge_flip": {}
    },
    'L': {
        "corners": [(5, 1), (6, 5), (2, 6), (1, 2)],
        "corner_orient": {1: 2, 2: 1, 6: 2, 5: 1},
        "edges": [(2, 10), (10, 6), (6, 9), (9, 2)],
        "edge_flip": {}
    },
    'R': {
        "corners": [(0, 4), (4, 7), (7, 3), (3, 0)],
        "corner_orient": {0: 1, 3: 2, 7: 1, 4: 2},
        "edges": [(0, 8), (8, 4), (4, 11), (11, 0)],
        "edge_flip": {}
    },
    'F': {
        "corners": [(0, 1), (1, 5), (5, 4), (4, 0)],
        "corner_orient": {0: 2, 1: 1, 5: 2, 4: 1},
        "edges": [(1, 9), (9, 5), (5, 8), (8, 1)],
        "edge_flip": {1: 1, 9: 1, 5: 1, 8: 1}
    },
    'B': {
        "corners": [(2, 3), (3, 7), (7, 6), (6, 2)],
        "corner_orient": {2: 2, 3: 1, 7: 2, 6: 1},
        "edges": [(3, 11), (11, 7), (7, 10), (10, 3)],
        "edge_flip": {3: 1, 11: 1, 7: 1, 10: 1}
    },
    'U2': {
        "corners": [],
        "corner_orient": {},
        "edges": [],
        "edge_flip": {}
    },
    'D2': {
        "corners": [],
        "corner_orient": {},
        "edges": [],
        "edge_flip": {}
    },
    'L2': {
        "corners": [],
        "corner_orient": {1: 2, 2: 1, 5: 1, 6: 2},
        "edges": [],
        "edge_flip": {}
    },
    'R2': {
        "corners": [],
        "corner_orient": {0: 2, 3: 1, 4: 1, 7: 2},
        "edges": [],
        "edge_flip": {}
    },
    'F2': {
        "corners": [],
        "corner_orient": {0: 2, 1: 1, 4: 1, 5: 2},
        "edges": [],
        "edge_flip": {1: 0, 5: 0, 8: 0, 9: 0}
    },
    'B2': {
        "corners": [],
        "corner_orient": {2: 2, 3: 1, 6: 1, 7: 2},
        "edges": [],
        "edge_flip": {3: 0, 7: 0, 10: 0, 11: 0}
    }
}
