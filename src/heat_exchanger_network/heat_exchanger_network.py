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
    # TODO: calculate enthalpy stage temperatures
    # TODO: random function for heat loads
    # TODO: random function for EAM (only hex stuff; mixer stuff needs to be updated from hex.operation_parameter)

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
        self.addresses = ExchangerAddresses(case_study)
        self.thermodynamic_parameter = ThermodynamicParameter(case_study)

        # Utilities
        self.hot_utilities_indices = case_study.hot_utilities_indices
        self.cold_utilities_indices = case_study.cold_utilities_indices
        self.hot_utility_demand = np.zeros([self.number_operating_cases])
        self.cold_utility_demand = np.zeros([self.number_operating_cases])

        # Heat exchangers
        self.heat_exchangers = list()
        for exchanger in case_study.range_heat_exchangers:
            self.heat_exchangers.append(HeatExchanger(self.addresses, self.thermodynamic_parameter, case_study, exchanger))

        # TODO: Initialize random EAM!
        # TODO: Initialize random heat loads!
        # TODO: if there is a split, update split fractions in operation parameter of hex!

        # Balance utility heat exchangers
        self.balance_utility_heat_exchanger = list()
        for exchanger in case_study.range_balance_utility_heat_exchangers:
            self.balance_utility_heat_exchanger.append(BalanceUtilityHeatExchanger(case_study, exchanger))

        # Restrictions
        self.restrictions = Restrictions(case_study)

        # Economics
        self.economics = Economics(case_study)

    def get_utility_heat_exchangers(self, stream_type):
        utility_heat_exchanger = []
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent and \
                ((stream_type == 'hot' and self.heat_exchangers[exchanger].topology.hot_stream in self.hot_utilities_indices) or
                 (stream_type == 'cold' and self.heat_exchangers[exchanger].topology.cold_stream in self.cold_utilities_indices)):
                utility_heat_exchanger.append(exchanger)
        return np.array(utility_heat_exchanger)

    def update_utility_demand(self, operating_cases):
        # TODO: utility demand of balance utility exchanger is not jet included!
        hot_utility_exchangers = self.get_utility_heat_exchangers('hot')
        cold_utility_exchangers = self.get_utility_heat_exchangers('cold')
        hot_utility_demand = np.zeros([self.number_operating_cases])
        cold_utility_demand = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            hot_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case] *
                                                         operating_cases[operating_case].duration for exchanger in hot_utility_exchangers])
            cold_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case] *
                                                          operating_cases[operating_case].duration for exchanger in cold_utility_exchangers])
        self.hot_utility_demand = hot_utility_demand
        self.cold_utility_demand = cold_utility_demand

    def is_feasible(self):
        # TODO: check is every heat exchanger is feasible and check is energy balance is fulfilled!
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass
