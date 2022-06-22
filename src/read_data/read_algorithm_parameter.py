import os
import sys

import numpy as np
import pandas as pd


class AlgorithmParameter:
    """Reads parameters for optimization algorithms"""

    def __init__(self, name_algorithm_parameter='AlgorithmParameter.xlsx'):
        self.name = name_algorithm_parameter
        self.genetic_algorithm_population_size = None
        self.genetic_algorithm_tournament_size = None
        self.genetic_algorithm_number_generations = None
        self.genetic_algorithm_hall_of_fame_size = None
        self.genetic_algorithm_probability_bit_flip = None
        self.genetic_algorithm_probability_crossover = None
        self.genetic_algorithm_probability_mutation = None
        self.differential_evolution_population_size = None
        self.differential_evolution_pareto_size = None
        self.differential_evolution_hall_of_fame_size = None
        self.differential_evolution_number_generations = None
        self.differential_evolution_perturbation_factor = None
        self.differential_evolution_probability_crossover = None
        self.differential_evolution_number_no_improvement = None
        self.read_parameter()

    def read_parameter(self):
        # Read data
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        os.chdir('data')
        algorithm_parameter = pd.read_excel(self.name, sheet_name='Parameter')
        self.number_workers = algorithm_parameter['NumProcessors'].iloc[0]
        # Genetic algorithm parameter
        self.genetic_algorithm_population_size = algorithm_parameter['PopSizeGA'].iloc[0]
        self.genetic_algorithm_tournament_size = algorithm_parameter['TournSizeGA'].iloc[0]
        self.genetic_algorithm_hall_of_fame_size = algorithm_parameter['HoFSizeGA'].iloc[0]
        self.genetic_algorithm_number_generations = algorithm_parameter['NumGenGA'].iloc[0]
        self.genetic_algorithm_probability_crossover = algorithm_parameter['CrossProbGA'].iloc[0]
        self.genetic_algorithm_probability_mutation = algorithm_parameter['MutProbGA'].iloc[0]
        # Differential evolution parameter
        self.differential_evolution_population_size = algorithm_parameter['PopSizeDE'].iloc[0]
        self.differential_evolution_pareto_size = algorithm_parameter['ParetoSize'].iloc[0]
        self.differential_evolution_number_generations = algorithm_parameter['NumGenDE'].iloc[0]
        self.differential_evolution_perturbation_factor = algorithm_parameter['PerturbationDE'].iloc[0]
        self.differential_evolution_probability_crossover = algorithm_parameter['CrossProbDE'].iloc[0]
        self.differential_evolution_number_no_improvement = algorithm_parameter['NumNoImprovDE'].iloc[0]
        os.chdir('..')
