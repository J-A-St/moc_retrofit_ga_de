from deap import tools
from deap import creator
from deap import base
import gc
import numpy as np
rng = np.random.default_rng()
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

from heat_exchanger_network.economics import Economics
from heat_exchanger_network.restrictions import Restrictions
from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork

class DifferentialEvolution():
    """Differential evolution (DE) algorithm for optimization of heat duties for from genetic algorithm predefined
    HEX matches"""

    def __init__(self, case_study, algorithm_parameter):
        self.case_study = case_study
        self.restrictions = Restrictions(case_study)
        self.economics = Economics(case_study)
        self.heat_exchanger_network = HeatExchangerNetwork(self.case_study)
        self.absolute_heat_load_tolerance = self.restrictions.absolute_heat_load_tolerance
        self.number_heat_exchangers = case_study.number_heat_exchangers
        self.range_heat_exchangers = case_study.range_heat_exchangers
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.number_hot_streams = case_study.number_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams
        self.min_heat_load = case_study.manual_parameter['MinimalHeatLoad'].iloc[0]
        self.population_size = algorithm_parameter.differential_evolution_population_size
        self.pareto_size = algorithm_parameter.differential_evolution_pareto_size
        self.number_generations = algorithm_parameter.differential_evolution_number_generations
        self.number_no_improvement = algorithm_parameter.differential_evolution_number_no_improvement
        self.probability_crossover = algorithm_parameter.differential_evolution_probability_crossover
        self.perturbation_factor = algorithm_parameter.differential_evolution_perturbation_factor
        self.objective_types = algorithm_parameter.objective_types
        self.pareto_front_de = None
        self.best_solution = None

    def initialize_individual(self, individual_class, exchanger_addresses):
        """Create an individual matrix of heat duties for all existing HEX matches"""
        heat_duties = np.zeros([self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            if exchanger_addresses[exchanger, 7] == 1:
                for operating_case in self.range_operating_cases:
                    max_heat_duty = np.nanmin((self.hot_streams[exchanger_addresses[exchanger, 0]].enthalpy_flows[operating_case], self.cold_streams[exchanger_addresses[exchanger, 1]].enthalpy_flows[operating_case]))
                    if max_heat_duty != 0:
                        heat_duties[exchanger, operating_case] = (max_heat_duty - self.min_heat_load) * rng.random() + self.min_heat_load
                    else:
                        heat_duties[exchanger, operating_case] = max_heat_duty
        individual = individual_class([heat_duties.tolist(), self.heat_exchanger_network])
        return individual
    
    def fitness_function(self, exchanger_addresses, individual):
        """Calculate the whole network including costs"""
        heat_exchanger_network = HeatExchangerNetwork(self.case_study)
        heat_exchanger_network.exchanger_addresses.matrix = exchanger_addresses
        heat_exchanger_network.thermodynamic_parameter.heat_loads = np.array(individual[0])
        for exchanger in self.range_heat_exchangers:
            if 'bypass_hot' in  heat_exchanger_network.heat_exchangers[exchanger].operation_parameter.mixer_types:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 3] = 1
            else:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 3] = 0
            if 'admixer_hot' in  heat_exchanger_network.heat_exchangers[exchanger].operation_parameter.mixer_types:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 4] = 1
            else:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 4] = 0
            if 'bypass_cold' in  heat_exchanger_network.heat_exchangers[exchanger].operation_parameter.mixer_types:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 5] = 1
            else:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 5] = 0
            if 'admixer_cold' in  heat_exchanger_network.heat_exchangers[exchanger].operation_parameter.mixer_types:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 6] = 1
            else:
                heat_exchanger_network.exchanger_addresses.matrix[exchanger, 6] = 0

        heat_exchanger_network.clear_cache()
        if heat_exchanger_network.is_feasible:
            objectives = np.zeros(len(self.objective_types))
            for of in range(len(self.objective_types)):
                if self.objective_types[of] == 'TAC':
                    objectives[of] = self.economics.initial_operating_costs / heat_exchanger_network.total_annual_cost
                elif self.objective_types[of] == 'CAP':
                    objectives[of] = self.economics.initial_operating_costs / (heat_exchanger_network.capital_costs * heat_exchanger_network.economics.annuity_factor)
                elif self.objective_types[of] == 'COP':
                    objectives[of] = self.economics.initial_operating_costs / heat_exchanger_network.operating_costs
                elif self.objective_types[of] == 'GHG':
                    objectives[of] = self.economics.initial_operating_emissions / heat_exchanger_network.operating_emissions

        else:
            quadratic_distance = sum([heat_exchanger_network.heat_exchangers[exchanger].infeasibility_temperature_differences[1] + heat_exchanger_network.heat_exchangers[exchanger].infeasibility_mixer[1] for exchanger in self.range_heat_exchangers] + heat_exchanger_network.infeasibility_energy_balance[1])
            objectives[0] = 1 / (4 + quadratic_distance)
            objectives[1] = 1 / (4 + quadratic_distance)
        return objectives[0], objectives[1], heat_exchanger_network

    def differential_evolution(self, exchanger_addresses):
        """Main differential evolution algorithm"""
        exchanger_addresses = np.array(exchanger_addresses)
        toolbox = base.Toolbox()
        toolbox.register('individual_de', self.initialize_individual, creator.Individual_de, exchanger_addresses)
        toolbox.register('population_de', tools.initRepeat, list, toolbox.individual_de)
        toolbox.register('select_parents_de', tools.selRandom, k=3)
        toolbox.register('select_de', tools.selNSGA2, k=2*self.pareto_size, nd='log')
        toolbox.register('evaluate_de', self.fitness_function, exchanger_addresses)

        # Initialize population
        population = toolbox.population_de(n=self.population_size)
        # Evaluate entire population
        fitness = list(toolbox.map(toolbox.evaluate_de, population))
        for individual, fit in zip(population, fitness):
            individual.fitness.values = fit[0:2]
            individual[1] = fit[2]

        number_generations_de = 0
        number_without_improvement_de = 0
        while number_generations_de <= self.number_generations and number_without_improvement_de <= self.number_no_improvement:
            # print('--DE: Generation %i --' % number_generations_de)
            number_generations_de += 1
            population_temporary = list()
            for pop, agent in enumerate(population):
                individual_r1, individual_r2, individual_r3 = np.array(toolbox.select_parents_de(population))
                individual_donor = toolbox.clone(agent)
                index = rng.choice(len(individual_r1[0]))
                for exchanger in self.range_heat_exchangers:
                    for operating_case in self.range_operating_cases:
                        # recombination / Crossover
                        if pop == index or rng.random() < self.probability_crossover:
                            # Mutation
                            if exchanger_addresses[exchanger, 7]:
                                individual_donor[0][exchanger][operating_case] = np.absolute(individual_r1[0][exchanger][operating_case] + self.perturbation_factor * (individual_r2[0][exchanger][operating_case] - individual_r3[0][exchanger][operating_case]))
                                max_heat_duty = np.nanmin((self.hot_streams[exchanger_addresses[exchanger, 0]].enthalpy_flows[operating_case], self.cold_streams[exchanger_addresses[exchanger, 1]].enthalpy_flows[operating_case]))
                                if max_heat_duty != 0 and (individual_donor[0][exchanger][operating_case] < self.min_heat_load or individual_donor[0][exchanger][operating_case] > max_heat_duty):
                                    individual_donor[0][exchanger][operating_case] = (max_heat_duty - self.min_heat_load) * rng.random() + self.min_heat_load
                            else:
                                individual_donor[0][exchanger][operating_case] = 0.0
                evaluated_donor = toolbox.evaluate_de(individual_donor)
                individual_donor.fitness.values = evaluated_donor[0:2]
                individual_donor[1] = evaluated_donor[2]
                # Selection
                if (individual_donor.fitness.values[0] > agent.fitness.values[0]) and (individual_donor.fitness.values[1] > agent.fitness.values[1]):
                    population_temporary.append(individual_donor)
                    number_without_improvement_de = 0
                elif (individual_donor.fitness.values[0] < agent.fitness.values[0]) and (individual_donor.fitness.values[1] < agent.fitness.values[1]):
                    population_temporary.append(agent)
                    number_without_improvement_de += 1
                else:
                    population_temporary.append(individual_donor)
                    population_temporary.append(agent)
                    number_without_improvement_de = 0
            del population
            population = toolbox.select_de(population_temporary)
            gc.collect()
        population_feasible = list()
        for individual in range(len(population)):
            if population[individual][1].is_feasible:
                population_feasible.append(population[individual])
        if len(population_feasible) > 0:
            self.pareto_front_de = tools.sortLogNondominated(population_feasible, k=self.pareto_size, first_front_only=True)
        else:
            self.pareto_front_de = list()
