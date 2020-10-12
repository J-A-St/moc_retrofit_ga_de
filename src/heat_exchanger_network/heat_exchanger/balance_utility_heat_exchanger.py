import numpy as np


class BalanceUtilityHeatExchanger:
    """Utility heat exchanger object"""

    def __init__(self, case_study, thermodynamic_parameter, number):
        self.number = number
        # Topology instance variables
        self.thermodynamic_parameter = thermodynamic_parameter
        self.thermodynamic_parameter.bind_to(self.update_all_heat_loads)
        self.all_heat_loads = self.thermodynamic_parameter.heat_loads
        self.utility_type = case_study.initial_exchanger_balance_utilities['H/C'][number]
        self.connected_stream = int(case_study.initial_exchanger_balance_utilities['stream'][number] - 1)

        # Streams
        self.hot_streams = case_study.hot_streams
        self.hot_utilities_indices = case_study.hot_utilities_indices
        self.cold_streams = case_study.cold_streams
        self.cold_utilities_indices = case_study.cold_utilities_indices

        # Operating cases
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.number_enthalpy_stages = case_study.number_enthalpy_stages

        # Operation parameter instance variables
        self.initial_heat_loads = np.array(case_study.initial_utility_balance_heat_loads)[number, 1:3]
        self.initial_area = case_study.initial_exchanger_balance_utilities['A_ex'][number]

        # Cost instance variables
        self.base_cost = case_study.initial_exchanger_balance_utilities['c_0'][number]
        self.specific_area_cost = case_study.initial_exchanger_balance_utilities['c_A'][number]
        self.degression_area = case_study.initial_exchanger_balance_utilities['d_f'][number]
        self.remove_costs = case_study.initial_exchanger_balance_utilities['c_R'][number]

    def update_all_heat_loads(self, parameter):
        self.all_heat_loads = parameter

    @property
    def film_heat_transfer_coefficient_utility(self):
        if self.utility_type == 'H':
            film_heat_transfer_coefficient_utility = self.hot_streams[self.hot_utilities_indices[0]].film_heat_transfer_coefficients
        elif self.utility_type == 'C':
            film_heat_transfer_coefficient_utility = self.cold_streams[self.cold_utilities_indices[0]].film_heat_transfer_coefficients
        return film_heat_transfer_coefficient_utility

    @property
    def film_heat_transfer_coefficient_stream(self):
        if self.utility_type == 'H':
            film_heat_transfer_coefficient_stream = self.cold_streams[self.connected_stream].film_heat_transfer_coefficients
        elif self.utility_type == 'C':
            film_heat_transfer_coefficient_stream = self.hot_streams[self.connected_stream].film_heat_transfer_coefficients
        return film_heat_transfer_coefficient_stream

    @property
    def overall_heat_transfer_coefficient(self):
        return 1 / (1 / self.film_heat_transfer_coefficient_utility + 1 / self.film_heat_transfer_coefficient_stream)

    @property
    def heat_capacity_flows(self):
        if self.utility_type == 'H':
            heat_capacity_flows = self.cold_streams[self.connected_stream].heat_capacity_flows
        elif self.utility_type == 'C':
            heat_capacity_flows = self.hot_streams[self.connected_stream].heat_capacity_flows
        return heat_capacity_flows

    @property
    def inlet_temperatures_utility(self):
        if self.utility_type == 'H':
            inlet_temperatures_utility = self.hot_streams[self.hot_utilities_indices[0]].supply_temperatures
        elif self.utility_type == 'C':
            inlet_temperatures_utility = self.cold_streams[self.cold_utilities_indices[0]].supply_temperatures
        return inlet_temperatures_utility

    @property
    def outlet_temperatures_utility(self):
        if self.utility_type == 'H':
            outlet_temperatures_utility = self.hot_streams[self.hot_utilities_indices[0]].target_temperatures
        elif self.utility_type == 'C':
            outlet_temperatures_utility = self.cold_streams[self.cold_utilities_indices[0]].target_temperatures
        return outlet_temperatures_utility

    @property
    def inlet_temperatures_stream(self):
        if self.utility_type == 'H':
            inlet_temperatures_stream = self.thermodynamic_parameter.enthalpy_stage_temperatures_cold_streams[self.connected_stream, self.number_enthalpy_stages, :]
        elif self.utility_type == 'C':
            inlet_temperatures_stream = self.thermodynamic_parameter.enthalpy_stage_temperatures_hot_streams[self.connected_stream, 0, :]
        return inlet_temperatures_stream

    @property
    def outlet_temperatures_stream(self):
        if self.utility_type == 'H':
            outlet_temperatures_stream = self.cold_streams[self.connected_stream].target_temperatures
        elif self.utility_type == 'C':
            outlet_temperatures_stream = self.hot_streams[self.connected_stream].target_temperatures
        return outlet_temperatures_stream

    @property
    def address_vector(self):
        return [self.utility_type, self.connected_stream, self.initial_area, self.base_cost, self.specific_area_cost, self.degression_area]

    @property
    def heat_loads(self):
        heat_loads = np.zeros([self.number_operating_cases])
        if self.utility_type == 'H':
            for operating_case in self.range_operating_cases:
                heat_loads[operating_case] = self.heat_capacity_flows[operating_case] * (self.outlet_temperatures_stream[operating_case] - self.inlet_temperatures_stream[operating_case])
        elif self.utility_type == 'C':
            for operating_case in self.range_operating_cases:
                heat_loads[operating_case] = self.heat_capacity_flows[operating_case] * (self.inlet_temperatures_stream[operating_case] - self.outlet_temperatures_stream[operating_case])
        return heat_loads

    @property
    def logarithmic_mean_temperature_differences(self):
        lograrithmic_temperature_differences = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            temperature_difference_a = abs(self.inlet_temperatures_utility[operating_case] - self.outlet_temperatures_stream[operating_case])
            temperature_difference_b = abs(self.outlet_temperatures_utility[operating_case] - self.inlet_temperatures_stream[operating_case])
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
