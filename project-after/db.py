import psycopg2
from comment import Comment

class CommentDatabase():
    def __init__(self, db_url):
        self.connection = psycopg2.connect(db_url)
        print("Connected.")
        cursor = self.connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS comments (id SERIAL, name TEXT, comment TEXT);')

    def __mapComments(self, comments):
        return list(map(lambda x: Comment(*x), comments))

    def createComment(self, comment):
        if not isinstance(comment, Comment):
            return
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO comments (name, comment) VALUES (%(name)s, %(comment)s)', comment.toDict())

    def __lookupComments(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM comments;')
        return cursor.fetchall()

    def getAllComments(self):
        return self.__mapComments(self.__lookupComments())
