import os

import numpy as np

from src.read_data.read_case_study_data import CaseStudy
from src.heat_exchanger_network.heat_exchanger.balance_utility_heat_exchanger import BalanceUtilityHeatExchanger


def setup_model():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('unit_tests')
    test_balance_exchanger = BalanceUtilityHeatExchanger(test_case, 0)
    return test_balance_exchanger, test_case


def test_logarithmic_mean_temperature_difference():
    test_balance_exchanger, test_case = setup_model()
    logarithmic_mean_temperature_difference = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_balance_exchanger.inlet_temperatures_hot_stream[operating_case] = 400
        test_balance_exchanger.outlet_temperatures_hot_stream[operating_case] = 300
        test_balance_exchanger.inlet_temperatures_cold_stream[operating_case] = 250
        test_balance_exchanger.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_mean_temperature_difference[operating_case] = 400 - 350
    for operating_case in test_case.range_operating_cases:
        assert logarithmic_mean_temperature_difference[operating_case] == test_balance_exchanger.logarithmic_mean_temperature_differences[operating_case]

    for operating_case in test_case.range_operating_cases:
        test_balance_exchanger.inlet_temperatures_hot_stream[operating_case] = 400
        test_balance_exchanger.outlet_temperatures_hot_stream[operating_case] = 300
        test_balance_exchanger.inlet_temperatures_cold_stream[operating_case] = 290
        test_balance_exchanger.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_mean_temperature_difference[operating_case] = (10-50) / np.log(10/50)
    for operating_case in test_case.range_operating_cases:
        assert logarithmic_mean_temperature_difference[operating_case] == test_balance_exchanger.logarithmic_mean_temperature_differences[operating_case]


def test_areas():
    test_balance_exchanger, test_case = setup_model()
    logarithmic_mean_temperature_difference = np.zeros([test_case.number_operating_cases])
    needed_areas = np.zeros([test_case.number_operating_cases])
    for operating_case in test_case.range_operating_cases:
        test_balance_exchanger.inlet_temperatures_hot_stream[operating_case] = 400
        test_balance_exchanger.outlet_temperatures_hot_stream[operating_case] = 300
        test_balance_exchanger.inlet_temperatures_cold_stream[operating_case] = 290
        test_balance_exchanger.outlet_temperatures_cold_stream[operating_case] = 350
        logarithmic_mean_temperature_difference[operating_case] = (10-50) / np.log(10/50)
        test_balance_exchanger.heat_loads[operating_case] = 2000
        needed_areas[operating_case] = 2000 / (test_balance_exchanger.overall_heat_transfer_coefficient[operating_case] * logarithmic_mean_temperature_difference[operating_case])
        assert test_balance_exchanger.needed_areas[operating_case] == needed_areas[operating_case]
    assert max(needed_areas) == test_balance_exchanger.area


def test_costs():
    test_balance_exchanger, test_case = setup_model()
    for operating_case in test_case.range_operating_cases:
        test_balance_exchanger.inlet_temperatures_hot_stream[operating_case] = 400
        test_balance_exchanger.outlet_temperatures_hot_stream[operating_case] = 300
        test_balance_exchanger.inlet_temperatures_cold_stream[operating_case] = 290
        test_balance_exchanger.outlet_temperatures_cold_stream[operating_case] = 350
        test_balance_exchanger.heat_loads[operating_case] = 2000
    assert test_balance_exchanger.exchanger_costs == test_balance_exchanger.base_cost + test_balance_exchanger.specific_area_cost * (test_balance_exchanger.area - test_balance_exchanger.initial_area) ** test_balance_exchanger.degression_area
    for operating_case in test_case.range_operating_cases:
        test_balance_exchanger.heat_loads[operating_case] = 10
    assert test_balance_exchanger.exchanger_costs == 0
    for operating_case in test_case.range_operating_cases:
        test_balance_exchanger.heat_loads[operating_case] = 0
    assert test_balance_exchanger.exchanger_costs == test_balance_exchanger.remove_costs
