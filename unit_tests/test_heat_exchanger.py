import os

import numpy as np

from src.read_data.read_case_study_data import CaseStudy
from src.heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger


def setup_module():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('unit_tests')
    test_exchanger = HeatExchanger(test_case, 0)
    return test_exchanger, test_case


def test_topology():
    test_exchanger, test_case = setup_module()
    heat_exchanger_topology = np.array(test_case.initial_exchanger_address_matrix, dtype=int)[0, 1:9]
    heat_exchanger_topology.tolist()
    heat_exchanger_topology[3] = not heat_exchanger_topology[3]
    heat_exchanger_topology[4] = not heat_exchanger_topology[4]
    heat_exchanger_topology[5] = not heat_exchanger_topology[5]
    heat_exchanger_topology[6] = not heat_exchanger_topology[6]
    heat_exchanger_topology[7] = not heat_exchanger_topology[7]
    test_exchanger.topology.hot_stream += 1
    test_exchanger.topology.cold_stream += 1
    test_exchanger.topology.enthalpy_stage += 1
    test_exchanger.topology.bypass_hot_stream_existent = not test_exchanger.topology.bypass_hot_stream_existent
    test_exchanger.topology.admixer_hot_stream_existent = not test_exchanger.topology.admixer_hot_stream_existent
    test_exchanger.topology.bypass_cold_stream_existent = not test_exchanger.topology.bypass_cold_stream_existent
    test_exchanger.topology.admixer_cold_stream_existent = not test_exchanger.topology.admixer_cold_stream_existent
    test_exchanger.topology.existent = not test_exchanger.topology.existent

    for indice in enumerate(heat_exchanger_topology):
        assert heat_exchanger_topology[indice[0]] == test_exchanger.topology.address_vector[indice[0]]


def test_operation_parameter():
    test_exchanger, test_case = setup_module()
    initial_area = test_case.initial_exchanger_address_matrix['A_ex'][0] * 1.2
    assert initial_area == test_exchanger.operation_parameter.initial_area * 1.2


def test_update_logarithmic_temperature_differences():
    test_exchanger, test_case = setup_module()
    logarithmic_temperature_difference = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 250
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_temperature_difference[operating_case] = 400 - 350
    test_exchanger.operation_parameter.update_logarithmic_temperature_differences()
    for operating_case in test_case.range_operating_cases:
        assert logarithmic_temperature_difference[operating_case] == test_exchanger.operation_parameter.logarithmic_temperature_differences[operating_case]

    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.inlet_temperatures_hot_stream[operating_case] = 400
        test_exchanger.operation_parameter.outlet_temperatures_hot_stream[operating_case] = 300
        test_exchanger.operation_parameter.inlet_temperatures_cold_stream[operating_case] = 290
        test_exchanger.operation_parameter.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_temperature_difference[operating_case] = (10-50) / np.log(10/50)
    test_exchanger.operation_parameter.update_logarithmic_temperature_differences()

    for operating_case in test_case.range_operating_cases:
        assert logarithmic_temperature_difference[operating_case] == test_exchanger.operation_parameter.logarithmic_temperature_differences[operating_case]


def test_update_area():
    test_exchanger, test_case = setup_module()
    hot_streams = test_case.hot_streams
    cold_streams = test_case.cold_streams
    topology = test_exchanger.topology
    areas = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_exchanger.operation_parameter.logarithmic_temperature_differences[operating_case] = 5 + 10 * operating_case

    test_exchanger.operation_parameter.update_needed_areas(topology, hot_streams, cold_streams)
    for operating_case in test_case.range_operating_cases:
        overall_heat_transfer_coefficient = 1 / (1 / hot_streams[topology.hot_stream].film_heat_transfer_coefficients[operating_case] +
                                                 1 / cold_streams[topology.cold_stream].film_heat_transfer_coefficients[operating_case])
        areas[operating_case] = test_exchanger.operation_parameter.heat_loads[operating_case] / \
            (overall_heat_transfer_coefficient * test_exchanger.operation_parameter.logarithmic_temperature_differences[operating_case])
    for operating_case in test_case.range_operating_cases:
        assert areas[operating_case] == test_exchanger.operation_parameter.needed_areas[operating_case]


def test_costs():
    test_exchanger, test_case = setup_module()
    base_cost = test_case.initial_exchanger_address_matrix['c_0_HEX'][0]
    assert base_cost == test_exchanger.costs.base_cost

    specific_area_cost = test_case.initial_exchanger_address_matrix['c_A_HEX'][0]
    assert specific_area_cost == test_exchanger.costs.specific_area_cost

    degression_area = test_case.initial_exchanger_address_matrix['d_f_HEX'][0]
    assert degression_area == test_exchanger.costs.degression_area

    remove_cost = test_case.initial_exchanger_address_matrix['c_R_HEX'][0]
    assert remove_cost == test_exchanger.costs.remove_cost

    base_split_cost = test_case.initial_exchanger_address_matrix['c_0_split'][0]
    assert base_split_cost == test_exchanger.costs.base_split_cost

    specific_split_cost = test_case.initial_exchanger_address_matrix['c_M_split'][0]
    assert specific_split_cost == test_exchanger.costs.specific_split_cost

    degression_split = test_case.initial_exchanger_address_matrix['d_f_split'][0]
    assert degression_split == test_exchanger.costs.degression_split

    remove_split_cost = test_case.initial_exchanger_address_matrix['c_R_split'][0]
    assert remove_split_cost == test_exchanger.costs.remove_split_cost

    base_bypass_cost = test_case.initial_exchanger_address_matrix['c_0_bypass'][0]
    assert base_bypass_cost == test_exchanger.costs.base_bypass_cost

    specific_bypass_cost = test_case.initial_exchanger_address_matrix['c_M_bypass'][0]
    assert specific_bypass_cost == test_exchanger.costs.specific_bypass_cost

    degression_bypass = test_case.initial_exchanger_address_matrix['d_f_bypass'][0]
    assert degression_bypass == test_exchanger.costs.degression_bypass

    remove_bypass_cost = test_case.initial_exchanger_address_matrix['c_R_bypass'][0]
    assert remove_bypass_cost == test_exchanger.costs.remove_bypass_cost

    base_admixer_cost = test_case.initial_exchanger_address_matrix['c_0_admixer'][0]
    assert base_admixer_cost == test_exchanger.costs.base_admixer_cost

    specific_admixer_cost = test_case.initial_exchanger_address_matrix['c_M_admixer'][0]
    assert specific_admixer_cost == test_exchanger.costs.specific_admixer_cost

    degression_admixer = test_case.initial_exchanger_address_matrix['d_f_admixer'][0]
    assert degression_admixer == test_exchanger.costs.degression_admixer

    remove_admixer_cost = test_case.initial_exchanger_address_matrix['c_R_admixer'][0]
    assert remove_admixer_cost == test_exchanger.costs.remove_admixer_cost

    base_repipe_cost = test_case.initial_exchanger_address_matrix['c_0_repipe'][0]
    assert base_repipe_cost == test_exchanger.costs.base_repipe_cost

    specific_repipe_cost = test_case.initial_exchanger_address_matrix['c_M_repipe'][0]
    assert specific_repipe_cost == test_exchanger.costs.specific_repipe_cost

    degression_repipe = test_case.initial_exchanger_address_matrix['d_f_repipe'][0]
    assert degression_repipe == test_exchanger.costs.degression_repipe

    base_resequence_cost = test_case.initial_exchanger_address_matrix['c_0_resequence'][0]
    assert base_resequence_cost == test_exchanger.costs.base_resequence_cost

    specific_resequence_cost = test_case.initial_exchanger_address_matrix['c_M_resequence'][0]
    assert specific_resequence_cost == test_exchanger.costs.specific_resequence_cost

    degression_resequence = test_case.initial_exchanger_address_matrix['d_f_resequence'][0]
    assert degression_resequence == test_exchanger.costs.degression_resequence
