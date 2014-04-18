import os
import json
import requests

from src.utils import settings, logger, RepeatTimer
from serveroperation.sofoperation import OperationKey, OperationValue, \
    RequestMethod, ResponseUris


_message_delimiter = '<EOF>'

allow_checkin = True


class NetManager():

    def __init__(self, seconds_to_checkin=60):
        """

        Args:

            - seconds_to_checkin: Time, in seconds, to check into the server
                and it defaults to 1 minute.

        Return:

            - Nothing

        """

        self._server_url = 'https://{0}/'.format(
            settings.ServerAddress
        )

        self._timer = RepeatTimer(seconds_to_checkin, self._agent_checkin)

    def incoming_callback(self, callback):
        """
        Sets the callback to be used when operations were received during
        agent check-in.
        @param callback: The operation callback.
        @return: Nothing
        """
        self._incoming_callback = callback

    def _agent_checkin(self):
        """
        Checks in to the server to retrieve all pending operations.
        @return: Nothing
        """
        if allow_checkin:
            root = {}
            root[OperationKey.Operation] = OperationValue.CheckIn
            root[OperationKey.OperationId] = ''
            root[OperationKey.AgentId] = settings.AgentId

            success = self.send_message(
                json.dumps(root),
                ResponseUris.get_response_uri(OperationValue.CheckIn),
                ResponseUris.get_request_method(OperationValue.CheckIn)
            )

            if not success:
                logger.error(
                    "Could not check-in to server. See logs for details."
                )

        else:
            logger.info("Checkin set to false.")

    def start(self):
        """
        Starts the repeating timer that checks-in to the server at
        set intervals.
        @return: Nothing
        """
        self._timer.start()

    def login(self):

        try:
            url = os.path.join(
                self._server_url,
                ResponseUris.get_response_uri(OperationValue.Login)
            )

            logger.debug("Logging into: {0}".format(url))

            self.http_session = requests.session()

            headers = {'content-type': 'application/json'}
            payload = {
                'name': settings.Username,
                'password': settings.Password
            }

            response = self.http_session.post(
                url,
                data=json.dumps(payload),
                headers=headers,
                verify=False,
                timeout=30
            )

            logger.debug("Login status code: %s " % response.status_code)
            logger.debug("Login server text: %s " % response.text)

            if response.status_code == 200:

                return True

        except Exception as e:

            logger.error("Agent was unable to login.")
            logger.exception(e)

        return False

    def _get_request_method(self, req_method):
        if req_method == RequestMethod.POST:
            return self.http_session.post
        if req_method == RequestMethod.PUT:
            return self.http_session.put
        if req_method == RequestMethod.GET:
            return self.http_session.get

    def send_message(self, data, uri, req_method):
        """Sends a message to the server and waits for data in return.

        Args:
            - data: JSON formatted str to send the server.

            - uri: RESTful uri to send the data.

            - req_method: HTTP Request Method

        Returns:

            - True if message was sent successfully. False otherwise.

        """

        logger.debug('Sending message to server')

        url = os.path.join(self._server_url, uri)
        headers = {'content-type': 'application/json'}
        payload = data
        sent = False

        logger.debug("Sending message to: {0}".format(url))

        try:

            if not self.login():
                logger.error("Agent was unable to login.")
                return False

            request_method = self._get_request_method(req_method)

            response = request_method(
                url,
                data=payload,
                headers=headers,
                verify=False,
                timeout=30
            )

            logger.debug("Url: %s " % url)
            logger.debug("Status code: %s " % response.status_code)
            logger.debug("Server text: %s " % response.text)

            if response.status_code == 200:

                sent = True

            received_data = []
            try:

                received_data = response.json()

            except Exception as e:

                logger.error("Unable to read data from server. Invalid JSON?")
                logger.exception(e)

            self._incoming_callback(received_data)

        except Exception as e:

            logger.error("Unable to send data to server.")
            logger.exception(e)

        return sent
