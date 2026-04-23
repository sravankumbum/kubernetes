from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

MongoDB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MongoDB_URI)

db = client["mydatabase"]

collection = db["Todo"]

@app.route("/status")
def status():
	return jsonify({"status": "ok", "message": "Server is running!"})

# The root route is kept for simple health check or information
@app.route("/")
def helloworld():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Todo API</title>
    </head>
    <body>
        <h1>Todo API Running</h1>
        <p>Use /todos to fetch todos and /process to add new ones.</p>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/process', methods=['POST'])
def process():
    # Expecting a todo item JSON with 'title' and 'description'
    print("Received data:", request.json)
    todo = {
        "title": request.json.get("title"),
        "description": request.json.get("description")
    }
    result = collection.insert_one(todo)
    return jsonify({"success": True, "message": f"Inserted {todo['title']}! Data successfully.", "id": str(result.inserted_id)})

@app.route('/todos', methods=['GET'])
def get_todos():
    # return all todos including the stringified _id so client can delete
    raw = list(collection.find({}))
    todos = []
    for doc in raw:
        todos.append({
            "_id": str(doc.get("_id")),
            "title": doc.get("title"),
            "description": doc.get("description"),
        })
    return jsonify(todos)


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        oid = ObjectId(todo_id)
    except Exception:
        return jsonify({"success": False, "message": "invalid id"}), 400
    result = collection.delete_one({"_id": oid})
    if result.deleted_count:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
