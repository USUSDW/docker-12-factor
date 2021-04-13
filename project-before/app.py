from flask import Flask, request

from comment import Comment
from db import CommentDatabase

app = Flask(__name__)
app.config["DEBUG"] = True

db_url = 'postgresql://comments:comment_pw@localhost/comments'

connection = CommentDatabase(db_url)

@app.route('/comments', methods=['GET'])
def getComments():
    return { 'comments': 
        [comment.toDict() for comment in connection.getAllComments()] 
    }

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
    app.run()