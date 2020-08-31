
class OperatingCase:
    """Operating case object"""

    def __init__(self, stream_data, number, number_operating_cases):
        self.number = number
        self.start_time = stream_data['tstart'][self.number * len(stream_data['tstart']) / number_operating_cases]
        self.end_time = stream_data['tend'][self.number * len(stream_data['tend']) / number_operating_cases]
        self.duration = self.end_time - self.start_time

    def __repr__(self):
        pass

    def __str__(self):
        pass
