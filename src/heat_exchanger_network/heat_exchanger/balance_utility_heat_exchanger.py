import numpy as np


class BalanceUtilityHeatExchanger:
    """Utility heat exchanger object"""
    # TODO: include investment cost

    def __init__(self, case_study, number):
        self.number = number
        # Topology instance variables
        self.utility_type = case_study.initial_exchanger_balance_utilities['H/C']
        self.connected_stream = int(case_study.initial_exchanger_balance_utilities['stream'][number] - 1)
        # Operation parameter instance variables
        self.initial_heat_loads = np.array(case_study.initial_utility_balance_heat_loads)[number, 1:3]
        self.initial_area = case_study.initial_exchanger_balance_utilities['A_ex'][number]
        # Cost instance variables
        self.base_cost = case_study.initial_exchanger_balance_utilities['c_0'][number]
        self.specific_area_cost = case_study.initial_exchanger_balance_utilities['c_A'][number]
        self.degression_area = case_study.initial_exchanger_balance_utilities['d_f'][number]

    @property
    def address_vector(self):
        return [self.utility_type, self.connected_stream, self.initial_area, self.base_cost, self.specific_area_cost, self.degression_area]

    def __repr__(self):
        pass

    def __str(self):
        pass
