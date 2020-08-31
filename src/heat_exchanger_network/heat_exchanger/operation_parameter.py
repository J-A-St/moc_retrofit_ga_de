import numpy as np


class OperationParameter:
    """Heat exchanger operation parameter"""

    def __init__(self, case_study, number):
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.initial_area = case_study.initial_exchanger_address_matrix['A_ex'][number]
        self.heat_loads = np.zeros([case_study.number_operating_cases])
        self.split_fractions_hot_stream = np.zeros([case_study.number_operating_cases])
        self.split_fractions_cold_stream = np.zeros([case_study.number_operating_cases])
        self.mixer_fractions_hot_stream = np.zeros([case_study.number_operating_cases])
        self.mixer_fractions_cold_stream = np.zeros([case_study.number_operating_cases])
        self.inlet_temperatures_hot_stream = np.zeros([case_study.number_operating_cases])
        self.outlet_temperatures_hot_stream = np.zeros([case_study.number_operating_cases])
        self.inlet_temperatures_cold_stream = np.zeros([case_study.number_operating_cases])
        self.outlet_temperatures_cold_stream = np.zeros([case_study.number_operating_cases])
        self.logarithmic_temperature_differences = np.zeros([case_study.number_operating_cases])
        self.needed_areas = np.zeros([case_study.number_operating_cases])
        self.area = 0

    @property
    def matrix(self):
        return np.array([self.heat_loads, self.split_fractions_hot_stream, self.split_fractions_cold_stream, self.mixer_fractions_hot_stream, self.mixer_fractions_cold_stream])

    def update_operating_parameter(self, heat_loads, split_fractions_hot_streams, split_fractions_cold_stream, mixer_fractions_hot_stream, mixer_fractions_cold_stream):
        """Update of operation parameter matrix"""
        self.heat_loads = heat_loads
        self.split_fractions_hot_stream = split_fractions_hot_streams
        self.split_fractions_cold_stream = split_fractions_cold_stream
        self.mixer_fractions_hot_stream = mixer_fractions_hot_stream
        self.mixer_fractions_cold_stream = mixer_fractions_cold_stream

    def update_logarithmic_temperature_differences(self):
        """Update logarithmic temperature differences in the heat exchanger. ATTENTION: Negative (both temperature differences are negative) or NaN (if only one temperature difference is negative) are possible. This is important for the penalty function"""
        # TODO: How do we consider NaN or negative LMTDs for penalty functions or rejection?
        lograrithmic_temperature_differences = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            temperature_difference_a = self.inlet_temperatures_hot_stream[operating_case] - self.outlet_temperatures_cold_stream[operating_case]
            temperature_difference_b = self.outlet_temperatures_hot_stream[operating_case] - self.inlet_temperatures_cold_stream[operating_case]
            if temperature_difference_a == temperature_difference_b:
                lograrithmic_temperature_differences[operating_case] = temperature_difference_a
            else:
                lograrithmic_temperature_differences[operating_case] = (temperature_difference_a - temperature_difference_b) / np.log(temperature_difference_a / temperature_difference_b)
        self.logarithmic_temperature_differences = lograrithmic_temperature_differences

    def update_needed_areas(self, topology, hot_streams, cold_streams):
        """Update area of the heat exchanger. ATTENTION: Negative (negative temperature difference) or NaN (NaN temperature difference) are possible. This is important for the penalty function"""
        for operating_case in self.range_operating_cases:
            overall_heat_transfer_coefficient = 1 / (1 / hot_streams[topology.hot_stream].film_heat_transfer_coefficients[operating_case] +
                                                     1 / cold_streams[topology.cold_stream].film_heat_transfer_coefficients[operating_case])
            self.needed_areas[operating_case] = self.heat_loads[operating_case] / (overall_heat_transfer_coefficient * self.logarithmic_temperature_differences[operating_case])

    def __repr__(self):
        pass

    def __str__(self):
        pass
