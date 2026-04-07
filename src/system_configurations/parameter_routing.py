PARAM_MAP = {

    # # # Infrastructure parameters
    'alphabet': lambda cfg, v: cfg['infrastructure'].__setitem__('alphabet', v),
    'channel': lambda cfg, v: cfg['infrastructure']['channel'].__setitem__('class', v),
    'error_prob': lambda cfg, v: cfg['infrastructure']['channel']['params'].__setitem__('error_prob', v),
    'channel_rng': lambda cfg, v: cfg['infrastructure']['channel']['params'].__setitem__('channel_rng', v),

    # # # Protocol stack parameters
    'top_layer': lambda cfg, v: cfg['protocol_stack'].__setitem__('top_layer', v),

    # # # Physical layer parameters

    # Channel code parameters
    'channel_code': lambda cfg, v: cfg['physical']['channel_code'].__setitem__('class', v),
    'repetition': lambda cfg, v: cfg['physical']['channel_code']['params'].__setitem__('repetition', v),

    # # # Link layer parameters
    'max_retries': lambda cfg, v: cfg['link'].__setitem__('max_retries', v),

    # Frame parameters
    'payload_size': lambda cfg, v: cfg['link']['frame_params'].__setitem__('payload_size', v),
    'seq_size': lambda cfg, v: cfg['link']['frame_params'].__setitem__('seq_size', v),
    'checksum_size': lambda cfg, v: cfg['link']['frame_params'].__setitem__('checksum_size', v),

    # Checksum parameters
    'checksum': lambda cfg, v: cfg['link']['checksum'].__setitem__('class', v),
    'crc_generator': lambda cfg, v: cfg['link']['checksum']['params'].__setitem__('crc_generator', v),
}
def route_param(config_dicts, key, value):
    try:
        PARAM_MAP[key](config_dicts, value)
    except KeyError:
        raise KeyError(f"Unknown config parameter: {key}")