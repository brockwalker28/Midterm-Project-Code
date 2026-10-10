import random
from collections import deque
import matplotlib.pyplot as plt

plt.rcParams["keymap.save"] = []

# Up, Right, Down, Left
DIRECTIONS = [
    (-1, 0),
    (0, 1),
    (1, 0),
    (0, -1)
]

MOVE_KEYS = {
    "w": 0,
    "d": 1,
    "s": 2,
    "a": 3,
}


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
    # All reachable cells from position
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

    # Look in all four directions
    for direction, (dr, dc) in enumerate(DIRECTIONS):

        current = player

        while True:
            r, c = current

            # Stop if wall blocks view
            if maze[r][c][direction] == 1:
                break

            nr = r + dr
            nc = c + dc

            # Stop if next cell is outside maze
            if not inside(maze, nr, nc):
                break

            current = (nr, nc)
            visible.add(current)

            # Find open directions
            open_directions = [
                d for d in range(4)
                if maze[nr][nc][d] == 0
            ]

            # Continue through straight hallway
            opposite = (direction + 2) % 4

            if len(open_directions) != 2:
                break

            if direction not in open_directions:
                break

            if opposite not in open_directions:
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


def random_cell(maze, forbidden):
    # Chooses a random cell that is allowed
    choices = [
        (r, c)
        for r in range(len(maze))
        for c in range(len(maze[0]))
        if (r, c) not in forbidden
    ]

    if not choices:
        raise ValueError("No available cells left")

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

class MazeGame:
    # Manage game state and show Matplotlib window
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig.canvas.manager.set_window_title("Maze Game")
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self.legend_text = self.fig.text(
            0.5, 0.035,
            "Blue circle = Player   |   Green square = Map / route   |   "
            "Red triangle = Hazard   |   Red star = Goal / Victory",
            ha="center", va="bottom", fontsize=8
        )

        self.new_game()
        self.redraw()
        self.fig.text(
            0.5, 0.005,
            "Use W/A/S/D to move. Press Q to quit",
            ha="center", fontsize=9
        )
        self.fig.tight_layout(rect=(0, 0.04, 1, 1))

    def new_game(self):
        self.maze, self.player, self.goal, self.map_position, self.hazard = (
            make_game()
        )
        #printed hazard position to ensure it was spawning
        #print("Hazard location:", self.hazard)
        # Keep map's original cell
        self.map_location = self.map_position
        self.state = "playing"
        self.map_collected = False
        self.route = []
        self.message = "Find the map, avoid the hazard, reach the goal"

    def on_key(self, event):
        # No need to press enter after every input
        if event.key is None:
            return

        key = event.key.lower()

        if self.state in ("won", "lost", "quit"):
            if key == "y" and self.state in ("won", "lost"):
                self.new_game()
                self.redraw()
            elif key in ("n", "q"):
                plt.close(self.fig)
            return

        if key == "q":
            self.state = "quit"
            self.message = "Goodbye"
            self.redraw()
            plt.close(self.fig)
            return

        if key not in MOVE_KEYS:
            return

        directions = MOVE_KEYS[key]
        r, c = self.player

        # If a wall blocks movement, do not change player position
        if self.maze[r][c][directions] == 1:
            self.message = "There is a wall"
            self.redraw()
            return

        dr, dc = DIRECTIONS[directions]
        self.player = (r + dr, c + dc)
        self.message = "Find the map, avoid the hazard, reach the goal"

        if self.map_collected:
            self.route = shortest_path(self.maze, self.player, self.goal)

        # Check game events immediately after moving.
        if self.player == self.map_position:
            self.map_position = None
            self.map_collected = True
            self.route = shortest_path(
                self.maze, self.player, self.goal
            )
            self.message = (
                "You found the map!"
                "The green cells show the shortest route to the exit"
            )

        if self.player == self.hazard:
            self.state = "lost"
            self.message = "Game Over! You found the hazard. Press Y to play again or Q to quit"
        elif self.player == self.goal:
            self.state = "won"
            self.message = "You Win! Press Y to play again or Q to quit"
                    
        self.redraw()

    def draw_walls(self, cells):
        # Draw the walls for the visible and explored cells
        rows = len(self.maze)
        cols = len(self.maze[0])

        for r, c in cells:
            if not inside(self.maze, r, c):
                continue

            if self.maze[r][c][0]:
                self.ax.plot([c - 0.5, c + 0.5],
                             [r - 0.5, r - 0.5], "k-", linewidth=1.3)
            if self.maze[r][c][1]:
                self.ax.plot([c + 0.5, c + 0.5],
                             [r - 0.5, r + 0.5], "k-", linewidth=1.3)
            if self.maze[r][c][2]:
                self.ax.plot([c - 0.5, c + 0.5],
                             [r + 0.5, r + 0.5], "k-", linewidth=1.3)
            if self.maze[r][c][3]:
                self.ax.plot([c - 0.5, c - 0.5],
                             [r - 0.5, r + 0.5], "k-", linewidth=1.3)

    def draw_local_view(self):
        visible = visible_cells(self.maze, self.player)

        cells = visible

        self.draw_walls(cells)

        # Once the map is collected it guides player to goal
        if getattr(self, "map_collected", False):
            # Route always starts at player and ends at goal
            self.route = shortest_path(self.maze, self.player, self.goal)
            visible_route = [cell for cell in self.route if cell in visible]
            for r, c in visible_route:
                if (r, c) != self.player and (r, c) != self.goal:
                    self.ax.plot(
                        c, r, marker="s", color="limegreen",
                        markersize=8, linestyle="None"
                    )


        # Only draws if object is visible
        if self.map_position is not None and self.map_position in visible:
            self.ax.plot(
                self.map_position[1], self.map_position[0],
                marker="s", color="green", markersize=10,
                linestyle="None", label="Map"
            )

        if self.hazard in visible:
            self.ax.plot(
                self.hazard[1], self.hazard[0],
                marker="^", color="red", markersize=11,
                linestyle="None", zorder=10
            )

        if self.goal in visible:
            self.ax.plot(
                self.goal[1], self.goal[0],
                marker="*", color="red", markersize=13,
                linestyle="None", label="Goal"
            )

        self.ax.plot(
            self.player[1], self.player[0],
            marker="o", color="blue", markersize=11,
            linestyle="None", label="Player"
        )

        # Set boundaries to not show future parts of the maze
        player_r, player_c = self.player
        min_r = min(r for r, c in cells)
        max_r = max(r for r, c in cells)
        min_c = min(c for r, c in cells)
        max_c = max(c for r, c in cells)

        half_height = max(
            4.5,
            player_r - min_r + 0.65,
            max_r - player_r + 0.65
        )

        half_width = max(
            4.5,
            player_c - min_c + 0.65,
            max_c - player_c + 0.65
        )

        self.ax.set_xlim(player_c - half_width, player_c + half_width)
        self.ax.set_ylim(player_r + half_height, player_r - half_height)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_title("Local View - Blue = Player")
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def draw_full_map(self):
        # Find the shortest path from the starting point
        map_start = random_cell(self.maze, {self.goal})
        path = shortest_path(self.maze, map_start, self.goal)

        for r, c in path:
            self.ax.plot(c, r, "s", color="green", markersize=5)

        all_cells = {
            (r, c)
            for r in range(len(self.maze))
            for c in range(len(self.maze[0]))
        }

        self.draw_walls(all_cells)

        self.ax.plot(
            self.player[1], self.player[0],
            marker="o", color="blue", markersize=9
        )
        self.ax.plot(
            self.goal[1], self.goal[0],
            marker="*", color="red", markersize=13
        )
        self.ax.plot(
            map_start[1], map_start[0],
            marker="s", color="green", markersize=10,
            linestyle="None", label="Map location"
        )
        self.ax.plot(
            self.hazard[1], self.hazard[0],
            marker="^", color="red", markersize=10,
            linestyle="None", label="Hazard"
        )

        self.ax.set_xlim(-0.6, len(self.maze[0]) - 0.4)
        self.ax.set_ylim(len(self.maze) - 0.4, 0.6)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_title("Map Found - Green = SHortest Path to Goal")
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def redraw(self):
        # Clear and redraw on the same figure
        self.ax.clear()

        self.draw_local_view()

        # Keep the legend visible at all times so the symbols are explained.
        legend_text = (
            "Blue circle = Player   |   Green square = Map / route   |   "
            "Red triangle = Hazard   |   Red star = Goal / Victory"
        )
        self.fig.suptitle(self.message, fontsize=10, y=0.98)
        self.legend_text.set_text(legend_text)
        self.fig.canvas.draw_idle()


def main():
    game = MazeGame()
    plt.show()


if __name__ == "__main__":
    main()
    