from typing import Type, Tuple, List, Dict, Union

from PyQt5.QtWidgets import QMessageBox

PointsTuple: Type = Tuple[List[float], List[float]]
GraphData = List[Dict[str, Union[PointsTuple, bool]]]
Buttons = Union[QMessageBox.StandardButtons, QMessageBox.StandardButton]
