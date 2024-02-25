from typing import Optional, List

from matplotlib import pyplot as plt
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MatplotlibWidget(FigureCanvas):
    def __init__(
        self,
        parent: Optional[FigureCanvasBase] = None,
        width: int = 9,
        height: int = 5,
        dpi: int = 200,
    ) -> None:
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

    def plot(
        self,
        x: List[float],
        y: List[float],
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        *,
        show_points: bool = True,
        points_only: bool = False,
        color: str = "blue",
    ) -> None:
        self.ax.plot(x, y, ("o" if points_only else "o-") if show_points else "", color=color)
        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.show_grid()
        self.draw()

    def show_grid(self, show: bool = True) -> None:
        self.ax.grid(show)
