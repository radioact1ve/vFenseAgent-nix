import unittest

from src.utils import hardware

class TestCpuInfoLinux(unittest.TestCase):
    single_cpu = \
        """
        processor	: 0
        vendor_id	: GenuineIntel
        cpu family	: 6
        model		: 58
        model name	: Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz
        stepping	: 9
        cpu MHz		: 2594.000
        cache size	: 3072 KB
        fpu		: yes
        fpu_exception	: yes
        cpuid level	: 13
        wp		: yes
        flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx rdtscp lm constant_tsc up nopl nonstop_tsc aperfmperf pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic popcnt aes xsave avx f16c rdrand hypervisor lahf_lm ida arat epb pln pts dtherm fsgsbase smep
        bogomips	: 5188.00
        clflush size	: 64
        cache_alignment	: 64
        address sizes	: 36 bits physical, 48 bits virtual
        power management:
        """

    multiple_cpus = \
        """
        processor	: 0
        vendor_id	: GenuineIntel
        cpu family	: 6
        model		: 58
        model name	: Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz
        stepping	: 9
        cpu MHz		: 2594.000
        cache size	: 3072 KB
        physical id	: 0
        siblings	: 2
        core id		: 0
        cpu cores	: 2
        apicid		: 0
        initial apicid	: 0
        fpu		: yes
        fpu_exception	: yes
        cpuid level	: 13
        wp		: yes
        flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx rdtscp lm constant_tsc nopl nonstop_tsc aperfmperf pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic popcnt aes xsave avx f16c rdrand hypervisor lahf_lm ida arat epb pln pts dtherm fsgsbase smep
        bogomips	: 5188.00
        clflush size	: 64
        cache_alignment	: 64
        address sizes	: 36 bits physical, 48 bits virtual
        power management:

        processor	: 1
        vendor_id	: GenuineIntel
        cpu family	: 6
        model		: 58
        model name	: Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz
        stepping	: 9
        cpu MHz		: 2594.000
        cache size	: 3072 KB
        physical id	: 0
        siblings	: 2
        core id		: 1
        cpu cores	: 2
        apicid		: 1
        initial apicid	: 1
        fpu		: yes
        fpu_exception	: yes
        cpuid level	: 13
        wp		: yes
        flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx rdtscp constant_tsc nopl nonstop_tsc aperfmperf pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic popcnt aes xsave avx f16c rdrand hypervisor lahf_lm ida arat epb pln pts dtherm fsgsbase smep
        bogomips	: 5188.00
        clflush size	: 64
        cache_alignment	: 64
        address sizes	: 36 bits physical, 48 bits virtual
        power management:
        """

    def test_single_cpu(self):
        cpu_info = hardware.CpuInfo()
        cpu_info._get_cat_cpu_info = lambda: self.single_cpu

        expecting = [
            {
                'cpu_id': 0,
                'name': "Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz",
                'cores': 1,
                'speed_mhz': 2594.000,
                'cache_kb': 3072,
                'bit_type': 64
            }
        ]

        self.assertEqual(cpu_info.get_cpu_list(), expecting)

    def test_multiple_cpu(self):
        cpu_info = hardware.CpuInfo()
        cpu_info._get_cat_cpu_info = lambda: self.multiple_cpus

        expecting = [
            {
                'cpu_id': 0,
                'name': "Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz",
                'cores': 2,
                'speed_mhz': 2594.000,
                'cache_kb': 3072,
                'bit_type': 64
            },
            {
                'cpu_id': 1,
                'name': "Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz",
                'cores': 2,
                'speed_mhz': 2594.000,
                'cache_kb': 3072,
                'bit_type': 32
            }
        ]

        self.assertEqual(cpu_info.get_cpu_list(), expecting)


class TestCpuInfoMac(unittest.TestCase):
    pass


class TestDisplayInfoLinux(unittest.TestCase):

    # \n\n is needed at the end so that the parsing can stop.
    # This simulates the real output from lscpi -v
    single_memory_entry = \
        """01:00.0 VGA compatible controller: Parallels, Inc. Accelerated Virtual Video Adapter (prog-if 00 [VGA controller])
            Subsystem: Parallels, Inc. Device 0400
            Flags: 66MHz, medium devsel, IRQ 21
            I/O ports at 6000 [size=32]
            Memory at b0000000 (32-bit, prefetchable) [size=32M]
            Expansion ROM at e2000000 [disabled] [size=64K]
            Kernel driver in use: prl_tg\n\n"""

    multiple_memory_entries = \
        """00:02.0 VGA compatible controller: Cirrus Logic GD 5446 (prog-if 00 [VGA controller])
            Subsystem: Red Hat, Inc Device 1100
            Flags: fast devsel
            Memory at fc000000 (32-bit, prefetchable) [size=32M]
            Memory at febf1000 (32-bit, non-prefetchable) [size=4K]
            Expansion ROM at febe0000 [disabled] [size=64K]
            Kernel modules: cirrusfb\n\n"""

    def test_display_info_parsing_single_memory_entry(self):
        display_info = hardware.DisplayInfo()
        expected = [{
            'speed_mhz': 66,
            'name': 'Parallels, Inc. Accelerated Virtual Video Adapter (prog-if 00 [VGA controller])',
            'ram_kb': 32768
        }]

        display_info._get_pci_device_info = lambda: self.single_memory_entry

        self.assertEqual(expected, display_info.get_display_list())

    def test_display_info_parsing_multiple_memory_entries(self):
        display_info = hardware.DisplayInfo()
        expected = [{
            'speed_mhz': 0,
            'name': 'Cirrus Logic GD 5446 (prog-if 00 [VGA controller])',
            'ram_kb': 32772
        }]

        display_info._get_pci_device_info = lambda: self.multiple_memory_entries

        self.assertEqual(expected, display_info.get_display_list())

    def test_display_info_parsing_multiple_vgas(self):
        display_info = hardware.DisplayInfo()
        multiple_vga_entries = self.multiple_memory_entries + self.single_memory_entry
        expected = [
            {
                'speed_mhz': 0,
                'name': 'Cirrus Logic GD 5446 (prog-if 00 [VGA controller])',
                'ram_kb': 32772
            },
            {
                'speed_mhz': 66,
                'name': 'Parallels, Inc. Accelerated Virtual Video Adapter (prog-if 00 [VGA controller])',
                'ram_kb': 32768
            }
        ]

        display_info._get_pci_device_info = lambda: multiple_vga_entries

        self.assertEqual(expected, display_info.get_display_list())


class TestDisplayInfoMac(unittest.TestCase):
    pass


class TestHarddriveInfoLinux(unittest.TestCase):
    df_output = \
"""
Filesystem                                             Type      1K-blocks    Used  Available Use% Mounted on
rootfs                                                 rootfs     19751804 4001308   14747132  22% /
udev                                                   devtmpfs      10240       0      10240   0% /dev
tmpfs                                                  tmpfs        205780     628     205152   1% /run
/dev/disk/by-uuid/4c27d106-25c1-4fe4-9484-f5f50a8fc707 ext4       19751804 4001308   14747132  22% /
tmpfs                                                  tmpfs          5120       0       5120   0% /run/lock
tmpfs                                                  tmpfs        591760     224     591536   1% /run/shm
none                                                   prl_fs   4294967296       0 4294967296   0% /media/psf
/dev/sr0                                               iso9660       14680   14680          0 100% /media/cdrom0
"""

    def test_hdd_list(self):
        hdd_info = hardware.HarddriveInfo()
        hdd_info._get_df_output = lambda: self.df_output

        expected = [
            {
                'free_size_kb': 10240,
                'name': 'udev',
                'size_kb': 10240,
                'file_system': 'devtmpfs'
            },
            {
                'free_size_kb': 14747132,
                'name': '/dev/disk/by-uuid/4c27d106-25c1-4fe4-9484-f5f50a8fc707',
                'size_kb': 18748440,
                'file_system': 'ext4'
            },
            {
                'free_size_kb': 0,
                'name': '/dev/sr0',
                'size_kb': 14680,
                'file_system': 'iso9660'
            }
        ]

        self.assertEqual(hdd_info.get_hdd_list(), expected)


class TestHarddriveInfoMac(unittest.TestCase):
    pass


class TestNicInfoLinux(unittest.TestCase):
    pass


class TestNicInfoMac(unittest.TestCase):
    pass


class TestMemoryInfoLinux(unittest.TestCase):
    pass


class TestMemoryInfoMac(unittest.TestCase):
    pass
