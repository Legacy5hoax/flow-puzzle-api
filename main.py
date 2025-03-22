from flask import Flask, request, jsonify
import random
from collections import deque

app = Flask(__name__)

def is_reachable(grid_size, start, end, occupied):
    """Check if there's a valid path between the start and end points, without crossing occupied cells."""
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

def place_path(grid_size, start, end, occupied):
    """Place a path between start and end, and mark the occupied cells."""
    visited = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    queue = deque([(start, [])])

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            # Mark the path as occupied
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

def generate_puzzle(grid_size, pairs):
    available_spots = [(x, y) for x in range(grid_size) for y in range(grid_size)]
    random.shuffle(available_spots)

    puzzle_data = {"grid_size": grid_size, "pairs": []}
    occupied = set()

    # Calculate the total number of cells in the grid
    total_cells = grid_size * grid_size
    # Calculate the maximum number of pairs possible based on grid size
    max_pairs = total_cells // 2

    # If the requested number of pairs exceeds the maximum possible pairs, adjust it
    if pairs > max_pairs:
        return {"error": f"Requested number of pairs exceeds the maximum ({max_pairs}) for the given grid size."}, 400

    print(f"Generating puzzle with grid size: {grid_size} and {pairs} pairs")

    # We try to place pairs, but first check that we have enough spots available
    if len(available_spots) < 2 * pairs:
        return {"error": "Not enough available spots to create the requested number of pairs."}, 400

    # Attempt to place each pair
    for _ in range(pairs):
        if len(available_spots) < 2:
            return {"error": "Not enough spots available to place more pairs."}, 400

        # Select a random pair of spots
        start = available_spots.pop()
        end = available_spots.pop()

        # Ensure the start and end points are connected without overlapping paths
        retry_attempts = 0
        while not is_reachable(grid_size, start, end, occupied) and retry_attempts < 10:
            print(f"Retrying pair placement. Attempts: {retry_attempts}")
            if len(available_spots) < 2:
                return {"error": "Not enough available spots to create valid paths."}, 400
            random.shuffle(available_spots)  # Reshuffle available spots to try again
            start = available_spots.pop()
            end = available_spots.pop()
            retry_attempts += 1

        if retry_attempts >= 10:
            return {"error": "Unable to find valid path for some pairs. Grid size might be too small."}, 400

        # Place the path and mark occupied cells
        if place_path(grid_size, start, end, occupied):
            puzzle_data["pairs"].append({"start": start, "end": end})

    print("Puzzle generated:", puzzle_data)
    return puzzle_data

@app.route("/", methods=["GET"])
def home():
    return "Flow Puzzle API is Running!"

@app.route("/generate_puzzle", methods=["POST"])
def generate():
    try:
        # Parse the request JSON data
        data = request.get_json()

        # Debugging print to check if the incoming data is valid
        print("Incoming data:", data)

        grid_size = int(data.get("grid_size", 5))  # Default to 5 if not provided
        pairs = int(data.get("pairs", 3))          # Default to 3 if not provided

        # Debugging print to check the grid_size and pairs
        print(f"Grid Size: {grid_size}, Pairs: {pairs}")

        # Early validation: Ensure requested pairs don't exceed max pairs
        total_cells = grid_size * grid_size
        max_pairs = total_cells // 2
        if pairs > max_pairs:
            return jsonify({"error": f"Requested number of pairs exceeds the maximum possible ({max_pairs}) for the given grid size."}), 400
        
        puzzle = generate_puzzle(grid_size, pairs)

        # Check if an error was returned in puzzle data
        if 'error' in puzzle:
            return jsonify(puzzle), 400

        return jsonify(puzzle)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
