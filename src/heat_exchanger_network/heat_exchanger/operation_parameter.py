from scipy.special import lambertw
import numpy as np
rng = np.random.default_rng()
from functools import cached_property


class OperationParameter:
    """Heat exchanger operation parameter"""

    def __init__(self, thermodynamic_parameter, topology, case_study, number):
        self.number = number
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.hot_stream = topology.hot_stream
        self.cold_stream = topology.cold_stream
        self.film_heat_transfer_coefficients_hot_stream = case_study.hot_streams[self.hot_stream].film_heat_transfer_coefficients
        self.film_heat_transfer_coefficients_cold_stream = case_study.cold_streams[self.cold_stream].film_heat_transfer_coefficients
        self.heat_capacity_flows_hot_stream = case_study.hot_streams[self.hot_stream].heat_capacity_flows
        self.heat_capacity_flows_cold_stream = case_study.cold_streams[self.cold_stream].heat_capacity_flows
        self.hot_utilities_indices = case_study.hot_utilities_indices
        self.cold_utilities_indices = case_study.cold_utilities_indices
        self.initial_area = case_study.initial_exchanger_address_matrix['A_ex'][number]
        self.thermodynamic_parameter = thermodynamic_parameter
        self.thermodynamic_parameter.bind_to(self.update_all_heat_loads)
        self.all_heat_loads = self.thermodynamic_parameter.heat_loads

    def update_all_heat_loads(self, all_heat_loads):
        self.all_heat_loads = all_heat_loads

    @property
    def heat_loads(self):
        return self.all_heat_loads[self.number, :]

    @property
    def temperatures_hot_stream_before_hex(self):
        return self.thermodynamic_parameter.temperatures_hot_stream_before_hex[self.number, :]

    @property
    def temperatures_hot_stream_after_hex(self):
        return self.thermodynamic_parameter.temperatures_hot_stream_after_hex[self.number, :]

    @property
    def temperatures_cold_stream_before_hex(self):
        return self.thermodynamic_parameter.temperatures_cold_stream_before_hex[self.number, :]

    @property
    def temperatures_cold_stream_after_hex(self):
        return self.thermodynamic_parameter.temperatures_cold_stream_after_hex[self.number, :]

    @property
    def logarithmic_mean_temperature_differences_no_mixer(self):
        """Update logarithmic temperature differences in the heat exchanger."""
        logarithmic_mean_temperature_differences = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            temperature_difference_a = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
            temperature_difference_b = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_cold_stream_after_hex[operating_case]
            if temperature_difference_a == temperature_difference_b:
                logarithmic_mean_temperature_differences[operating_case] = temperature_difference_a
            elif temperature_difference_a <= 0 or temperature_difference_b <= 0:
                logarithmic_mean_temperature_differences[operating_case] = np.nan
            else:
                logarithmic_mean_temperature_differences[operating_case] = (temperature_difference_a - temperature_difference_b) / np.log(temperature_difference_a / temperature_difference_b)
        return logarithmic_mean_temperature_differences

    @property
    def overall_heat_transfer_coefficients(self):
        return 1 / (1 / self.film_heat_transfer_coefficients_hot_stream + 1 / self.film_heat_transfer_coefficients_cold_stream)

    @property
    def needed_areas(self):
        """Update area of the heat exchanger."""
        needed_areas = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if np.isnan(self.logarithmic_mean_temperature_differences_no_mixer[operating_case]) or self.logarithmic_mean_temperature_differences_no_mixer[operating_case] <= 0:
                needed_areas[operating_case] = np.nan
            else:
                needed_areas[operating_case] = self.heat_loads[operating_case] / (self.overall_heat_transfer_coefficients[operating_case] * self.logarithmic_mean_temperature_differences_no_mixer[operating_case])
        return needed_areas

    @property
    def area(self):
        """Maximal possible area for feasible heat transfer"""
        if any(np.isnan(self.needed_areas)):
            return np.nan
        return np.max(self.needed_areas)

    @property
    def logarithmic_mean_temperature_differences(self):
        """Logarithmic mean temperature difference due to area"""
        logarithmic_mean_temperature_differences = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if np.isnan(self.area) or self.area == 0.0:
                logarithmic_mean_temperature_differences[operating_case] = np.nan
            else:
                logarithmic_mean_temperature_differences[operating_case] = self.heat_loads[operating_case] / (self.overall_heat_transfer_coefficients[operating_case] * self.area)
        return logarithmic_mean_temperature_differences

    @cached_property
    def mixer_types(self):
        mixer_types = []
        for operating_case in self.range_operating_cases:
            if self.hot_stream in self.hot_utilities_indices or self.cold_stream in self.cold_utilities_indices:
                mixer_types.append('none')
            elif self.needed_areas[operating_case] != self.area:
                if self.heat_capacity_flows_hot_stream[operating_case] > self.heat_capacity_flows_cold_stream[operating_case]:
                    temperature_difference_1 = self.temperatures_cold_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
                    temperature_difference_2 = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
                    if temperature_difference_1 > temperature_difference_2:
                        mixer_types.append('admixer_cold')
                    else:
                        mixer_types.append('bypass_cold')
                elif self.heat_capacity_flows_hot_stream[operating_case] < self.heat_capacity_flows_cold_stream[operating_case]:
                    temperature_difference_1 = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
                    temperature_difference_2 = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_hot_stream_after_hex[operating_case]
                    if temperature_difference_1 > temperature_difference_2:
                        mixer_types.append('bypass_hot')
                    else:
                        mixer_types.append('admixer_hot')
                else:
                    mixer_types.append(self.random_choice(['bypass_hot', 'bypass_cold', 'admixer_hot', 'admixer_cold']))
            else:
                mixer_types.append('none')
        return mixer_types

    @cached_property
    def inlet_temperatures_hot_stream(self):
        inlet_temperatures_hot_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'admixer_hot' and self.heat_loads[operating_case] != 0:  
                temperature_difference_2 = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
                temperature_difference_2_ratio = temperature_difference_2 / self.logarithmic_mean_temperature_differences[operating_case]
                if np.isnan(self.logarithmic_mean_temperature_differences[operating_case]) or abs(temperature_difference_2_ratio) > 709:
                    inlet_temperatures_hot_stream[operating_case] = np.nan
                else:
                    if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1 = temperature_difference_2
                    elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                        # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                    inlet_temperatures_hot_stream[operating_case] = self.temperatures_cold_stream_after_hex[operating_case] + temperature_difference_1
            else:
                inlet_temperatures_hot_stream[operating_case] = self.temperatures_hot_stream_before_hex[operating_case]
        return inlet_temperatures_hot_stream

    @cached_property
    def outlet_temperatures_hot_stream(self):
        outlet_temperatures_hot_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'bypass_hot' and self.heat_loads[operating_case] != 0:  
                temperature_difference_2 = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_cold_stream_after_hex[operating_case]
                temperature_difference_2_ratio = temperature_difference_2 / self.logarithmic_mean_temperature_differences[operating_case]
                if np.isnan(self.logarithmic_mean_temperature_differences[operating_case]) or abs(temperature_difference_2_ratio) > 709:
                    outlet_temperatures_hot_stream[operating_case] = np.nan
                else:
                    if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1 = temperature_difference_2
                    elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:                       
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                        # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                    outlet_temperatures_hot_stream[operating_case] = self.temperatures_cold_stream_before_hex[operating_case] + temperature_difference_1
            else:
                outlet_temperatures_hot_stream[operating_case] = self.temperatures_hot_stream_after_hex[operating_case]
        return outlet_temperatures_hot_stream

    @cached_property
    def inlet_temperatures_cold_stream(self):
        inlet_temperatures_cold_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'admixer_cold' and self.heat_loads[operating_case] != 0:  
                temperature_difference_2 = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_cold_stream_after_hex[operating_case]
                temperature_difference_2_ratio = temperature_difference_2 / self.logarithmic_mean_temperature_differences[operating_case]
                if np.isnan(self.logarithmic_mean_temperature_differences[operating_case]) or abs(temperature_difference_2_ratio) > 709:
                    inlet_temperatures_cold_stream[operating_case] = np.nan
                else:
                    if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1 = temperature_difference_2
                    elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                        # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                    inlet_temperatures_cold_stream[operating_case] = self.temperatures_hot_stream_after_hex[operating_case] - temperature_difference_1
            else:
                inlet_temperatures_cold_stream[operating_case] = self.temperatures_cold_stream_before_hex[operating_case]
        return inlet_temperatures_cold_stream

    @cached_property
    def outlet_temperatures_cold_stream(self):
        outlet_temperatures_cold_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'bypass_cold' and self.heat_loads[operating_case] != 0:  
                temperature_difference_2 = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
                temperature_difference_2_ratio = temperature_difference_2 / self.logarithmic_mean_temperature_differences[operating_case]
                if np.isnan(self.logarithmic_mean_temperature_differences[operating_case]) or abs(temperature_difference_2_ratio) > 709:
                    outlet_temperatures_cold_stream[operating_case] = np.nan
                else:
                    if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1 = temperature_difference_2
                    elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                        temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                        temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                        # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                    outlet_temperatures_cold_stream[operating_case] = self.temperatures_hot_stream_before_hex[operating_case] - temperature_difference_1
            else:
                outlet_temperatures_cold_stream[operating_case] = self.temperatures_cold_stream_after_hex[operating_case]
        return outlet_temperatures_cold_stream

    @cached_property
    def mixer_fractions_hot_stream(self):
        mixer_fractions_hot_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.heat_loads[operating_case] == 0  or self.needed_areas[operating_case] == self.area: 
                mixer_fractions_hot_stream[operating_case] = 0
            elif self.mixer_types[operating_case] == 'admixer_hot':
                mixer_fractions_hot_stream[operating_case] = (self.temperatures_hot_stream_before_hex[operating_case] - self.inlet_temperatures_hot_stream[operating_case]) / (self.inlet_temperatures_hot_stream[operating_case] - self.outlet_temperatures_hot_stream[operating_case])
            elif self.mixer_types[operating_case] == 'bypass_hot':
                mixer_fractions_hot_stream[operating_case] = (self.temperatures_hot_stream_after_hex[operating_case] - self.outlet_temperatures_hot_stream[operating_case]) / (self.inlet_temperatures_hot_stream[operating_case] - self.outlet_temperatures_hot_stream[operating_case])
            else:
                mixer_fractions_hot_stream[operating_case] = 0
        return mixer_fractions_hot_stream

    @cached_property
    def mixer_fractions_cold_stream(self):
        mixer_fractions_cold_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.heat_loads[operating_case] == 0 or self.needed_areas[operating_case] == self.area:  
                mixer_fractions_cold_stream[operating_case] = 0
            elif self.mixer_types[operating_case] == 'admixer_cold':
                mixer_fractions_cold_stream[operating_case] = (self.temperatures_cold_stream_before_hex[operating_case] - self.inlet_temperatures_cold_stream[operating_case]) / (self.inlet_temperatures_cold_stream[operating_case] - self.outlet_temperatures_cold_stream[operating_case])
            elif self.mixer_types[operating_case] == 'bypass_cold':
                mixer_fractions_cold_stream[operating_case] = (self.temperatures_cold_stream_after_hex[operating_case] - self.outlet_temperatures_cold_stream[operating_case]) / (self.inlet_temperatures_cold_stream[operating_case] - self.outlet_temperatures_cold_stream[operating_case])
            else:
                mixer_fractions_cold_stream[operating_case] = 0
        return mixer_fractions_cold_stream

    def random_choice(self, array, seed=None): 
        return np.random.default_rng(seed=seed).choice(array)

    
    def clear_cache(self):
        try:
            del self.__dict__['mixer_types']
            del self.__dict__['inlet_temperatures_hot_stream']
            del self.__dict__['outlet_temperatures_hot_stream']
            del self.__dict__['inlet_temperatures_cold_stream']
            del self.__dict__['outlet_temperatures_cold_stream']
            del self.__dict__['mixer_fractions_hot_stream']
            del self.__dict__['mixer_fractions_cold_stream']
        except KeyError:
            pass

    def __repr__(self):
        pass

    def __str__(self):
        pass
