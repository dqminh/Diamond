from test import CollectorTestCase
from test import get_collector_config
from test import unittest
from mock import Mock
from mock import patch
from cpuacct_cgroup import CPUacctCGroupCollector

class TestCPUacctCGroupCollector(CollectorTestCase):
    def setUp(self):
        config = get_collector_config('CPUCacctCGroupCollector', {
            'interval': 10
        })

        self.collector = CPUacctCGroupCollector(config, None)

    def test_import(self):
        self.assertTrue(CPUacctCGroupCollector)
