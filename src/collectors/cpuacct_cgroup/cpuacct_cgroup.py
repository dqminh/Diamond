# coding=utf-8

"""
The CPUCGroupCollector collects CPU utilization metric for cgroups

#### Dependencies

/sys/fs/cgroup/cpuacct/cpuacct.stat
"""

import diamond.collector
import os

class CPUacctCGroupCollector(diamond.collector.Collector):
    CPUACCT_PATH = '/sys/fs/cgroup/cpuacct/'
    MAX_VALUES = {
        'user': diamond.collector.MAX_COUNTER,
        'system': diamond.collector.MAX_COUNTER,
    }

    def get_default_config_help(self):
        config_help = super(CPUacctCGroupCollector, self).get_default_config_help()
        config_help.update({
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(CPUacctCGroupCollector, self).get_default_config()
        config.update({
            'enabled':  'True',
            'path':     'cpuacct',
            'xenfix':   None,
        })
        return config

    def collect(self):
        """
        Collector cpu stats for cgroups
        What we are going to do

        - walk /sys/fs/cgroup/cpuacct and its subfolder
        - find all cpuacct.stat and get utime and stime from them
        - if cpuacct.stat is inside subfolder, associate them with the
          combination of parent folder's name
        - publish the stat for fun and profit
        """
        matches = []
        for root, dirnames, filenames in os.walk(self.CPUACCT_PATH):
            for filename in filenames:
                if filename == 'cpuacct.stat':
                    # matches will contain a tuple contain path to cpuacct.stat
                    # and the parent of the stat
                    parent = root.replace(self.CPUACCT_PATH, "").replace("/", ".")
                    if parent == '':
                        parent = 'system'
                    matches.append((parent, os.path.join(root, filename)))

        # Read utime and stime from cpuacct files
        results = {}
        for match in matches:
            results[match[0]] = {}
            with open(match[1]) as file:
                elements = [ line.split() for line in file ]
                for el in elements:
                    results[match[0]][el[0]] = el[1]

        # create metrics from collected utimes and stimes for cgroups
        metrics = {}
        for parent, cpuacct in results.iteritems():
            for key, value in cpuacct.iteritems():
                # Get Metric Name
                metric_name = '.'.join([parent, key])
                # Get actual data
                metrics[metric_name] = self.derivative(metric_name, long(value),
                        self.MAX_VALUES[key])

        ## Publish Metric Derivative
        for metric_name in metrics.keys():
            self.publish(metric_name, metrics[metric_name])
        return True
