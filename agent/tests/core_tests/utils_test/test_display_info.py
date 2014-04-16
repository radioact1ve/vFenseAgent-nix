import unittest

from src.utils import hardware


class TestDisplayInfoLinux(unittest.TestCase):

    # \n\n is needed at the end so that the parsing can stop.
    # This simulates the real output from lscpi -v
    one = \
        """00:02.0 VGA compatible controller: Cirrus Logic GD 5446 (prog-if 00 [VGA controller])
            Subsystem: Red Hat, Inc Device 1100
            Flags: fast devsel
            Memory at fc000000 (32-bit, prefetchable) [size=32M]
            Memory at febf1000 (32-bit, non-prefetchable) [size=4K]
            Expansion ROM at febe0000 [disabled] [size=64K]
            Kernel modules: cirrusfb\n\n"""

    two = \
        """01:00.0 VGA compatible controller: Parallels, Inc. Accelerated Virtual Video Adapter (prog-if 00 [VGA controller])
            Subsystem: Parallels, Inc. Device 0400
            Flags: 66MHz, medium devsel, IRQ 21
            I/O ports at 6000 [size=32]
            Memory at b0000000 (32-bit, prefetchable) [size=32M]
            Expansion ROM at e2000000 [disabled] [size=64K]
            Kernel driver in use: prl_tg\n\n"""

    def test_display_info_parsing_multiple_memory_entries(self):
        display_info = hardware.DisplayInfo()
        expected = [{
            'speed_mhz': 0,
            'name': 'Cirrus Logic GD 5446 (prog-if 00 [VGA controller])',
            'ram_kb': 32772
        }]

        display_info._get_pci_device_info = lambda: self.one

        self.assertEqual(expected, display_info.get_display_list())

    def test_display_info_parsing_single_memory_entry(self):
        display_info = hardware.DisplayInfo()
        expected = [{
            'speed_mhz': 66,
            'name': 'Parallels, Inc. Accelerated Virtual Video Adapter (prog-if 00 [VGA controller])',
            'ram_kb': 32768
        }]

        display_info._get_pci_device_info = lambda: self.two

        self.assertEqual(expected, display_info.get_display_list())

    def test_display_info_parsing_multiple_vgas(self):
        display_info = hardware.DisplayInfo()
        three = self.one + self.two
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

        display_info._get_pci_device_info = lambda: three

        self.assertEqual(expected, display_info.get_display_list())


class TestDisplayInfoMac(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
