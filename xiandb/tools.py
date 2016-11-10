def update_dictionary(existing, new):
    if existing['_id'] != new['_id']:
        return existing

    return new
