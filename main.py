from flask import Flask, request, jsonify
import random
from collections import deque

app = Flask(__name__)

def is_reachable(grid_size, start, end):
    """Check if there's a valid path between the start and end points in the grid."""
    visited = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    queue = deque([start])

    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return True
        if (x, y) not in visited:
            visited.add((x, y))
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in visited:
                    queue.append((nx, ny))
    return False

def generate_puzzle(grid_size, pairs):
    available_spots = [(x, y) for x in range(grid_size) for y in range(grid_size)]
    random.shuffle(available_spots)

    puzzle_data = {"grid_size": grid_size, "pairs": []}
    
    for _ in range(pairs):
        if len(available_spots) < 2:
            break
        start = available_spots.pop()
        end = available_spots.pop()

        # Ensure the start and end points are connected
        while not is_reachable(grid_size, start, end):
            random.shuffle(available_spots)  # Reshuffle available spots to try again
            start = available_spots.pop()
            end = available_spots.pop()

        puzzle_data["pairs"].append({"start": start, "end": end})

    return puzzle_data

@app.route("/", methods=["GET"])
def home():
    return "Flow Puzzle API is Running!"

@app.route("/generate_puzzle", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        grid_size = int(data.get("grid_size", 5))
        pairs = int(data.get("pairs", 3))
        puzzle = generate_puzzle(grid_size, pairs)
        return jsonify(puzzle)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
