

class Restrictions:
    """Restrictions for topology modifications of the heat exchanger network"""

    def __init__(self, case_study):
        self.max_splits = case_study.manual_parameter['MaxSplitsPerk'].iloc[0]  # (-)
        self.temperature_difference_lower_bound = case_study.manual_parameter['dTLb'].iloc[0]  # (°C)
        self.minimal_heat_load = case_study.manual_parameter['MinimalHeatLoad'].iloc[0]  # (kW)
        self.absolute_heat_load_tolerance = case_study.manual_parameter['AbsHeatLoadTol'].iloc[0]  # (kW)
