# -*- coding: utf-8 -*-

import server.frontendstructs as struct
from server.dal import Dal, REF_FEATURE_SET


def create_user_dummy(user_id, password, interests):
    dal = Dal()
    dummy_doc1 = struct.Document.make_from_scratch(
        url='https://www.google.com', url_hash='hash_create_user_dummy_1_' + user_id, title='google.com',
        summary='we will buy you',
        feature_vector=struct.FeatureVector.make_from_scratch([], REF_FEATURE_SET))
    dummy_doc2 = struct.Document.make_from_scratch(
        url='gator.life', url_hash='hash_create_user_dummy_2_' + user_id, title='gator.life', summary='YGNI',
        feature_vector=struct.FeatureVector.make_from_scratch([], REF_FEATURE_SET))
    dal.doc.save_documents([dummy_doc1, dummy_doc2])

    new_user = struct.User.make_from_scratch(email=user_id, interests=interests)
    dal.user.save_user(new_user, password)
    user_doc1 = struct.UserDocument.make_from_scratch(document=dummy_doc1, grade=1.0)
    user_doc2 = struct.UserDocument.make_from_scratch(document=dummy_doc2, grade=0.5)
    dal.user_doc.save_user_docs(new_user, [user_doc1, user_doc2])

    return new_user


def init_features_dummy(feature_set_id):
    dal = Dal()
    dal.feature_set.save_feature_set(
        struct.FeatureSet.make_from_scratch(feature_set_id, feature_names=['sport', 'trading', 'bmw', 'c++']))


NEW_USER_ID = "new_user_id"
