import os
import mock
import numpy as np

from src.read_data.read_case_study_data import CaseStudy
from src.heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork


def setup_model():
    """Setup testing model"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    os.chdir('unit_tests')
    test_network = HeatExchangerNetwork(test_case)
    return test_network, test_case


def test_heat_exchanger_address_matrix():
    test_network, test_case = setup_model()
    for exchanger in test_case.range_heat_exchangers:
        assert all(test_network.exchanger_addresses.matrix[exchanger] == test_network.heat_exchangers[exchanger].topology.address_vector)


def test_balance_utility_heat_exchangers():
    test_network, test_case = setup_model()
    for exchanger in test_case.range_balance_utility_heat_exchangers:
        utility_type = 'H'
        connected_stream = test_network.balance_utility_heat_exchangers[exchanger].connected_stream + 1
        initial_area = test_network.balance_utility_heat_exchangers[exchanger].initial_area * 1.2
        for operating_case in test_case.range_operating_cases:
            initial_heat_load = test_network.balance_utility_heat_exchangers[exchanger].initial_heat_loads[operating_case] * 1.2
            test_network.balance_utility_heat_exchangers[exchanger].initial_heat_loads[operating_case] *= 1.2
            assert initial_heat_load == test_network.balance_utility_heat_exchangers[exchanger].initial_heat_loads[operating_case]
        base_cost = test_network.balance_utility_heat_exchangers[exchanger].base_cost * 1.2
        specific_area_cost = test_network.balance_utility_heat_exchangers[exchanger].specific_area_cost * 1.2
        degression_area = test_network.balance_utility_heat_exchangers[exchanger].degression_area * 1.2
        address_vector = [utility_type, connected_stream, initial_area, base_cost, specific_area_cost, degression_area]
        test_network.balance_utility_heat_exchangers[exchanger].utility_type = 'H'
        test_network.balance_utility_heat_exchangers[exchanger].connected_stream += 1
        test_network.balance_utility_heat_exchangers[exchanger].initial_area *= 1.2
        test_network.balance_utility_heat_exchangers[exchanger].base_cost *= 1.2
        test_network.balance_utility_heat_exchangers[exchanger].specific_area_cost *= 1.2
        test_network.balance_utility_heat_exchangers[exchanger].degression_area *= 1.2
        for i, _ in enumerate(test_network.balance_utility_heat_exchangers[exchanger].address_vector):
            assert test_network.balance_utility_heat_exchangers[exchanger].address_vector[i] == address_vector[i]


def test_restrictions():
    test_network, test_case = setup_model()
    assert test_network.restrictions.max_splits == test_case.manual_parameter['MaxSplitsPerk'].iloc[0]
    assert test_network.restrictions.max_bypass_fraction == test_case.manual_parameter['MaxBypass'].iloc[0]
    assert test_network.restrictions.max_admix_fraction == test_case.manual_parameter['MaxAdmix'].iloc[0]
    assert test_network.restrictions.temperature_difference_upper_bound == test_case.manual_parameter['dTUb'].iloc[0]
    assert test_network.restrictions.temperature_difference_lower_bound == test_case.manual_parameter['dTLb'].iloc[0]
    assert test_network.restrictions.minimal_heat_load == test_case.manual_parameter['MinimalHeatLoad'].iloc[0]


def test_enthalpy_stage_temperatures():
    test_network, _ = setup_model()
    test_network.thermodynamic_parameter.heat_loads = np.array([[3500, 0], [0, 3800], [0, 100], [5800, 0], [1500, 3500], [0, 0], [0, 0]])
    test_temperatures_enthalpy_stages_hot_streams = test_network.thermodynamic_parameter.enthalpy_stage_temperatures_hot_streams - 273.15
    test_temperatures_enthalpy_stages_cold_streams = test_network.thermodynamic_parameter.enthalpy_stage_temperatures_cold_streams - 273.15
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 0, 0] - 94) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 1, 0] - 210) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 2, 0] - 210) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 3, 0] - 210) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 4, 0] - 280) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 0, 1] - 225) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 1, 1] - 225) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 2, 1] - 226.67) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 3, 1] - 290) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 4, 1] - 290) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 0, 0] - 188.57) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 1, 0] - 188.57) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 2, 0] - 188.57) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 3, 0] - 210) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 4, 0] - 210) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 0, 1] - 110) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 1, 1] - 110) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 2, 1] - 110) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 3, 1] - 180) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 4, 1] - 180) <= 10e-3

    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 0, 0] - 30) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 1, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 2, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 3, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 4, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 0, 1] - 160) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 1, 1] - 160) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 2, 1] - 160) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 3, 1] - 255) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 4, 1] - 255) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 0, 0] - 150) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 1, 0] - 150) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 2, 0] - 150) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 3, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 4, 0] - 233.33) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 0, 1] - 70) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 1, 1] - 70) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 2, 1] - 71.67) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 3, 1] - 130) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 4, 1] - 130) <= 10e-3

    test_network.exchanger_addresses.matrix = np.array(
        [
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 1, 1, 0, 0, 0, 1],
            [0, 0, 3, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    test_temperatures_enthalpy_stages_hot_streams = test_network.thermodynamic_parameter.enthalpy_stage_temperatures_hot_streams - 273.15
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 0, 0] - 94) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 1, 0] - 94) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 2, 0] - 94) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 3, 0] - 94) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 4, 0] - 280) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 0, 1] - 225) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 1, 1] - 225) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 2, 1] - 226.67) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 3, 1] - 290) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[0, 4, 1] - 290) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 0, 0] - 188.57) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 1, 0] - 188.57) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 2, 0] - 188.57) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 3, 0] - 210) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 4, 0] - 210) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 0, 1] - 110) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 1, 1] - 110) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 2, 1] - 110) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 3, 1] - 180) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_hot_streams[1, 4, 1] - 180) <= 10e-3
    test_network.exchanger_addresses.matrix = np.array(
        [
            [0, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 1, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    test_temperatures_enthalpy_stages_cold_streams = test_network.thermodynamic_parameter.enthalpy_stage_temperatures_cold_streams - 273.15
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 0, 0] - 30) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 1, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 2, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 3, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 4, 0] - 175) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 0, 1] - 160) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 1, 1] - 160) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 2, 1] - 160) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 3, 1] - 255) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[0, 4, 1] - 255) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 0, 0] - 150) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 1, 0] - 150) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 2, 0] - 150) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 3, 0] - 233.33) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 4, 0] - 233.33) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 0, 1] - 70) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 1, 1] - 70) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 2, 1] - 71.67) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 3, 1] - 130) <= 10e-3
    assert abs(test_temperatures_enthalpy_stages_cold_streams[1, 4, 1] - 130) <= 10e-3


def test_utility_demands():
    test_network, _ = setup_model()
    test_network.thermodynamic_parameter.heat_loads = np.array([[3500, 0], [0, 3800], [0, 100], [5800, 0], [1500, 3500], [0, 0], [0, 0]])
    assert abs(test_network.balance_utility_heat_exchangers[0].heat_loads[0] - 2200) <= 10e-3
    assert abs(test_network.balance_utility_heat_exchangers[0].heat_loads[1] - 8700) <= 10e-3
    assert abs(test_network.balance_utility_heat_exchangers[1].heat_loads[0] - 6200) <= 10e-3
    assert abs(test_network.balance_utility_heat_exchangers[1].heat_loads[1] - 0) <= 10e-3
    assert abs(test_network.balance_utility_heat_exchangers[2].heat_loads[0] - 600) <= 10e-3
    assert abs(test_network.balance_utility_heat_exchangers[2].heat_loads[1] - 1800) <= 10e-3
    assert abs(test_network.balance_utility_heat_exchangers[3].heat_loads[0] - 2800) <= 10e-3
    assert abs(test_network.balance_utility_heat_exchangers[3].heat_loads[1] - 0) <= 10e-3
    assert abs(test_network.hot_utility_demand[0] - 15857600) <= 10e-3
    assert abs(test_network.hot_utility_demand[1] - 6004800) <= 10e-3
    assert abs(test_network.cold_utility_demand[0] - 39177600) <= 10e-3
    assert abs(test_network.cold_utility_demand[1] - 29023200) <= 10e-3


def test_sorted_heat_exchangers_on_stream():
    pass


def test_sorted_heat_exchangers_on_initial_stream():
    pass


def test_utility_heat_exchangers():
    pass


def test_utility_demand():
    pass


def test_split_costs():
    test_network, _ = setup_model()
    test_network.exchanger_addresses.matrix = np.array(
        [
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 3, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 3, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    assert test_network.split_costs == test_network.heat_exchangers[0].costs.base_split_costs + 2 * test_network.heat_exchangers[1].costs.base_split_costs + 2 * test_network.heat_exchangers[2].costs.base_split_costs + 2 * test_network.heat_exchangers[3].costs.base_split_costs + 2 * test_network.heat_exchangers[4].costs.base_split_costs
    test_network.heat_exchangers[3].topology.initial_enthalpy_stage = 3
    test_network.exchanger_addresses.matrix = np.array(
        [
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 1, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    assert test_network.split_costs == test_network.heat_exchangers[0].costs.remove_split_costs + test_network.heat_exchangers[3].costs.remove_split_costs
    test_network.heat_exchangers[2].topology.initial_enthalpy_stage = 3
    test_network.heat_exchangers[3].topology.initial_enthalpy_stage = 0
    test_network.exchanger_addresses.matrix = np.array(
        [
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 1, 1, 0, 0, 0, 1],
            [0, 0, 3, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    assert test_network.split_costs == test_network.heat_exchangers[3].costs.base_split_costs + test_network.heat_exchangers[2].costs.remove_split_costs + test_network.heat_exchangers[0].costs.remove_split_costs + test_network.heat_exchangers[2].costs.remove_split_costs


def test_repipe_costs():
    pass


def test_resequence_costs():
    pass


def test_match_costs():
    pass


def test_capital_costs():
    pass


def test_operating_costs():
    pass


def test_total_annual_costs():
    pass


def test_heat_exchanger_feasibility():
    pass


def test_energy_balance_feasibility():
    pass


def test_split_heat_exchanger_violation_distance():
    test_network, _ = setup_model()
    test_eam = np.array(
        [
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 3, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 3, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 3, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    assert test_network.split_heat_exchanger_violation_distance(test_eam) == 3


def test_utility_connection_violation_distance():
    pass


def test_topology_violation_distance():
    pass


def test_is_feasible():
    pass
