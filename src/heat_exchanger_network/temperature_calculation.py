import numpy as np


class TemperatureCalculation:
    # TODO: Use calculation from ga_de_retrofit and include lambert w calculation for determining mixer with corresponding temperatures
    # TODO: Implement non existing streams in some OC's: are there any 1/(enthalpy_flow_stream) and dT in HEXs needs to be = dT_UB
    def __init__(self, heat_exchanger_network, case_study):
        self.heat_exchanger_network = heat_exchanger_network
        self.hot_streams = case_study.hot_streams
        self.cold_streams = case_study.cold_streams
        self.range_hot_streams = case_study.range_hot_streams
        self.range_cold_streams = case_study.range_cold_streams

    def update_temperatures(self):
        stream_types = ['hot', 'cold']
        for _, stream_type in enumerate(stream_types):
            if stream_type == 'hot':
                split_type = 4
                mixer_type = 6
                split_fraction_type = 1
                mixer_fraction_type = 3
                range_streams = self.range_hot_streams
                streams = self.hot_streams
                signum_heat_loads = -1

            elif stream_type == 'cold':
                split_type = 5
                mixer_type = 7
                split_fraction_type = 2
                mixer_fraction_type = 4
                range_streams = self.range_cold_streams
                streams = self.cold_streams
                signum_heat_loads = 1

            temperatures = np.zeros([self.heat_exchanger_network.number_heat_exchangers, self.heat_exchanger_network.number_operating_cases, 4])
            for stream in range_streams:
                sorted_heat_exchangers_on_stream = self.heat_exchanger_network.get_sorted_heat_exchangers_on_stream(stream, stream_type)
                for index, exchanger in enumerate(sorted_heat_exchangers_on_stream):
                    temperatures[:, :, 0] = self.get_supply_temperatures(streams[stream].supply_temperatures, index, exchanger, sorted_heat_exchangers_on_stream, split_type, stream_type, temperatures)
                    temperatures[:, :, 3] = self.get_target_temperatures(streams[stream], exchanger, split_type, stream_type, signum_heat_loads, temperatures)
                    temperatures[:, :, 1] = self.get_inlet_temperatures(exchanger, mixer_type, mixer_fraction_type, temperatures)
                    temperatures[:, :, 2] = self.get_outlet_temperatures(streams[stream], exchanger, mixer_type, mixer_fraction_type, split_fraction_type, signum_heat_loads, temperatures)
                    if stream_type == 'hot':
                        self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.temperatures_hot_side = temperatures[exchanger, :, :]
                    elif stream_type == 'cold':
                        self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.temperatures_cold_side = temperatures[exchanger, :, :]

    def get_supply_temperatures(self, supply_temperatures_stream, index, exchanger, sorted_heat_exchangers_on_stream, split_type, stream_type, temperatures):
        supply_temperatures = temperatures[:, :, 0]
        target_temperatures = temperatures[:, :, 3]
        if exchanger != sorted_heat_exchangers_on_stream[0]:
            # If heat exchanger is not first on the stream
            if self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[split_type] != 0:
                # If there is a split get all exchangers in split
                heat_exchanger_in_split = self.heat_exchanger_network.get_heat_exchangers_in_split(
                    self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[split_type], stream_type)
            else:
                heat_exchanger_in_split = []

            for operating_case in self.heat_exchanger_network.range_operating_cases:
                if exchanger not in heat_exchanger_in_split:
                    # Supply temperature of exchanger is equal to target temperature of exchanger before (no split, or first exchanger on stream)
                    supply_temperatures[exchanger, operating_case] = target_temperatures[sorted_heat_exchangers_on_stream[index-1], operating_case]
                else:
                    # Supply temperature for all exchanger in a split is the same
                    supply_temperatures[exchanger, operating_case] = supply_temperatures[sorted_heat_exchangers_on_stream[index-1], operating_case]
        else:
            # Supply temperature of first heat exchanger is equal to supply temperature of stream
            supply_temperatures[exchanger] = supply_temperatures_stream
        return supply_temperatures

    def get_target_temperatures(self, stream, exchanger, split_type, stream_type, signum_heat_loads, temperatures):
        supply_temperatures = temperatures[:, :, 0]
        target_temperatures = temperatures[:, :, 3]
        if self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[split_type] != 0:
            # If there is a split the enthalpy difference is equal to the heat loads of all heat exchangers in the split
            heat_exchanger_in_split = self.heat_exchanger_network.get_heat_exchangers_in_split(
                self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[split_type], stream_type)
        else:
            heat_exchanger_in_split = []
        for operating_case in self.heat_exchanger_network.range_operating_cases:
            if exchanger in heat_exchanger_in_split:
                enthalpy_difference = 0
                for split_exchanger in heat_exchanger_in_split:
                    enthalpy_difference += signum_heat_loads * self.heat_exchanger_network.heat_exchangers[split_exchanger].process_quantities.heat_loads[operating_case]
            else:
                enthalpy_difference = signum_heat_loads * self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.heat_loads[operating_case]

            target_temperatures[exchanger, operating_case] = supply_temperatures[exchanger, operating_case] + \
                enthalpy_difference / stream.heat_capacity_flows[operating_case]
        return target_temperatures

    def get_inlet_temperatures(self, exchanger, mixer_type, mixer_fraction_type, temperatures):
        supply_temperatures = temperatures[:, :, 0]
        inlet_temperatures = temperatures[:, :, 1]
        target_temperatures = temperatures[:, :, 3]
        if self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[mixer_type] != 3:
            # If there is no mixer or a bypass
            for operating_case in self.heat_exchanger_network.range_operating_cases:
                inlet_temperatures[exchanger, operating_case] = supply_temperatures[exchanger, operating_case]
        else:
            # If there is an admixer
            for operating_case in self.heat_exchanger_network.range_operating_cases:
                inlet_temperatures[exchanger, operating_case] = (supply_temperatures[exchanger, operating_case] +
                                                                 self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[mixer_fraction_type, operating_case] * target_temperatures[exchanger, operating_case]) / (1+self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[mixer_fraction_type, operating_case])
        return inlet_temperatures

    def get_outlet_temperatures(self, stream, exchanger, mixer_type, mixer_fraction_type, split_fraction_type, signum_heat_loads, temperatures):
        inlet_temperatures = temperatures[:, :, 1]
        outlet_temperatures = temperatures[:, :, 2]
        for operating_case in self.heat_exchanger_network.range_operating_cases:
            if self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[mixer_type] == 1:
                # If there is no mixer
                outlet_temperatures[exchanger, operating_case] = inlet_temperatures[exchanger, operating_case] + \
                    signum_heat_loads * self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.heat_loads[operating_case] / \
                    (self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[split_fraction_type, operating_case] * stream.heat_capacity_flows[operating_case])
            elif self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[mixer_type] == 2:
                # If there is a bypass
                if self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[mixer_fraction_type, operating_case] == 1:
                    # If heat exchanger is completely bypassed
                    outlet_temperatures[exchanger, operating_case] = inlet_temperatures[exchanger, operating_case]
                else:
                    # If heat exchanger is not completely bypassed
                    outlet_temperatures[exchanger, operating_case] = inlet_temperatures[exchanger, operating_case] + \
                        signum_heat_loads * self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.heat_loads[operating_case] / \
                        ((1-self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[mixer_fraction_type, operating_case]) *
                         self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[split_fraction_type, operating_case] * stream.heat_capacity_flows[operating_case])
            elif self.heat_exchanger_network.heat_exchangers[exchanger].topology.address_vector[mixer_type] == 3:
                # If there is an admixer
                outlet_temperatures[exchanger, operating_case] = inlet_temperatures[exchanger, operating_case] + \
                    signum_heat_loads * self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.heat_loads[operating_case] / \
                    ((1+self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[mixer_fraction_type, operating_case]) *
                     self.heat_exchanger_network.heat_exchangers[exchanger].process_quantities.matrix[split_fraction_type, operating_case] * stream.heat_capacity_flows[operating_case])

        return outlet_temperatures

    def __repr__(self):
        pass

    def __str__(self):
        pass
