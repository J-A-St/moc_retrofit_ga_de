
from src.heat_exchanger_network.heat_exchanger.costs import Costs
from src.heat_exchanger_network.heat_exchanger.operation_parameter import OperationParameter
from src.heat_exchanger_network.heat_exchanger.topology import Topology


class HeatExchanger:
    """"Heat exchanger object"""

    def __init__(self, case_study, number):
        self.number = number
        # Topology instance variables
        self.topology = Topology(case_study, number)
        # Operation parameter instance variables
        self.operation_parameter = OperationParameter(case_study, number)
        # Cost instance variables
        self.costs = Costs(case_study, number)

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
                          'logarithmic temperature difference: {}'.format(self.operation_parameter.logarithmic_temperature_differences),
                          'needed areas: {}'.format(self.operation_parameter.needed_areas),
                          'area: {}'.format(self.operation_parameter.area)])

    def __str__(self):
        pass
