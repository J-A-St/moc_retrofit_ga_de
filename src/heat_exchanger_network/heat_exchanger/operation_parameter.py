import numpy as np


class OperationParameter:
    """Heat exchanger operation parameter"""
    # TODO: temperature calculation due to mixer (Lambert-w) needs to be done in here too!

    def __init__(self, thermodynamic_parameter, topology, case_study, number):
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.film_heat_transfer_coefficients_hot_stream = case_study.hot_streams[topology.hot_stream].film_heat_transfer_coefficients
        self.film_heat_transfer_coefficients_cold_stream = case_study.cold_streams[topology.cold_stream].film_heat_transfer_coefficients
        self.initial_area = case_study.initial_exchanger_address_matrix['A_ex'][number]
        self.split_fractions_hot_stream = np.zeros([case_study.number_operating_cases])
        self.split_fractions_cold_stream = np.zeros([case_study.number_operating_cases])
        self.mixer_fractions_hot_stream = np.zeros([case_study.number_operating_cases])
        self.mixer_fractions_cold_stream = np.zeros([case_study.number_operating_cases])
        self.heat_loads = thermodynamic_parameter.matrix[0][:, number]
        self.temperatures_hot_stream_before_hex = thermodynamic_parameter.matrix[1][:, number]
        self.temperatures_hot_stream_after_hex = thermodynamic_parameter.matrix[2][:, number]
        self.temperatures_cold_stream_before_hex = thermodynamic_parameter.matrix[3][:, number]
        self.temperatures_cold_stream_after_hex = thermodynamic_parameter.matrix[4][:, number]
        self.inlet_temperatures_hot_stream = np.zeros([case_study.number_operating_cases])
        self.outlet_temperatures_hot_stream = np.zeros([case_study.number_operating_cases])
        self.inlet_temperatures_cold_stream = np.zeros([case_study.number_operating_cases])
        self.outlet_temperatures_cold_stream = np.zeros([case_study.number_operating_cases])

    @property
    def matrix(self):
        return np.array([self.heat_loads, self.split_fractions_hot_stream, self.split_fractions_cold_stream, self.mixer_fractions_hot_stream, self.mixer_fractions_cold_stream])

    @property
    def logarithmic_mean_temperature_differences_no_mixer(self):
        """Update logarithmic temperature differences in the heat exchanger."""
        lograrithmic_mean_temperature_differences = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            temperature_difference_a = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
            temperature_difference_b = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_cold_stream_after_hex[operating_case]
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
            if np.isnan(self.logarithmic_mean_temperature_differences_no_mixer[operating_case]) or self.logarithmic_mean_temperature_differences_no_mixer[operating_case] <= 0:
                needed_areas[operating_case] = 0
            else:
                needed_areas[operating_case] = self.heat_loads[operating_case] / (self.overall_heat_transfer_coefficients[operating_case] * self.logarithmic_mean_temperature_differences_no_mixer[operating_case])
        return needed_areas

    @property
    def area(self):
        """Maximal possible area for feasible heat transfer"""
        return np.max(self.needed_areas)
        # TODO: random decision for every OC if bypass, admixer or no mixer (only if needed_area_oc==max_area resp. area)
        # TODO: calculate outlet respectively inlet temperatures (Lambert W-function) and check with constraints if possible, if not possible check the other options, if non possible reject the solution!

    def __repr__(self):
        pass

    def __str__(self):
        pass
