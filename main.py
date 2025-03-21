from flask import Flask, request, jsonify
import random

app = Flask(__name__)

def generate_puzzle(grid_size, pairs):
    available_spots = [(x, y) for x in range(grid_size) for y in range(grid_size)]
    random.shuffle(available_spots)

    puzzle_data = {"grid_size": grid_size, "pairs": []}
    
    for _ in range(pairs):  # Corrected the loop with "_"
        if len(available_spots) < 2:
            break
        start, end = available_spots.pop(), available_spots.pop()
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
