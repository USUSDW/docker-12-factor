from flask import Flask, request
from os import getenv
from dotenv import load_dotenv
from comment import Comment

load_dotenv()

app = Flask(__name__)
app.config["DEBUG"] = getenv("DEBUG").lower() == "true"

from db import CommentDatabase

db_url = getenv('DB_URL')

connection = CommentDatabase(db_url)

@app.route('/comments', methods=['GET'])
def getComments():
    return { 'comments': [comment.toDict() for comment in connection.getAllComments()] }

@app.route('/comments', methods=['POST'])
def addComment():
    data = request.json
    print(data)
    if not 'name' in data:
        return { 'error': 'Name is required.' }, 400
    if not 'comment' in data:
        return { 'error': 'Comment is required.' }, 400
    connection.createComment(Comment(-1, data['name'], data['comment']))
    return '', 201

if __name__ == "__main__":
    app.run(host=getenv('HOST'), port=getenv('PORT'))