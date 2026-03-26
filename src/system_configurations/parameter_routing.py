PARAM_MAP = {
    'top_layer': lambda cfg, v: cfg['system'].__setitem__('top_layer', v),

    'channel': lambda cfg, v: cfg['physical']['channel'].__setitem__('class', v),
    'error_prob': lambda cfg, v: cfg['physical']['channel']['params'].__setitem__('error_prob', v),
    'channel_rng': lambda cfg, v: cfg['physical']['channel']['params'].__setitem__('channel_rng', v),
    'channel_code': lambda cfg, v: cfg['physical']['channel_code'].__setitem__('class', v),

    'max_retries': lambda cfg, v: cfg['link'].__setitem__('max_retries', v),
    'payload_size': lambda cfg, v: cfg['link']['frame_params'].__setitem__('payload_size', v),
    'seq_size': lambda cfg, v: cfg['link']['frame_params'].__setitem__('seq_size', v),
    'checksum_size': lambda cfg, v: cfg['link']['frame_params'].__setitem__('checksum_size', v),
    'checksum': lambda cfg, v: cfg['link']['checksum'].__setitem__('class', v),
}
def route_param(config_dicts, key, value):
    try:
        PARAM_MAP[key](config_dicts, value)
    except KeyError:
        raise KeyError(f"Unknown config parameter: {key}")