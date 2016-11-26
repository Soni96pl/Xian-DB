def list_update(target, replacement, upsert=False):
    for index, value in enumerate(target):
        if value['_id'] == replacement['_id']:
            for key, value in replacement.items():
                target[index][key] = value
            break
    else:
        if upsert is True:
            target.append(replacement)
    return target


def list_upsert(target, replacement):
    return list_update(target, replacement, upsert=True)


def list_remove(target, _id):
    return filter(lambda v: v['_id'] != _id, target)


def path_to_keys(path):
    try:
        if path[-1] == '.':
            path = path[:-1]
        if path[0] == '.':
            path = path[1:]
    except (TypeError, IndexError):
        return None
    return path.split('.')


def data_get(target, path=None, keys=None, force=False):
    def process(target, keys):
        key = keys[0]
        if isinstance(target, dict):
            target = target[key]
        elif isinstance(target, list):
            try:
                target = target[int(key)]
            except IndexError:
                if force is False:
                    raise
                target = target[0]

        if len(keys) == 1:
            return target
        return process(target, keys[1:])

    if path is None and keys is None:
        return target
    elif path is not None:
        keys = path_to_keys(path)
        if keys is None:
            return target
    return process(target, keys)


def data_update(target, replacement, path=None):
    def process_level(keys, target, replacement):
        if len(keys) > 0:
            if isinstance(target, dict):
                key = keys[0]
            elif isinstance(target, list):
                key = int(keys[0])

            try:
                target[key] = process_level(keys[1:], target[key], replacement)
            except (KeyError, IndexError):
                pass
        else:
            if isinstance(target, dict):
                for k, v in replacement.items():
                    target[k] = v
            elif isinstance(target, list):
                if isinstance(replacement, list):
                    target = replacement
                else:
                    target.append(replacement)
            else:
                target = replacement
        return target

    keys = path_to_keys(path)
    if keys is None:
        return replacement

    return process_level(keys, target, replacement)


def data_remove(target, path):
    def process_level(keys, target):
        if isinstance(target, dict):
            key = keys[0]
        elif isinstance(target, list):
            key = int(keys[0])

        try:
            if len(keys) > 1:
                target[key] = process_level(keys[1:], target[key])
            else:
                del target[key]
        except (KeyError, IndexError):
            pass

        return target

    keys = path_to_keys(path)
    if keys is None:
        return target

    return process_level(keys, target)
