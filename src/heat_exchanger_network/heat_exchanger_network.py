import numpy as np

from src.heat_exchanger_network.economics import Economics
from src.heat_exchanger_network.exchanger_addresses import ExchangerAddresses
from src.heat_exchanger_network.thermodynamic_parameter import ThermodynamicParameter
from src.heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger
from src.heat_exchanger_network.heat_exchanger.balance_utility_heat_exchanger import BalanceUtilityHeatExchanger
from src.heat_exchanger_network.restrictions import Restrictions


class HeatExchangerNetwork:
    """Heat exchanger network object"""
    # TODO: include HEN (sum of all HEX costs) utility balance HEX, split, re-piping, re-sequencing, match costs, and operation costs

    def __init__(self, case_study):
        self.number_heat_exchangers = case_study.number_heat_exchangers
        self.range_heat_exchangers = case_study.range_heat_exchangers
        self.number_hot_streams = case_study.number_hot_streams
        self.range_hot_streams = case_study.range_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.range_cold_streams = case_study.range_cold_streams
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.number_enthalpy_stages = case_study.number_enthalpy_stages
        self.range_enthalpy_stages = case_study.range_enthalpy_stages
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams
        self.addresses = ExchangerAddresses(case_study)
        self.thermodynamic_parameter = ThermodynamicParameter(case_study)

        # Utilities
        self.hot_utilities_indices = case_study.hot_utilities_indices
        self.cold_utilities_indices = case_study.cold_utilities_indices

        # Heat exchangers
        self.heat_exchangers = list()
        for exchanger in case_study.range_heat_exchangers:
            self.heat_exchangers.append(HeatExchanger(self.addresses, self.thermodynamic_parameter, case_study, exchanger))

        # Balance utility heat exchangers
        self.balance_utility_heat_exchanger = list()
        for exchanger in case_study.range_balance_utility_heat_exchangers:
            self.balance_utility_heat_exchanger.append(BalanceUtilityHeatExchanger(case_study, exchanger))

        # Restrictions
        self.restrictions = Restrictions(case_study)

        # Economics
        self.economics = Economics(case_study)

        # Assign enthalpy stage temperatures to heat exchanger
        self.update_heat_exchanger_temperatures()

    @property
    def enthalpy_stage_temperatures_hot_streams(self):
        enthalpy_stage_temperatures_hot_streams = np.zeros([self.number_hot_streams, self.number_enthalpy_stages + 1, self.number_operating_cases])
        for stream in self.range_hot_streams:
            for stage in range(self.number_enthalpy_stages, -1, -1):
                enthalpy_difference = np.zeros([self.number_operating_cases])
                for operating_case in self.range_operating_cases:
                    for exchanger in self.range_heat_exchangers:
                        if self.heat_exchangers[exchanger].topology.hot_stream == stream and \
                                self.heat_exchangers[exchanger].topology.enthalpy_stage == stage:
                            enthalpy_difference[operating_case] += self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case]
                    if stage == self.number_enthalpy_stages:
                        enthalpy_stage_temperatures_hot_streams[stream, stage, operating_case] = self.hot_streams[stream].supply_temperatures[operating_case]
                    else:
                        enthalpy_stage_temperatures_hot_streams[stream, stage, operating_case] = enthalpy_stage_temperatures_hot_streams[stream, stage + 1, operating_case] - enthalpy_difference[operating_case] / (self.hot_streams[stream].heat_capacity_flows[operating_case])
        return enthalpy_stage_temperatures_hot_streams

    @property
    def enthalpy_stage_temperatures_cold_streams(self):
        enthalpy_stage_temperatures_cold_streams = np.zeros([self.number_cold_streams, self.number_enthalpy_stages + 1, self.number_operating_cases])
        for stream in self.range_cold_streams:
            for stage in range(self.number_enthalpy_stages + 1):
                enthalpy_difference = np.zeros([self.number_operating_cases])
                for operating_case in self.range_operating_cases:
                    for exchanger in self.range_heat_exchangers:
                        if self.heat_exchangers[exchanger].topology.cold_stream == stream and \
                                self.heat_exchangers[exchanger].topology.enthalpy_stage == stage - 1:
                            enthalpy_difference[operating_case] += self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case]
                    if stage == 0:
                        enthalpy_stage_temperatures_cold_streams[stream, stage, operating_case] = self.cold_streams[stream].supply_temperatures[operating_case]
                    else:
                        enthalpy_stage_temperatures_cold_streams[stream, stage, operating_case] = enthalpy_stage_temperatures_cold_streams[stream, stage - 1, operating_case] + enthalpy_difference[operating_case] / (self.cold_streams[stream].heat_capacity_flows[operating_case])
        return enthalpy_stage_temperatures_cold_streams

    def update_heat_exchanger_temperatures(self):
        for exchanger in self.range_heat_exchangers:
            for operating_case in self.range_operating_cases:
                self.thermodynamic_parameter.matrix[1][operating_case, exchanger] = self.enthalpy_stage_temperatures_hot_streams[self.heat_exchangers[exchanger].topology.hot_stream, self.heat_exchangers[exchanger].topology.enthalpy_stage + 1, operating_case]
                self.thermodynamic_parameter.matrix[2][operating_case, exchanger] = self.enthalpy_stage_temperatures_hot_streams[self.heat_exchangers[exchanger].topology.hot_stream, self.heat_exchangers[exchanger].topology.enthalpy_stage, operating_case]
                self.thermodynamic_parameter.matrix[3][operating_case, exchanger] = self.enthalpy_stage_temperatures_cold_streams[self.heat_exchangers[exchanger].topology.cold_stream, self.heat_exchangers[exchanger].topology.enthalpy_stage, operating_case]
                self.thermodynamic_parameter.matrix[4][operating_case, exchanger] = self.enthalpy_stage_temperatures_cold_streams[self.heat_exchangers[exchanger].topology.cold_stream, self.heat_exchangers[exchanger].topology.enthalpy_stage + 1, operating_case]

    def get_utility_heat_exchangers(self, stream_type):
        utility_heat_exchanger = []
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent and \
                ((stream_type == 'hot' and self.heat_exchangers[exchanger].topology.hot_stream in self.hot_utilities_indices) or
                 (stream_type == 'cold' and self.heat_exchangers[exchanger].topology.cold_stream in self.cold_utilities_indices)):
                utility_heat_exchanger.append(exchanger)
        return np.array(utility_heat_exchanger)

    @property
    def hot_utility_demand(self, operating_cases):
        # TODO: utility demand of balance utility exchanger is not jet included! (balance utility needs to be calculated first and needs to be 0 <= demand)
        hot_utility_exchangers = self.get_utility_heat_exchangers('hot')
        hot_utility_demand = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            hot_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case] * operating_cases[operating_case].duration for exchanger in hot_utility_exchangers])
        return hot_utility_demand

    @property
    def cold_utility_demand(self, operating_cases):
        # TODO: utility demand of balance utility exchanger is not jet included! (balance utility needs to be calculated first and needs to be 0 <= demand)
        cold_utility_exchangers = self.get_utility_heat_exchangers('cold')
        cold_utility_demand = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            cold_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case] * operating_cases[operating_case].duration for exchanger in cold_utility_exchangers])
        return cold_utility_demand

    def is_feasible(self):
        # TODO: check is every heat exchanger is feasible and check is energy balance is fulfilled!
        # TODO: reformulate to property
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass
