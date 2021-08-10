import os
import sys
import code
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from read_data.read_case_study_data import CaseStudy
from read_data.read_algorithm_parameter import AlgorithmParameter
from algorithm.genetic_algorithm import GeneticAlgorithm
from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    case_study = CaseStudy('Zweifel.xlsx')
    algorithm_parameter = AlgorithmParameter('AlgorithmParameter_short_comp.xlsx')
    print(210*"-")
    print("\n Input ''weighted,, for a multi-objective optimization with the selected weight factor or ''pareto,, for a pareto optimization (ATTENTION: computation duration is increased by around 10 times).\n")
    print(210*"-")
    optimization = input()
    while optimization != 'weighted' and optimization != 'pareto':
        print(210*"-")
        print("\nNon-valid input. Input ''weighted,, for a multi-objective optimization with the selected weight factor or ''pareto,, for a pareto optimization (ATTENTION: computation time is increased by around 10 times).\n")
        print(210*"-")
        optimization = input()
    if optimization == 'weighted':
        genetic_algorithm = GeneticAlgorithm(case_study, algorithm_parameter, case_study.weight_factor)
        best_solution = genetic_algorithm.genetic_algorithm()
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
        print(210*"-")
        print("\nMulti-objective optimization is finished. Do you want to access the results? Input yes/no?\n")
        print(210*"-")
        answer = input()
        while answer != 'yes' and answer != 'no':
            print(210*"-")
            print("\nNon-valid input. Input ''yes,, to access the results or ''no,, to terminate\n")
            print(210*"-")
            answer = input()
        if answer == 'no':
            sys.exit(0)
        elif answer == 'yes':
            print(20*"-")
            print("\nPress exit() to exit\n")
            print(20*"-")
            code.interact(local=locals())
    elif optimization == 'pareto':
        pareto_solutions = list()
        pareto_networks = list()
        for weight_factor in np.arange(1, -0.1, -0.1):
            print(210*"-")
            print("\nPareto weight factor = %s.\n" % round(weight_factor,1))
            print(210*"-")
            genetic_algorithm = GeneticAlgorithm(case_study, algorithm_parameter, weight_factor)
            best_solution = genetic_algorithm.genetic_algorithm()
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
            pareto_solutions.append((weight_factor, heat_exchanger_network.total_annual_cost, heat_exchanger_network.operating_emissions))
            pareto_networks.append((weight_factor, heat_exchanger_network))
        total_annual_cost = np.zeros(len(pareto_solutions))
        operating_emissions = np.zeros(len(pareto_solutions))
        for solution, pareto_solution in enumerate(pareto_solutions):
            total_annual_cost[solution] = pareto_solution[1]
            operating_emissions[solution] = pareto_solution[2]
        fig, ax = plt.subplots()
        ax.plot(total_annual_cost, operating_emissions, '-o')
        for solution, weight in enumerate(np.arange(1, -0.1, -0.1)):
            ax.annotate("w=%s" %round(weight, 2), (total_annual_cost[solution], operating_emissions[solution]))
        ax.grid()
        ax.set(ylabel='Operating emissions 1/kgCO2', xlabel='Total annual cost y/CHF', title='Pareto front')
        plt.show()

        print(210*"-")
        print("\nPareto optimization is finished. Do you want to access the results? Input yes/no?\n")
        print(210*"-")
        answer = input()
        while answer != 'yes' and answer != 'no':
            print(210*"-")
            print("\nNon-valid input. Input ''yes,, to access the results or ''no,, to terminate\n")
            print(210*"-")
            answer = input()
        if answer == 'no':
            sys.exit(0)
        elif answer == 'yes':
            print(20*"-")
            print("\nPress exit() to exit\n")
            print(20*"-")
            code.interact(local=locals())
        

if __name__ == "__main__":
    main()
            
