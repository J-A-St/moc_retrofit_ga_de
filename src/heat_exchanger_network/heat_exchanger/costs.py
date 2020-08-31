
class Costs:
    """"Heat exchanger cost data"""

    def __init__(self, case_study, number):
        self.base_cost = case_study.initial_exchanger_address_matrix['c_0_HEX'][number]
        self.specific_area_cost = case_study.initial_exchanger_address_matrix['c_A_HEX'][number]
        self.degression_area = case_study.initial_exchanger_address_matrix['d_f_HEX'][number]
        self.remove_cost = case_study.initial_exchanger_address_matrix['c_R_HEX'][number]
        self.base_split_cost = case_study.initial_exchanger_address_matrix['c_0_split'][number]
        self.specific_split_cost = case_study.initial_exchanger_address_matrix['c_M_split'][number]
        self.degression_split = case_study.initial_exchanger_address_matrix['d_f_split'][number]
        self.remove_split_cost = case_study.initial_exchanger_address_matrix['c_R_split'][number]
        self.base_bypass_cost = case_study.initial_exchanger_address_matrix['c_0_bypass'][number]
        self.specific_bypass_cost = case_study.initial_exchanger_address_matrix['c_M_bypass'][number]
        self.degression_bypass = case_study.initial_exchanger_address_matrix['d_f_bypass'][number]
        self.remove_bypass_cost = case_study.initial_exchanger_address_matrix['c_R_bypass'][number]
        self.base_admixer_cost = case_study.initial_exchanger_address_matrix['c_0_admixer'][number]
        self.specific_admixer_cost = case_study.initial_exchanger_address_matrix['c_M_admixer'][number]
        self.degression_admixer = case_study.initial_exchanger_address_matrix['d_f_admixer'][number]
        self.remove_admixer_cost = case_study.initial_exchanger_address_matrix['c_R_admixer'][number]
        self.base_repipe_cost = case_study.initial_exchanger_address_matrix['c_0_repipe'][number]
        self.specific_repipe_cost = case_study.initial_exchanger_address_matrix['c_M_repipe'][number]
        self.degression_repipe = case_study.initial_exchanger_address_matrix['d_f_repipe'][number]
        self.base_resequence_cost = case_study.initial_exchanger_address_matrix['c_0_resequence'][number]
        self.specific_resequence_cost = case_study.initial_exchanger_address_matrix['c_M_resequence'][number]
        self.degression_resequence = case_study.initial_exchanger_address_matrix['d_f_resequence'][number]

    def __repr__(self):
        pass

    def __str__(self):
        pass
