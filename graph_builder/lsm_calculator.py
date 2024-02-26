from abc import ABC, abstractmethod
from typing import Tuple, List

import numpy as np


class BaseLSMCalculator(ABC):
    def __init__(self, points: Tuple[List[float], List[float]]) -> None:
        self._x_points, self._y_points = points[0], points[1]
        self._point_num = len(self._x_points)

    def sum_xi(self) -> float:
        return sum(self._x_points)

    def sum_xi_squared(self) -> float:
        return sum([point**2 for point in self._x_points])

    def sum_xi_cubed(self) -> float:
        return sum([point**3 for point in self._x_points])

    def sum_xi_quadrupled(self) -> float:
        return sum([point**4 for point in self._x_points])

    def sum_yi(self) -> float:
        return sum(self._y_points)

    def sum_xi_yi(self) -> float:
        return sum(
            [
                point_x * point_y
                for point_x, point_y in zip(self._x_points, self._y_points)
            ]
        )

    def sum_xi_squared_yi(self) -> float:
        return sum(
            [
                (point_x**2) * point_y
                for point_x, point_y in zip(self._x_points, self._y_points)
            ]
        )

    @abstractmethod
    def calculate(self) -> Tuple[float, ...]:
        raise NotImplementedError

    @abstractmethod
    def recalculate(self, *a_values, x_values: List[float]) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_lsm_points(self) -> Tuple[List[float], List[float]]:
        raise NotImplementedError


class LinearCalculator(BaseLSMCalculator):
    def __init__(self, points: Tuple[List[float], List[float]]) -> None:
        super().__init__(points)

    def calculate(self) -> Tuple[float, ...]:
        left_matrix_half = np.array(
            [
                [self._point_num, self.sum_xi()],
                [self.sum_xi(), self.sum_xi_squared()],
            ]
        )

        right_matrix_half = np.array([self.sum_yi(), self.sum_xi_yi()])

        return tuple(np.linalg.solve(left_matrix_half, right_matrix_half))

    def recalculate(self, *a_val, x_values: List[float]) -> List[float]:
        return [round(a_val[0] + (a_val[1] * x), 3) for x in x_values]

    def find_lsm_points(self) -> Tuple[List[float], List[float]]:
        a0, a1 = self.calculate()
        recalculated_y_values = self.recalculate(a0, a1, x_values=self._x_points)
        return self._x_points, recalculated_y_values


class ParabolicCalculator(BaseLSMCalculator):
    def __init__(self, points: Tuple[List[float], List[float]]) -> None:
        super().__init__(points)

    def calculate(self) -> Tuple[float, ...]:
        left_matrix_half = np.array(
            [
                [self._point_num, self.sum_xi(), self.sum_xi_squared()],
                [self.sum_xi(), self.sum_xi_squared(), self.sum_xi_cubed()],
                [self.sum_xi_squared(), self.sum_xi_cubed(), self.sum_xi_quadrupled()],
            ]
        )

        right_matrix_half = np.array(
            [self.sum_yi(), self.sum_xi_yi(), self.sum_xi_squared_yi()]
        )

        return tuple(np.linalg.solve(left_matrix_half, right_matrix_half))

    def recalculate(self, *a_val, x_values: List[float]) -> List[float]:
        return [
            round(a_val[0] + (a_val[1] * x) + (a_val[2] * x**2), 3) for x in x_values
        ]

    def find_lsm_points(self) -> Tuple[List[float], List[float]]:
        a0, a1, a2 = self.calculate()
        recalculated_y_values = self.recalculate(a0, a1, a2, x_values=self._x_points)
        return self._x_points, recalculated_y_values
