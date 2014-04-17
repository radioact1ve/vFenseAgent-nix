import subprocess
import re
import platform

from distro.mac.hardware import MacHardware
from src.utils import settings
from src.utils import logger


def get_hw_info():
    """ This method basically just calls the respected hardware class
    to get the specs.
    """

    hw_info = {}

    if platform.system() == "Darwin":
        hw_info = MacHardware().get_specs()
    else:
        hw_info['cpu'] = CpuInfo().get_cpu_list()
        hw_info['memory'] = get_total_ram()
        hw_info['display'] = DisplayInfo().get_display_list()
        hw_info['storage'] = HarddriveInfo().get_hdd_list()
        hw_info['nic'] = NicInfo().get_nic_list()

    format_hw_info(hw_info)

    return hw_info


# TODO: completely remove
def format_hw_info(hw_dict):
    # CPU info
    for cpu in hw_dict['cpu']:
        if cpu['cpu_id']:
            cpu['cpu_id'] = int(cpu['cpu_id'])

        if cpu['bit_type']:
            cpu['bit_type'] = int(cpu['bit_type'])

        if cpu['speed_mhz']:
            cpu['speed_mhz'] = float(cpu['speed_mhz'])

        if cpu['cores']:
            cpu['cores'] = int(cpu['cores'])

        if cpu['cache_kb']:
            cpu['cache_kb'] = float(cpu['cache_kb'])

    # Memory info
    hw_dict['memory'] = float(hw_dict['memory'])

    # Storage info
    for hdd in hw_dict['storage']:
        hdd['free_size_kb'] = int(hdd['free_size_kb'])
        hdd['size_kb'] = int(hdd['size_kb'])


class CpuInfo():
    """Retrieve information about the computers cpu(s)."""

    def _get_cat_cpu_info(self):
        """Retrieve cpu info from the command 'cat /proc/cpuinfo'.

        Returns:
            str: Raw output from subprocess call to 'cat /proc/cpuinfo'
        """
        cmd = ['cat', '/proc/cpuinfo']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        raw_output, _ = process.communicate()

        return raw_output

    def _parse_cpu_data(self, raw_output):
        """Parse cpu information from the 'cat /proc/cpuinfo' subprocess call.

        Args:
            raw_output (str): String which follows a format identical to the
                              'cat /proc/info' output.

        Returns:
            list: List of dictionaries which hold data for each cpu found.
                  Each dict has the following keys:
                    cpu_id (int)
                    name (str)
                    cores (int)
                    speed_mhz (float)
                    cache_kb (int)
                    bit_type (int)

            Example:
            [
                {
                    'cpu_id': 0,
                    'name': "Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz",
                    'cores': 1,
                    'speed_mhz': 2594.000,
                    'cache_kb': 3072,
                    'bit_type': 64
                },
                ...
            ]
        """
        cpu_list = []

        cpu_info_blocks = raw_output.split('\n\n')

        for info_block in cpu_info_blocks:
            # Setting defaults for variables that are known
            # to not show in the raw_output
            cpu_data = {
                'cores': 1,
            }

            for line in info_block.split('\n'):
                line = line.strip()

                if re.match("processor", line):
                    cpu_id = line.split(':')[1].strip()
                    cpu_data['cpu_id'] = int(cpu_id)

                elif re.match("model name", line):
                    name = line.split(':')[1].strip()
                    cpu_data['name'] = name

                elif re.match("cpu cores", line):
                    cores = line.split(':')[1].strip()
                    cpu_data['cores'] = int(cores)

                elif re.match("cpu MHz", line):
                    speed_mhz = line.split(':')[1].strip()
                    cpu_data['speed_mhz'] = float(speed_mhz)

                elif re.match("cache size", line):
                    cache_kb = line.split(':')[1].strip()
                    cpu_data['cache_kb'] = int(cache_kb.replace('KB', ''))

                elif re.match("flags", line):
                    bit_type = 32

                    # lm is the flag set by linux to indicate 64bit
                    # X86_FEATURE_LM (long mode)
                    if " lm " in line:
                        bit_type = 64

                    cpu_data['bit_type'] = bit_type

            cpu_list.append(cpu_data)

        return cpu_list

    def get_cpu_list(self):
        """Get cpu info for every cpu found from the 'cat /proc/cpuinfo'
            subprocess call.

        Returns:
            list: List of dictionaries which hold data for each cpu found.
                  Each dict has the following keys:
                    cpu_id (int)
                    name (str)
                    cores (int)
                    speed_mhz (float)
                    cache_kb (int)
                    bit_type (int)

            Example:
            [
                {
                    'cpu_id': 0,
                    'name': "Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz",
                    'cores': 1,
                    'speed_mhz': 2594.000,
                    'cache_kb': 3072,
                    'bit_type': 64
                },
                ...
            ]
        """

        try:
            raw_output = self._get_cat_cpu_info()
            cpu_list = self._parse_cpu_data(raw_output)
        except Exception as e:
            logger.error("Error getting cpu info.")
            logger.exception(e)
            cpu_list = []

        return cpu_list


class DisplayInfo():
    """Retrieve information about the computers display."""

    def _get_pci_device_info(self):
        """Retrieves all PCI device info from the lscpi command.

        Returns:
           str: Raw output from the 'lspci -v' command through subprocess.
        """
        cmd = ['lspci', '-v']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        raw_output, _ = process.communicate()

        return raw_output

    def _parse_vga_information(self, raw_output):
        """Parses output for 'VGA compatible controller' entry.

        Args:
            raw_output (str): Output in the format of what you get from
                              'lspci -v'.

        Returns:
            Dictionary with 3 keys:
                name (str)
                speed_mhz (int)
                ram_kb (int)

            Example:
                {
                    'name': 'Parallels, Inc. Accelerated Virtual Video Adapter (prog-if 00 [VGA controller])',
                    'speed_mhz': 66,
                    'ram_kb': 32768
                }
        """
        tmp_list = []
        for s in raw_output.splitlines():
            tmp_list.append(s.replace("\t", ''))

        output = tmp_list
        display_dict = None
        display_list = []

        reading_vga = False
        for entry in output:

            if 'VGA compatible controller:' in entry:
                name = entry.partition('VGA compatible controller:')[2].strip()
                display_dict = {'name': name}

                reading_vga = True

                continue

            elif 'Flags:' in entry and reading_vga:
                flags = entry.partition(':')[2].strip()
                match = re.match(r'[0-9]+MHz', flags)

                speed_mhz = 0
                if match:
                    speed_mhz = int(match.group().split('MHz')[0])

                # TODO: string or int?
                display_dict['speed_mhz'] = speed_mhz

                continue

            elif 'Memory at' in entry and \
                 'prefetchable' in entry and \
                 reading_vga:

                size_string = entry.split("[size=")[1].replace(']', '')

                size_kb = 0

                # KB
                if 'K' in size_string:
                    size_kb = int(size_string.replace('K', ''))

                # MB
                elif 'M' in size_string:
                    size = int(size_string.replace('M', ''))
                    size_kb = size * 1024

                # GB
                elif 'G' in size_string:
                    size = int(size_string.replace('G', ''))
                    size_kb = (size * 1024) * 1024

                display_dict['ram_kb'] = \
                    display_dict.get('ram_kb', 0) + size_kb

                continue

            # Empty line means the beginning of a new processor item. Save.
            elif entry == "" and reading_vga:
                display_list.append(display_dict.copy())
                reading_vga = False

        return display_list

    def get_display_list(self):
        """Retrieves data corresponding to the computers display.

        Returns:
            Dictionary with 3 keys:
                name (str)
                speed_mhz (int)
                ram_kb (int)

            Example:
                {
                    'name': 'Parallels, Inc. Accelerated Virtual Video Adapter (prog-if 00 [VGA controller])',
                    'speed_mhz': 66,
                    'ram_kb': 32768
                }
            """
        raw_output = self._get_pci_device_info()

        try:
            display_list = self._parse_vga_information(raw_output)
        except Exception:
            display_list = []

        return display_list


class HarddriveInfo():

    def __init__(self):

        self._hdd_list = []

        try:
            # df options:
            # 'h': print sizes in human readable format ('k' = KB)
            # 'l': local file systems. 'T': file system type (ext3/ext4/db)
            cmd = ['df', '-hklT']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            self._raw_output, _stderr = process.communicate()
            self._parse_output()
        except Exception as e:
            logger.error("Error reading hard drive info.", 'error')
            logger.exception(e)
            self._hdd_list = []  # Something went wrong, set to empty list.

    def _parse_output(self):
        self._output = []
        for line in self._raw_output.splitlines():
            self._output.append([x for x in line.split(' ') if x != ''])

        _partition_blacklist = [
            'tmpfs',
            'rootfs',
            'none',
            'devtmpfs',
            'Filesystem'
        ]

        tmp_dict = {}
        for entry in self._output:

            if entry[0] in _partition_blacklist:
                continue

            # An ideal entry would consist of 7 items. It would look like:
            # ['/dev/sda1', 'ext4', '495844', '38218', '432026', '9%', '/boot']
            if len(entry) == 7:
                tmp_dict['name'] = entry[0]

                tmp_dict['size_kb'] = int(entry[3]) + int(entry[4])
                tmp_dict['free_size_kb'] = entry[4]
                tmp_dict['file_system'] = entry[1]
            else:
                # But less then 7 items means the name of the partition and its
                # data were split across two entries:
                # ['/dev/mapper/vg_centosmon-lv_root'],
                # ['ext4', '12004544', '3085772', '8796828', '26%', '/']
                # Taking that into consideration here.
                if len(entry) == 1:
                    tmp_dict['name'] = entry[0]
                    continue
                elif len(entry) == 6:
                    tmp_dict['size_kb'] = int(entry[2]) + int(entry[3])
                    tmp_dict['free_size_kb'] = entry[3]
                    tmp_dict['file_system'] = entry[0]

            self._hdd_list.append(tmp_dict.copy())

    def get_hdd_list(self):
        return self._hdd_list


class NicInfo():

    def __init__(self):

        self._nics = []

        try:
            cmd = ['ip', 'addr']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            self._raw_output, _stderr = process.communicate()
            self._parse_output()
        except Exception as e:
            logger.error("Error reading nic info.", 'error')
            logger.exception(e)
            self._nics = []  # Something went wrong, set to empty dict.

    def _parse_output(self):
        self._output = [line.strip() for line in self._raw_output.splitlines()]

        #### Inserting a '\n' between interfaces. Easier to parse...
        indices = []
        for i in range(len(self._output)):
            match = re.match(r'[0-9]+:', self._output[i])
            if match:
                if i > 1:
                    indices.append(i)

        for i in indices:
            self._output.insert(i, '')

        self._output.insert(len(self._output), '')
        #######################################################

        reading_flag = False
        temp_dict = {}
        for entry in self._output:

            match = re.match(r'[0-9]+:', entry)
            if match:
                temp_dict = {}

                iface_num = match.group()
                new_entry = entry.replace(iface_num, '').strip()

                reading_flag = True
                temp_dict['name'] = new_entry.partition(':')[0]

                continue

            elif entry.find('link/loopback') == 0:
                reading_flag = False
                temp_dict = {}
                continue

            elif entry.find('link/ether') == 0 and reading_flag:

                mac = (entry
                       .replace('link/ether', '')
                       .partition('brd')[0]
                       .strip())

                mac = mac.replace(':', '')  # Server doesn't expect ':'s
                temp_dict['mac'] = mac

            # Space after 'inet' to prevent check with 'inet6'
            elif entry.find('inet ') == 0 and reading_flag:

                ip = entry.replace('inet ', '').partition('/')[0].strip()
                temp_dict['ip_address'] = ip

            elif entry == "" and reading_flag:
                reading_flag = False
                self._nics.append(temp_dict.copy())

    def get_nic_list(self):

        return self._nics


def get_total_ram():

    try:
        cmd = ['cat', '/proc/meminfo']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        _raw_output, _stderr = process.communicate()

        total_output = _raw_output.splitlines()[0]
        mem = total_output.partition(":")[2].split(" ")[-2]

    except Exception as e:
        logger.error("Error reading memory info.", 'error')
        logger.exception(e)
        mem = settings.EmptyValue

    return mem
