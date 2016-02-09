#!/usr/bin/env python
# -*- coding: utf-8 -*-

import server.frontendstructs as struct
import server.dal as dal


def init_user_dummy(user_id, password, interests):
    dummy_doc1 = struct.Document.make_from_scratch(
        url='https://www.google.com', title='google.com', summary='we will buy you',
        feature_vector=struct.FeatureVector.make_from_scratch([], dal.REF_FEATURE_SET))
    dummy_doc2 = struct.Document.make_from_scratch(
        url='gator.life', title='gator.life', summary='YGNI',
        feature_vector=struct.FeatureVector.make_from_scratch([], dal.REF_FEATURE_SET))
    dal.save_documents([dummy_doc1, dummy_doc2])

    new_user = struct.User.make_from_scratch(email=user_id, password=password, interests=interests)
    dal.save_user(new_user)
    user_doc1 = struct.UserDocument.make_from_scratch(document=dummy_doc1, grade=1.0)
    user_doc2 = struct.UserDocument.make_from_scratch(document=dummy_doc2, grade=0.5)
    dal.save_user_docs(new_user, [user_doc1, user_doc2])

    return new_user


def init_features_dummy(feature_set_id):
    dal.save_features(feature_set_id, feature_names=['sport', 'trading', 'bmw', 'c++'])


NEW_USER_ID = "new_user_id"
