"""
Asynchronous client for Heat, using treq.
"""

from __future__ import print_function


import json

from otter.util import logging_treq as treq
from otter.util.http import (append_segments, headers, check_success,
                             wrap_request_error, raise_error_on_code,
                             APIError, RequestError)


class MutuallyExclusiveArgumentsError(Exception):
    def __init__(self, args):
        self.args = args
        super(MutuallyExclusiveArgumentsError, self).__init___(
            "%s are mutually exclusive" % (self.args,))


class HeatClient(object):
    def __init__(self, auth_token, log):
        self.auth_token = auth_token
        self.log = log.bind(heatclient=True)

    def create_stack(self, heat_url, stack_name, environment, files,
                     parameters, timeout, disable_rollback,
                     template=None, template_url=None):
        """Create a stack!"""
        payload = {
            "stack_name": stack_name,
            "parameters": parameters,
            "timeout_mins": timeout
        }
        if template is not None:
            payload['template'] = template
        elif template_url is not None:
            payload['template_url'] = template_url
        else:
            raise MutuallyExclusiveArgumentsError('template', 'template_url')
        log = self.log.bind(event='create-stack', stack_name=stack_name)
        result = treq.post(
            append_segments(heat_url, 'stacks'),
            data=json.dumps(payload),
            headers=headers(self.auth_token), log=log)
        result.addCallback(check_success, [200, 201])
        return result.addCallback(treq.json_content)

    def update_stack(self, stack_url, environment, files,
                     parameters, timeout, template=None, template_url=None):
        """Update a stack!"""
        payload = {
            "parameters": parameters,
            "timeout_mins": timeout
        }
        if template is not None:
            payload['template'] = template
        elif template_url is not None:
            payload['template_url'] = template_url
        else:
            raise MutuallyExclusiveArgumentsError('template', 'template_url')
        log = self.log.bind(event='update-stack')
        result = treq.put(stack_url,
                  data=json.dumps(payload),
                  headers=headers(self.auth_token),
                  log=log)
        result.addCallback(check_success, [200, 201])
        result.addCallback(treq.json_content)
        return result

    def get_stack(self, stack_url):
        """Get the metadata about a stack."""
        result = treq.get(stack_url, headers=headers(self.auth_token),
                          log=self.log)
        result.addCallback(check_success, [200])
        result.addCallback(treq.json_content)
        return result

    def get_resources(self, stack_name):
        """
        Get a list of resources from a stack.
        """

    def delete_stack(self, stack_name):
        """Delete a stack."""


def main(reactor, *args):
    import os, yaml
    from otter.log import log
    template = yaml.safe_load(open(args[1]))
    tenant = os.environ['OS_TENANT_ID']
    client = HeatClient(os.environ['OS_AUTH_TOKEN'], log)

    heat_root = 'https://dfw.orchestration.api.rackspacecloud.com/v1/' + tenant
    stack_url = heat_root + '/stacks/my-stack-name'
    result = client.get_stack(stack_url)
    def got_stack(result):
        print("here's a stack:", result)
        result = client.update_stack(stack_url, None, None,
                                     {}, 60, template=template)
        return result
    def no_stack(failure):
        failure.trap(APIError)
        if failure.value.code != 404:
            return failure
        result = client.create_stack(
             heat_root,
            'my-stack-name', None, None, {}, 60, False, template=template)
        return result
    result.addCallback(got_stack).addErrback(no_stack)
    return result.addCallback(lambda r: print("FINAL RESULT", r))


if __name__ == '__main__':
    import sys
    from twisted.internet.task import react
    from twisted.python.log import startLogging, addObserver
    from otter.log.setup import observer_factory
    addObserver(observer_factory())
    react(main, sys.argv)
