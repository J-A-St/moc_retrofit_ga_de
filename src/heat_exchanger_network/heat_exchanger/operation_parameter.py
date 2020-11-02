from scipy.special import lambertw
import numpy as np
rng = np.random.default_rng()


class OperationParameter:
    """Heat exchanger operation parameter"""

    def __init__(self, thermodynamic_parameter, topology, case_study, number):
        self.number = number
        self.number_operating_cases = case_study.number_operating_cases
        self.range_operating_cases = case_study.range_operating_cases
        self.film_heat_transfer_coefficients_hot_stream = case_study.hot_streams[topology.hot_stream].film_heat_transfer_coefficients
        self.film_heat_transfer_coefficients_cold_stream = case_study.cold_streams[topology.cold_stream].film_heat_transfer_coefficients
        self.initial_area = case_study.initial_exchanger_address_matrix['A_ex'][number]
        self.one_mixer_per_hex = case_study.manual_parameter['OneMixerBool'].iloc[0]

        self.thermodynamic_parameter = thermodynamic_parameter
        self.thermodynamic_parameter.bind_to(self.update_all_heat_loads)
        self.all_heat_loads = self.thermodynamic_parameter.heat_loads

        # self.operation_parameter = thermodynamic_parameter._matrix

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
            # temperature_difference_a = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
            # temperature_difference_b = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_cold_stream_after_hex[operating_case]

            temperature_difference_a = self.thermodynamic_parameter.temperatures_hot_stream_after_hex[self.number, operating_case] - self.thermodynamic_parameter.temperatures_cold_stream_before_hex[self.number, operating_case]
            temperature_difference_b = self.thermodynamic_parameter.temperatures_hot_stream_before_hex[self.number, operating_case] - self.thermodynamic_parameter.temperatures_cold_stream_after_hex[self.number, operating_case]

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
                needed_areas[operating_case] = 0.0
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
            if self.area == 0.0:  # TODO: Needs testing!
                logarithmic_mean_temperature_differences[operating_case] = np.nan
            else:
                logarithmic_mean_temperature_differences[operating_case] = self.heat_loads[operating_case] / (self.overall_heat_transfer_coefficients[operating_case] * self.area)
        return logarithmic_mean_temperature_differences

    @property
    def mixer_types(self):
        # TODO: should not occur for gaseous streams! (practicability) --> argument for SA algorithm!
        possible_mixer_types = ['bypass_hot', 'bypass_cold', 'admixer_hot', 'admixer_cold']
        mixer_types = []
        if self.one_mixer_per_hex:
            if any(self.needed_areas != self.area):
                # TODO: should here be a area difference tolerance?
                mixer_type = self.random_choice(possible_mixer_types)
            else:
                mixer_type = 'none'
            for operating_case in self.range_operating_cases:
                mixer_types.append(mixer_type)
        elif not self.one_mixer_per_hex:
            for operating_case in self.range_operating_cases:
                if self.needed_areas[operating_case] != self.area:
                    # TODO: should here be a area difference tolerance?
                    mixer_types.append(self.random_choice(possible_mixer_types))
                else:
                    mixer_types.append('none')
        return mixer_types

    @property
    def inlet_temperatures_hot_stream(self):
        # TODO: add case if logarithmic_mean_temperature == 0 (heat loads == 0)
        inlet_temperatures_hot_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'admixer_hot' and self.heat_loads[operating_case] != 0:  # TODO: Needs testing!
                temperature_difference_2 = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
                if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                    temperature_difference_1 = temperature_difference_2
                elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                inlet_temperatures_hot_stream[operating_case] = self.temperatures_cold_stream_after_hex[operating_case] + temperature_difference_1
            else:
                inlet_temperatures_hot_stream[operating_case] = self.temperatures_hot_stream_before_hex[operating_case]
        return inlet_temperatures_hot_stream

    @property
    def outlet_temperatures_hot_stream(self):
        # TODO: add case if logarithmic_mean_temperature == 0 (heat loads == 0)
        outlet_temperatures_hot_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'bypass_hot' and self.heat_loads[operating_case] != 0:  # TODO: Needs testing!
                temperature_difference_2 = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_cold_stream_after_hex[operating_case]
                if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                    temperature_difference_1 = temperature_difference_2
                elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                outlet_temperatures_hot_stream[operating_case] = self.temperatures_cold_stream_before_hex[operating_case] + temperature_difference_1
            else:
                outlet_temperatures_hot_stream[operating_case] = self.temperatures_hot_stream_after_hex[operating_case]
        return outlet_temperatures_hot_stream

    @property
    def inlet_temperatures_cold_stream(self):
        # TODO: add case if logarithmic_mean_temperature == 0 (heat loads == 0)
        inlet_temperatures_cold_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'admixer_cold' and self.heat_loads[operating_case] != 0:  # TODO: Needs testing!
                temperature_difference_2 = self.temperatures_hot_stream_before_hex[operating_case] - self.temperatures_cold_stream_after_hex[operating_case]
                if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                    temperature_difference_1 = temperature_difference_2
                elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                inlet_temperatures_cold_stream[operating_case] = self.temperatures_hot_stream_after_hex[operating_case] - temperature_difference_1
            else:
                inlet_temperatures_cold_stream[operating_case] = self.temperatures_cold_stream_before_hex[operating_case]
        return inlet_temperatures_cold_stream

    @property
    def outlet_temperatures_cold_stream(self):
        # TODO: add case if logarithmic_mean_temperature == 0 (heat loads == 0)
        outlet_temperatures_cold_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.mixer_types[operating_case] == 'bypass_cold' and self.heat_loads[operating_case] != 0:  # TODO: Needs testing!
                temperature_difference_2 = self.temperatures_hot_stream_after_hex[operating_case] - self.temperatures_cold_stream_before_hex[operating_case]
                if temperature_difference_2 == self.logarithmic_mean_temperature_differences[operating_case]:
                    temperature_difference_1 = temperature_difference_2
                elif temperature_difference_2 > self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), 0).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                elif temperature_difference_2 < self.logarithmic_mean_temperature_differences[operating_case]:
                    logarithmic_mean_temperature_difference = self.logarithmic_mean_temperature_differences[operating_case]
                    temperature_difference_2_ratio = temperature_difference_2 / logarithmic_mean_temperature_difference
                    temperature_difference_1_ratio = - lambertw(-temperature_difference_2_ratio * np.exp(-temperature_difference_2_ratio), -1).real / temperature_difference_2_ratio
                    temperature_difference_1 = temperature_difference_1_ratio * temperature_difference_2
                    # temperature_difference_1 = (2 * self.logarithmic_mean_temperature_differences[operating_case]**0.3275-temperature_difference_2**0.3275)**(1/0.3275)

                outlet_temperatures_cold_stream[operating_case] = self.temperatures_hot_stream_before_hex[operating_case] - temperature_difference_1
            else:
                outlet_temperatures_cold_stream[operating_case] = self.temperatures_cold_stream_after_hex[operating_case]
        return outlet_temperatures_cold_stream

    @property
    def mixer_fractions_hot_stream(self):
        mixer_fractions_hot_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.heat_loads[operating_case] == 0:  # TODO: Needs testing! Is this correct or should it be 1?
                mixer_fractions_hot_stream[operating_case] = 0
            elif self.mixer_types[operating_case] == 'admixer_hot':
                mixer_fractions_hot_stream[operating_case] = (self.temperatures_hot_stream_before_hex[operating_case] - self.inlet_temperatures_hot_stream[operating_case]) / (self.inlet_temperatures_hot_stream[operating_case] - self.outlet_temperatures_hot_stream[operating_case])
            elif self.mixer_types[operating_case] == 'bypass_hot':
                mixer_fractions_hot_stream[operating_case] = (self.temperatures_hot_stream_after_hex[operating_case] - self.outlet_temperatures_hot_stream[operating_case]) / (self.inlet_temperatures_hot_stream[operating_case] - self.outlet_temperatures_hot_stream[operating_case])
            else:
                mixer_fractions_hot_stream[operating_case] = 0
        return mixer_fractions_hot_stream

    @property
    def mixer_fractions_cold_stream(self):
        mixer_fractions_cold_stream = np.zeros([self.number_operating_cases])
        for operating_case in self.range_operating_cases:
            if self.heat_loads[operating_case] == 0:  # TODO: Needs testing! Is this correct or should it be 1?
                mixer_fractions_cold_stream[operating_case] = 0
            elif self.mixer_types[operating_case] == 'admixer_cold':
                mixer_fractions_cold_stream[operating_case] = (self.temperatures_cold_stream_before_hex[operating_case] - self.inlet_temperatures_cold_stream[operating_case]) / (self.inlet_temperatures_cold_stream[operating_case] - self.outlet_temperatures_cold_stream[operating_case])
            elif self.mixer_types[operating_case] == 'bypass_cold':
                mixer_fractions_cold_stream[operating_case] = (self.temperatures_cold_stream_after_hex[operating_case] - self.outlet_temperatures_cold_stream[operating_case]) / (self.inlet_temperatures_cold_stream[operating_case] - self.outlet_temperatures_cold_stream[operating_case])
            else:
                mixer_fractions_cold_stream[operating_case] = 0
        return mixer_fractions_cold_stream

    def random_choice(self, array, seed=rng.bit_generator._seed_seq.entropy):
        return np.random.default_rng(seed=seed).choice(array)

    def __repr__(self):
        pass

    def __str__(self):
        pass
