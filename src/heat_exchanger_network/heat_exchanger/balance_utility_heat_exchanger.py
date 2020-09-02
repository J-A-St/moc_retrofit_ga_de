import numpy as np


class BalanceUtilityHeatExchanger:
    """Utility heat exchanger object"""

    def __init__(self, case_study, number):
        self.number = number
        # Topology instance variables
        self.utility_type = case_study.initial_exchanger_balance_utilities['H/C'][number]
        self.connected_stream = int(case_study.initial_exchanger_balance_utilities['stream'][number] - 1)
        # Operating cases
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        # Operation parameter instance variables
        self.initial_heat_loads = np.array(case_study.initial_utility_balance_heat_loads)[number, 1:3]
        self.initial_area = case_study.initial_exchanger_balance_utilities['A_ex'][number]
        if self.utility_type == 'H':
            self.film_heat_transfer_coefficient_utility = case_study.hot_streams[case_study.hot_utilities_indices[0]].film_heat_transfer_coefficients
            self.film_heat_transfer_coefficient_stream = case_study.cold_streams[self.connected_stream].film_heat_transfer_coefficients
            self.overall_heat_transfer_coefficient = 1 / (1 / self.film_heat_transfer_coefficient_utility + 1 / self.film_heat_transfer_coefficient_stream)
        elif self.utility_type == 'C':
            self.film_heat_transfer_coefficient_utility = case_study.hot_streams[case_study.hot_utilities_indices[0]].film_heat_transfer_coefficients
            self.film_heat_transfer_coefficient_stream = case_study.cold_streams[self.connected_stream].film_heat_transfer_coefficients
            self.overall_heat_transfer_coefficient = 1 / (1 / self.film_heat_transfer_coefficient_utility + 1 / self.film_heat_transfer_coefficient_stream)

        self.heat_loads = np.zeros([case_study.number_operating_cases])
        self.inlet_temperatures_hot_stream = np.zeros([case_study.number_operating_cases])
        self.outlet_temperatures_hot_stream = np.zeros([case_study.number_operating_cases])
        self.inlet_temperatures_cold_stream = np.zeros([case_study.number_operating_cases])
        self.outlet_temperatures_cold_stream = np.zeros([case_study.number_operating_cases])
        # Cost instance variables
        self.base_cost = case_study.initial_exchanger_balance_utilities['c_0'][number]
        self.specific_area_cost = case_study.initial_exchanger_balance_utilities['c_A'][number]
        self.degression_area = case_study.initial_exchanger_balance_utilities['d_f'][number]
        self.remove_costs = case_study.initial_exchanger_balance_utilities['c_R'][number]

    @property
    def address_vector(self):
        return [self.utility_type, self.connected_stream, self.initial_area, self.base_cost, self.specific_area_cost, self.degression_area]

    @property
    def logarithmic_mean_temperature_differences(self):
        lograrithmic_temperature_differences = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            temperature_difference_a = self.inlet_temperatures_hot_stream[operating_case] - self.outlet_temperatures_cold_stream[operating_case]
            temperature_difference_b = self.outlet_temperatures_hot_stream[operating_case] - self.inlet_temperatures_cold_stream[operating_case]
            if temperature_difference_a == temperature_difference_b:
                lograrithmic_temperature_differences[operating_case] = temperature_difference_a
            else:
                lograrithmic_temperature_differences[operating_case] = (temperature_difference_a - temperature_difference_b) / np.log(temperature_difference_a / temperature_difference_b)
        return lograrithmic_temperature_differences

    @property
    def needed_areas(self):
        needed_areas = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            needed_areas[operating_case] = self.heat_loads[operating_case] / (self.overall_heat_transfer_coefficient[operating_case] * self.logarithmic_mean_temperature_differences[operating_case])
        return needed_areas

    @property
    def area(self):
        return max(self.needed_areas)

    @property
    def exchanger_costs(self):
        exchanger_costs = 0
        if self.area > self.initial_area:
            exchanger_costs += self.base_cost + self.specific_area_cost * (self.area - self.initial_area) ** self.degression_area
        elif self.area <= 0:
            exchanger_costs += self.remove_costs
        return exchanger_costs

    def __repr__(self):
        pass

    def __str(self):
        pass
