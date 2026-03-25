PARAM_MAP = {
    'top_layer': ('system', 'top_layer'),

    'channel': ('physical', 'channel', 'class'),
    'error_prob': ('physical', 'channel', 'params', 'error_prob'),
    'channel_rng': ('physical', 'channel', 'params', 'rng'),
    'channel_code': ('physical', 'channel_code', 'class'),

    'payload_size': ('link', 'frame', 'payload_size'),
    'seq_size': ('link', 'frame', 'seq_size'),
    'checksum_size': ('link', 'frame', 'checksum_size'),
    'checksum': ('link', 'checksum', 'class'),
    'max_retries': ('link', 'max_retries'),
}

def route_param(config_obj, key, value):
    if key not in PARAM_MAP:
        raise KeyError(f"Unknown config parameter: {key}")

    path = PARAM_MAP[key]
    section = path[0]

    try:
        attr_name = config_obj.CONFIG_SECTIONS[section]
    except KeyError:
        raise KeyError(f"Unknown config section: {section}")

    target = getattr(config_obj, attr_name)

    for p in path[1:-1]:
        if p not in target:
            raise KeyError(f"Invalid config path: {path}")
        target = target[p]

    target[path[-1]] = value
