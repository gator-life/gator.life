from google.appengine.ext import testbed

def make_gae_testbed():
    """
    # standard set of calls to initialize unit test ndb environment
    :return: activated testbed, on which you must call deactivate() on TearDown
    """
    gae_testbed = testbed.Testbed()
    gae_testbed.activate()
    gae_testbed.init_datastore_v3_stub()
    gae_testbed.init_memcache_stub()
    return gae_testbed
