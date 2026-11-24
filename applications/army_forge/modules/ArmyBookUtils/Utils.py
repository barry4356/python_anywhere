def book_name_to_json_name(name):
    return name.replace(' ','_') + '.json'

def json_name_to_book_name(name):
    return name.replace("_", " ").replace('.json','')