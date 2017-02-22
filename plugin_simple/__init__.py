def handle_event(event):
    message = "Kind: {0}; Name: {1}".format(event['object']['kind'], event['object']['metadata']['name'])
    log_level = "INFO"
    return message, log_level
