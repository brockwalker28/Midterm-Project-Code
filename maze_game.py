import random
from collections import deque
import matplotlib.pyplot as plt


# Up, Right, Down, Left
DIRECTIONS = [
    (-1, 0),
    (0, 1),
    (1, 0),
    (0, -1)
]


def inside(maze, r, c):
    return 0 <= r < len(maze) and 0 <= c < len(maze[0])


def generate_maze(rows=15, cols=15):
    # Each cell has walls: [up, right, down, left]
    maze = [
        [[1, 1, 1, 1] for c in range(cols)]
        for r in range(rows)
    ]

    visited = {(0, 0)}
    stack = [(0, 0)]

    # Generate the main maze
    while stack:

        r, c = stack[-1]
        choices = []

        for i, (dr, dc) in enumerate(DIRECTIONS):

            nr = r + dr
            nc = c + dc

            if inside(maze, nr, nc) and (nr, nc) not in visited:
                choices.append((i, nr, nc))

        if not choices:
            stack.pop()
            continue

        direction, nr, nc = random.choice(choices)

        maze[r][c][direction] = 0
        maze[nr][nc][(direction + 2) % 4] = 0

        visited.add((nr, nc))
        stack.append((nr, nc))

    # Remove extra walls so the maze has loops
    for r in range(rows):
        for c in range(cols):

            for direction in [1, 2]:

                nr = r + DIRECTIONS[direction][0]
                nc = c + DIRECTIONS[direction][1]

                if inside(maze, nr, nc):

                    if maze[r][c][direction] == 1:

                        if random.random() < 0.12:

                            maze[r][c][direction] = 0
                            maze[nr][nc][(direction + 2) % 4] = 0

    return maze


def neighbors(maze, position):

    r, c = position
    result = []

    for direction, (dr, dc) in enumerate(DIRECTIONS):

        nr = r + dr
        nc = c + dc

        if inside(maze, nr, nc):

            if maze[r][c][direction] == 0:
                result.append((nr, nc))

    return result


def visible_cells(maze, player):

    visible = {player}

    r, c = player

    # Look in all four directions
    for direction, (dr, dc) in enumerate(DIRECTIONS):

        current = player

        while True:

            r, c = current
            nr = r + dr
            nc = c + dc

            if not inside(maze, nr, nc):
                break

            if maze[r][c][direction] == 1:
                break

            current = (nr, nc)
            visible.add(current)

            # Stop when reaching a turn or dead end
            exits = neighbors(maze, current)

            if len(exits) != 2:
                break

    return visible


def shortest_path(maze, start, goal):

    queue = deque([start])
    previous = {start: None}

    while queue:

        current = queue.popleft()

        if current == goal:

            path = []

            while current is not None:
                path.append(current)
                current = previous[current]

            return path[::-1]

        for next_cell in neighbors(maze, current):

            if next_cell not in previous:

                previous[next_cell] = current
                queue.append(next_cell)

    return []


def draw_local_view(maze, player, explored):

    visible = visible_cells(maze, player)

    radius = 4

    rows = len(maze)
    cols = len(maze[0])

    r1 = max(0, player[0] - radius)
    r2 = min(rows - 1, player[0] + radius)

    c1 = max(0, player[1] - radius)
    c2 = min(cols - 1, player[1] + radius)

    plt.figure(figsize=(7, 7))

    cells = visible | explored

    for r, c in cells:

        if not (r1 <= r <= r2 and c1 <= c <= c2):
            continue

        # Top wall
        if maze[r][c][0]:
            plt.plot(
                [c - 0.5, c + 0.5],
                [r - 0.5, r - 0.5],
                'k'
            )

        # Right wall
        if maze[r][c][1]:
            plt.plot(
                [c + 0.5, c + 0.5],
                [r - 0.5, r + 0.5],
                'k'
            )

        # Bottom wall
        if maze[r][c][2]:
            plt.plot(
                [c - 0.5, c + 0.5],
                [r + 0.5, r + 0.5],
                'k'
            )

        # Left wall
        if maze[r][c][3]:
            plt.plot(
                [c - 0.5, c - 0.5],
                [r - 0.5, r + 0.5],
                'k'
            )

    # Player
    plt.plot(
        player[1],
        player[0],
        'bo',
        markersize=12
    )

    plt.xlim(c1 - 0.5, c2 + 0.5)
    plt.ylim(r2 + 0.5, r1 - 0.5)

    plt.xticks([])
    plt.yticks([])

    plt.title("Your View of the Maze")

    # Important: does not stop the terminal
    plt.show(block=False)
    plt.pause(0.1)


def draw_map(maze, player, goal, map_start):

    path = shortest_path(
        maze,
        map_start,
        goal
    )

    plt.figure(figsize=(8, 8))

    for r in range(len(maze)):

        for c in range(len(maze[0])):

            # Show path
            if (r, c) in path:
                plt.plot(
                    c,
                    r,
                    'gs',
                    markersize=8
                )

            # Top wall
            if maze[r][c][0]:
                plt.plot(
                    [c - 0.5, c + 0.5],
                    [r - 0.5, r - 0.5],
                    'k'
                )

            # Right wall
            if maze[r][c][1]:
                plt.plot(
                    [c + 0.5, c + 0.5],
                    [r - 0.5, r + 0.5],
                    'k'
                )

            # Bottom wall
            if maze[r][c][2]:
                plt.plot(
                    [c - 0.5, c + 0.5],
                    [r + 0.5, r + 0.5],
                    'k'
                )

            # Left wall
            if maze[r][c][3]:
                plt.plot(
                    [c - 0.5, c - 0.5],
                    [r - 0.5, r + 0.5],
                    'k'
                )

    # Player
    plt.plot(
        player[1],
        player[0],
        'bo',
        markersize=12
    )

    # Goal
    plt.plot(
        goal[1],
        goal[0],
        'r*',
        markersize=15
    )

    # Starting point of path
    plt.plot(
        map_start[1],
        map_start[0],
        'gs',
        markersize=10
    )

    plt.xlim(
        -0.5,
        len(maze[0]) - 0.5
    )

    plt.ylim(
        len(maze) - 0.5,
        -0.5
    )

    plt.xticks([])
    plt.yticks([])

    plt.title("Map Found - Green = Path to Goal")

    plt.show(block=False)
    plt.pause(0.1)


def random_cell(maze, forbidden):

    choices = []

    for r in range(len(maze)):

        for c in range(len(maze[0])):

            if (r, c) not in forbidden:
                choices.append((r, c))

    return random.choice(choices)


def make_game():

    maze = generate_maze()

    player = random_cell(
        maze,
        set()
    )

    goal = random_cell(
        maze,
        {player}
    )

    # Make sure player cannot see goal
    while goal in visible_cells(maze, player):

        goal = random_cell(
            maze,
            {player}
        )

    map_position = random_cell(
        maze,
        {player, goal}
    )

    # Hazard is the extra requirement
    hazard = random_cell(
        maze,
        {player, goal, map_position}
    )

    return (
        maze,
        player,
        goal,
        map_position,
        hazard
    )


def move_player(maze, player):

    moves = {
        'w': 0,
        'd': 1,
        's': 2,
        'a': 3
    }

    while True:

        move = input(
            "Move W/A/S/D (Q to quit): "
        ).lower()

        if move == 'q':
            return None

        if move not in moves:

            print(
                "Please enter W, A, S, D, or Q."
            )

            continue

        direction = moves[move]

        # Check for wall
        if maze[player[0]][player[1]][direction] == 1:

            print("There is a wall there.")
            continue

        dr, dc = DIRECTIONS[direction]

        return (
            player[0] + dr,
            player[1] + dc
        )


def main():

    while True:

        maze, player, goal, map_position, hazard = make_game()

        explored = {player}

        print()
        print("Welcome to the Maze Game!")
        print("Find the goal without hitting the hazard.")
        print()
        print("W = Up")
        print("A = Left")
        print("S = Down")
        print("D = Right")
        print("Q = Quit")
        print()

        while True:

            draw_local_view(
                maze,
                player,
                explored
            )

            # Found the map
            if player == map_position:

                print()
                print("You found the map!")

                map_start = random_cell(
                    maze,
                    {goal}
                )

                draw_map(
                    maze,
                    player,
                    goal,
                    map_start
                )

                map_position = None

            # Hit hazard
            if player == hazard:

                print()
                print("GAME OVER!")
                print("You found the hazard.")

                break

            # Reached goal
            if player == goal:

                print()
                print("YOU WIN!")
                print("You reached the goal.")

                break

            # Get next move
            next_position = move_player(
                maze,
                player
            )

            if next_position is None:

                print()
                print("Thanks for playing!")

                return

            player = next_position
            explored.add(player)

        # Ask to play again
        again = input(
            "\nPlay again? (y/n): "
        ).lower()

        if again != 'y':

            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
    