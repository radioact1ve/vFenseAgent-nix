import time
import uuid

from utils import settings
try:
    import simplejson as json
except ImportError:
    import json


class OperationValue():
    # The corresponding SOF equivalent. (Case sensitive)
    NewAgent = 'new_agent'
    NewAgentId = 'new_agent_id'
    Startup = 'startup'
    Reboot = 'reboot'
    Shutdown = 'shutdown'
    InvalidAgentId = 'invalid_agent_id'
    CheckIn = 'check_in'

    SystemInfo = 'system_info'
    HardwareInfo = 'hardware'

    Result = 'result'


class OperationKey():

    Operation = 'operation'
    OperationId = 'operation_id'
    Plugin = 'plugin'
    Data = 'data'
    AgentId = 'agent_id'
    Success = 'success'
    Error = 'error'
    Reboot = 'reboot'
    RebootRequired = 'reboot_required'
    Rebooted = 'rebooted'
    VendorId = 'vendor_id'
    RvId = 'id'
    CustomerName = 'customer_name'
    Message = 'message'

    ServerQueueTTL = 'server_queue_ttl'
    AgentQueueTTL = 'agent_queue_ttl'

    ResponseURI = 'response_uri'
    RequestMethod = 'request_method'

    Core = 'core'
    Plugins = 'plugins'


class OperationError():
    pass


class RequestMethod():
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'


class CoreUris():

    # *********************************************************
    # IMPORTANT: Use the provided methods to get the attributes.
    # *********************************************************

    # Must not start with a '/'
    Reboot = 'rvl/v1/{0}/core/results/reboot'
    Shutdown = 'rvl/v1/{0}/core/results/shutdown'
    Checkin = 'rvl/v1/{0}/core/checkin'
    Startup = 'rvl/v1/{0}/core/startup'
    NewAgent = 'rvl/v1/core/newagent'
    Login = 'rvl/login'
    Logout = 'rvl/logout'

    @staticmethod
    def get_checkin_uri():
        return CoreUris.Checkin.format(settings.AgentId)

    @staticmethod
    def get_reboot_uri():
        return CoreUris.Reboot.format(settings.AgentId)

    @staticmethod
    def get_shutdown_uri():
        return CoreUris.Shutdown.format(settings.AgentId)

    @staticmethod
    def get_startup_uri():
        return CoreUris.Startup.format(settings.AgentId)

    @staticmethod
    def get_new_agent_uri():
        return CoreUris.NewAgent

    @staticmethod
    def get_login_uri():
        return CoreUris.Login

    @staticmethod
    def get_logout_uri():
        return CoreUris.Logout


SelfGeneratedOpId = '-agent'


class SofOperation(object):

    def __init__(self, message=None):

        self.data = []
        self.raw_result = settings.EmptyValue
        self.core_data = {}
        self.plugin_data = {}
        self.rebooted = 'no'
        self.reboot_delay_seconds = 90
        self.shutdown_delay_seconds = 90
        self.error = settings.EmptyValue

        self.server_queue_ttl = None
        self.agent_queue_ttl = None

        self.response_uri = ''
        self.request_method = ''

        if message:
            self._load_message(message)

        else:
            self.json_message = settings.EmptyValue

            self.id = self.self_assigned_id()
            self.plugin = settings.EmptyValue
            self.type = settings.EmptyValue
            self.raw_operation = settings.EmptyValue

    def _load_message(self, message):
        self.raw_operation = message
        self.json_message = json.loads(message)

        self.id = self.json_message.get(
            OperationKey.OperationId, self.self_assigned_id()
        )

        self.plugin = self.json_message.get(
            OperationKey.Plugin, settings.EmptyValue
        )

        self.type = self.json_message[OperationKey.Operation]

        self.server_queue_ttl = self.json_message.get(
            OperationKey.ServerQueueTTL, None
        )
        self.agent_queue_ttl = self.json_message.get(
            OperationKey.AgentQueueTTL, None
        )

        # Fail if missing
        self.response_uri = self.json_message.get(
            OperationKey.ResponseURI, ''
        )
        self.request_method = self.json_message.get(
            OperationKey.RequestMethod, ''
        )

    def is_savable(self):
        non_savable = [OperationValue.Reboot, OperationValue.Shutdown,
                       OperationValue.Startup, OperationValue.NewAgent]

        if self.type in non_savable:
            return False

        return True

    def server_queue_ttl_valid(self):
        if self.server_queue_ttl is not None:
            if time.time() > self.server_queue_ttl:
                return False

        return True

    def agent_queue_ttl_valid(self):
        if self.agent_queue_ttl is not None:
            if time.time() > self.agent_queue_ttl:
                return False

        return True

    def self_assigned_id(self):

        return str(uuid.uuid4()) + SelfGeneratedOpId

    def add_result(self, result):
        """
        Adds the values of a SofResult to this operation instance.
        @param result: SofResult object with the operation results.
        @return: Nothing
        """

        root = {}
        root[OperationKey.RvId] = result.id
        root[OperationKey.Success] = str(result.successful).lower()

        if result.successful:
            root[OperationKey.Reboot] = str(result.restart).lower()
        else:
            root[OperationKey.Error] = result.specific_message

        self.data.append(root)

    def add_dependency(self, deps):
        self.data.append(deps)

    def to_json(self):
        json_dict = {
            OperationKey.AgentId: settings.AgentId,
            OperationKey.OperationId: self.id,
            OperationKey.Operation: self.type,
            OperationKey.CustomerName: settings.Customer,
            OperationKey.Rebooted: self.rebooted,
            OperationKey.Plugins: self.plugin_data,
        }

        json_dict.update(self.core_data)

        return json.dumps(json_dict)


class ResultOperation():
    """ Allows you to set a timeout for sending results back.

        Presumably this result cannot be sent to server unless the current
        time since epoch is greater than that set in wait_until.
    """

    def __init__(self, operation, retry):
        """
        Arguments:

        operation
            An object which MUST contain a raw_result, response_uri,
            and request_method attribute.

        retry
            Tells the result loop whether or not to retry sending results
            if a failure occurs on an attempt.

        timeout
        """

        self.id = self.self_assigned_id()
        self.type = OperationValue.Result
        self.operation = operation
        self.retry = retry

        # Sets current time, no timeout
        self.wait_until = self._time_in_seconds()

    def _time_in_seconds(self):
        """ Returns current time in seconds since epoch. """

        return int(time.time())

    def timeout(self, seconds=60):
        """
        Timeout this result by the amount specified in seconds.
        """

        self.wait_until = self._time_in_seconds() + seconds

    def should_be_sent(self):
        """ Says whether this result should be sent to server. """

        if self._time_in_seconds() > self.wait_until:
            return True

        return False

    def is_savable(self):
        non_savable = [OperationValue.Startup, OperationValue.NewAgent]

        if self.operation.type in non_savable:
            return False

        return True

    def self_assigned_id(self):
        return str(uuid.uuid4()) + SelfGeneratedOpId


class SofResult():
    """
    Data structure to pass around operation results.
    """
    def __init__(self, operation, success, reboot_required, error):
        self.id = operation.id
        self.type = operation.type
        self.success = success
        self.reboot_required = reboot_required
        self.error = error

        self.response_uri = operation.response_uri
        self.request_method = operation.request_method

        self.raw_result = self.to_json()

    def to_json(self):
        json_dict = {
            OperationKey.OperationId: self.id,
            OperationKey.Success: self.success,
            OperationKey.RebootRequired: self.reboot_required,
            OperationKey.Error: self.error
        }

        return json.dumps(json_dict)
