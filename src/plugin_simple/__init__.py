def handle_event(watcher, event, config):
    message = "Kind: {0}; Name: {1}; Event Type:{2}".format(event['object']['kind'], event['object']['metadata']['name'], event['type'])
    log_level = config.get('message_log_level','INFO')
    return message, log_level
