
from src.read_data.read_case_study_data import CaseStudy
from src.read_data.read_algorithm_parameter import AlgorithmParameter
from src.algorithm.genetic_algorithm import GeneticAlgorithm


def main():
    case_study = CaseStudy('Jones_P3_PinCH_2.xlsx')
    algorithm_parameter = AlgorithmParameter('AlgorithmParameter.xlsx')
    genetic_algorithm = GeneticAlgorithm(case_study, algorithm_parameter)
    genetic_algorithm.genetic_algorithm()


if __name__ == "__main__":
    main()
