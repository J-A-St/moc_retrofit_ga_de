import os
import numpy as np

from read_data.read_case_study_data import CaseStudy
from read_data.read_algorithm_parameter import AlgorithmParameter
from algorithm.genetic_algorithm import GeneticAlgorithm
from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    case_study = CaseStudy('Zweifel.xlsx')
    algorithm_parameter = AlgorithmParameter('AlgorithmParameter.xlsx')
    genetic_algorithm = GeneticAlgorithm(case_study, algorithm_parameter)
    best_solution = genetic_algorithm.genetic_algorithm()
    return best_solution, case_study

if __name__ == "__main__":
    best_solution, case_study = main()
    heat_exchanger_network = HeatExchangerNetwork(case_study)
    heat_exchanger_network.exchanger_addresses.matrix = np.array(best_solution[0])
    heat_exchanger_network.thermodynamic_parameter.heat_loads = np.array(best_solution[0].individual_de[0])
    for exchanger in heat_exchanger_network.range_heat_exchangers:
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

