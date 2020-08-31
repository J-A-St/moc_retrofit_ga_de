import os
import pytest
import numpy as np

from src.read_data.read_case_study_data import CaseStudy
from src.heat_exchanger_network.stream import Stream
from src.heat_exchanger_network.restrictions import Restrictions
from src.heat_exchanger_network.operating_case import OperatingCase
from src.heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger
from src.heat_exchanger_network.economics import Economics
from src.heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork


def setup_model():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('unit_tests')
    test_network = HeatExchangerNetwork(test_test_case)
    return test_network, test_test_case


def test_heat_exchanger_address_matrix():
    test_network, test_case = setup_model()
    for exchanger in test_case.range_heat_exchangers:
        assert all(test_network.address_matrix[exchanger] == test_network.heat_exchangers[exchanger].topology.address_vector)


def test_operation_parameter_matrix():
    test_network, test_case = setup_model()
    for exchanger in test_case.range_heat_exchangers:
        for parameter in range(len(test_network.heat_exchangers[0].operation_parameter.matrix)):
            assert all(test_network.operation_parameter_matrix[parameter, exchanger] == test_network.heat_exchangers[exchanger].operation_parameter.matrix[parameter])


def test_balance_utility_heat_exchangers():
    test_network, test_case = setup_model()
    for exchanger in test_case.range_balance_utility_heat_exchangers:
        utility_type = 'H'
        connected_stream = test_network.balance_utility_heat_exchanger[exchanger].connected_stream + 1
        initial_area = test_network.balance_utility_heat_exchanger[exchanger].initial_area * 1.2
        for operating_case in test_case.range_operating_cases:
            initial_heat_load = test_network.balance_utility_heat_exchanger[exchanger].initial_heat_loads[operating_case] * 1.2
            test_network.balance_utility_heat_exchanger[exchanger].initial_heat_loads[operating_case] *= 1.2
            assert initial_heat_load == test_network.balance_utility_heat_exchanger[exchanger].initial_heat_loads[operating_case]
        base_cost = test_network.balance_utility_heat_exchanger[exchanger].base_cost * 1.2
        specific_area_cost = test_network.balance_utility_heat_exchanger[exchanger].specific_area_cost * 1.2
        degression_area = test_network.balance_utility_heat_exchanger[exchanger].degression_area * 1.2
        address_vector = [utility_type, connected_stream, initial_area, base_cost, specific_area_cost, degression_area]
        test_network.balance_utility_heat_exchanger[exchanger].utility_type = 'H'
        test_network.balance_utility_heat_exchanger[exchanger].connected_stream += 1
        test_network.balance_utility_heat_exchanger[exchanger].initial_area *= 1.2
        test_network.balance_utility_heat_exchanger[exchanger].base_cost *= 1.2
        test_network.balance_utility_heat_exchanger[exchanger].specific_area_cost *= 1.2
        test_network.balance_utility_heat_exchanger[exchanger].degression_area *= 1.2
        for i, _ in enumerate(test_network.balance_utility_heat_exchanger[exchanger].address_vector):
            assert test_network.balance_utility_heat_exchanger[exchanger].address_vector[i] == address_vector[i]


def test_restrictions():
    test_network, test_case = setup_model()
    assert test_network.restrictions.max_splits == test_case.manual_parameter['MaxSplitsPerk'].iloc[0]
    assert test_network.restrictions.max_bypass_fraction == test_case.manual_parameter['MaxBypass'].iloc[0]
    assert test_network.restrictions.max_admix_fraction == test_case.manual_parameter['MaxAdmix'].iloc[0]
    assert test_network.restrictions.temperature_difference_upper_bound == test_case.manual_parameter['dTUb'].iloc[0]
    assert test_network.restrictions.temperature_difference_lower_bound == test_case.manual_parameter['dTLb'].iloc[0]
    assert test_network.restrictions.minimal_heat_load == test_case.manual_parameter['MinimalHeatLoad'].iloc[0]


def test_economics():
    pass
