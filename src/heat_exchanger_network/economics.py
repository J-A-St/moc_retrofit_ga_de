import numpy as np


class Economics:
    """Economic data and cost calculations for heat exchanger network"""

    def __init__(self, case_study):
        self.specific_hot_utilities_cost = np.empty([len(case_study.hot_utilities_indices), case_study.number_operating_cases])  # e.g. (CHF/kWh)
        self.specific_hot_utilities_emissions = np.empty([len(case_study.hot_utilities_indices), case_study.number_operating_cases])  # (tCO2/kWh)
        self.specific_cold_utilities_cost = np.empty([len(case_study.cold_utilities_indices), case_study.number_operating_cases])  # e.g. (CHF/kWh)
        self.specific_cold_utilities_emissions = np.empty([len(case_study.cold_utilities_indices), case_study.number_operating_cases])  # e.g. (tCO2/kWh)
        for operating_case in case_study.range_operating_cases:
            hot_utility = 0
            cold_utility = 0
            for stream in case_study.range_streams:
                if case_study.stream_data['H/C'][stream] == 'H' and not np.isnan(case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]):
                    self.specific_hot_utilities_cost[hot_utility, operating_case] = case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]
                    self.specific_hot_utilities_emissions[hot_utility, operating_case] = case_study.stream_data['tonsCO2emissionsperkWh'][stream + case_study.number_streams * operating_case]
                    hot_utility += 1
                elif case_study.stream_data['H/C'][stream] == 'C' and not np.isnan(case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]):
                    self.specific_cold_utilities_cost[cold_utility, operating_case] = case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]
                    self.specific_cold_utilities_emissions[cold_utility, operating_case] = case_study.stream_data['tonsCO2emissionsperkWh'][stream + case_study.number_streams * operating_case]
                    cold_utility += 1

        self.specific_hot_utilities_cost = np.squeeze(self.specific_hot_utilities_cost)
        self.specific_cold_utilities_cost = np.squeeze(self.specific_cold_utilities_cost)
        self.specific_hot_utilities_emissions = np.squeeze(self.specific_hot_utilities_emissions)
        self.specific_cold_utilities_emissions = np.squeeze(self.specific_cold_utilities_emissions)
        self.match_cost = case_study.match_cost.values[:, 2:]  # (y)
        self.deprecation_lifetime = case_study.economic_data['DeprecationLifetime'].iloc[0]  # (-)
        self.interest_rate = case_study.economic_data['InterestRate'].iloc[0]
        self.annuity_factor = (self.interest_rate * (1 + self.interest_rate) ** self.deprecation_lifetime) / ((1 + self.interest_rate) ** self.deprecation_lifetime - 1)
        self.initial_operating_costs = sum(case_study.initial_hot_utility_demand * self.specific_hot_utilities_cost) + sum(case_study.initial_cold_utility_demand * self.specific_cold_utilities_cost)
        self.initial_operating_emissions = sum(case_study.initial_hot_utility_demand * self.specific_hot_utilities_emissions) + sum(case_study.initial_cold_utility_demand * self.specific_cold_utilities_emissions)

    def __repr__(self):
        pass

    def __str__(self):
        pass
