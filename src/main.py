import os
import sys
import code
import pickle

if sys.platform == "linux":
    import resource
    resource.setrlimit(resource.RLIMIT_DATA, (2147483648,2147483648))

from read_data.read_case_study_data import CaseStudy
from read_data.read_algorithm_parameter import AlgorithmParameter
from algorithm.genetic_algorithm import GeneticAlgorithm
from heat_exchanger_network.heat_exchanger_network import HeatExchangerNetwork

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    case_study = CaseStudy('Zweifel.xlsx')
    algorithm_parameter = AlgorithmParameter('AlgorithmParameter_short_comp.xlsx')
    genetic_algorithm = GeneticAlgorithm(case_study, algorithm_parameter)
    hall_of_fame = genetic_algorithm.genetic_algorithm()
    file = open("HallOfFame.pkl", "wb")
    pickle.dump([[[hall_of_fame[z][y][x] for x in range(len(hall_of_fame[z][y]))] for y in range(len(hall_of_fame[z]))] for z in range(len(hall_of_fame.items))], file)
    file.close()
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

def load_results():
    file = open("HallOfFame_1.pkl", "rb")
    hall_of_fame = pickle.load(file)
    file.close()
    print(210*"-")
    print("\nResults are loaded. Do you want to access the results? Input yes/no?\n")
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

def print_pareto_front():
    file = open("HallOfFame_1.pkl", "rb")
    hall_of_fame = pickle.load(file)
    file.close()
    print(210*"-")
    print("\nResults are loaded. Which Pareto Front in the Hall of Fame (1 to 10) do you want to print?\n")
    print(210*"-")
    try: 
        answer = input()
        answer = int(answer) 
    except:
        print("\nNon-valid input. Your input is not an integer!\n") 
    while answer not in range(1,11):
        print("\nNon-valid input. Your input is not an integer or not within the range of Hall of Fame solutions (1 to 10)\n")
        try: 
            answer = input()
            answer = int(answer) 
        except:
            print("\nNon-valid input. Your input is not an integer!\n")             
    answer -= 1
    x = list()
    y = list()
    for i in range(len(hall_of_fame[answer])):
        y.append(hall_of_fame[answer][i][1].total_annual_cost)
    for i in range(len(hall_of_fame[answer])):
        x.append(hall_of_fame[answer][i][1].operating_emissions)

    for i in range(len(x)):
        print(round(x[i]/1000,2),round(y[i]/1000,2),"\\\\")
        
if __name__ == "__main__":
    main()
    # load_results()
    # print_pareto_front()

            
