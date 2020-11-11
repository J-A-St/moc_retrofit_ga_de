import os
import sys
import platform
import numpy as np
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
from algorithm.genetic_algorithm import GeneticAlgorithm

def setup_model():
    """Setup testing model"""
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # os.chdir('..')
    test_case = CaseStudy('Jones_P3_PinCH_2.xlsx')
    algorithm_parameter = AlgorithmParameter('AlgorithmParameter.xlsx')
    genetic_algorithm = GeneticAlgorithm(test_case, algorithm_parameter)
    # os.chdir('unit_tests')
    weights_de_individual = np.ones([test_case.number_heat_exchangers, test_case.number_operating_cases])
    creator.create('FitnessMin_ga', base.Fitness, weights=(1.0, 1.0, weights_de_individual))
    creator.create('Individual_ga', list, fitness=creator.FitnessMin_ga)
    creator.create('FitnessMin_de', base.Fitness, weights=(1.0,))
    creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
    toolbox = base.Toolbox()
    toolbox.register('individual_ga', genetic_algorithm.initialize_individual, creator.Individual_ga)
    toolbox.register('population_ga', tools.initRepeat, list, toolbox.individual_ga)
    population = toolbox.population_ga(algorithm_parameter.genetic_algorithm_population_size)
    return test_case, population, genetic_algorithm
    

# def test_initialize_individual():
#     test_case, _, genetic_algorithm = setup_model()
#     creator.create('FitnessMin_ga', base.Fitness, weights=(1.0, 1.0, weights_de_individual))
#     creator.create('Individual_ga', list, fitness=creator.FitnessMin_ga)
#     genetic_algorithm.initialize_individual(creator.Individual_ga)

# def test_mutation():
#     test_case, population, genetic_aglorithm = setup_model()
#     genetic_aglorithm.mutation(population[0])


