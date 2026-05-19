def _set_infrastructure(cfg, key, value):
    cfg['infrastructure'][key] = value

def _set_protocol_stack_param(cfg, key, value):
    cfg['protocol_stack'][key] = value

def _set_physical_code_class(cfg, value):
    cfg['physical']['channel_code']['class'] = value

def _set_physical_code_param(cfg, key, value):
    cfg['physical']['channel_code']['params'][key] = value

def _set_link_param(cfg, key, value):
    cfg['link'][key] = value

def _set_link_frame_param(cfg, key, value):
    cfg['link']['frame_params'][key] = value

def _set_link_checksum_class(cfg, value):
    cfg['link']['checksum']['class'] = value

def _set_link_checksum_param(cfg, key, value):
    cfg['link']['checksum']['params'][key] = value


PARAM_MAP = {
    'alphabet': lambda cfg, v: _set_infrastructure(cfg, 'alphabet', v),
    'top_layer': lambda cfg, v: _set_protocol_stack_param(cfg, 'top_layer', v),
    'channel_code': lambda cfg, v: _set_physical_code_class(cfg, v),
    'repetition': lambda cfg, v: _set_physical_code_param(cfg, 'repetition', v),
    'max_retries': lambda cfg, v: _set_link_param(cfg, 'max_retries', v),
    'payload_size': lambda cfg, v: _set_link_frame_param(cfg, 'payload_size', v),
    'seq_size': lambda cfg, v: _set_link_frame_param(cfg, 'seq_size', v),
    'checksum_size': lambda cfg, v: _set_link_frame_param(cfg, 'checksum_size', v),
    'checksum': lambda cfg, v: _set_link_checksum_class(cfg, v),
    'crc_generator': lambda cfg, v: _set_link_checksum_param(cfg, 'crc_generator', v),
}


def route_param(config_dicts, key, value):
    try:
        PARAM_MAP[key](config_dicts, value)
    except KeyError:
        raise KeyError(f"Unknown config parameter: {key}")