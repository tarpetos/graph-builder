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
        self.__raise_conditional_exception(
            len(self.MAIN_MATRIX) < 2, ValueError, "Matrix size is less than 2x2!"
        )
        self.__raise_conditional_exception(
            len(self.MAIN_MATRIX) != len(self.COLUMN_VECTOR),
            ValueError,
            "Size of the column vector is not equal to the number of rows in the main matrix!",
        )
        self.__raise_conditional_exception(
            any(len(row) != len(self.COLUMN_VECTOR) for row in self.MAIN_MATRIX),
            ValueError,
            "Matrix is not square!",
        )
        transposed_matrix = list(zip(*self.MAIN_MATRIX))
        self.__raise_conditional_exception(
            any(all(value == 0 for value in row) for row in self.MAIN_MATRIX)
            or any(all(value == 0 for value in row) for row in transposed_matrix),
            ValueError,
            "System of linear equations has no real "
            "solutions or it has infinite number of solutions!",
        )

    @staticmethod
    def __raise_conditional_exception(
        condition: bool,
        exception: type(Exception),
        message: str,
    ) -> None:
        if condition:
            raise exception(message)


class GaussianEliminator:
    def __init__(self, main_matrix: Matrix, column_vector: Vector) -> None:
        self._matrix: Matrix = main_matrix
        self._vector: Vector = column_vector
        self._augmented_matrix: Matrix = [
            row.append(col_val) or row for row, col_val in zip(main_matrix, column_vector)
        ]
        self.solution_vector: Vector = [0.0 for _ in range(len(self._vector))]

    def convert_2_row_echelon_form(self) -> None:
        self._straight_gait()
        self._reversed_gait()

    def _straight_gait(self) -> None:
        ...

    def _reversed_gait(self) -> None:
        ...


sle_matrix: SLE = SLE(
    MAIN_MATRIX=[
        [0, 2],
        [1, 5],
    ],
    COLUMN_VECTOR=[10, 11],
)
eliminator: GaussianEliminator = GaussianEliminator(*sle_matrix)
eliminator.convert_2_row_echelon_form()
