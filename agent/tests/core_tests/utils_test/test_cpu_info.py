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
