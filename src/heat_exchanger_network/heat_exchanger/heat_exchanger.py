import numpy as np

from src.heat_exchanger_network.heat_exchanger.costs import Costs
from src.heat_exchanger_network.heat_exchanger.operation_parameter import OperationParameter
from src.heat_exchanger_network.heat_exchanger.topology import Topology


class HeatExchanger:
    """"Heat exchanger object"""
    # TODO: include HEX, bypass, and admixer cost here

    def __init__(self, case_study, number):
        self.number = number
        # Topology instance variables
        self.topology = Topology(case_study, number)
        # Operation parameter instance variables
        self.operation_parameter = OperationParameter(case_study, self.topology, number)
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

    def __repr__(self):
        return '\n'.join(['heat exchanger number {}:'.format(self.number), 'address matrix: {}'.format(self.topology.address_vector),
                          'heat loads: {}'.format(self.operation_parameter.heat_loads), 'hot stream split factions: {}'.format(self.operation_parameter.split_fractions_hot_stream),
                          'cold stream split fractions: {}'.format(self.operation_parameter.split_fractions_cold_stream),
                          'hot stream mixer fractions: {}'.format(self.operation_parameter.mixer_fractions_hot_stream),
                          'cold stream mixer fractions: {}'.format(self.operation_parameter.mixer_fractions_cold_stream),
                          'inlet temperatures hot stream: {}'.format(self.operation_parameter.inlet_temperatures_hot_stream),
                          'outlet temperatures hot stream: {}'.format(self.operation_parameter.outlet_temperatures_hot_stream),
                          'inlet temperatures cold stream: {}'.format(self.operation_parameter.inlet_temperatures_cold_stream),
                          'outlet temperatures cold stream: {}'.format(self.operation_parameter.outlet_temperatures_cold_stream),
                          'logarithmic temperature difference: {}'.format(self.operation_parameter.logarithmic_mean_temperature_differences),
                          'needed areas: {}'.format(self.operation_parameter.needed_areas),
                          'area: {}'.format(self.operation_parameter.area)])

    def __str__(self):
        pass
