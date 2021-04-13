class Comment:
    def __init__(self, id, name, comment):
        self.id = id
        self.name = name
        self.comment = comment

    def toDict(self):
        return { 'id': self.id, 'name': self.name, 'comment': self.comment }