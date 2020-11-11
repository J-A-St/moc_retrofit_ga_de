import os
import sys
import platform
import numpy as np
import cProfile
import pstats
import io
from deap import tools
from deap import creator
from deap import base

operating_system = platform.system()
if operating_system == 'Windows':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'\\src')
elif operating_system == 'Linux':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/src')

from read_data.read_case_study_data import CaseStudy
from read_data.read_algorithm_parameter import AlgorithmParameter
from heat_exchanger_network.heat_exchanger.heat_exchanger import HeatExchanger
from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork
from algorithm.differential_evolution import DifferentialEvolution


def profile(fnc):
    """A decorator that uses cProfile to profile a function"""

    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        # sortby = 'calls'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


@profile
def run_heat_exchanger():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    heat_exchanger_network = HeatExchangerNetwork(test_case)
    heat_exchanger_network.exchanger_addresses.matrix = np.array(
        [
            [0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    heat_exchanger_network.thermodynamic_parameter.heat_loads = np.array(
        [
            [3500, 0],
            [0, 3800],
            [0, 100],
            [5800, 0],
            [1500, 3500],
            [0, 0],
            [0, 0]
        ]
    )
    # heat_exchanger_network.heat_exchangers[0].operation_parameter.logarithmic_mean_temperature_differences_no_mixer
    heat_exchanger_network.heat_exchangers[0].is_feasible
    # print(heat_exchanger_network.heat_exchangers[0].operation_parameter.temperatures_hot_stream_before_hex)
    # print(heat_exchanger_network.heat_exchangers[0].operation_parameter.temperatures_hot_stream_after_hex)
    # print(heat_exchanger_network.heat_exchangers[0].operation_parameter.temperatures_cold_stream_before_hex)
    # print(heat_exchanger_network.heat_exchangers[0].operation_parameter.temperatures_cold_stream_after_hex)


@profile
def initialize_differential_evolution():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    test_parameter = AlgorithmParameter('AlgorithmParameter_profiling.xlsx')
    creator.create('FitnessMin_de', base.Fitness, weights=(1.0,))
    creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
    differential_evolution = DifferentialEvolution(test_case, test_parameter)
    exchanger_addresses = np.array(
        [
            [0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    toolbox = base.Toolbox()
    toolbox.register('individual_de', differential_evolution.initialize_individual, creator.Individual_de, exchanger_addresses)
    toolbox.register('population_de', tools.initRepeat, list, toolbox.individual_de)
    toolbox.register('select_parents_de', tools.selRandom, k=3)
    toolbox.register('evaluate_de', differential_evolution.fitness_function, exchanger_addresses)

@profile
def evaluate_single_solution():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    test_parameter = AlgorithmParameter('AlgorithmParameter_profiling.xlsx')
    creator.create('FitnessMin_de', base.Fitness, weights=(1.0,))
    creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
    differential_evolution = DifferentialEvolution(test_case, test_parameter)
    exchanger_addresses = np.array(
        [
            [0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    toolbox = base.Toolbox()
    toolbox.register('individual_de', differential_evolution.initialize_individual, creator.Individual_de, exchanger_addresses)
    toolbox.register('population_de', tools.initRepeat, list, toolbox.individual_de)
    # toolbox.register('select_parents_de', tools.selRandom, k=3)
    toolbox.register('evaluate_de', differential_evolution.fitness_function, exchanger_addresses)
    population = toolbox.population_de(n=1)
    toolbox.evaluate_de(population[0])



@profile
def evaluate_initial_population():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    test_parameter = AlgorithmParameter('AlgorithmParameter_profiling.xlsx')
    creator.create('FitnessMin_de', base.Fitness, weights=(1.0,))
    creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
    differential_evolution = DifferentialEvolution(test_case, test_parameter)
    exchanger_addresses = np.array(
        [
            [0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    toolbox = base.Toolbox()
    toolbox.register('individual_de', differential_evolution.initialize_individual, creator.Individual_de, exchanger_addresses)
    toolbox.register('population_de', tools.initRepeat, list, toolbox.individual_de)
    toolbox.register('select_parents_de', tools.selRandom, k=3)
    toolbox.register('evaluate_de', differential_evolution.fitness_function, exchanger_addresses)
    population = toolbox.population_de(n=differential_evolution.population_size)
    # Evaluate entire population
    fitness = list(toolbox.map(toolbox.evaluate_de, population))
    for individual, fit in zip(population, fitness):
        individual.fitness.values = fit


@profile
def run_differential_evolution():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    test_parameter = AlgorithmParameter('AlgorithmParameter.xlsx')
    creator.create('FitnessMin_de', base.Fitness, weights=(1.0,))
    creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
    differential_evolution = DifferentialEvolution(test_case, test_parameter)
    exchanger_addresses = np.array(
        [
            [0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 2, 1, 0, 0, 0, 1],
            [0, 1, 3, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 2, 1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    )
    differential_evolution.differential_evolution(exchanger_addresses)


if __name__ == "__main__":
    # evaluate_single_solution()
    # evaluate_initial_population()
    run_differential_evolution()
