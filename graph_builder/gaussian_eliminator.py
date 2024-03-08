from dataclasses import dataclass
from typing import Generator, Any

from .types import Matrix, Vector


@dataclass
class SLE:
    MAIN_MATRIX: Matrix
    COLUMN_VECTOR: Vector

    def __iter__(self) -> Generator[Any, Any, None]:
        return (getattr(self, attr) for attr in vars(self))

    def __post_init__(self) -> None:
        if len(self.MAIN_MATRIX) < 2:
            raise ValueError("Matrix size is less than 2x2!")

        if len(self.MAIN_MATRIX) != len(self.COLUMN_VECTOR):
            raise ValueError("Invalid matrix dimensions!")

        matrix_is_square: bool = all(len(row) == len(self.COLUMN_VECTOR) for row in self.MAIN_MATRIX)
        if not matrix_is_square:
            raise ValueError("Matrix is not square!")

        # first_row_size: int = len(self.MAIN_MATRIX[0])
        # print([len(row) == first_row_size for row in self.MAIN_MATRIX[1:]])
        # print(is_square)
        # print(list(zip(*self.MAIN_MATRIX)))


class GaussianEliminator:
    def __init__(self, main_matrix: Matrix, column_vector: Vector) -> None:
        self._matrix: Matrix = main_matrix
        self._vector: Vector = column_vector

        # self.__is_solvable: bool = True

    # def _parse_input(self) -> None:
    #     if len(self._matrix) != len(self._vector):
    #         self.__is_solvable = False


sle_matrix: SLE = SLE(
    MAIN_MATRIX=[[1, 2], [4, 5]],
    COLUMN_VECTOR=[10, 11],
)
eliminator: GaussianEliminator = GaussianEliminator(*sle_matrix)
