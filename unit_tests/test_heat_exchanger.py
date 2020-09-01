import os

import numpy as np

from src.read_data.read_case_study_data import CaseStudy
from src.heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger
from src.heat_exchanger_network.exchanger_addresses import ExchangerAddresses


def setup_module():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('unit_tests')
    addresses = ExchangerAddresses(test_case)
    test_exchanger = HeatExchanger(addresses, test_case, 0)
    return test_exchanger, test_case, addresses


def test_topology():
    test_exchanger, test_case, exchanger_adresses = setup_module()
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
    test_exchanger, test_case, _ = setup_module()
    initial_area = test_case.initial_exchanger_address_matrix['A_ex'][0] * 1.2
    assert initial_area == test_exchanger.operation_parameter.initial_area * 1.2


def test_logarithmic_temperature_differences():
    test_exchanger, test_case, _ = setup_module()
    logarithmic_mean_temperature_difference = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 250
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_mean_temperature_difference[operating_case] = 400 - 350
    for operating_case in test_case.range_operating_cases:
        assert logarithmic_mean_temperature_difference[operating_case] == test_exchanger.operation_parameter.logarithmic_mean_temperature_differences[operating_case]

    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 290
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_mean_temperature_difference[operating_case] = (10-50) / np.log(10/50)
    for operating_case in test_case.range_operating_cases:
        assert logarithmic_mean_temperature_difference[operating_case] == test_exchanger.operation_parameter.logarithmic_mean_temperature_differences[operating_case]


def test_needed_areas():
    test_exchanger, test_case, _ = setup_module()
    hot_streams = test_case.hot_streams
    cold_streams = test_case.cold_streams
    topology = test_exchanger.topology
    logarithmic_mean_temperature_difference = np.zeros([test_case.number_operating_cases])
    areas = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 290
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_mean_temperature_difference[operating_case] = (10-50) / np.log(10/50)

    for operating_case in test_case.range_operating_cases:
        overall_heat_transfer_coefficient = 1 / (1 / hot_streams[topology.hot_stream].film_heat_transfer_coefficients[operating_case] +
                                                 1 / cold_streams[topology.cold_stream].film_heat_transfer_coefficients[operating_case])
        areas[operating_case] = test_exchanger.operation_parameter.heat_loads[operating_case] / \
            (overall_heat_transfer_coefficient * test_exchanger.operation_parameter.logarithmic_mean_temperature_differences[operating_case])
    for operating_case in test_case.range_operating_cases:
        assert areas[operating_case] == test_exchanger.operation_parameter.needed_areas[operating_case]


def test_costs_coefficients():
    test_exchanger, test_case, _ = setup_module()
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
    test_exchanger, test_case, addresses = setup_module()
    test_exchanger.operation_parameter.area = 2000
    exchanger_costs = test_exchanger.costs.base_costs + test_exchanger.costs.specific_area_costs * (test_exchanger.operation_parameter.area - test_exchanger.operation_parameter.initial_area)**test_exchanger.costs.degression_area
    assert exchanger_costs == test_exchanger.exchanger_costs
    test_exchanger.operation_parameter.area = 1000
    assert test_exchanger.exchanger_costs == 0
    addresses.matrix[0, 7] = False
    assert test_exchanger.exchanger_costs == test_exchanger.costs.remove_costs
    test_exchanger_5 = HeatExchanger(addresses, test_case, 5)
    addresses.matrix[5, 7] = True
    test_exchanger_5.operation_parameter.area = 2000
    exchanger_costs_5 = test_exchanger_5.costs.base_costs + test_exchanger_5.costs.specific_area_costs * (test_exchanger_5.operation_parameter.area - test_exchanger_5.operation_parameter.initial_area)**test_exchanger_5.costs.degression_area
    assert exchanger_costs_5 == test_exchanger_5.exchanger_costs
    addresses.matrix[5, 7] = False
    assert test_exchanger_5.exchanger_costs == 0


def test_admixer_costs():
    test_exchanger, _, addresses = setup_module()
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
    test_exchanger, _, addresses = setup_module()
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
    test_exchanger, test_case, _ = setup_module()
    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.heat_loads[operating_case] = 2000
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 290
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
    assert test_exchanger.is_feasible
    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.heat_loads[operating_case] = 2000
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 200
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
    assert not test_exchanger.is_feasible
    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.heat_loads[operating_case] = 2000
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
    assert not test_exchanger.is_feasible
