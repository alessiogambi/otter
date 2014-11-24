"""
System Integration tests autoscaling with RCv3
"""

import random
import time
import pprint

from test_repo.autoscale.fixtures import AutoscaleFixture
from autoscale.models.response.autoscale_response import RackConnectLBPools
from cafe.drivers.unittest.decorators import tags


class AutoscaleRCV3Tests(AutoscaleFixture):
    """
    System tests to verify RCv3 integration with autoscale
    """
    @classmethod
    def setUpClass(cls):
        """
        Create 3 load balancers.

        This is just a dummy to get something, anything, working at all.
        """
        super(AutoscaleRCV3Tests, cls).setUpClass()
        cls.load_balancer_1_response = cls.lbaas_client.create_load_balancer('test', [],
                                                                             'HTTP', 80, "PUBLIC")
        cls.load_balancer_1 = cls.load_balancer_1_response.entity.id
        cls.resources.add(cls.load_balancer_1, cls.lbaas_client.delete_load_balancer)
        cls.load_balancer_2_response = cls.lbaas_client.create_load_balancer('test', [],
                                                                             'HTTP', 80, "PUBLIC")
        cls.load_balancer_2 = cls.load_balancer_2_response.entity.id
        cls.resources.add(cls.load_balancer_2, cls.lbaas_client.delete_load_balancer)
        cls.load_balancer_3_response = cls.lbaas_client.create_load_balancer('test', [],
                                                                             'HTTP', 80, "PUBLIC")
        cls.load_balancer_3 = cls.load_balancer_3_response.entity.id
        cls.resources.add(cls.load_balancer_3, cls.lbaas_client.delete_load_balancer)
        cls.lb_other_region = 0000

    @tags(speed='slow', type='lbaas')
    def test_always_works(self):
        pools_response = self.rcv3_client.try_marshalling()
        pools = pools_response.entity
        pp = pprint.PrettyPrinter(indent=4)
        assert(pools is not None)
        pp.pprint(vars(pools))
        self.assertEquals(2, 2)

