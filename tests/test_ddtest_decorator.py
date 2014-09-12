import unittest
from ddtest.decorators import DataDrivenFixture, data_driven_test
from ddtest.datasets import TestMultiplier, DatasetGenerator


@DataDrivenFixture
class DDTestFixture(unittest.TestCase):

    @unittest.skip
    @data_driven_test(TestMultiplier(1))
    def ddtest_sample_test(self):
        pass

    #@data_driven_test(
    #    DatasetGenerator([{"param": "test1"}, {"param": "test2"}]))
    #def ddtest_handle_params(self, param=None):
    #    assert param is not None
