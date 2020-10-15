import difflib
import numpy as np

from src.heat_exchanger_network.economics import Economics
from src.heat_exchanger_network.exchanger_addresses import ExchangerAddresses
from src.heat_exchanger_network.thermodynamic_parameter import ThermodynamicParameter
from src.heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger
from src.heat_exchanger_network.heat_exchanger.balance_utility_heat_exchanger import BalanceUtilityHeatExchanger
from src.heat_exchanger_network.restrictions import Restrictions


class HeatExchangerNetwork:
    """Heat exchanger network object"""
    # TODO: include HEN (sum of all HEX costs) utility balance HEX, split, re-piping, re-sequencing, match costs, operation costs, and feasibility check

    def __init__(self, case_study):
        self.number_heat_exchangers = case_study.number_heat_exchangers
        self.range_heat_exchangers = case_study.range_heat_exchangers
        self.range_balance_utility_heat_exchangers = case_study.range_balance_utility_heat_exchangers
        self.number_hot_streams = case_study.number_hot_streams
        self.range_hot_streams = case_study.range_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.range_cold_streams = case_study.range_cold_streams
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.operating_cases = case_study.operating_cases
        self.number_enthalpy_stages = case_study.number_enthalpy_stages
        self.range_enthalpy_stages = case_study.range_enthalpy_stages
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams
        self.exchanger_addresses = ExchangerAddresses(case_study)
        self.thermodynamic_parameter = ThermodynamicParameter(case_study, self.exchanger_addresses)

        # Utilities
        self.hot_utilities_indices = case_study.hot_utilities_indices
        self.cold_utilities_indices = case_study.cold_utilities_indices

        # Heat exchangers
        self.heat_exchangers = list()
        for exchanger in case_study.range_heat_exchangers:
            self.heat_exchangers.append(HeatExchanger(self.exchanger_addresses, self.thermodynamic_parameter, case_study, exchanger))

        # Restrictions
        self.restrictions = Restrictions(case_study)

        # Economics
        self.economics = Economics(case_study)

        # Balance utility heat exchangers
        self.balance_utility_heat_exchangers = list()
        for exchanger in case_study.range_balance_utility_heat_exchangers:
            self.balance_utility_heat_exchangers.append(BalanceUtilityHeatExchanger(case_study, self.thermodynamic_parameter, exchanger))

    def get_sorted_heat_exchangers_on_stream(self, stream, stream_type):
        heat_exchanger_on_stream = []
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent and \
                ((stream_type == 'hot' and self.heat_exchangers[exchanger].topology.hot_stream == stream) or
                 (stream_type == 'cold' and self.heat_exchangers[exchanger].topology.cold_stream == stream)):
                heat_exchanger_on_stream.append(exchanger)
        heat_exchanger_on_stream_sorted = np.zeros([len(heat_exchanger_on_stream)], dtype=int)
        if stream_type == 'hot':
            heat_exchanger_on_stream_sorted = sorted(heat_exchanger_on_stream, key=lambda on_stream: self.heat_exchangers[on_stream].topology.enthalpy_stage)
        elif stream_type == 'cold':
            heat_exchanger_on_stream_sorted = sorted(heat_exchanger_on_stream, key=lambda on_stream: self.heat_exchangers[on_stream].topology.enthalpy_stage)
        return np.array(heat_exchanger_on_stream_sorted)

    def get_sorted_heat_exchangers_on_initial_stream(self, stream, stream_type):
        heat_exchanger_on_stream = []
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent and \
                ((stream_type == 'hot' and self.heat_exchangers[exchanger].topology.initial_hot_stream == stream) or
                 (stream_type == 'cold' and self.heat_exchangers[exchanger].topology.initial_cold_stream == stream)):
                heat_exchanger_on_stream.append(exchanger)
        heat_exchanger_on_stream_sorted = np.zeros([len(heat_exchanger_on_stream)], dtype=int)
        if stream_type == 'hot':
            heat_exchanger_on_stream_sorted = sorted(heat_exchanger_on_stream, key=lambda on_stream: self.heat_exchangers[on_stream].topology.initial_enthalpy_stage)
        elif stream_type == 'cold':
            heat_exchanger_on_stream_sorted = sorted(heat_exchanger_on_stream, key=lambda on_stream: self.heat_exchangers[on_stream].topology.initial_enthalpy_stage)
        return np.array(heat_exchanger_on_stream_sorted)

    def get_utility_heat_exchangers(self, stream_type):
        utility_heat_exchanger = []
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent and \
                ((stream_type == 'hot' and self.heat_exchangers[exchanger].topology.hot_stream in self.hot_utilities_indices) or
                 (stream_type == 'cold' and self.heat_exchangers[exchanger].topology.cold_stream in self.cold_utilities_indices)):
                utility_heat_exchanger.append(exchanger)
        return np.array(utility_heat_exchanger)

    @property
    def hot_utility_demand(self):
        hot_utility_exchangers = self.get_utility_heat_exchangers('hot')
        hot_utility_demand = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            hot_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case] * self.operating_cases[operating_case].duration for exchanger in hot_utility_exchangers])
            for exchanger in self.range_balance_utility_heat_exchangers:
                if self.balance_utility_heat_exchangers[exchanger].utility_type == 'H':
                    hot_utility_demand[operating_case] += self.balance_utility_heat_exchangers[exchanger].heat_loads[operating_case] * self.operating_cases[operating_case].duration
        return hot_utility_demand

    @property
    def cold_utility_demand(self):
        cold_utility_exchangers = self.get_utility_heat_exchangers('cold')
        cold_utility_demand = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            cold_utility_demand[operating_case] = np.sum([self.heat_exchangers[exchanger].operation_parameter.heat_loads[operating_case] * self.operating_cases[operating_case].duration for exchanger in cold_utility_exchangers])
            for exchanger in self.range_balance_utility_heat_exchangers:
                if self.balance_utility_heat_exchangers[exchanger].utility_type == 'C':
                    cold_utility_demand[operating_case] += self.balance_utility_heat_exchangers[exchanger].heat_loads[operating_case] * self.operating_cases[operating_case].duration
        return cold_utility_demand

    @property
    def split_costs(self):
        split_costs = 0
        for stage in self.range_enthalpy_stages:
            for hot_stream in self.range_hot_streams:
                number_heat_exchangers_hot = 0
                number_heat_exchangers_hot_initial = 0
                initial_split_heat_exchanger_hot = []
                split_heat_exchanger_hot = []
                for exchanger in self.range_heat_exchangers:
                    if self.heat_exchangers[exchanger].topology.existent and \
                            self.heat_exchangers[exchanger].topology.enthalpy_stage == stage and \
                            self.heat_exchangers[exchanger].topology.hot_stream == hot_stream:
                        split_heat_exchanger_hot.append(exchanger)
                        number_heat_exchangers_hot += 1
                    if self.heat_exchangers[exchanger].topology.initial_existent and \
                            self.heat_exchangers[exchanger].topology.initial_enthalpy_stage == stage and \
                            self.heat_exchangers[exchanger].topology.hot_stream == hot_stream:
                        initial_split_heat_exchanger_hot.append(exchanger)
                        number_heat_exchangers_hot_initial += 1
                if number_heat_exchangers_hot > 1 and number_heat_exchangers_hot_initial > 1:
                    # if split is modified
                    for exchanger in self.range_heat_exchangers:
                        if exchanger in split_heat_exchanger_hot and exchanger not in initial_split_heat_exchanger_hot:
                            split_costs += self.heat_exchangers[exchanger].costs.base_split_costs
                        elif exchanger not in split_heat_exchanger_hot and exchanger in initial_split_heat_exchanger_hot:
                            split_costs += self.heat_exchangers[exchanger].costs.remove_split_costs

                elif number_heat_exchangers_hot <= 1 and number_heat_exchangers_hot_initial > 1:
                    # if split is removed
                    for exchanger in self.range_heat_exchangers:
                        if exchanger in initial_split_heat_exchanger_hot:
                            split_costs += self.heat_exchangers[exchanger].costs.remove_split_costs

                elif number_heat_exchangers_hot > 1 and number_heat_exchangers_hot_initial <= 1:
                    # if split is added
                    for exchanger in self.range_heat_exchangers:
                        if exchanger in split_heat_exchanger_hot:
                            split_costs += self.heat_exchangers[exchanger].costs.base_split_costs

            for cold_stream in self.range_cold_streams:
                number_heat_exchangers_cold = 0
                number_heat_exchangers_cold_initial = 0
                initial_split_heat_exchanger_cold = []
                split_heat_exchanger_cold = []
                for exchanger in self.range_heat_exchangers:
                    if self.heat_exchangers[exchanger].topology.existent and \
                            self.heat_exchangers[exchanger].topology.enthalpy_stage == stage and \
                            self.heat_exchangers[exchanger].topology.cold_stream == cold_stream:
                        split_heat_exchanger_cold.append(exchanger)
                        number_heat_exchangers_cold += 1
                    if self.heat_exchangers[exchanger].topology.existent and \
                            self.heat_exchangers[exchanger].topology.initial_enthalpy_stage == stage and \
                            self.heat_exchangers[exchanger].topology.initial_cold_stream == cold_stream:
                        initial_split_heat_exchanger_cold.append(exchanger)
                        number_heat_exchangers_cold_initial += 1

                if number_heat_exchangers_cold > 1 and number_heat_exchangers_cold_initial > 1:
                    # if split is modified
                    for exchanger in self.range_heat_exchangers:
                        if exchanger in split_heat_exchanger_cold and exchanger not in initial_split_heat_exchanger_cold:
                            split_costs += self.heat_exchangers[exchanger].costs.base_split_costs
                        elif exchanger not in split_heat_exchanger_cold and exchanger in initial_split_heat_exchanger_cold:
                            split_costs += self.heat_exchangers[exchanger].costs.remove_split_costs

                elif number_heat_exchangers_cold <= 1 and number_heat_exchangers_cold_initial > 1:
                    # if split is removed
                    for exchanger in self.range_heat_exchangers:
                        if exchanger in initial_split_heat_exchanger_cold:
                            split_costs += self.heat_exchangers[exchanger].costs.remove_split_costs

                elif number_heat_exchangers_cold > 1 and number_heat_exchangers_cold_initial <= 1:
                    # if split is added
                    for exchanger in self.range_heat_exchangers:
                        if exchanger in split_heat_exchanger_cold:
                            split_costs += self.heat_exchangers[exchanger].costs.base_split_costs

        return split_costs

    @property
    def repipe_costs(self):
        repipe_costs = 0
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent and \
                    self.heat_exchangers[exchanger].topology.initial_existent:
                if self.heat_exchangers[exchanger].topology.hot_stream != self.heat_exchangers[exchanger].topology.initial_hot_stream:
                    repipe_costs += self.heat_exchangers[exchanger].costs.base_repipe_costs
                if self.heat_exchangers[exchanger].topology.cold_stream != self.heat_exchangers[exchanger].topology.initial_cold_stream:
                    repipe_costs += self.heat_exchangers[exchanger].costs.base_repipe_costs
        return repipe_costs

    @property
    def resequence_costs(self):
        resequence_costs_hot_cold = 0
        for stream_type in ['hot', 'cold']:
            modified_heat_exchangers = np.array([], dtype=int)
            for stream in self.range_hot_streams:
                heat_exchangers_on_initial_stream = self.get_sorted_heat_exchangers_on_initial_stream(stream, stream_type).tolist()
                heat_exchangers_on_stream = self.get_sorted_heat_exchangers_on_stream(stream, stream_type).tolist()
                for exchanger in range(len(heat_exchangers_on_initial_stream)):
                    if heat_exchangers_on_initial_stream[exchanger] not in heat_exchangers_on_stream:
                        heat_exchangers_on_initial_stream = heat_exchangers_on_initial_stream[heat_exchangers_on_initial_stream != heat_exchangers_on_initial_stream[exchanger]]
                    if heat_exchangers_on_stream[exchanger] not in heat_exchangers_on_initial_stream:
                        heat_exchangers_on_stream = heat_exchangers_on_stream[heat_exchangers_on_stream != heat_exchangers_on_stream[exchanger]]
                matcher = difflib.SequenceMatcher(None, heat_exchangers_on_initial_stream, heat_exchangers_on_stream)
                for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
                    if tag == 'delete':
                        modified_heat_exchangers = np.append(modified_heat_exchangers, heat_exchangers_on_initial_stream[i1:i2])
                        del heat_exchangers_on_initial_stream[i1:i2]
                    elif tag == 'insert':
                        modified_heat_exchangers = np.append(modified_heat_exchangers, heat_exchangers_on_stream[j1:j2])
                        heat_exchangers_on_initial_stream[i1:i2] = heat_exchangers_on_stream[j1:j2]
                    elif tag == 'replace':
                        modified_heat_exchangers = np.append(modified_heat_exchangers, heat_exchangers_on_initial_stream[i1:i2])
                        modified_heat_exchangers = np.append(modified_heat_exchangers, heat_exchangers_on_stream[j1:j2])
                        heat_exchangers_on_initial_stream[i1:i2] = heat_exchangers_on_stream[j1:j2]
            modified_heat_exchangers_unique = np.unique(np.squeeze(modified_heat_exchangers))
            resequence_costs = 0
            for exchanger in modified_heat_exchangers_unique:
                resequence_costs += self.heat_exchangers[exchanger].costs.base_resequence_costs
            resequence_costs_hot_cold += resequence_costs
        return resequence_costs_hot_cold

    @property
    def match_costs(self):
        match_costs = 0
        for exchanger in self.range_heat_exchangers:
            if self.heat_exchangers[exchanger].topology.existent:
                if (self.heat_exchangers[exchanger].topology.hot_stream != self.heat_exchangers[exchanger].topology.initial_hot_stream) or \
                        (self.heat_exchangers[exchanger].topology.cold_stream != self.heat_exchangers[exchanger].topology.initial_cold_stream):
                    match_costs += self.economics.match_cost[self.heat_exchangers[exchanger].topology.cold_stream, self.heat_exchangers[exchanger].topology.hot_stream]
        return match_costs

    @property
    def heat_exchanger_costs(self):
        heat_exchanger_costs = 0
        for exchanger in self.range_heat_exchangers:
            heat_exchanger_costs += self.heat_exchangers[exchanger].total_costs
        for exchanger in self.range_balance_utility_heat_exchangers:
            heat_exchanger_costs += self.balance_utility_heat_exchangers[exchanger].exchanger_costs
        return heat_exchanger_costs

    @property
    def capital_costs(self):
        return self.split_costs + self.repipe_costs + self.resequence_costs + self.match_costs + self.heat_exchanger_costs

    @property
    def operating_costs(self):
        return sum(self.hot_utility_demand * self.economics.specific_hot_utilities_cost) + sum(self.cold_utility_demand * self.economics.specific_cold_utilities_cost)

    @property
    def total_annual_costs(self):
        # TODO: heat loads and whole calculation should also be performed if topology is feasible!
        return self.economics.annuity_factor * self.capital_costs + self.operating_costs

    @property
    def heat_exchanger_feasibility(self):
        # TODO: needs testing!
        for exchanger in self.range_heat_exchangers:
            if not self.heat_exchangers[exchanger].is_feasible:
                return False
        return True

    @property
    def energy_balance_feasibility(self):
        if self.hot_utility_demand >= 0 and \
                self.cold_utility_demand >= 0:
            return True
        else:
            return False

    def split_heat_exchanger_violation_distance(self, exchanger_addresses):
        # TODO: needs testing!
        number_split_violations = 0
        for stage in self.range_enthalpy_stages:
            for stream in self.range_hot_streams:
                h_dubs = 0
                for exchanger in self.range_heat_exchangers:
                    if stream not in self.hot_utilities_indices and \
                            exchanger_addresses[exchanger][7] and \
                            exchanger_addresses[exchanger][0] == stream and \
                            exchanger_addresses[exchanger][2] == stage:
                        h_dubs += 1
                if h_dubs > self.restrictions.max_splits:
                    number_split_violations += h_dubs - (self.restrictions.max_splits + 1)
            for stream in self.range_cold_streams:
                c_dubs = 0
                for exchanger in self.range_heat_exchangers:
                    if stream not in self.cold_utilities_indices and \
                            exchanger_addresses[exchanger][7] and \
                            exchanger_addresses[exchanger][1] == stream and \
                            exchanger_addresses[exchanger][2] == stage:
                        c_dubs += 1
                if c_dubs > self.restrictions.max_splits:
                    number_split_violations += c_dubs - (self.restrictions.max_splits + 1)
        return number_split_violations

    def utility_connections_violation_distance(self, exchanger_addresses):
        # TODO: needs testing!
        utility_connections = 0
        for exchanger in self.range_heat_exchangers:
            if exchanger_addresses[0][exchanger] in self.hot_utilities_indices and \
                    exchanger_addresses[1][exchanger] in self.cold_utilities_indices:
                utility_connections += 1
        return utility_connections

    def topology_violation_distance(self, exchanger_addresses):
        # TODO: needs testing!
        # TODO: needs to be called before creating a network (using only the EAM)
        return self.split_heat_exchanger_violation_distance(exchanger_addresses) + self.utility_connections_violation_distance(exchanger_addresses)

    @property
    def is_feasible(self):
        # TODO: maybe a distance function is needed too
        if self.heat_exchanger_feasibility and  \
                self.energy_balance_feasibility:
            return True
        else:
            return False

    def __repr__(self):
        pass

    def __str__(self):
        pass
