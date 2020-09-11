import numpy as np
from src.read_data.read_case_study_data import CaseStudy
from src.heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger
from src.heat_exchanger_network.exchanger_addresses import ExchangerAddresses
from src.heat_exchanger_network.thermodynamic_parameter import ThermodynamicParameter

import os
import pytest
import mock
from mock import patch


def setup_module():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('unit_tests')
    addresses = ExchangerAddresses(test_case)
    parameter = ThermodynamicParameter(test_case)
    test_exchanger = HeatExchanger(addresses, parameter, test_case, 0)
    return test_exchanger, test_case, addresses, parameter


def test_topology():
    test_exchanger, test_case, exchanger_adresses, _ = setup_module()
    heat_exchanger_topology = np.array(test_case.initial_exchanger_address_matrix, dtype=int)[0, 1:9]
    heat_exchanger_topology.tolist()
    heat_exchanger_topology[3] = not heat_exchanger_topology[3]
    heat_exchanger_topology[4] = not heat_exchanger_topology[4]
    heat_exchanger_topology[5] = not heat_exchanger_topology[5]
    heat_exchanger_topology[6] = not heat_exchanger_topology[6]
    heat_exchanger_topology[7] = not heat_exchanger_topology[7]
    exchanger_adresses.matrix[0, 0] += 1
    exchanger_adresses.matrix[0, 1] += 1
    exchanger_adresses.matrix[0, 2] += 1
    exchanger_adresses.matrix[0, 3] = not exchanger_adresses.matrix[0, 3]
    exchanger_adresses.matrix[0, 4] = not exchanger_adresses.matrix[0, 4]
    exchanger_adresses.matrix[0, 5] = not exchanger_adresses.matrix[0, 5]
    exchanger_adresses.matrix[0, 6] = not exchanger_adresses.matrix[0, 6]
    exchanger_adresses.matrix[0, 7] = not exchanger_adresses.matrix[0, 7]

    for indice in enumerate(heat_exchanger_topology):
        assert heat_exchanger_topology[indice[0]] == test_exchanger.topology.address_vector[indice[0]]

    assert test_exchanger.topology.initial_existent != test_exchanger.topology.existent


def test_operation_parameter():
    test_exchanger, test_case, _, _ = setup_module()
    initial_area = test_case.initial_exchanger_address_matrix['A_ex'][0] * 1.2
    assert initial_area == test_exchanger.operation_parameter.initial_area * 1.2


def test_logarithmic_temperature_differences_no_mixer():
    test_exchanger, test_case, _, test_parameter = setup_module()
    logarithmic_mean_temperature_difference = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[1][operating_case, 0] = 400
        test_parameter.matrix[2][operating_case, 0] = 300
        test_parameter.matrix[3][operating_case, 0] = 250
        test_parameter.matrix[4][operating_case, 0] = 350
        logarithmic_mean_temperature_difference[operating_case] = 400 - 350
    for operating_case in test_case.range_operating_cases:
        assert logarithmic_mean_temperature_difference[operating_case] == test_exchanger.operation_parameter.logarithmic_mean_temperature_differences_no_mixer[operating_case]

    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[1][operating_case, 0] = 400
        test_parameter.matrix[2][operating_case, 0] = 300
        test_parameter.matrix[3][operating_case, 0] = 290
        test_parameter.matrix[4][operating_case, 0] = 350
        logarithmic_mean_temperature_difference[operating_case] = (10-50) / np.log(10/50)
    for operating_case in test_case.range_operating_cases:
        assert logarithmic_mean_temperature_difference[operating_case] == test_exchanger.operation_parameter.logarithmic_mean_temperature_differences_no_mixer[operating_case]


def test_area():
    test_exchanger, test_case, _, test_parameter = setup_module()
    hot_streams = test_case.hot_streams
    cold_streams = test_case.cold_streams
    topology = test_exchanger.topology
    logarithmic_mean_temperature_difference = np.zeros([test_case.number_operating_cases])
    areas = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] = 2000
        test_parameter.matrix[1][operating_case, 0] = 400 * (operating_case + 1)
        test_parameter.matrix[2][operating_case, 0] = 300 * (operating_case + 1)
        test_parameter.matrix[3][operating_case, 0] = 290 * (operating_case + 1)
        test_parameter.matrix[4][operating_case, 0] = 350 * (operating_case + 1)
        temperature_difference_1 = test_parameter.matrix[2][operating_case, 0] - test_parameter.matrix[3][operating_case, 0]
        temperature_difference_2 = test_parameter.matrix[1][operating_case, 0] - test_parameter.matrix[4][operating_case, 0]
        logarithmic_mean_temperature_difference[operating_case] = (temperature_difference_1 - temperature_difference_2) / np.log(temperature_difference_1 / temperature_difference_2)

    for operating_case in test_case.range_operating_cases:
        overall_heat_transfer_coefficient = 1 / (1 / hot_streams[topology.hot_stream].film_heat_transfer_coefficients[operating_case] +
                                                 1 / cold_streams[topology.cold_stream].film_heat_transfer_coefficients[operating_case])
        areas[operating_case] = test_exchanger.operation_parameter.heat_loads[operating_case] / \
            (overall_heat_transfer_coefficient * test_exchanger.operation_parameter.logarithmic_mean_temperature_differences_no_mixer[operating_case])
    for operating_case in test_case.range_operating_cases:
        assert areas[operating_case] == test_exchanger.operation_parameter.needed_areas[operating_case]
    assert np.max(areas) == test_exchanger.operation_parameter.area


def test_logarithmic_temperature_differences():
    test_exchanger, test_case, _, test_parameter = setup_module()
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] = 2000
        test_parameter.matrix[1][operating_case, 0] = 400 * (operating_case + 1)
        test_parameter.matrix[2][operating_case, 0] = 300 * (operating_case + 1)
        test_parameter.matrix[3][operating_case, 0] = 290 * (operating_case + 1)
        test_parameter.matrix[4][operating_case, 0] = 350 * (operating_case + 1)
        logarithmic_mean_temperature_difference = test_parameter.matrix[0][operating_case, 0] / (test_exchanger.operation_parameter.overall_heat_transfer_coefficients[operating_case] * test_exchanger.operation_parameter.area)
        assert logarithmic_mean_temperature_difference == test_exchanger.operation_parameter.logarithmic_mean_temperature_differences[operating_case]


def test_mixer_type(monkeypatch):
    _, test_case, test_addresses, test_parameter = setup_module()
    test_exchanger = HeatExchanger(test_addresses, test_parameter, test_case, 0)
    monkeypatch.setattr('src.heat_exchanger_network.heat_exchanger.heat_exchanger.OperationParameter.random_choice.__defaults__', (0,))
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] = 2000
        test_parameter.matrix[1][operating_case, 0] = 400 * (operating_case + 1)
        test_parameter.matrix[2][operating_case, 0] = 300 * (operating_case + 1)
        test_parameter.matrix[3][operating_case, 0] = 290 * (operating_case + 1)
        test_parameter.matrix[4][operating_case, 0] = 350 * (operating_case + 1)
    test_exchanger.operation_parameter.one_mixer_per_hex = True
    for operating_case in test_case.range_operating_cases:
        assert test_exchanger.operation_parameter.mixer_types[operating_case] == 'admixer_cold'
    monkeypatch.setattr('src.heat_exchanger_network.heat_exchanger.heat_exchanger.OperationParameter.random_choice.__defaults__', (None,))
    test_exchanger.operation_parameter.one_mixer_per_hex = False
    base_case = np.squeeze(np.argwhere(test_exchanger.operation_parameter.needed_areas == test_exchanger.operation_parameter.area))
    for operating_case in test_case.range_operating_cases:
        if operating_case != base_case:
            assert test_exchanger.operation_parameter.mixer_types[operating_case] != test_exchanger.operation_parameter.mixer_types[base_case]


def test_bypass_hot_stream():
    _, test_case, test_addresses, test_parameter = setup_module()
    test_exchanger = HeatExchanger(test_addresses, test_parameter, test_case, 0)
    with mock.patch('src.heat_exchanger_network.heat_exchanger.heat_exchanger.OperationParameter.mixer_types', new_callable=mock.PropertyMock) as mock_property:
        mock_property.return_value = ['none', 'bypass_hot']
        for operating_case in test_case.range_operating_cases:
            test_parameter.matrix[0][operating_case, 0] = 2000
            test_parameter.matrix[1][operating_case, 0] = 400 * (operating_case + 1)
            test_parameter.matrix[2][operating_case, 0] = 300 * (operating_case + 1)
            test_parameter.matrix[3][operating_case, 0] = 290 * (operating_case + 1)
            test_parameter.matrix[4][operating_case, 0] = 350 * (operating_case + 1)
        for operating_case in test_case.range_operating_cases:
            assert test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] == test_exchanger.operation_parameter.temperatures_hot_stream_before_hex[operating_case]
            assert test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] == test_exchanger.operation_parameter.temperatures_cold_stream_before_hex[operating_case]
            assert test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] == test_exchanger.operation_parameter.temperatures_cold_stream_after_hex[operating_case]
            if operating_case == 0:
                assert test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] == test_exchanger.operation_parameter.temperatures_hot_stream_after_hex[operating_case]
            elif operating_case == 1:
                assert test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] == (test_exchanger.operation_parameter.temperatures_hot_stream_after_hex[operating_case] - test_exchanger.operation_parameter.temperatures_hot_stream_before_hex[operating_case] * test_exchanger.operation_parameter.mixer_fractions_hot_stream[operating_case]) / (1-test_exchanger.operation_parameter.mixer_fractions_hot_stream[operating_case])
            temperature_difference_1 = test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] - test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case]
            temperature_difference_2 = test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] - test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case]
            if temperature_difference_1 == temperature_difference_2:
                logarithmic_mean_temperature_difference = temperature_difference_1
            else:
                logarithmic_mean_temperature_difference = (temperature_difference_1 - temperature_difference_2) / np.log(temperature_difference_1 / temperature_difference_2)
            assert logarithmic_mean_temperature_difference - test_exchanger.operation_parameter.logarithmic_mean_temperature_differences[operating_case] <= 10e-3


def test_costs_coefficients():
    test_exchanger, test_case, _, _ = setup_module()
    base_costs = test_case.initial_exchanger_address_matrix['c_0_HEX'][0]
    assert base_costs == test_exchanger.costs.base_costs
    specific_area_costs = test_case.initial_exchanger_address_matrix['c_A_HEX'][0]
    assert specific_area_costs == test_exchanger.costs.specific_area_costs
    degression_area = test_case.initial_exchanger_address_matrix['d_f_HEX'][0]
    assert degression_area == test_exchanger.costs.degression_area
    remove_costs = test_case.initial_exchanger_address_matrix['c_R_HEX'][0]
    assert remove_costs == test_exchanger.costs.remove_costs
    base_split_costs = test_case.initial_exchanger_address_matrix['c_0_split'][0]
    assert base_split_costs == test_exchanger.costs.base_split_costs
    specific_split_costs = test_case.initial_exchanger_address_matrix['c_M_split'][0]
    assert specific_split_costs == test_exchanger.costs.specific_split_costs
    degression_split = test_case.initial_exchanger_address_matrix['d_f_split'][0]
    assert degression_split == test_exchanger.costs.degression_split
    remove_split_costs = test_case.initial_exchanger_address_matrix['c_R_split'][0]
    assert remove_split_costs == test_exchanger.costs.remove_split_costs
    base_bypass_costs = test_case.initial_exchanger_address_matrix['c_0_bypass'][0]
    assert base_bypass_costs == test_exchanger.costs.base_bypass_costs
    specific_bypass_costs = test_case.initial_exchanger_address_matrix['c_M_bypass'][0]
    assert specific_bypass_costs == test_exchanger.costs.specific_bypass_costs
    degression_bypass = test_case.initial_exchanger_address_matrix['d_f_bypass'][0]
    assert degression_bypass == test_exchanger.costs.degression_bypass
    remove_bypass_costs = test_case.initial_exchanger_address_matrix['c_R_bypass'][0]
    assert remove_bypass_costs == test_exchanger.costs.remove_bypass_costs
    base_admixer_costs = test_case.initial_exchanger_address_matrix['c_0_admixer'][0]
    assert base_admixer_costs == test_exchanger.costs.base_admixer_costs
    specific_admixer_costs = test_case.initial_exchanger_address_matrix['c_M_admixer'][0]
    assert specific_admixer_costs == test_exchanger.costs.specific_admixer_costs
    degression_admixer = test_case.initial_exchanger_address_matrix['d_f_admixer'][0]
    assert degression_admixer == test_exchanger.costs.degression_admixer
    remove_admixer_costs = test_case.initial_exchanger_address_matrix['c_R_admixer'][0]
    assert remove_admixer_costs == test_exchanger.costs.remove_admixer_costs
    base_repipe_costs = test_case.initial_exchanger_address_matrix['c_0_repipe'][0]
    assert base_repipe_costs == test_exchanger.costs.base_repipe_costs
    specific_repipe_costs = test_case.initial_exchanger_address_matrix['c_M_repipe'][0]
    assert specific_repipe_costs == test_exchanger.costs.specific_repipe_costs
    degression_repipe = test_case.initial_exchanger_address_matrix['d_f_repipe'][0]
    assert degression_repipe == test_exchanger.costs.degression_repipe
    base_resequence_costs = test_case.initial_exchanger_address_matrix['c_0_resequence'][0]
    assert base_resequence_costs == test_exchanger.costs.base_resequence_costs
    specific_resequence_costs = test_case.initial_exchanger_address_matrix['c_M_resequence'][0]
    assert specific_resequence_costs == test_exchanger.costs.specific_resequence_costs
    degression_resequence = test_case.initial_exchanger_address_matrix['d_f_resequence'][0]
    assert degression_resequence == test_exchanger.costs.degression_resequence


def test_heat_exchanger_costs():
    test_exchanger, test_case, addresses, test_parameter = setup_module()
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] = 5000
        test_parameter.matrix[1][operating_case, 0] = 400
        test_parameter.matrix[2][operating_case, 0] = 300
        test_parameter.matrix[3][operating_case, 0] = 290
        test_parameter.matrix[4][operating_case, 0] = 350
    exchanger_costs = test_exchanger.costs.base_costs + test_exchanger.costs.specific_area_costs * (test_exchanger.operation_parameter.area - test_exchanger.operation_parameter.initial_area)**test_exchanger.costs.degression_area
    assert exchanger_costs == test_exchanger.exchanger_costs
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] *= 10e-2
    assert test_exchanger.exchanger_costs == 0
    addresses.matrix[0, 7] = False
    assert test_exchanger.exchanger_costs == test_exchanger.costs.remove_costs
    test_exchanger_5 = HeatExchanger(addresses, test_parameter, test_case, 5)
    addresses.matrix[5, 7] = True
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 5] = 5000
        test_parameter.matrix[1][operating_case, 5] = 400
        test_parameter.matrix[2][operating_case, 5] = 300
        test_parameter.matrix[3][operating_case, 5] = 290
        test_parameter.matrix[4][operating_case, 5] = 350
    exchanger_costs_5 = test_exchanger_5.costs.base_costs + test_exchanger_5.costs.specific_area_costs * (test_exchanger_5.operation_parameter.area - test_exchanger_5.operation_parameter.initial_area)**test_exchanger_5.costs.degression_area
    assert exchanger_costs_5 == test_exchanger_5.exchanger_costs
    addresses.matrix[5, 7] = False
    assert test_exchanger_5.exchanger_costs == 0


def test_admixer_costs():
    test_exchanger, _, addresses, _ = setup_module()
    addresses.matrix[0, 4] = True
    addresses.matrix[0, 6] = True
    assert test_exchanger.admixer_costs == test_exchanger.costs.base_admixer_costs * 2
    addresses.matrix[0, 4] = False
    addresses.matrix[0, 6] = True
    assert test_exchanger.admixer_costs == test_exchanger.costs.base_admixer_costs + test_exchanger.costs.remove_admixer_costs
    addresses.matrix[0, 4] = False
    addresses.matrix[0, 6] = False
    assert test_exchanger.admixer_costs == 0
    addresses.matrix[0, 4] = True
    addresses.matrix[0, 6] = False
    assert test_exchanger.admixer_costs == test_exchanger.admixer_costs == test_exchanger.costs.base_admixer_costs


def test_bypass_costs():
    test_exchanger, _, addresses, _ = setup_module()
    addresses.matrix[0, 3] = True
    addresses.matrix[0, 5] = False
    assert test_exchanger.bypass_costs == 0
    addresses.matrix[0, 3] = False
    addresses.matrix[0, 5] = True
    assert test_exchanger.bypass_costs == test_exchanger.costs.remove_bypass_costs + test_exchanger.costs.base_bypass_costs
    addresses.matrix[0, 3] = False
    addresses.matrix[0, 5] = False
    assert test_exchanger.bypass_costs == test_exchanger.costs.remove_bypass_costs
    addresses.matrix[0, 3] = True
    addresses.matrix[0, 5] = True
    assert test_exchanger.bypass_costs == test_exchanger.costs.base_bypass_costs


def test_feasible():
    test_exchanger, test_case, _, test_parameter = setup_module()
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] = 2000
        test_parameter.matrix[1][operating_case, 0] = 400
        test_parameter.matrix[2][operating_case, 0] = 300
        test_parameter.matrix[3][operating_case, 0] = 290
        test_parameter.matrix[4][operating_case, 0] = 350
    assert test_exchanger.is_feasible
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] = 2000
        test_parameter.matrix[1][operating_case, 0] = 200
        test_parameter.matrix[2][operating_case, 0] = 300
        test_parameter.matrix[3][operating_case, 0] = 400
        test_parameter.matrix[4][operating_case, 0] = 350
    assert not test_exchanger.is_feasible
    for operating_case in test_case.range_operating_cases:
        test_parameter.matrix[0][operating_case, 0] = 2000
        test_parameter.matrix[1][operating_case, 0] = 400
        test_parameter.matrix[2][operating_case, 0] = 300
        test_parameter.matrix[3][operating_case, 0] = 400
        test_parameter.matrix[4][operating_case, 0] = 350
    assert not test_exchanger.is_feasible
