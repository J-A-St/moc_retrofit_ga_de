from multiprocessing import Pool
from timeit import default_timer as timer
import numpy as np
from deap import tools
from deap import creator
from deap import base
rng = np.random.default_rng()

from algorithm.differential_evolution import DifferentialEvolution
from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork

class GeneticAlgorithm:
    """genetic algorithm (GA) for optimization of the heat exchanger network topology"""

    def __init__(self, case_study, algorithm_parameter):
        self.case_study = case_study
        self.algorithm_parameter = algorithm_parameter
        self.heat_exchanger_network = HeatExchangerNetwork(case_study)
        self.differential_evolution = DifferentialEvolution(case_study, algorithm_parameter)

    def initialize_individual(self, individual_class):
        """Creates an individual (HEN topology) with the genes: hot_stream, cold_stream, enthalpy_stage, bypass_hot_stream (in DE determined),
           admixer_hot_stream (in DE determined), bypass_cold_stream (in DE determined), admixer_cold_stream (in DE determined), existent"""
        exchanger_addresses = []
        for _ in self.case_study.range_heat_exchangers:
            existent = rng.choice([True, False])
            if existent:
                hot_stream = rng.integers(0, self.case_study.number_hot_streams)
                cold_stream = rng.integers(0, self.case_study.number_cold_streams)
                enthalpy_stage = rng.integers(0, self.case_study.number_enthalpy_stages)
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
        individual = individual_class(np.transpose(exchanger_addresses).tolist())
        return individual
    
    def fitness_function(self, individual):
        """Evaluation of HEN topology (if feasible DE population is generated and optimized)"""
        quadratic_distance_split_infeasibility = (0 - self.heat_exchanger_network.split_heat_exchanger_violation_distance(individual))**2
        quadratic_distance_utility_connection_infeasibility = (0 - self.heat_exchanger_network.utility_connections_violation_distance(individual))**2
        if quadratic_distance_split_infeasibility > 0 or quadratic_distance_utility_connection_infeasibility > 0:
            fitness = 1 / (2 + (quadratic_distance_split_infeasibility + quadratic_distance_utility_connection_infeasibility) / 10)
            best_individual_differential_evolution = np.zeros([self.case_study.number_heat_exchangers, self.case_study.number_operating_cases]).tolist()
            best_individual_differential_evolution = [best_individual_differential_evolution, self.heat_exchanger_network]
            total_annual_costs = self.differential_evolution.economics.initial_operating_costs * 2
            operating_emissions = self.differential_evolution.economics.initial_operating_emissions * 2
        else:
            self.differential_evolution.differential_evolution(individual)
            fitness = self.differential_evolution.best_solution.fitness.values[0]
            best_individual_differential_evolution = self.differential_evolution.best_solution
            total_annual_costs = best_individual_differential_evolution[1].total_annual_cost
            operating_emissions = best_individual_differential_evolution[1].operating_emissions
            for exchanger in self.case_study.range_heat_exchangers:
                if best_individual_differential_evolution[1].heat_exchangers[exchanger].topology.existent:
                    if 'bypass_hot' in best_individual_differential_evolution[1].heat_exchangers[exchanger].operation_parameter.mixer_types:
                        individual[exchanger][3] = 1
                    if 'admixer_hot' in best_individual_differential_evolution[1].heat_exchangers[exchanger].operation_parameter.mixer_types:
                        individual[exchanger][4] = 1
                    if 'bypass_cold' in best_individual_differential_evolution[1].heat_exchangers[exchanger].operation_parameter.mixer_types:
                        individual[exchanger][5] = 1
                    if 'admixer_cold' in best_individual_differential_evolution[1].heat_exchangers[exchanger].operation_parameter.mixer_types:
                        individual[exchanger][6] = 1
                else:
                    individual[exchanger][3] = 0
                    individual[exchanger][4] = 0
                    individual[exchanger][5] = 0
                    individual[exchanger][6] = 0
                
        return fitness, total_annual_costs, best_individual_differential_evolution, individual 

    @staticmethod
    def crossover(child_1, child_2):
        """Crossover operator of genes"""
        cxpoint = rng.integers(1, len(child_1))
        child_1[cxpoint:], child_2[cxpoint:] = child_2[cxpoint:].copy(), child_1[cxpoint:].copy()

    def mutation(self, individual):
        """Mutation operator of alleles: uniform distribution for process streams and enthalpy intervals, bounded by their max and min values,
         and random bit flip for the existence of a heat exchanger"""
        mutated = False
        allele_numbers = [7, 2, 1, 0]
        exchanger_number = 0
        while exchanger_number < self.case_study.number_heat_exchangers:
            allele_index = 0
            while allele_index < len(allele_numbers):
                if allele_numbers[allele_index] == 7 and \
                   rng.random() < self.algorithm_parameter.genetic_algorithm_probability_mutation:
                    mutated = True
                    individual[exchanger_number][7] = not individual[exchanger_number][7]
                    if individual[exchanger_number][7]:
                        individual[exchanger_number][0] = rng.integers(0, self.case_study.number_hot_streams)
                        individual[exchanger_number][1] = rng.integers(0, self.case_study.number_cold_streams)
                        individual[exchanger_number][2] = rng.integers(0, self.case_study.number_enthalpy_stages)
                        break
                    else:
                        individual[exchanger_number][0] = 0
                        individual[exchanger_number][1] = 0
                        individual[exchanger_number][2] = 0
                        break
                elif allele_numbers[allele_index] == 2 and \
                     individual[exchanger_number][7] and \
                     rng.random() < self.algorithm_parameter.genetic_algorithm_probability_mutation:
                    mutated = True
                    individual[exchanger_number][2] = rng.integers(0, self.case_study.number_enthalpy_stages)
                    allele_index += 1
                elif allele_numbers[allele_index] == 1 and \
                     individual[exchanger_number][7] and  \
                     rng.random() < self.algorithm_parameter.genetic_algorithm_probability_mutation:
                    mutated = True
                    individual[exchanger_number][1] = rng.integers(0, self.case_study.number_cold_streams)
                    allele_index += 1
                elif allele_numbers[allele_index] == 0 and \
                     individual[exchanger_number][7] and \
                     rng.random() < self.algorithm_parameter.genetic_algorithm_probability_mutation:
                    mutated = True
                    individual[exchanger_number][0] = rng.integers(0, self.case_study.number_hot_streams)
                    allele_index += 1
                else:
                    allele_index += 1
            exchanger_number += 1
        return mutated
        
    def genetic_algorithm(self):
        """Genetic algorithm (topology optimization)"""
        # GA: Create GA classes
        creator.create('FitnessMin_ga', base.Fitness, weights=(1.0, 1.0))
        creator.create('Individual_ga', list, fitness=creator.FitnessMin_ga)
        # DE: Create DE classes
        creator.create('FitnessMin_de', base.Fitness, weights=(1.0,))
        creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
        # GA: Define individuals of exchanger address matrices
        toolbox = base.Toolbox()
        toolbox.register('individual_ga', self.initialize_individual, creator.Individual_ga)
        toolbox.register('population_ga', tools.initRepeat, list, toolbox.individual_ga)
        toolbox.register('evaluate_ga', self.fitness_function)
        toolbox.register('select_ga', tools.selTournament, tournsize=self.algorithm_parameter.genetic_algorithm_tournament_size)
        toolbox.register('mate_ga', self.crossover)
        toolbox.register('mutate_ga', self.mutation)
        # GA: Generate population
        population_ga = toolbox.population_ga(self.algorithm_parameter.genetic_algorithm_population_size)
        hall_of_fame_ga = tools.HallOfFame(maxsize=self.algorithm_parameter.genetic_algorithm_hall_of_fame_size)
        # GA: Evaluate entire population
        if self.algorithm_parameter.number_workers == 1:
            fitness = list(map(toolbox.evaluate_ga, population_ga))
        elif np.isnan(self.algorithm_parameter.number_workers):
            with Pool() as worker: 
                fitness = list(worker.map(toolbox.evaluate_ga, population_ga))
        else:
            with Pool(self.algorithm_parameter.number_workers) as worker:
                fitness = list(worker.map(toolbox.evaluate_ga, population_ga))

        for individual in range(len(population_ga)):
            population_ga[individual] = fitness[individual][3]
        for individual, fit in zip(population_ga, fitness):
            individual.fitness.values = fit[0:2]
            individual.individual_de = fit[2]

        number_generations_ga = 0
        start = timer()
        while number_generations_ga < self.algorithm_parameter.genetic_algorithm_number_generations:
            """Genetic algorithm"""
            number_generations_ga += 1
            print('--GA: Generation %i --' % number_generations_ga)
            # GA: Select the next generation of individuals
            offspring = toolbox.select_ga(population_ga, len(population_ga))
            # GA: Clone selected individuals
            offspring = list(toolbox.map(toolbox.clone, offspring))
            # GA: crossover
            for child_1, child_2 in zip(offspring[::2], offspring[1::2]):
                if rng.random() < self.algorithm_parameter.genetic_algorithm_probability_crossover:
                    toolbox.mate_ga(child_1, child_2)
                    del child_1.fitness.values
                    del child_2.fitness.values
            for mutant in offspring:
                toolbox.mutate_ga(mutant)
                del mutant.fitness.values
            # GA: Evaluate individuals with invalid fitness (parallel computing of DE)
            invalid_individual_ga = [individual for individual in offspring if not individual.fitness.valid]

            if self.algorithm_parameter.number_workers == 1:
                fitness = list(map(toolbox.evaluate_ga, invalid_individual_ga))

            elif np.isnan(self.algorithm_parameter.number_workers):
                with Pool() as worker: 
                    fitness = list(worker.map(toolbox.evaluate_ga, invalid_individual_ga))
            else:
                with Pool(self.algorithm_parameter.number_workers) as worker: 
                    fitness = list(worker.map(toolbox.evaluate_ga, invalid_individual_ga))

            for ind in range(len(offspring)):
                if not offspring[ind].fitness.valid:
                    offspring[ind] = fitness[ind][3]
                    offspring[ind].fitness.values = fitness[ind][0:2]
                    offspring[ind].individual_de = fitness[ind][2]        
            population_ga[:] = offspring

            # GA: Update Hall of Fame
            if number_generations_ga == 1:
                hall_of_fame_ga.update(population_ga)
            elif number_generations_ga != 1:
                old = sum(hall_of_fame_ga[0].fitness.getValues())
                hall_of_fame_ga.update(population_ga)
                new = sum(hall_of_fame_ga[0].fitness.getValues())

            print('TAC:', hall_of_fame_ga[0].individual_de[1].total_annual_cost)
            print('CO2:', hall_of_fame_ga[0].individual_de[1].operating_emissions)
            print('fitness:', hall_of_fame_ga[0].fitness.values[0])
            print('GA chromosome:', hall_of_fame_ga[0])
            print('DE chromosome:', hall_of_fame_ga[0].individual_de[0])

        print('-- End of evolution --')
        end = timer()
        print('Computation time: %s s' % (end - start))
        print('Hall of fame list:')
        for i in range(len(hall_of_fame_ga)):
            print('Rank:', i + 1)
            print('TAC:', hall_of_fame_ga[0].individual_de[1].total_annual_cost)
            print('CO2:', hall_of_fame_ga[0].individual_de[1].operating_emissions)
            print('fitness:', hall_of_fame_ga[i].fitness.values[0])
            print('GA chromosome:', hall_of_fame_ga[i])
            print('DE chromosome:', hall_of_fame_ga[i].individual_de[0])
            print(10*'-')
        del creator.FitnessMin_ga
        del creator.Individual_ga
        del creator.FitnessMin_de
        del creator.Individual_de
        return hall_of_fame_ga
