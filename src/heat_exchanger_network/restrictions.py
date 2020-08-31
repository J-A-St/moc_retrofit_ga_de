

class Restrictions:
    """Restrictions for topology modifications of the heat exchanger network"""

    def __init__(self, case_study):
        self.max_splits = case_study.manual_parameter['MaxSplitsPerk'].iloc[0]  # (-)
        self.max_bypass_fraction = case_study.manual_parameter['MaxBypass'].iloc[0]  # (-)
        self.max_admix_fraction = case_study.manual_parameter['MaxAdmix'].iloc[0]  # (-)
        self.temperature_difference_upper_bound = case_study.manual_parameter['dTUb'].iloc[0]   # (°C)
        self.temperature_difference_lower_bound = case_study.manual_parameter['dTLb'].iloc[0]  # (kW)
        self.minimal_heat_load = case_study.manual_parameter['MinimalHeatLoad'].iloc[0]  # (-)

    def __repr__(self):
        pass

    def __str__(self):
        pass
