from multiprocessing import Pool
from timeit import default_timer as timer
import copy as cp
import bisect as bc
import numpy as np
from deap import tools
from deap.tools._hypervolume import hv
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
    
    def initialize_pseudo_pareto_front_de(self, toolbox):
        """Create a pseudo differential evolution pareto front for infeasible genetic algorithm individuals"""
        pseudo_exchanger_addresses = np.zeros([self.case_study.number_heat_exchangers, 8],dtype=int)
        toolbox.register('pseudo_individual_de', self.differential_evolution.initialize_individual, creator.Individual_de, pseudo_exchanger_addresses)
        toolbox.register('pseudo_population_de', tools.initRepeat, list, toolbox.pseudo_individual_de)
        pseudo_population_de = toolbox.pseudo_population_de(n=1)
        pseudo_population_de[0][1].exchanger_addresses.matrix = pseudo_exchanger_addresses
        return pseudo_population_de

    def fitness_function(self, individual):
        """Evaluation of HEN topology (if feasible DE population is generated and optimized)"""
        quadratic_distance_split_infeasibility = (0 - self.heat_exchanger_network.split_heat_exchanger_violation_distance(individual))**2
        quadratic_distance_utility_connection_infeasibility = (0 - self.heat_exchanger_network.utility_connections_violation_distance(individual))**2
        quadratic_distance = quadratic_distance_split_infeasibility + quadratic_distance_utility_connection_infeasibility
        if quadratic_distance > 0:
            of_total_annual_cost = 1 / (2 + quadratic_distance)
            of_greenhouse_gases = 1 / (2 + quadratic_distance)
            self.pseudo_pareto_front_de[0][1].exchanger_addresses.matrix = individual
            self.pseudo_pareto_front_de[0].fitness.values = (of_total_annual_cost, of_greenhouse_gases)
            pareto_front_de = cp.deepcopy(self.pseudo_pareto_front_de)
        else:
            self.differential_evolution.differential_evolution(individual)
            pareto_front_de = cp.deepcopy(self.differential_evolution.pareto_front_de)
        return pareto_front_de  

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
    def evaluate_hypervolume(self, population_ga):
        """Evaluates the hypervolumes of all differential evolution pareto fronts. These values are used for the selection in the GA algorithm"""
        fitnesses = []
        for _, individual_ga in enumerate(population_ga):
            ind_de = 0
            while ind_de < len(individual_ga):
                fitnesses.append(individual_ga[ind_de].fitness.wvalues)
                ind_de += 1
        fitnesses = np.array(fitnesses)
        reference_point = (np.max(fitnesses[:,0])+1, np.max(fitnesses[:,1])+1)
        for _, individual_ga in enumerate(population_ga):
            if len(individual_ga) <=1 and np.sum(individual_ga[0][0]) == 0.0:
                # All heat loads are zero if we use the pseudo Pareto front (infeasible GA solutions)
                individual_ga.indicator.values = -100,
            else:
                fitnesses_de = np.array([ind_de.fitness.wvalues for ind_de in individual_ga])
                individual_ga.indicator.values = hv.hypervolume(fitnesses_de, reference_point) * -1, 

    def reformat_individual_evolution(self, individual_de):
        """Reformat the DE individual for the GA evolution and optimization"""
        del individual_de[0][0:2]
        if not isinstance(individual_de[0][0], list):
            individual_de[0][0:7] = individual_de[0][0].tolist()
        if len(individual_de[0]) < 7:
            individual_de = cp.copy(individual_de[0])
        del individual_de[0].fitness.values
        return individual_de[0]

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
        creator.create('HyperVolumeIndicator_ga', base.Fitness, weights=(1.0,))
        creator.create('ParetoIndividual_ga', list, indicator=creator.HyperVolumeIndicator_ga)
        # DE: Create DE classes
        creator.create('FitnessMin_de', base.Fitness, weights=(1.0,1.0))
        creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
        # GA: Define individuals of exchanger address matrices: 
        toolbox = base.Toolbox()
        toolbox.register('individual_ga', self.initialize_individual, creator.Individual_ga)
        toolbox.register('initial_population_ga', tools.initRepeat, list, toolbox.individual_ga)
        toolbox.register('population_pareto', tools.initRepeat, list, creator.ParetoIndividual_ga)
        toolbox.register('evaluate_ga', self.fitness_function)
        toolbox.register('select_ga', tools.selTournament, k=self.algorithm_parameter.genetic_algorithm_population_size, tournsize=self.algorithm_parameter.genetic_algorithm_tournament_size)
        toolbox.register('mate_ga', self.crossover)
        toolbox.register('mutate_ga', self.mutation)
        # GA: Create a pseudo DE population for infeasible GA individuals
        self.pseudo_pareto_front_de = self.initialize_pseudo_pareto_front_de(toolbox)
        # GA: Generate population
        population_initial = toolbox.initial_population_ga(self.algorithm_parameter.genetic_algorithm_population_size)
        hall_of_fame = tools.HallOfFame(maxsize=self.algorithm_parameter.genetic_algorithm_hall_of_fame_size) 
        # GA: Evaluate entire population 
        if self.algorithm_parameter.number_workers == 1:
            results_de = list(map(toolbox.evaluate_ga, population_initial)) 
        elif np.isnan(self.algorithm_parameter.number_workers):
            with Pool() as worker: 
                results_de = list(worker.map(toolbox.evaluate_ga, population_initial))
        else:
            with Pool(self.algorithm_parameter.number_workers) as worker:
                results_de = list(worker.map(toolbox.evaluate_ga, population_initial))
        population_ga = self.update_population_ga(toolbox, results_de)

        self.evaluate_hypervolume(population_ga)

        number_generations_ga = 0
        start = timer()
        while number_generations_ga < self.algorithm_parameter.genetic_algorithm_number_generations:
            """Genetic algorithm"""
            number_generations_ga += 1
            print('--GA: Generation %i --' % number_generations_ga)
            # GA: Select the next generation of individuals 
            offspring = toolbox.select_ga(population_ga, fit_attr="indicator") 
            # GA: Clone selected individuals and bring offspring in initial population design
            offspring = list(toolbox.map(toolbox.clone, offspring))
            # GA: crossover
            invalid_individuals = toolbox.initial_population_ga(0) 
            valid_individuals = toolbox.initial_population_ga(0) 
            for child_1, child_2 in zip(offspring[::2], offspring[1::2]):
                if rng.random() < self.algorithm_parameter.genetic_algorithm_probability_crossover:
                    child_1 = self.reformat_individual_evolution(child_1)
                    child_2 = self.reformat_individual_evolution(child_2)
                    toolbox.mate_ga(child_1, child_2)
                    toolbox.mutate_ga(child_1)
                    toolbox.mutate_ga(child_2)
                    invalid_individuals.append(child_1)
                    invalid_individuals.append(child_2)
                else:
                    child_1_temporary = cp.deepcopy(child_1)
                    child_1_temporary = self.reformat_individual_evolution(child_1_temporary)
                    child_2_temporary = cp.deepcopy(child_2)
                    child_2_temporary = self.reformat_individual_evolution(child_2_temporary)
                    mutated_child_1 = toolbox.mutate_ga(child_1_temporary)
                    mutated_child_2 = toolbox.mutate_ga(child_2_temporary)
                    if mutated_child_1:
                        invalid_individuals.append(child_1_temporary)
                    else:
                        del child_1.indicator.values
                        valid_individuals.append(child_1)
                    if mutated_child_2:
                        invalid_individuals.append(child_2_temporary)
                    else:
                        del child_2.indicator.values
                        valid_individuals.append(child_2)

            if not len(offspring) % 2 == 0:
                last_individual = offspring[-1]
                last_individual_temporary = cp.deepcopy(offspring[-1])
                last_individual_temporary = self.reformat_individual_evolution(last_individual_temporary)
                mutated = toolbox.mutate_ga(last_individual_temporary)
                if mutated:
                    invalid_individuals.append(last_individual_temporary)
                else:
                    del last_individual.indicator.values
                    valid_individuals.append(last_individual)

            if self.algorithm_parameter.number_workers == 1:
                results_de = list(map(toolbox.evaluate_ga, invalid_individuals))

            elif np.isnan(self.algorithm_parameter.number_workers):
                with Pool() as worker: 
                    results_de = list(worker.map(toolbox.evaluate_ga, invalid_individuals))
            else:
                with Pool(self.algorithm_parameter.number_workers) as worker: 
                    results_de = list(worker.map(toolbox.evaluate_ga, invalid_individuals))
            
            population_ga_updated = self.update_population_ga(toolbox, results_de)
            for _, valid_individual in enumerate(valid_individuals):
                population_ga_updated.append(valid_individual)

            self.evaluate_hypervolume(population_ga_updated)
            population_ga = toolbox.select_ga(population_ga_updated, fit_attr="indicator")

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
