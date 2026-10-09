from maze_game import (
    generate_maze,
    neighbors,
    shortest_path,
    visible_cells
)


def test_maze_is_connected():

    maze = generate_maze()

    visited = {(0, 0)}
    stack = [(0, 0)]

    while stack:

        current = stack.pop()

        for cell in neighbors(
            maze,
            current
        ):

            if cell not in visited:

                visited.add(cell)
                stack.append(cell)

    assert len(visited) == 15 * 15


def test_maze_has_loops():

    maze = generate_maze()

    edges = 0

    for r in range(15):

        for c in range(15):

            edges += len(
                neighbors(
                    maze,
                    (r, c)
                )
            )

    edges = edges // 2

    # A 15x15 tree has 224 edges.
    # More than 224 means the maze has a loop.
    assert edges > 224


def test_path_exists():

    maze = generate_maze()

    path = shortest_path(
        maze,
        (0, 0),
        (14, 14)
    )

    assert path[0] == (0, 0)
    assert path[-1] == (14, 14)


def test_player_is_visible():

    maze = generate_maze()

    visible = visible_cells(
        maze,
        (7, 7)
    )

    assert (7, 7) in visible