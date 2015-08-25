#plugin found here: https://gist.github.com/SpainTrain/b5d4689156f0190700ef#file-gae_pylint_plugin-py
#look like : http://docs.pylint.org/plugins.html
#used for NDB becauses it adds properties at runtime that are not detected by pylint (and so add false positives)


from astroid import MANAGER
from astroid import scoped_nodes

NDB_PROPERTIES = [
    'DateTimeProperty',
    'StringProperty',
    'KeyProperty',
    'StructuredProperty',
    'FloatProperty'
]


def register(linter):
    pass


def transform(modu):
    if modu.name == 'google.appengine.ext.ndb':
        for f in NDB_PROPERTIES:
            modu.locals[f] = [scoped_nodes.Class(f, None)]

MANAGER.register_transform(scoped_nodes.Module, transform)
