from typing import Tuple, List


class Navigator:
    def __init__(
        self, origin: List, strict: bool = False, limits: Tuple[List, List] = None
    ):
        self.coordinates = self.original_coordinates = origin

        if strict and not limits:
            raise Exception

        self.strict = strict
        self.limits = limits

    @property
    def limits(self):
        return self._limits

    @limits.setter
    def limits(self, value: Tuple[List, List]):
        self._limits = value

    def reset(self):
        self.coordinates = self.original_coordinates

    def move(self, axis: int, distance=1):
        self.coordinates[axis] += distance

        if self.strict:
            if (
                self.coordinates[axis] < self.limits[0][axis]
                or self.coordinates[axis] > self.limits[1][axis]
            ):
                self.coordinates[axis] -= distance

    def __getitem__(self, index):
        return self.coordinates[index]
