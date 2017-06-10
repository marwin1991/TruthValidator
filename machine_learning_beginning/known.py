import sqlite3


class Topic:
    def __init__(self, name, key_words, knowledge):
        self.name = name
        self.key_words = key_words
        self.knowledge = knowledge
        self.size = 0
        connection = sqlite3.connect('brain.db')
        cur = connection.cursor()
        cur.execute("create table if not exists " + self.name +
                    " (statement text, true_rate real)")
        connection.close()

    def add_atom(self, atom):
        if id(self) != id(atom):
            self.knowledge.append(atom)
            self.size += 1

    def add_key_words(self, key_words):
        self.key_words.append(key_words)

    def save_to_db(self):
        connection = sqlite3.connect('brain.db')
        cur = connection.cursor()
        for elem in self.knowledge:
            if isinstance(elem, Atom):
                cur.execute("INSERT INTO " + self.name + " values (\'" +
                            elem.statement + "\',\'" + str(elem.true_rate) +
                            "\')")
        connection.commit()
        connection.close()

    def import_from_db(self):
        connection = sqlite3.connect('brain.db')
        cur = connection.cursor()
        cur.execute('select * from ' + self.name)
        db_return = cur.fetchall()
        for elem in db_return:
            self.knowledge.append(Atom(elem[0], elem[1]))
        connection.close()


class Atom:
    def __init__(self, statement, true_rate):
        self.statement = statement
        self.true_rate = true_rate

#   def __conform__(self, protocol):
#       if protocol is sqlite3.PrepareProtocol:
#           return "%text;%f" % (self.statement, self.true_rate)

    def __str__(self):
        return self.statement + " " + str(self.true_rate)
