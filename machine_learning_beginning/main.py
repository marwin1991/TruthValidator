from known import *

topic = Topic('body', ['finger', 'head'])
# topic.add_atom(Atom('Head is important', 1.0))
# topic.save_to_db()
topic.import_from_db()
print(topic.knowledge[0])
