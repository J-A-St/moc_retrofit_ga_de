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
from algorithm.differential_evolution import DifferentialEvolution

def setup_model():
    """Setup testing model"""
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # os.chdir('..')
    test_case = CaseStudy('Zweifel_relaxed.xlsx')
    algorithm_parameter = AlgorithmParameter('AlgorithmParameter.xlsx')
    differential_evolution = DifferentialEvolution(test_case, algorithm_parameter)
    # os.chdir('unit_tests')
    creator.create('FitnessMin_de', base.Fitness, weights=(1.0,))
    creator.create('Individual_de', list, fitness=creator.FitnessMin_de)
    
    return test_case, differential_evolution

def test_initialize_individual():
    test_case, differential_evolution = setup_model()
    test_exchanger_address_matrix = np.array(test_case.initial_exchanger_address_matrix)[:, 1:9].astype(int)
    test_exchanger_address_matrix[:, 0:3] -= 1
    individual = differential_evolution.initialize_individual(creator.Individual_de, test_exchanger_address_matrix)

def test_fitness_function():
    test_case, differential_evolution = setup_model()
    test_exchanger_address_matrix = np.array(test_case.initial_exchanger_address_matrix)[:, 1:9].astype(int)
    test_exchanger_address_matrix[:, 0:3] -= 1
    individual = differential_evolution.initialize_individual(creator.Individual_de, test_exchanger_address_matrix)
    differential_evolution.fitness_function(test_exchanger_address_matrix, individual)

def test_differential_evolution():
    test_case, differential_evolution = setup_model()
    test_exchanger_address_matrix = np.array(test_case.initial_exchanger_address_matrix)[:, 1:9].astype(int)
    test_exchanger_address_matrix[:, 0:3] -= 1
    differential_evolution.differential_evolution(test_exchanger_address_matrix)