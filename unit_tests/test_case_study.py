import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'\\src')

from read_data.read_case_study_data import CaseStudy


def setup_model():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('data')
    test_stream_data = pd.read_excel(test_case.file, sheet_name='StreamData')
    os.chdir('../unit_tests')
    return test_case, test_stream_data


def test_case_study():
    test_case, test_stream_data = setup_model()
    number_operating_cases = int(max(test_stream_data['OC']))
    assert number_operating_cases == test_case.number_operating_cases

    number_streams = int(len(test_stream_data) / number_operating_cases)
    assert number_streams == test_case.number_streams

    number_hot_streams = sum(test_stream_data[0:test_case.number_streams]['H/C'].str.count('H'))
    assert number_hot_streams == test_case.number_hot_streams

    number_cold_streams = sum(test_case.stream_data[0:test_case.number_streams]['H/C'].str.count('C'))
    assert number_cold_streams == test_case.number_cold_streams

    number_heat_exchangers = len(test_case.initial_exchanger_address_matrix['HEX'])
    assert number_heat_exchangers == test_case.number_heat_exchangers

    number_balance_utility_exchangers = len(test_case.initial_exchanger_balance_utilities['HEX'])
    assert number_balance_utility_exchangers == test_case.number_balance_utility_heat_exchangers


def test_operating_cases():
    test_case, _ = setup_model()
    for operating_case in test_case.range_operating_cases:
        duration = test_case.operating_cases[operating_case].end_time - test_case.operating_cases[operating_case].start_time
        assert duration == test_case.operating_cases[operating_case].duration


def test_streams():
    test_case, _ = setup_model()
    for operating_case in test_case.range_operating_cases:

        for hot_stream in test_case.range_hot_streams:
            enthalpy_flow = test_case.hot_streams[hot_stream].specific_heat_capacities[operating_case] * test_case.hot_streams[hot_stream].mass_flows[operating_case] * \
                abs(test_case.hot_streams[hot_stream].target_temperatures[operating_case] - test_case.hot_streams[hot_stream].supply_temperatures[operating_case])
            assert enthalpy_flow == test_case.hot_streams[hot_stream].enthalpy_flows[operating_case]
        for cold_stream in test_case.range_cold_streams:
            enthalpy_flow = test_case.cold_streams[cold_stream].specific_heat_capacities[operating_case] * test_case.cold_streams[cold_stream].mass_flows[operating_case] * \
                abs(test_case.cold_streams[cold_stream].target_temperatures[operating_case] - test_case.cold_streams[cold_stream].supply_temperatures[operating_case])
            assert enthalpy_flow == test_case.cold_streams[cold_stream].enthalpy_flows[operating_case]
