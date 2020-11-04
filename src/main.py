import os

from read_data.read_case_study_data import CaseStudy
from read_data.read_algorithm_parameter import AlgorithmParameter
from algorithm.genetic_algorithm import GeneticAlgorithm


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')
    case_study = CaseStudy('Jones_P3_PinCH_2.xlsx')
    algorithm_parameter = AlgorithmParameter('AlgorithmParameter.xlsx')
    genetic_algorithm = GeneticAlgorithm(case_study, algorithm_parameter)
    genetic_algorithm.genetic_algorithm()


if __name__ == "__main__":
    main()
