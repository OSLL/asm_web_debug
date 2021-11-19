def code_to_dict(document):
    code = document.to_mongo().to_dict()
    return code
