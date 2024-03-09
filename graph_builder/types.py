from typing import Type, Tuple, List, Dict, Union

from PyQt5.QtWidgets import QMessageBox

PointsTuple: Type = Tuple[List[float], List[float]]
GraphData: Type = List[Dict[str, Union[PointsTuple, bool]]]
Buttons: Type = Union[QMessageBox.StandardButtons, QMessageBox.StandardButton]
RealNumber: Type = Union[float, int]
Vector: Type = List[RealNumber]
Matrix: Type = List[Vector]
