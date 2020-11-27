import os
import sys
import platform
import mock
import numpy as np

operating_system = platform.system()
if operating_system == 'Windows':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'\\src')
elif operating_system == 'Linux':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/src')


from read_data.read_case_study_data import CaseStudy
from heat_exchanger_network.exchanger_addresses import ExchangerAddresses
from heat_exchanger_network.thermodynamic_parameter import ThermodynamicParameter
from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork
from heat_exchanger_network.heat_exchanger.balance_utility_heat_exchanger import BalanceUtilityHeatExchanger


def setup_model():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('unit_tests')
    test_network = HeatExchangerNetwork(test_case)
    test_addresses = ExchangerAddresses(test_case)
    test_parameter = ThermodynamicParameter(test_case, test_addresses)
    test_balance_exchanger = BalanceUtilityHeatExchanger(test_case, test_parameter, 0)
    return test_balance_exchanger, test_case, test_network


def test_heat_loads():
    test_balance_exchanger, test_case, test_network = setup_model()
    for operating_case in test_case.range_operating_cases:
        if test_balance_exchanger.utility_type == 'HU':
            assert test_balance_exchanger.heat_loads[operating_case] == test_balance_exchanger.heat_capacity_flows[operating_case] * (test_network.cold_streams[test_balance_exchanger.connected_stream].target_temperatures[operating_case] - test_network.thermodynamic_parameter.enthalpy_stage_temperatures_cold_streams[test_balance_exchanger.connected_stream, 0, operating_case])
        if test_balance_exchanger.utility_type == 'CU':
            assert test_balance_exchanger.heat_loads[operating_case] == test_balance_exchanger.heat_capacity_flows[operating_case] * (test_network.thermodynamic_parameter.enthalpy_stage_temperatures_hot_streams[test_balance_exchanger.connected_stream, test_case.number_enthalpy_stages, operating_case] - test_network.hot_streams[test_balance_exchanger.connected_stream].target_temperatures[operating_case])


def test_logarithmic_mean_temperature_difference():
    test_balance_exchanger, test_case, test_network = setup_model()
    for operating_case in test_case.range_operating_cases:
        if test_balance_exchanger.utility_type == 'HU':
            inlet_temperatures_utility = test_case.hot_streams[test_case.hot_utilities_indices[0]].supply_temperatures[operating_case]
            outlet_temperatures_utility = test_case.hot_streams[test_case.hot_utilities_indices[0]].target_temperatures[operating_case]
            inlet_temperatures_stream = test_case.cold_streams[test_balance_exchanger.connected_stream].supply_temperatures[operating_case]
            outlet_temperatures_stream = test_network.thermodynamic_parameter.enthalpy_stage_temperatures_cold_streams[test_balance_exchanger.connected_stream, test_case.number_enthalpy_stages, operating_case]
            temperature_difference_a = outlet_temperatures_utility - inlet_temperatures_stream
            temperature_difference_b = inlet_temperatures_utility - outlet_temperatures_stream

        if test_balance_exchanger.utility_type == 'CU':
            inlet_temperatures_utility = test_case.cold_streams[test_case.cold_utilities_indices[0]].supply_temperatures[operating_case]
            outlet_temperatures_utility = test_case.cold_streams[test_case.cold_utilities_indices[0]].target_temperatures[operating_case]
            inlet_temperatures_stream = test_network.thermodynamic_parameter.enthalpy_stage_temperatures_hot_streams[test_balance_exchanger.connected_stream, 0, operating_case]
            outlet_temperatures_stream = test_case.hot_streams[test_balance_exchanger.connected_stream].target_temperatures[operating_case]
            temperature_difference_a = outlet_temperatures_stream - inlet_temperatures_utility
            temperature_difference_b = inlet_temperatures_stream - outlet_temperatures_utility

        assert test_balance_exchanger.logarithmic_mean_temperature_differences[operating_case] == (temperature_difference_a - temperature_difference_b) / np.log(temperature_difference_a / temperature_difference_b)


def test_areas():
    test_balance_exchanger, test_case, test_network = setup_model()
    test_balance_exchanger = BalanceUtilityHeatExchanger(test_case, test_network.thermodynamic_parameter, 0)
    with mock.patch('heat_exchanger_network.heat_exchanger.balance_utility_heat_exchanger.BalanceUtilityHeatExchanger.logarithmic_mean_temperature_differences', new_callable=mock.PropertyMock) as mock_property:
        mock_property.return_value = [10, 50]
        needed_areas = np.zeros([2])
        for operating_case in test_case.range_operating_cases:
            needed_areas[operating_case] = test_balance_exchanger.heat_loads[operating_case] / (test_balance_exchanger.overall_heat_transfer_coefficient[operating_case] * test_balance_exchanger.logarithmic_mean_temperature_differences[operating_case])
            assert test_balance_exchanger.needed_areas[operating_case] == needed_areas[operating_case]
        assert test_balance_exchanger.area == np.max(needed_areas)
