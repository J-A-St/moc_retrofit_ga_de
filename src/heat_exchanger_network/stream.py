import numpy as np


class Stream:
    """Stream object"""

    def __init__(self, number, number_operating_cases, range_operating_cases, number_streams, stream_data):
        self.number = number
        self.target_temperatures = np.zeros([number_operating_cases])
        self.supply_temperatures = np.zeros([number_operating_cases])
        self.film_heat_transfer_coefficients = np.zeros([number_operating_cases])
        self.specific_heat_capacities = np.zeros([number_operating_cases])
        self.mass_flows = np.zeros([number_operating_cases])
        self.heat_capacity_flows = np.zeros([number_operating_cases])
        self.enthalpy_flows = np.zeros([number_operating_cases])
        self.extreme_temperatures = np.zeros([number_operating_cases])
        for operating_case in range_operating_cases:
            self.target_temperatures[operating_case] = stream_data['Tout'][number + number_streams * operating_case] + 273.15
            self.supply_temperatures[operating_case] = stream_data['Tin'][number + number_streams * operating_case] + 273.15
            self.film_heat_transfer_coefficients[operating_case] = stream_data['h'][number + number_streams * operating_case]
            self.specific_heat_capacities[operating_case] = stream_data['cp'][number + number_streams * operating_case]
            self.mass_flows[operating_case] = stream_data['m_dot'][number + number_streams * operating_case]
            self.heat_capacity_flows[operating_case] = self.specific_heat_capacities[operating_case] * self.mass_flows[operating_case]
            self.enthalpy_flows[operating_case] = self.heat_capacity_flows[operating_case] * abs(self.target_temperatures[operating_case] - self.supply_temperatures[operating_case])
            self.extreme_temperatures[operating_case] = stream_data['ExtremT'][number + number_streams * operating_case]

    def __repr__(self):
        pass

    def __str__(self):
        pass
