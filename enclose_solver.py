"""
Solver for enclose.horse puzzle "Unlucky" - Day 62
Level ID: -WNG4b, 9x9 grid, Wall Budget: 8

Uses Integer Linear Programming (ILP) via PuLP with distance-based
anti-cycle constraints to correctly model reachability.
"""

import pulp
from collections import deque

# Grid definition from screenshot analysis
# ~ = water, . = grass, H = horse, C = cherry, S = bee swarm
GRID = [
    ['~', '~', '.', '.', '.', '.', '.', '~', '~'],
    ['~', '.', '.', '.', '~', '.', '.', 'S', '~'],
    ['.', '.', 'S', '.', '.', '.', 'C', '.', '.'],
    ['.', '.', '.', '.', '~', '.', '.', '.', '.'],
    ['.', '~', '.', '.', '~', '.', '.', '~', '.'],
    ['~', '.', '~', '.', '.', 'H', '.', '~', '~'],
    ['.', '.', '.', '.', 'C', '.', '.', '.', '~'],
    ['~', '.', '.', '~', '.', '~', '.', 'S', '~'],
    ['~', '~', '.', '~', '~', '~', '.', '~', '~'],
]

ROWS = len(GRID)
COLS = len(GRID[0])
WALL_BUDGET = 8
M = ROWS + COLS  # Big-M constant


def is_water(r, c):
    return GRID[r][c] == '~'


def is_edge(r, c):
    return r == 0 or r == ROWS - 1 or c == 0 or c == COLS - 1


def neighbors(r, c):
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            result.append((nr, nc))
    return result


def tile_value(r, c):
    """Score contribution if this tile is enclosed."""
    t = GRID[r][c]
    if t == 'C':
        return 4   # 1 base + 3 cherry bonus
    elif t == 'S':
        return -4  # 1 base - 5 bee penalty
    else:
        return 1   # grass or horse


def solve():
    horse_pos = None
    for r in range(ROWS):
        for c in range(COLS):
            if GRID[r][c] == 'H':
                horse_pos = (r, c)
                break

    if horse_pos is None:
        print("ERROR: No horse found in grid!")
        return

    print(f"Horse at: {horse_pos}")
    print(f"Grid size: {ROWS}x{COLS}")
    print(f"Wall budget: {WALL_BUDGET}")

    # Identify non-water tiles and categorize
    non_water = []
    edge_tiles = []
    interior_tiles = []
    for r in range(ROWS):
        for c in range(COLS):
            if not is_water(r, c):
                non_water.append((r, c))
                if is_edge(r, c):
                    edge_tiles.append((r, c))
                else:
                    interior_tiles.append((r, c))

    print(f"Non-water tiles: {len(non_water)} ({len(edge_tiles)} edge, {len(interior_tiles)} interior)")

    # Create ILP problem
    prob = pulp.LpProblem("EncloseHorse", pulp.LpMaximize)

    # --- Decision variables ---

    # w[r,c] = 1 if we place a wall at (r,c)
    w = {}
    for r, c in non_water:
        if (r, c) == horse_pos:
            continue  # Can't wall the horse
        w[r, c] = pulp.LpVariable(f"w_{r}_{c}", cat="Binary")

    # e[r,c] = 1 if tile (r,c) is escapable (reachable from edge)
    e = {}
    for r, c in non_water:
        e[r, c] = pulp.LpVariable(f"e_{r}_{c}", cat="Binary")

    # D[r,c] = distance to edge for escapable tiles (0 for edge, >=1 for interior)
    D = {}
    for r, c in non_water:
        D[r, c] = pulp.LpVariable(f"D_{r}_{c}", lowBound=0, upBound=M, cat="Integer")

    # y[r,c,nr,nc] = 1 if tile (r,c) escapes through neighbor (nr,nc)
    # Only for non-edge tiles
    y = {}
    for r, c in interior_tiles:
        for nr, nc in neighbors(r, c):
            if not is_water(nr, nc):
                y[r, c, nr, nc] = pulp.LpVariable(f"y_{r}_{c}_{nr}_{nc}", cat="Binary")

    # z[r,c] = enclosed indicator (linearized product of (1-e)*(1-w))
    z = {}
    for r, c in non_water:
        z[r, c] = pulp.LpVariable(f"z_{r}_{c}", lowBound=0, upBound=1)

    # --- Constraints ---

    # 1. Wall budget
    prob += pulp.lpSum(w[r, c] for r, c in w) <= WALL_BUDGET, "WallBudget"

    # 2. Horse must be enclosed (not escapable)
    prob += e[horse_pos] == 0, "HorseEnclosed"

    # 3. Walled tiles can't be escapable: e <= 1 - w
    for r, c in non_water:
        if (r, c) in w:
            prob += e[r, c] <= 1 - w[r, c], f"WallBlock_{r}_{c}"

    # 4. Edge tiles: if not walled, they're escapable
    for r, c in edge_tiles:
        if (r, c) in w:
            prob += e[r, c] >= 1 - w[r, c], f"EdgeEsc_{r}_{c}"
        else:
            prob += e[r, c] == 1, f"EdgeEsc_{r}_{c}"

    # 5. Forward propagation: if neighbor escapable and tile not walled, tile is escapable
    for r, c in non_water:
        w_val = w.get((r, c), 0)
        for nr, nc in neighbors(r, c):
            if not is_water(nr, nc):
                prob += e[r, c] >= e[nr, nc] - w_val, f"FwdProp_{r}_{c}_{nr}_{nc}"

    # 6. Distance constraints for edge tiles: if escapable, D = 0
    for r, c in edge_tiles:
        prob += D[r, c] <= M * (1 - e[r, c]), f"EdgeDist_{r}_{c}"

    # 7. Anti-cycle: non-edge escapable tiles must have a predecessor
    for r, c in interior_tiles:
        nw_neighbors = [(nr, nc) for nr, nc in neighbors(r, c) if not is_water(nr, nc)]

        # If escapable, exactly one predecessor
        y_vars = [y[r, c, nr, nc] for nr, nc in nw_neighbors if (r, c, nr, nc) in y]
        if y_vars:
            prob += pulp.lpSum(y_vars) == e[r, c], f"Pred_{r}_{c}"
        else:
            # No non-water neighbors means can't be escapable (isolated)
            prob += e[r, c] == 0, f"Isolated_{r}_{c}"

        # Predecessor constraints
        for nr, nc in nw_neighbors:
            if (r, c, nr, nc) in y:
                yvar = y[r, c, nr, nc]
                # Predecessor must be escapable
                prob += yvar <= e[nr, nc], f"PredEsc_{r}_{c}_{nr}_{nc}"
                # Distance must increase: D[i,j] >= D[predecessor] + 1 when y = 1
                prob += D[r, c] >= D[nr, nc] + 1 - M * (1 - yvar), f"DistInc_{r}_{c}_{nr}_{nc}"

    # 8. Interior escapable tiles have D >= 1
    for r, c in interior_tiles:
        prob += D[r, c] >= e[r, c], f"IntDist_{r}_{c}"

    # 9. Linearization of z = (1-e)*(1-w) for enclosed indicator
    for r, c in non_water:
        w_val = w.get((r, c), 0)
        prob += z[r, c] <= 1 - e[r, c], f"Zub_e_{r}_{c}"
        prob += z[r, c] <= 1 - w_val, f"Zub_w_{r}_{c}"
        prob += z[r, c] >= 1 - e[r, c] - w_val, f"Zlb_{r}_{c}"

    # --- Objective: maximize score ---
    prob += pulp.lpSum(tile_value(r, c) * z[r, c] for r, c in non_water), "Score"

    # Solve
    print("\nSolving...")
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=120))

    status = pulp.LpStatus[prob.status]
    print(f"Status: {status}")

    if status != "Optimal":
        print("No optimal solution found!")
        return

    score = pulp.value(prob.objective)
    print(f"\nILP Optimal Score: {int(round(score))}")

    # Extract wall placements
    walls_placed = []
    for r, c in w:
        if pulp.value(w[r, c]) > 0.5:
            walls_placed.append((r, c))

    print(f"\nWalls placed ({len(walls_placed)}):")
    for r, c in sorted(walls_placed):
        print(f"  Row {r}, Col {c} (was: {GRID[r][c]})")

    # Show ILP board
    print("\nILP solution board:")
    print_board(walls_placed, e, z, use_ilp=True)

    # BFS verification
    print("\n--- BFS Verification ---")
    bfs_score = verify_with_bfs(walls_placed)

    return walls_placed, bfs_score


def print_board(walls, e_vars=None, z_vars=None, use_ilp=False, escapable_set=None):
    wall_set = set(walls)
    print("  " + " ".join(str(c) for c in range(COLS)))
    for r in range(ROWS):
        row_str = f"{r} "
        for c in range(COLS):
            if is_water(r, c):
                row_str += "~ "
            elif (r, c) in wall_set:
                row_str += "W "
            elif use_ilp and z_vars and pulp.value(z_vars.get((r, c), 0)) > 0.5:
                t = GRID[r][c]
                row_str += {'H': 'H ', 'C': 'C ', 'S': 'B '}.get(t, '# ')
            elif not use_ilp and escapable_set and (r, c) not in escapable_set:
                t = GRID[r][c]
                row_str += {'H': 'H ', 'C': 'C ', 'S': 'B '}.get(t, '# ')
            else:
                row_str += ". "
        print(row_str)


def verify_with_bfs(walls):
    """Verify the score using BFS flood fill from edges."""
    wall_set = set(walls)

    # BFS from all edge non-water, non-wall tiles
    escapable = set()
    queue = deque()
    for r in range(ROWS):
        for c in range(COLS):
            if is_edge(r, c) and not is_water(r, c) and (r, c) not in wall_set:
                escapable.add((r, c))
                queue.append((r, c))

    while queue:
        r, c = queue.popleft()
        for nr, nc in neighbors(r, c):
            if (nr, nc) not in escapable and not is_water(nr, nc) and (nr, nc) not in wall_set:
                escapable.add((nr, nc))
                queue.append((nr, nc))

    # Count enclosed tiles
    enclosed = []
    for r in range(ROWS):
        for c in range(COLS):
            if not is_water(r, c) and (r, c) not in wall_set and (r, c) not in escapable:
                enclosed.append((r, c))

    horse_pos = None
    for r in range(ROWS):
        for c in range(COLS):
            if GRID[r][c] == 'H':
                horse_pos = (r, c)

    horse_enclosed = horse_pos in enclosed
    print(f"Horse enclosed: {horse_enclosed}")

    score = 0
    base_tiles = 0
    cherry_bonus = 0
    bee_penalty = 0
    for r, c in enclosed:
        t = GRID[r][c]
        base_tiles += 1
        if t == 'C':
            cherry_bonus += 3
        elif t == 'S':
            bee_penalty += 5

    score = base_tiles + cherry_bonus - bee_penalty
    print(f"Enclosed tiles: {base_tiles}")
    print(f"Cherry bonus: +{cherry_bonus}")
    print(f"Bee penalty: -{bee_penalty}")
    print(f"BFS verified score: {score}")

    print("\nBFS board:")
    print_board(walls, escapable_set=escapable)

    return score


if __name__ == "__main__":
    solve()
