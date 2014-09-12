import inspect
import six
from six.moves import zip_longest
from types import FunctionType
from unittest import TestCase
import functools
import pprint

from ddtest.exceptions import DataDrivenFixtureError
from ddtest.constants import DATA_DRIVEN_TEST_ATTR, DATA_DRIVEN_TEST_PREFIX


def data_driven_test(*dataset_sources, **kwargs):
    """Used to define the data source for a data driven test in a
    DataDrivenFixture decorated Unittest TestCase class"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # dataset_source checked for backward compatibility
            combined_lists = kwargs.get("dataset_source") or []
            for dataset_list in dataset_sources:
                combined_lists += dataset_list
            setattr(func, DATA_DRIVEN_TEST_ATTR, combined_lists)
            return func
        return wrapper()
    return decorator


def DataDrivenFixture(cls):
    """Generates new unittest test methods from methods defined in the
    decorated class"""

    if not issubclass(cls, TestCase):
        raise DataDrivenFixtureError

    test_case_attrs = dir(cls)
    for attr_name in test_case_attrs:
        if attr_name.startswith(DATA_DRIVEN_TEST_PREFIX) is False:
            # Not a data driven test, skip it
            continue

        original_test = getattr(cls, attr_name, None).__func__
        pprint.pprint(dir(original_test))
        test_data = getattr(original_test, DATA_DRIVEN_TEST_ATTR, None)

        if test_data is None:
            # no data was provided to the datasource decorator or this is not a
            # data driven test, skip it.
            continue

        for dataset in test_data:
            # Name the new test based on original and dataset names
            base_test_name = str(original_test.__name__)[
                int(len(DATA_DRIVEN_TEST_PREFIX)):]
            new_test_name = "test_{0}_{1}".format(
                base_test_name, dataset.name)

            # Create a new test from the old test
            new_test = FunctionType(
                six.get_function_code(original_test),
                six.get_function_globals(original_test),
                name=new_test_name)

            # Copy over any other attributes the original test had (mainly to
            # support test tag decorator)
            for attr in list(set(dir(original_test)) - set(dir(new_test))):
                setattr(new_test, attr, getattr(original_test, attr))

            # Change the new test's default keyword values to the appropriate
            # new data as defined by the datasource decorator
            args, _, _, defaults = inspect.getargspec(original_test)

            # Self doesn't have a default, so we need to remove it
            args.remove('self')

            # Make sure we take into account required arguments
            kwargs = dict(
                zip_longest(
                    args[::-1], list(defaults or ())[::-1], fillvalue=None))

            kwargs.update(dataset.data)

            # Make sure the updated values are in the correct order
            new_default_values = [kwargs[arg] for arg in args]
            setattr(new_test, "func_defaults", tuple(new_default_values))

            # Add the new test to the decorated TestCase
            setattr(cls, new_test_name, new_test)

    return cls
