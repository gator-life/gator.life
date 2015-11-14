__author__ = 'nico'






#get list of docs with features, list of users with features, return list of users with documents
def match(documents, users):

    doc_matrix = extract_doc_feature_matrix(documents)
    user_matrix = extract_user_feature_matrix(users)


    user_docs_matrix = doc_matrix*user_matrix


