from src.heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork
from deap import tools
from deap import creator
from deap import base
import numpy as np
rng = np.random.default_rng()


class DifferentialEvolution():
    """Differential evolution (DE) algorithm for optimization of heat duties for from genetic algorithm predefined
    HEX matches"""

    def __init__(self, case_study):
        self.case_study = case_study
        self.number_heat_exchangers = case_study.number_heat_exchanger
        self.range_heat_exchangers = case_study.range_heat_exchanger
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.number_hot_streams = case_study.number_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams
        self.min_heat_load = case_study.manual_parameter['MinimalHeatLoad'].iloc[0]
        self.penalty_total_annual_cost_value = case_study.manual_parameter['GA_TAC_Penalty'].iloc[0]

    def initialize_individual(self, individual_class, exchanger_addresses):
        """Create an individual matrix of heat duties for all existing HEX matches"""
        # TODO: needs testing!
        heat_duties = np.zeros([self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            if exchanger_addresses[exchanger, 7] == 1:
                for operating_case in self.range_operating_cases:
                    max_heat_duty = np.nanmin(self.hot_streams[exchanger_addresses[exchanger, 0]].enthalpy_flows[operating_case], self.cold_streams[exchanger_addresses[exchanger, 1]].enthalpy_flows[operating_case])
                    if max_heat_duty != 0:
                        heat_duties[exchanger, operating_case] = rng.standard_normal(self.min_heat_load, max_heat_duty)
                    else:
                        heat_duties[exchanger, operating_case] = max_heat_duty
        individual = individual_class(heat_duties.tolist())
        return individual

    def fitness_function(self, individual, exchanger_addresses):
        heat_exchanger_network = HeatExchangerNetwork(self.case_study)
        heat_exchanger_network.exchanger_addresses.matrix = exchanger_addresses
        heat_exchanger_network.thermodynamic_parameter.heat_loads = individual
        if heat_exchanger_network.is_feasible:
            fitness = 1 / heat_exchanger_network.total_annual_costs
        else:
            quadratic_distance = sum([heat_exchanger_network.heat_exchangers[exchanger].infeasibility_logarithmic_mean_temperature_differences[1] + heat_exchanger_network.heat_exchangers[exchanger].infeasibility_temperature_differences[1] + heat_exchanger_network.heat_exchangers[exchanger].infeasibility_mixer[1] for exchanger in self.range_heat_exchangers] + heat_exchanger_network.infeasibility_energy_balance[1])

            fitness = 1 / (self.penalty_total_annual_cost_value + quadratic_distance)
        return fitness,
