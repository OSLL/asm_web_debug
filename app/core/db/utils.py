from datetime import datetime 


def code_to_dict(document):
    code = document.to_mongo().to_dict()
    code['last_update'] = code['last_update'].timestamp()
    return code

def task_to_dict(document):
    task = document.to_mongo().to_dict()
    return task
