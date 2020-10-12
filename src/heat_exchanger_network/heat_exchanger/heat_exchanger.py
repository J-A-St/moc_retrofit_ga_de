import numpy as np

from src.heat_exchanger_network.heat_exchanger.costs import Costs
from src.heat_exchanger_network.heat_exchanger.operation_parameter import OperationParameter
from src.heat_exchanger_network.heat_exchanger.topology import Topology


class HeatExchanger:
    """"Heat exchanger object"""

    def __init__(self, exchanger_addresses, thermodynamic_parameter, case_study, number):
        self.number = number
        # Topology instance variables
        self.topology = Topology(exchanger_addresses, case_study, number)
        # Operation parameter instance variables
        self.operation_parameter = OperationParameter(thermodynamic_parameter, self.topology, case_study, number)
        self.extreme_temperature_hot_stream = case_study.hot_streams[self.topology.hot_stream].extreme_temperatures
        self.extreme_temperature_cold_stream = case_study.cold_streams[self.topology.cold_stream].extreme_temperatures
        # Cost instance variables
        self.costs = Costs(case_study, number)

    @property
    def exchanger_costs(self):
        exchanger_costs = 0
        if self.topology.existent and self.topology.initial_existent:
            if self.operation_parameter.area > self.operation_parameter.initial_area:
                exchanger_costs = self.costs.base_costs + self.costs.specific_area_costs * (self.operation_parameter.area - self.operation_parameter.initial_area) ** self.costs.degression_area
        elif self.topology.existent and not self.topology.initial_existent:
            exchanger_costs = self.costs.base_costs + self.costs.specific_area_costs * self.operation_parameter.area ** self.costs.degression_area
        elif not self.topology.existent and self.topology.initial_existent:
            exchanger_costs = self.costs.remove_costs
        return exchanger_costs

    @property
    def admixer_costs(self):
        admixer_costs = 0
        if self.topology.existent:
            if self.topology.admixer_hot_stream_existent and not self.topology.initial_admixer_hot_stream_existent:
                admixer_costs += self.costs.base_admixer_costs
            elif not self.topology.admixer_hot_stream_existent and self.topology.initial_admixer_hot_stream_existent:
                admixer_costs += self.costs.remove_admixer_costs
            if self.topology.admixer_cold_stream_existent and not self.topology.initial_admixer_cold_stream_existent:
                admixer_costs += self.costs.base_admixer_costs
            elif not self.topology.admixer_cold_stream_existent and self.topology.initial_admixer_cold_stream_existent:
                admixer_costs += self.costs.remove_admixer_costs
        else:
            admixer_costs += self.costs.remove_admixer_costs
        return admixer_costs

    @property
    def bypass_costs(self):
        bypass_costs = 0
        if self.topology.existent:
            if self.topology.bypass_hot_stream_existent and not self.topology.initial_bypass_hot_stream_existent:
                bypass_costs += self.costs.base_bypass_costs
            elif not self.topology.bypass_hot_stream_existent and self.topology.initial_bypass_hot_stream_existent:
                bypass_costs += self.costs.remove_bypass_costs
            if self.topology.bypass_cold_stream_existent and not self.topology.initial_bypass_cold_stream_existent:
                bypass_costs += self.costs.base_bypass_costs
            elif not self.topology.bypass_cold_stream_existent and self.topology.initial_bypass_cold_stream_existent:
                bypass_costs += self.costs.remove_bypass_costs
        else:
            bypass_costs += self.costs.remove_bypass_costs
        return bypass_costs

    @property
    def total_costs(self):
        return self.exchanger_costs + self.admixer_costs + self.bypass_costs

    @property
    def feasibility_logarithmic_mean_temperature_differences(self):
        is_feasible = [False] * self.operation_parameter.number_operating_cases
        for operating_case in self.operation_parameter.range_operating_cases:
            if np.isnan(self.operation_parameter.logarithmic_mean_temperature_differences_no_mixer[operating_case]) or self.operation_parameter.logarithmic_mean_temperature_differences_no_mixer[operating_case] <= 0:
                is_feasible[operating_case] = False
            else:
                is_feasible[operating_case] = True
        return all(is_feasible)

    @property
    def feasibility_temperature_differences(self):
        is_feasible = [False] * self.operation_parameter.number_operating_cases
        for operating_case in self.operation_parameter.range_operating_cases:
            if self.operation_parameter.outlet_temperatures_hot_stream[operating_case] <= self.operation_parameter.inlet_temperatures_cold_stream[operating_case]:
                is_feasible[operating_case] = False
            elif self.operation_parameter.inlet_temperatures_hot_stream[operating_case] <= self.operation_parameter.outlet_temperatures_cold_stream[operating_case]:
                is_feasible[operating_case] = False
            else:
                is_feasible[operating_case] = True
        return all(is_feasible)

    @property
    def feasibility_mixer(self):
        is_feasible = [False] * self.operation_parameter.number_operating_cases
        for operating_case in self.operation_parameter.range_operating_cases:
            if self.operation_parameter.mixer_types[operating_case] == 'bypass_hot' and self.operation_parameter.outlet_temperatures_hot_stream[operating_case] < self.extreme_temperature_hot_stream[operating_case]:
                is_feasible[operating_case] = False
            elif self.operation_parameter.mixer_types[operating_case] == 'admixer_hot' and self.operation_parameter.inlet_temperatures_hot_stream[operating_case] <= self.operation_parameter.outlet_temperatures_hot_stream[operating_case]:
                is_feasible[operating_case] = False
            elif self.operation_parameter.mixer_types[operating_case] == 'bypass_cold' and self.operation_parameter.outlet_temperatures_cold_stream[operating_case] > self.extreme_temperature_cold_stream[operating_case]:
                is_feasible[operating_case] = False
            elif self.operation_parameter.mixer_types[operating_case] == 'admixer_cold' and self.operation_parameter.inlet_temperatures_cold_stream[operating_case] >= self.operation_parameter.outlet_temperatures_cold_stream[operating_case]:
                is_feasible[operating_case] = False
            else:
                is_feasible[operating_case] = True
        return all(is_feasible)

    @property
    def is_feasible(self):
        if self.feasibility_logarithmic_mean_temperature_differences and self.feasibility_temperature_differences and self.feasibility_mixer:
            return True
        else:
            return False

    def __repr__(self):
        pass
        # return '\n'.join(['heat exchanger number {}:'.format(self.number), 'address matrix: {}'.format(self.topology.address_vector),
        #                   'is feasible: {}'.format(self.is_feasible),
        #                   'heat loads: {}'.format(self.operation_parameter.heat_loads), 'hot stream split factions: {}'.format(self.operation_parameter.split_fractions_hot_stream),
        #                   'cold stream split fractions: {}'.format(self.operation_parameter.split_fractions_cold_stream),
        #                   'hot stream mixer fractions: {}'.format(self.operation_parameter.mixer_fractions_hot_stream),
        #                   'cold stream mixer fractions: {}'.format(self.operation_parameter.mixer_fractions_cold_stream),
        #                   'inlet temperatures hot stream: {}'.format(self.operation_parameter.inlet_temperatures_hot_stream),
        #                   'outlet temperatures hot stream: {}'.format(self.operation_parameter.outlet_temperatures_hot_stream),
        #                   'inlet temperatures cold stream: {}'.format(self.operation_parameter.inlet_temperatures_cold_stream),
        #                   'outlet temperatures cold stream: {}'.format(self.operation_parameter.outlet_temperatures_cold_stream),
        #                   'logarithmic temperature difference: {}'.format(self.operation_parameter.logarithmic_mean_temperature_differences_no_mixer),
        #                   'needed areas: {}'.format(self.operation_parameter.needed_areas),
        #                   'area: {}'.format(self.operation_parameter.area)])

    def __str__(self):
        pass
