from flask import Flask, request, jsonify
import random
from collections import deque

app = Flask(__name__)

# Function to check if a path exists between start and end using BFS
def is_reachable(grid_size, start, end, occupied):
    visited = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    queue = deque([start])

    while queue:
        x, y = queue.popleft()
        if (x, y) == end:
            return True
        if (x, y) not in visited and (x, y) not in occupied:
            visited.add((x, y))
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    queue.append((nx, ny))
    return False

# Function to mark the path as occupied
def place_path(grid_size, start, end, occupied):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    visited = set()
    queue = deque([(start, [])])

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            # Mark all cells in the path as occupied
            for px, py in path + [(x, y)]:
                occupied.add((px, py))
            return True
        if (x, y) not in visited and (x, y) not in occupied:
            visited.add((x, y))
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    queue.append(((nx, ny), path + [(x, y)]))
    return False

# Function to generate a solvable puzzle
def generate_puzzle(grid_size, pairs):
    total_cells = grid_size * grid_size
    max_pairs = total_cells // 2

    # Ensure requested pairs don't exceed the maximum possible pairs
    if pairs > max_pairs:
        return {"error": f"Requested pairs exceed the maximum possible pairs for this grid size: {max_pairs}"}, 400

    available_spots = [(x, y) for x in range(grid_size) for y in range(grid_size)]
    random.shuffle(available_spots)

    puzzle_data = {"grid_size": grid_size, "pairs": []}
    occupied = set()

    # Check if there are enough available spots
    if len(available_spots) < 2 * pairs:
        return {"error": "Not enough available spots to create the requested number of pairs."}, 400

    # Try to place each pair
    for _ in range(pairs):
        placed = False
        attempts = 0
        while not placed and attempts < 100:  # Limit the attempts to avoid infinite loops
            start, end = random.sample(available_spots, 2)  # Get two random spots
            # Ensure no overlap
            if start not in occupied and end not in occupied:
                # Check if a valid path exists between start and end
                if is_reachable(grid_size, start, end, occupied):
                    if place_path(grid_size, start, end, occupied):
                        puzzle_data["pairs"].append({"start": start, "end": end})
                        placed = True
            attempts += 1
        
        if not placed:
            return {"error": "Unable to place all pairs with no overlap. Try reducing the number of pairs."}, 400

    return puzzle_data

@app.route("/", methods=["GET"])
def home():
    return "Flow Puzzle API is Running!"

@app.route("/generate_puzzle", methods=["POST"])
def generate():
    try:
        # Parse the request JSON data
        data = request.get_json()
        grid_size = int(data.get("grid_size", 5))
        pairs = int(data.get("pairs", 3))

        # Ensure the number of pairs doesn't exceed the max possible pairs
        total_cells = grid_size * grid_size
        max_pairs = total_cells // 2
        if pairs > max_pairs:
            return jsonify({"error": f"Requested pairs exceed the maximum possible pairs for this grid size: {max_pairs}"}), 400
        
        puzzle = generate_puzzle(grid_size, pairs)
        if "error" in puzzle:
            return jsonify(puzzle), 400

        return jsonify(puzzle)
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
