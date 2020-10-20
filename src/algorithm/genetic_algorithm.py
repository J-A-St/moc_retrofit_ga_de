from src.algorithm.differential_evolution import DifferentalEvolution
from src.heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork
from multiprocessing import Pool
from timeit import default_timer as timer
import numpy as np
from deap import tools
from deap import creator
from deap import base
import numpy as np
rng = np.random.default_rng()


class GeneticAlgorithm:
    """genetic algorithm (GA) for optimization of the heat exchanger network topology"""

    def __init__(self, case_study, algorithm_parameter):
        self.range_heat_exchangers = case_study.range_heat_exchangers
        self.number_hot_streams = case_study.number_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.number_enthalpy_stages = case_study.number_enthalpy_stages

        self.penalty_total_annual_cost_value = case_study.manual_parameter['GA_TAC_Penalty'].iloc[0]
        self.probability_bit_flip = algorithm_parameter.genetic_algorithm_probability_bit_flip

        self.heat_exchanger_network = HeatExchangerNetwork(case_study)
        self.differential_evolution = DifferentalEvolution(case_study, algorithm_parameter)

    def initialize_individual(self, individual_class):
        """Creates an individual (HEN topology) with the genes: hot_stream, cold_stream, enthalpy_stage, bypass_hot_stream (in DE determined),
           admixer_hot_stream (in DE determined), bypass_cold_stream (in DE determined), admixer_cold_stream (in DE determined), existent"""
        exchanger_addresses = []
        for _ in self.range_heat_exchangers:
            existent = rng.choice(True, False)
            if existent:
                hot_stream = rng.integers(0, self.number_hot_streams + 1)
                cold_stream = rng.integers(0, self.number_cold_streams + 1)
                enthalpy_stage = rng.integers(0, self.number_enthalpy_stages + 1)
            else:
                hot_stream = 0
                cold_stream = 0
                enthalpy_stage = 0
            bypass_hot_stream = 0
            admixer_hot_stream = 0
            bypass_cold_stream = 0
            admixer_cold_stream = 0
            exchanger_addresses.append([hot_stream, cold_stream, enthalpy_stage, bypass_hot_stream, admixer_hot_stream, bypass_cold_stream, admixer_cold_stream, existent])
        exchanger_addresses = list(map(list, zip(*exchanger_addresses)))
        individual = individual_class(exchanger_addresses)
        return individual

    def fitness_function(self, individual):
        """Evaluation of HEN topology (if feasible DE population is generated and optimized)"""
        # TODO: add differential evolution solution to GA solution! (see ga_de_retrofit)
        quadratic_distance_split_infeasibility = (0 - self.heat_exchanger_network.split_heat_exchanger_violation_distance(individual))**2
        quadratic_distance_utility_connection_infeasibility = (0 - self.heat_exchanger_network.utility_connections_violation_distance(individual))**2
        if quadratic_distance_split_infeasibility > 0 or quadratic_distance_utility_connection_infeasibility > 0:
            fitness = 1 / (self.penalty_total_annual_cost_value + quadratic_distance_split_infeasibility + quadratic_distance_utility_connection_infeasibility)
        else:
            fitness = self.differential_evolution.differential_evolution(individual)
        return fitness,

    @staticmethod
    def crossover(self, child_1, child_2):
        """Crossover operator of genes"""
        for exchanger in self.range_heat_exchangers:
            child_1[exchanger], child_2[exchanger] = list(tools.cx0nePoint(child_1[exchanger], child_2[exchanger]))
        return child_1, child_2

    def mutation(self, individual):
        """Mutation operator of alleles: uniform distribution for process streams and enthalpy intervals, bounded by their max and min values,
         and random bit flip for the existence of a heat exchanger"""
        for gene_number, gene in enumerate(individual):
            if gene_number == 0:
                individual[gene_number] = list(tools.mutUniformInt(gene, 0, self.number_hot_streams, self.probability_bit_flip))
                individual[gene_number] = individual[gene_number].pop(0)
            elif gene_number == 1:
                individual[gene_number] = list(tools.mutUniformInt(gene, 0, self.number_cold_streams, self.probability_bit_flip))
                individual[gene_number] = individual[gene_number].pop(0)
            elif gene_number == 2:
                individual[gene_number] = list(tools.mutUniformInt(gene, 0, self.number_enthalpy_stages, self.probabiliy_bit_flip))
                individual[gene_number] = individual[gene_number].pop(0)
            elif gene_number == 7:
                individual[gene_number] = list(tools.mutFlipBit(gene, self.probability_bit_flip))
                individual[gene_number] = individual[gene_number].pop(0)
        return individual
