import numpy as np


class OperationParameter:
    """Heat exchanger operation parameter"""
    # TODO: properties need to come from operation parameter matrix!

    def __init__(self, case_study, topology, number):
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.film_heat_transfer_coefficients_hot_stream = case_study.hot_streams[topology.hot_stream].film_heat_transfer_coefficients
        self.film_heat_transfer_coefficients_cold_stream = case_study.cold_streams[topology.cold_stream].film_heat_transfer_coefficients
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
        self.area = 0

    @property
    def matrix(self):
        return np.array([self.heat_loads, self.split_fractions_hot_stream, self.split_fractions_cold_stream, self.mixer_fractions_hot_stream, self.mixer_fractions_cold_stream])

    @property
    def logarithmic_mean_temperature_differences(self):
        """Update logarithmic temperature differences in the heat exchanger."""
        lograrithmic_mean_temperature_differences = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            temperature_difference_a = self.inlet_temperatures_hot_stream[operating_case] - self.outlet_temperatures_cold_stream[operating_case]
            temperature_difference_b = self.outlet_temperatures_hot_stream[operating_case] - self.inlet_temperatures_cold_stream[operating_case]
            if temperature_difference_a == temperature_difference_b:
                lograrithmic_mean_temperature_differences[operating_case] = temperature_difference_a
            else:
                lograrithmic_mean_temperature_differences[operating_case] = (temperature_difference_a - temperature_difference_b) / np.log(temperature_difference_a / temperature_difference_b)
        return lograrithmic_mean_temperature_differences

    @property
    def overall_heat_transfer_coefficients(self):
        return 1 / (1 / self.film_heat_transfer_coefficients_hot_stream + 1 / self.film_heat_transfer_coefficients_cold_stream)

    @property
    def needed_areas(self):
        """Update area of the heat exchanger."""
        needed_areas = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if np.isnan(self.logarithmic_mean_temperature_differences[operating_case]) or self.logarithmic_mean_temperature_differences[operating_case] <= 0:
                needed_areas[operating_case] = 0
            else:
                needed_areas[operating_case] = self.heat_loads[operating_case] / (self.overall_heat_transfer_coefficients[operating_case] * self.logarithmic_mean_temperature_differences[operating_case])
        return needed_areas

    def __repr__(self):
        pass

    def __str__(self):
        pass
