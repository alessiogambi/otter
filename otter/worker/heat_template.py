PROPERTY_RENAMES = {
    'imageRef': 'image',
    'flavorRef': 'flavor',
    'OS-DCF:diskConfig': 'diskConfig',
}


def rename_keys(mapping, renames):
    result = {}
    for key, val in mapping.iteritems():
        new_key = renames.get(key, key)
        result[new_key] = val
    return result


def lc_to_resource(lc):
    assert lc['type'] == 'launch_server'
    server = lc['args']['server']

    # metadata? 
    resource_definition = {
        'type': 'OS::Nova::Server',
        'properties': rename_keys(server, PROPERTY_RENAMES)
    }
    return resource_definition


def generate_template(launch_config, desired_capacity):
    """
    Generates a template based on the launch config and the desired capacity
    
    TODO:
    1. handle previous resources - if the launch config has changed, this
       implementation just overwrites all the old ones.
    2. handle eviction - this implementation just regenerates a template from
       scratch based on desired capacity, and will evict the newest servers
       first.
    """
    resource_definition = lc_to_resource(launch_config)
    name = launch_config['args']['server'].get('name', 'server')
    resources = {'{0}-{1}'.format(name, i): resource_definition
                 for i in range(desired_capacity)}
    return {'resources': resources}
