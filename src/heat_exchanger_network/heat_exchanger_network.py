import numpy as np

from src.heat_exchanger_network.economics import Economics
from src.heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger
from src.heat_exchanger_network.heat_exchanger.balance_utility_heat_exchanger import BalanceUtilityHeatExchanger
from src.heat_exchanger_network.restrictions import Restrictions
from src.heat_exchanger_network.temperature_calculation import TemperatureCalculation


class HeatExchangerNetwork:
    """Heat exchanger network object"""
    # TODO: include HEN (sum of all HEX costs) utility balance HEX, split, re-piping, re-sequencing, and operation costs

    def __init__(self, case_study):
        self.number_heat_exchangers = case_study.number_heat_exchangers
        self.range_heat_exchangers = case_study.range_heat_exchangers
        self.number_hot_streams = case_study.number_hot_streams
        self.range_hot_streams = case_study.range_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.range_cold_streams = case_study.range_cold_streams
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams

        # Utilities
        self.hot_utilities_indices = case_study.hot_utilities_indices
        self.cold_utilities_indices = case_study.cold_utilities_indices
        self.hot_utility_demand = np.zeros([self.number_operating_cases])
        self.cold_utility_demand = np.zeros([self.number_operating_cases])

        # Heat exchangers
        self.heat_exchangers = list()
        for exchanger in case_study.range_heat_exchangers:
            self.heat_exchangers.append(HeatExchanger(case_study, exchanger))

        # Balance utility heat exchangers
        self.balance_utility_heat_exchanger = list()
        for exchanger in case_study.range_balance_utility_heat_exchangers:
            self.balance_utility_heat_exchanger.append(BalanceUtilityHeatExchanger(case_study, exchanger))

        # Restrictions
        self.restrictions = Restrictions(case_study)

        # Economics
        self.economics = Economics(case_study)

    @property
    def address_matrix(self):
        heat_exchanger_address_matrix = np.zeros([self.number_heat_exchangers, len(self.heat_exchangers[0].topology.address_vector)], dtype=int)
        for exchanger in self.range_heat_exchangers:
            heat_exchanger_address_matrix[exchanger] = self.heat_exchangers[exchanger].topology.address_vector
        return heat_exchanger_address_matrix

    @property
    def operation_parameter_matrix(self):
        operation_parameter_matrix = np.zeros([len(self.heat_exchangers[0].operation_parameter.matrix), self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            for parameter in range(len(self.heat_exchangers[0].operation_parameter.matrix)):
                operation_parameter_matrix[parameter, exchanger] = self.heat_exchangers[exchanger].operation_parameter.matrix[parameter]
        return operation_parameter_matrix

    # def get_sorted_heat_exchangers_on_stream(self, stream, stream_type):
    #     heat_exchanger_on_stream = []
    #     for exchanger in self.range_heat_exchangers:
    #         if self.heat_exchangers[exchanger].topology.existent and \
    #             ((stream_type == 'hot' and self.heat_exchangers[exchanger].topology.hot_stream == stream) or
    #              (stream_type == 'cold' and self.heat_exchangers[exchanger].topology.cold_stream == stream)):
    #             heat_exchanger_on_stream.append(exchanger)
    #     heat_exchanger_on_stream_sorted = np.zeros([len(heat_exchanger_on_stream)], dtype=int)
    #     if stream_type == 'hot':
    #         heat_exchanger_on_stream_sorted = sorted(heat_exchanger_on_stream, key=lambda on_stream: self.heat_exchangers[on_stream].topology.number_on_hot_stream)
    #     elif stream_type == 'cold':
    #         heat_exchanger_on_stream_sorted = sorted(heat_exchanger_on_stream, key=lambda on_stream: self.heat_exchangers[on_stream].topology.number_on_cold_stream)
    #     return np.array(heat_exchanger_on_stream_sorted)

    # def get_heat_exchanger_above_on_stream(self, stream, stream_type, exchanger):
    #     sorted_heat_exchanger_on_stream = self.get_sorted_heat_exchangers_on_stream(stream, stream_type)
    #     if exchanger == sorted_heat_exchanger_on_stream[-1]:
    #         raise Exception('This is the last or the sole heat exchanger on the stream, you cannot get a heat exchanger above!')
    #     return sorted_heat_exchanger_on_stream[np.argwhere(sorted_heat_exchanger_on_stream == exchanger) + 1]

    # def get_heat_exchanger_below_on_stream(self, stream, stream_type, exchanger):
    #     sorted_heat_exchanger_on_stream = self.get_sorted_heat_exchangers_on_stream(
    #         stream, stream_type)
    #     if exchanger == sorted_heat_exchanger_on_stream[0]:
    #         raise Exception('This it the first or the sole heat exchanger on the stream, you cannot get a heat exchanger below!')
    #     return sorted_heat_exchanger_on_stream[np.argwhere(sorted_heat_exchanger_on_stream == exchanger) - 1]

    def get_utility_heat_exchangers(self, stream_type):
        utility_heat_exchanger = []
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent and \
                ((stream_type == 'hot' and self.heat_exchangers[exchanger].topology.hot_stream in self.hot_utilities_indices) or
                 (stream_type == 'cold' and self.heat_exchangers[exchanger].topology.cold_stream in self.cold_utilities_indices)):
                utility_heat_exchanger.append(exchanger)
        return np.array(utility_heat_exchanger)

    def update_utility_demand(self, operating_cases):
        hot_utility_exchangers = self.get_utility_heat_exchangers('hot')
        cold_utility_exchangers = self.get_utility_heat_exchangers('cold')
        hot_utility_demand = np.zeros([self.number_operating_cases])
        cold_utility_demand = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            hot_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].process_quantities.heat_loads[operating_case] *
                                                         operating_cases[operating_case].duration for exchanger in hot_utility_exchangers])
            cold_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].process_quantities.heat_loads[operating_case] *
                                                          operating_cases[operating_case].duration for exchanger in cold_utility_exchangers])
        self.hot_utility_demand = hot_utility_demand
        self.cold_utility_demand = cold_utility_demand

    def is_feasible(self):
        # TODO: function from evaluation
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass
