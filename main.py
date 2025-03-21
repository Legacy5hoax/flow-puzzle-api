from flask import Flask, request, jsonify
import random

app = Flask(name)

def generate_puzzle(grid_size, pairs):
    available_spots = [(x, y) for x in range(grid_size) for y in range(grid_size)]
    random.shuffle(available_spots)

    puzzle_data = {"grid_size": gridsize, "pairs": []}
    for  in range(pairs):
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
    data = request.json
    grid_size = data.get("grid_size", 5)
    pairs = data.get("pairs", 3)
    puzzle = generate_puzzle(grid_size, pairs)
    return jsonify(puzzle)

if name == "main":
    app.run(host="0.0.0.0", port=8080)
