from flask import Flask, request, jsonify
import os
import uuid 
app = Flask(__name__)

BASE_DIR = "files"
os.makedirs(BASE_DIR, exist_ok=True)

@app.route("/")
def index():
    return "ok"


@app.route("/files", methods=["GET"])
def list_files():
    try:
        files = os.listdir(BASE_DIR)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files/<filename>", methods=["GET"])
def read_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File does not exist"}), 404
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"filename": filename, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files", methods=["POST"])
def create_file():
    data = request.get_json()
    filename = data.get("filename")
    content = data.get("content", "")

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        return jsonify({"error": "File already exists"}), 400

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return jsonify({"message": f"File '{filename}' was created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["GET", "POST"])
def upload_file_form():
    if request.method == "POST":
        filename = request.form.get("filename")
        content = request.form.get("content")

        if not filename:
            return "You must specify a filename", 400

        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            return "File already exists", 400

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content or "")
            return f"File '{filename}' was created successfully!"
        except Exception as e:
            return f"Error: {str(e)}", 50

@app.route("/files/auto", methods=["POST"])
def create_file_auto_name():
    data = request.get_json()
    content = data.get("content", "")


    filename = f"file_{uuid.uuid4().hex[:8]}.txt"
    filepath = os.path.join(BASE_DIR, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return jsonify({
            "message": "File was created successfully!",
            "filename": filename
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File does not exist"}), 404

    try:
        os.remove(filepath)
        return jsonify({"message": f"File '{filename}' has been deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/files/<filename>", methods=["PUT"])
def update_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File doesn't exist"}), 404

    data = request.get_json()
    content = data.get("content", "")

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return jsonify({"message": f"File '{filename}' has been updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
