import os
from gcloud import datastore


def main(): #pylint: disable=too-many-statements
    os.environ["DATASTORE_HOST"] = "http://localhost:33001"
    os.environ["DATASTORE_DATASET"] = "gator-01"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/nico/projects/gator/not_versioned/gator-484905471895_gae_key.json"

    #client = datastore.Client(dataset_id="test")
    client = datastore.Client()

    # Let's create a new entity of type "Thing" and name it 'Toy':
    key = client.key('Thing')
    toy = datastore.Entity(key)
    toy.update({'name': 'Toy'})

    # Now let's save it to our datastore:
    client.put(toy)

    # If we look it up by its key, we should find it...
    print client.get(toy.key)

    # And we should be able to delete it...
    client.delete(toy.key)

    # Since we deleted it, if we do another lookup it shouldn't be there again:
    print client.get(toy.key)

    # Now let's try a more advanced query.
    # First, let's create some entities.
    sample_data = [
        (1234, 'Computer', 10),
        (2345, 'Computer', 8),
        (3456, 'Laptop', 10),
        (4567, 'Printer', 11),
        (5678, 'Printer', 12),
        (6789, 'Computer', 13)]
    sample_keys = []
    for sample_id, name, age in sample_data:
        key = client.key('Thing', sample_id)
        sample_keys.append(key)
        entity = datastore.Entity(key)
        entity['name'] = name
        entity['age'] = age
        client.put(entity)
    # We'll start by look at all Thing entities:
    query = client.query(kind='Thing')

    # Let's look at the first two.
    print list(query.fetch(limit=2))

    # Now let's check for Thing entities named 'Computer'
    query.add_filter('name', '=', 'Computer')
    print list(query.fetch())

    # If you want to filter by multiple attributes,
    # you can call .add_filter multiple times on the query.
    query.add_filter('age', '=', 10)
    print list(query.fetch())

    # Now delete them.
    client.delete_multi(sample_keys)

    # You can also work inside a transaction.
    # (Check the official docs for explanations of what's happening here.)
    with client.transaction() as xact:
        print 'Creating and saving an entity...'
        key = client.key('Thing', 'foo')
        thing = datastore.Entity(key)
        thing['age'] = 10
        xact.put(thing)

        print 'Creating and saving another entity...'
        key2 = client.key('Thing', 'bar')
        thing2 = datastore.Entity(key2)
        thing2['age'] = 15
        xact.put(thing2)

        print 'Committing the transaction...'

    # Now that the transaction is commited, let's delete the entities.
    client.delete_multi([key, key2])

    # To rollback a transaction, just call .rollback()
    with client.transaction() as xact:
        key = client.key('Thing', 'another')
        thing = datastore.Entity(key)
        xact.put(thing)
        xact.rollback()

    # Let's check if the entity was actually created:
    created = client.get(key)
    print 'yes' if created else 'no'

    # Remember, a key won't be complete until the transaction is commited.
    # That is, while inside the transaction block, thing.key will be incomplete.
    with client.transaction() as xact:
        key = client.key('Thing')  # partial
        thing = datastore.Entity(key)
        xact.put(thing)
        print thing.key  # This will still be partial

    print thing.key  # This will be complete

    # Now let's delete the entity.
    client.delete(thing.key)


if __name__ == '__main__':
    main()
