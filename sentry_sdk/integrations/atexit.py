from __future__ import absolute_import

import atexit
import os
import sys

from sentry_sdk._types import TYPE_CHECKING
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration
from sentry_sdk.utils import logger

if TYPE_CHECKING:

    pass


def default_callback(pending, timeout):
    # type: (int, int) -> None
    """This is the default shutdown callback that is set on the options.
    It prints out a message to stderr that informs the user that some events
    are still pending and the process is waiting for them to flush out.
    """

    def echo(msg):
        # type: (str) -> None
        sys.stderr.write(msg + "\n")

    echo("Sentry is attempting to send %i pending error messages" % pending)
    echo("Waiting up to %s seconds" % timeout)
    echo("Press Ctrl-%s to quit" % (os.name == "nt" and "Break" or "C"))
    sys.stderr.flush()


class AtexitIntegration(Integration):
    identifier = "atexit"

    def __init__(self, callback=None):
        # type: (Optional[Any]) -> None
        if callback is None:
            callback = default_callback
        self.callback = callback

    @staticmethod
    def setup_once():
        # type: () -> None
        @atexit.register
        def _shutdown():
            # type: () -> None
            logger.debug("atexit: got shutdown signal")
            hub = Hub.main
            print('Shudown phase #1')
            integration = hub.get_integration(AtexitIntegration)
            print('Shudown phase #2')
            if integration is not None:
                print('Shudown phase #3')
                logger.debug("atexit: shutting down client")

                # If there is a session on the hub, close it now.
                hub.end_session()
                print('Shudown phase #4')

                # If an integration is there, a client has to be there.
                client = hub.client  # type: Any
                client.close(callback=integration.callback)
                print('Shudown phase #5')
            print('Shudown phase #6')
            sys.exit()
            print('Shudown phase #7')
