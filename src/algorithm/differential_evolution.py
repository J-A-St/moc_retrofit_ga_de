from deap import tools
from deap import creator
from deap import base
import numpy as np
rng = np.random.default_rng()

from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork


class DifferentialEvolution():
    """Differential evolution (DE) algorithm for optimization of heat duties for from genetic algorithm predefined
    HEX matches"""

    def __init__(self, case_study, algorithm_parameter):
        self.case_study = case_study
        self.number_heat_exchangers = case_study.number_heat_exchangers
        self.range_heat_exchangers = case_study.range_heat_exchangers
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.number_hot_streams = case_study.number_hot_streams
        self.number_cold_streams = case_study.number_cold_streams
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams
        self.min_heat_load = case_study.manual_parameter['MinimalHeatLoad'].iloc[0]
        self.penalty_total_annual_cost_value = case_study.manual_parameter['GA_TAC_Penalty'].iloc[0]

        self.population_size = algorithm_parameter.differential_evolution_population_size
        self.hall_of_fame_size = algorithm_parameter.differential_evolution_hall_of_fame_size
        self.number_generations = algorithm_parameter.differential_evolution_number_generations
        self.number_no_improvement = algorithm_parameter.differential_evolution_number_no_improvement
        self.probability_crossover = algorithm_parameter.differential_evolution_probability_crossover
        self.scaling_factor = algorithm_parameter.differential_evolution_scaling_factor

        self.best_solution = None

    def initialize_individual(self, individual_class, exchanger_addresses):
        """Create an individual matrix of heat duties for all existing HEX matches"""
        # TODO: needs testing!
        heat_duties = np.zeros([self.number_heat_exchangers, self.number_operating_cases])
        for exchanger in self.range_heat_exchangers:
            if exchanger_addresses[exchanger, 7] == 1:
                for operating_case in self.range_operating_cases:
                    max_heat_duty = np.nanmin((self.hot_streams[exchanger_addresses[exchanger, 0]].enthalpy_flows[operating_case], self.cold_streams[exchanger_addresses[exchanger, 1]].enthalpy_flows[operating_case]))
                    if max_heat_duty != 0:
                        heat_duties[exchanger, operating_case] = (max_heat_duty - self.min_heat_load) * rng.random() + self.min_heat_load
                    else:
                        heat_duties[exchanger, operating_case] = max_heat_duty
        individual = individual_class(heat_duties.tolist())
        return individual

    def fitness_function(self, exchanger_addresses, individual):
        """Calculate the whole network including costs"""
        heat_exchanger_network = HeatExchangerNetwork(self.case_study)
        heat_exchanger_network.exchanger_addresses.matrix = exchanger_addresses
        heat_exchanger_network.thermodynamic_parameter.clear_temperature_cache()
        heat_exchanger_network.thermodynamic_parameter.heat_loads = np.array(individual)
        if heat_exchanger_network.is_feasible:
            fitness = 1 / heat_exchanger_network.total_annual_costs
        else:
            quadratic_distance = sum([heat_exchanger_network.heat_exchangers[exchanger].infeasibility_logarithmic_mean_temperature_differences[1] + heat_exchanger_network.heat_exchangers[exchanger].infeasibility_temperature_differences[1] + heat_exchanger_network.heat_exchangers[exchanger].infeasibility_mixer[1] for exchanger in self.range_heat_exchangers] + heat_exchanger_network.infeasibility_energy_balance[1])

            fitness = 1 / (self.penalty_total_annual_cost_value + quadratic_distance)
        return fitness,

    def differential_evolution(self, exchanger_addresses):
        """Main differential evolution algorithm"""
        exchanger_addresses = np.array(exchanger_addresses)
        toolbox = base.Toolbox()
        toolbox.register('individual_de', self.initialize_individual, creator.Individual_de, exchanger_addresses)  # TODO: exchanger addresses?
        toolbox.register('population_de', tools.initRepeat, list, toolbox.individual_de)
        toolbox.register('select_parents_de', tools.selRandom, k=3)
        toolbox.register('evaluate_de', self.fitness_function, exchanger_addresses)  # TODO: exchanger addresses?

        # Initialize population
        population = toolbox.population_de(n=self.population_size)
        hall_of_fame_de = tools.HallOfFame(maxsize=self.hall_of_fame_size, similar=np.array_equal)
        # Evaluate entire population
        fitness = list(toolbox.map(toolbox.evaluate_de, population))  # TODO: exchanger addresses?
        for individual, fit in zip(population, fitness):
            individual.fitness.values = fit

        number_generations_de = 0
        number_without_improvement_de = 0
        while number_generations_de <= self.number_generations and number_without_improvement_de <= self.number_no_improvement:
            # print('--DE: Generation %i --' % number_generations_de)
            number_generations_de += 1
            for pop, agent in enumerate(population):
                individual_r1, individual_r2, individual_r3 = np.array(toolbox.select_parents_de(population))
                individual_donor = toolbox.clone(agent)
                index = rng.choice(len(individual_r1))
                for exchanger in self.range_heat_exchangers:
                    for operating_case in self.range_operating_cases:
                        # recombination / Crossover
                        if pop == index or rng.random() < self.probability_crossover:
                            # Mutation
                            individual_donor[exchanger][operating_case] = np.absolute(individual_r1[exchanger][operating_case] + self.scaling_factor * (individual_r2[exchanger][operating_case] - individual_r3[exchanger][operating_case]))
                            max_heat_duty = np.nanmin((self.hot_streams[exchanger_addresses[exchanger, 0]].enthalpy_flows[operating_case], self.cold_streams[exchanger_addresses[exchanger, 1]].enthalpy_flows[operating_case]))
                            if max_heat_duty != 0 and (individual_donor[exchanger][operating_case] < self.min_heat_load or individual_donor[exchanger][operating_case] > max_heat_duty):
                                individual_donor[exchanger][operating_case] = (max_heat_duty - self.min_heat_load) * rng.random() + self.min_heat_load
                individual_donor.fitness.values = toolbox.evaluate_de(individual_donor)  # TODO: exchanger addresses?
                # Selection (objective 1/TAC)
                if individual_donor.fitness.values[0] > agent.fitness.values[0]:
                    population[pop] = individual_donor
            if number_generations_de > 1:
                best_old = hall_of_fame_de[0].fitness.values[0]
                hall_of_fame_de.update(population)
                best_new = hall_of_fame_de[0].fitness.values[0]
                if best_old >= best_new:
                    number_without_improvement_de += 1
                else:
                    number_without_improvement_de = 0
            else:
                hall_of_fame_de.update(population)
        self.best_solution = hall_of_fame_de[0]
        _ = toolbox.evaluate_de(hall_of_fame_de[0])
        # TODO: best DE solution has to be attached to the GA solution (heat loads and mixer fractions; mixer types have to be updated in the exchanger addresses!)
