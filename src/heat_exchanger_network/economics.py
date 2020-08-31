import numpy as np


class Economics:
    """Economic data and cost calculations for heat exchanger network"""
    # TODO: add cost functions

    def __init__(self, case_study):
        self.hot_utilities_cost = np.empty([len(case_study.hot_utilities_indices), case_study.number_operating_cases])  # e.g. (CHF/m2)
        self.cold_utilities_cost = np.empty([len(case_study.cold_utilities_indices), case_study.number_operating_cases])  # e.g. (CHF/m2)
        for operating_case in case_study.range_operating_cases:
            hot_utility = 0
            cold_utility = 0
            for stream in case_study.range_streams:
                if case_study.stream_data['H/C'][stream] == 'H' and not np.isnan(case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]):
                    self.hot_utilities_cost[hot_utility, operating_case] = case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]
                    hot_utility += 1
                elif case_study.stream_data['H/C'][stream] == 'C' and not np.isnan(case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]):
                    self.cold_utilities_cost[cold_utility, operating_case] = case_study.stream_data['UtilityCostperkWh'][stream + case_study.number_streams * operating_case]
                    cold_utility += 1

        self.match_cost = case_study.match_cost.values[:, 1:]  # (y)
        self.deprecation_lifetime = case_study.economic_data['DeprecationLifetime'].iloc[0]  # (-)
        self.interest_rate = case_study.economic_data['InterestRate'].iloc[0]
        self.annuity_factor = (self.interest_rate * (1 + self.interest_rate) ** self.deprecation_lifetime) / ((1 + self.interest_rate) ** self.deprecation_lifetime - 1)
        self.capital_cost_resequence = None
        self.captial_cost_heat_exchanger = None
        self.capital_cost_split = None
        self.captial_cost_mixer = None
        self.capical_cost_repipe = None
        self.capital_cost_resequence = None
        self.annual_operating_cost = None
        self.annualized_capital_cost = None
        self.total_annual_cost = None

    def __repr__(self):
        pass

    def __str__(self):
        pass
