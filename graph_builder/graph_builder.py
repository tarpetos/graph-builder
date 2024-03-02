import os
from dataclasses import dataclass, asdict
from typing import Callable, Optional, Any, Generator, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QVBoxLayout,
    QDockWidget,
    QGraphicsScene,
    QCheckBox,
    QGraphicsPixmapItem,
    QMessageBox,
    QSpinBox,
    QShortcut,
)
from sympy import symbols, sympify, lambdify, SympifyError

from .lsm_calculator import LinearCalculator, ParabolicCalculator
from .messagebox import MessageBox
from .plot_widget import MatplotlibWidget
from .types import PointsTuple, GraphData
from .zoomable_graphic_view import ZoomableGraphView


@dataclass
class Coefficients:
    A: float = -0.7
    B: float = 0.7
    C: int = 13

    def __iter__(self) -> Generator[Any, Any, None]:
        return (getattr(self, attr) for attr in vars(self))


@dataclass
class PlotData:
    points: PointsTuple
    show_points: bool = True
    points_only: bool = False


class GraphBuilderWindow(QMainWindow):
    MIN_SIZE = 640, 480
    TITLE = "Graph Builder"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle(self.TITLE)
        self.setMinimumSize(*self.MIN_SIZE)

        self.__func_prefix = "calc_"
        self.__action_suffix = "_action"
        self.__arg_var = "x"
        self._chosen_action = None
        self._chosen_func = None
        self._matplotlib_widget = None

        self._init_ui()
        self._make_layout()

        self._click_on_buttons()
        self._create_tool_bar()

        self._coefficients = Coefficients()
        self._set_initial_values()

    def _init_ui(self) -> None:
        self.central_widget = QWidget()
        self.main_grid_layout = QGridLayout()

        self.scene = QGraphicsScene(self)
        self.graph_pixmap_image = QGraphicsPixmapItem()
        self.scene.addItem(self.graph_pixmap_image)
        self.graph_view = ZoomableGraphView(self.scene)

        self.box = QGroupBox()
        self.box_layout = QVBoxLayout()

        self.func_box = QGroupBox("Enter function")
        self.func_box_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("sin(x^2) + 2")
        self.set_func_button = QPushButton("Set")

        self.coordinates_box = QGroupBox("Enter x")
        self.coordinates_box_layout = QVBoxLayout()
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("x")
        self.calculate_funcs_res = QLabel("")
        self.calculate_funcs_button = QPushButton("Calculate")

        self.coefficients_box = QGroupBox("Enter coefficients")
        self.coefficients_box_layout = QVBoxLayout()
        self.a_input = QLineEdit()
        self.a_input.setPlaceholderText("A")
        self.b_input = QLineEdit()
        self.b_input.setPlaceholderText("B")
        self.c_input = QSpinBox(minimum=2, maximum=100000)
        self.update_button = QPushButton("Update view")

        self.checker_box = QGroupBox()
        self.checker_box_layout = QVBoxLayout()
        self.show_linear = QCheckBox("Line")
        self.show_parabola = QCheckBox("Parabola")
        self.show_points = QCheckBox("Points")
        self.show_linear.setChecked(True)
        self.show_parabola.setChecked(True)
        self.show_points.setChecked(True)
        self.clear_button = QPushButton("Clear view")

        self.cleat_everything_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)

    def _make_layout(self) -> None:
        self._set_layout(
            self.func_box,
            self.func_box_layout,
            widgets=[self.func_input, self.set_func_button],
        )
        self._set_layout(
            self.coordinates_box,
            self.coordinates_box_layout,
            widgets=[
                self.x_input,
                self.calculate_funcs_button,
                self.calculate_funcs_res,
            ],
        )
        self._set_layout(
            self.coefficients_box,
            self.coefficients_box_layout,
            widgets=[self.a_input, self.b_input, self.c_input, self.update_button],
        )
        self._set_layout(
            self.checker_box,
            self.checker_box_layout,
            widgets=[
                self.show_linear,
                self.show_parabola,
                self.show_points,
                self.clear_button,
            ],
        )
        self._set_layout(
            self.box,
            self.box_layout,
            widgets=[
                self.func_box,
                self.coordinates_box,
                self.coefficients_box,
                self.checker_box,
            ],
        )

        self.main_grid_layout.addWidget(self.box, 0, 0)
        self.main_grid_layout.addWidget(self.graph_view, 0, 1)
        self.central_widget.setLayout(self.main_grid_layout)
        self.setCentralWidget(self.central_widget)

    def _click_on_buttons(self) -> None:
        self.set_func_button.clicked.connect(self._set_calc_func)
        self.calculate_funcs_button.clicked.connect(self._calculate_funcs)
        self.update_button.clicked.connect(self._update_scene)
        self.show_linear.clicked.connect(self._plot_rebuild)
        self.show_parabola.clicked.connect(self._plot_rebuild)
        self.show_points.clicked.connect(self._plot_rebuild)
        self.clear_button.clicked.connect(self._clear_scene)
        self.cleat_everything_shortcut.activated.connect(self._process_clear_action)

    def _process_clear_action(self) -> None:
        self._clear_scene()
        self._chosen_func = None
        self.func_input.setText("")
        self.x_input.setText("")
        self.a_input.setText("")
        self.b_input.setText("")
        self.c_input.setValue(2)
        self.calculate_funcs_res.setText("")
        self.show_linear.setChecked(False)
        self.show_parabola.setChecked(False)
        self.show_points.setChecked(False)

    def _get_coeffs(self) -> Optional[Coefficients]:
        coeffs = self.a_input.text(), self.b_input.text(), self.c_input.text()
        try:
            parsed_coeffs = [float(coeff) for coeff in coeffs[:2]]
            parsed_coeffs.append(int(coeffs[-1]))
            return Coefficients(*parsed_coeffs)
        except ValueError:
            MessageBox(
                title="Invalid input",
                text="One or more coefficients has invalid format or not entered!",
                icon=QMessageBox.Warning,
            ).display()

    def _build_plot(self) -> None:
        points = self.get_points(self._chosen_func, *self._coefficients)
        show_points = self.show_points.isChecked()
        self._generate_plot(
            [
                self._get_plot(points, self.show_points, points_only=True),
                self._get_plot(
                    LinearCalculator(points).find_lsm_points(),
                    self.show_linear,
                    show_points=show_points,
                ),
                self._get_plot(
                    ParabolicCalculator(points).find_lsm_points(),
                    self.show_parabola,
                    show_points=show_points,
                ),
            ]
        )

    def _calculate_funcs(self) -> None:
        x_value = self.x_input.text()
        try:
            x_value = float(x_value)
        except ValueError:
            return None

        if not x_value or not self._chosen_func or not self._coefficients:
            return None

        points = self.get_points(self._chosen_func, *self._coefficients)
        lin_calc = LinearCalculator(points)
        par_calc = ParabolicCalculator(points)
        a0, a1 = lin_calc.calculate()
        lin_res = lin_calc.recalculate(a0, a1, x_values=[x_value])[0]
        a0, a1, a2 = par_calc.calculate()
        par_res = par_calc.recalculate(a0, a1, a2, x_values=[x_value])[0]
        self.calculate_funcs_res.setText(
            f"Linear result (x = {x_value}): {lin_res}\n"
            f"Parabolic result (x = {x_value}): {par_res}"
        )

    def _update_scene(self) -> None:
        self._coefficients = self._get_coeffs()
        self._plot_rebuild()

    def _clear_scene(self, *args) -> None:
        self.scene.clear()

    def _reload_scene(self) -> None:
        self._clear_scene()
        image_path = os.path.join("graph_builder", "temp_generate_plot.png")
        self.graph_pixmap_image = QGraphicsPixmapItem(QPixmap(image_path))
        self.scene.addItem(self.graph_pixmap_image)
        os.remove(image_path)

    def _create_tool_bar(self) -> None:
        tool_bar = QDockWidget()
        tool_bar.setWidget(self.box)
        tool_bar.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, tool_bar)

    def _plot_rebuild(self) -> None:
        if self._chosen_func and self._coefficients:
            self._build_plot()
            self._reload_scene()
        else:
            self._coefficients and MessageBox(
                title="No function",
                text="Function not selected!",
                icon=QMessageBox.Warning,
                detailed_text='Enter desired function -> Press "Set" -> Get result graph',
            ).display()

    def _generate_plot(
        self,
        graphs_values: GraphData,
    ) -> None:
        self._matplotlib_widget = MatplotlibWidget()
        for graph_data, color in zip(graphs_values, ("yellow", "blue", "black")):
            if graph_data is None:
                continue
            x, y = graph_data["points"]
            self._matplotlib_widget.plot(
                x,
                y,
                show_points=graph_data["show_points"],
                points_only=graph_data["points_only"],
                color=color,
            )

        temp_file = f"temp_generate_plot.png"
        temp_image_path = os.path.join("graph_builder", temp_file)
        self._matplotlib_widget.fig.savefig(temp_image_path)

    def _set_initial_values(self) -> None:
        self.func_input.setText("sin(x^2) + 2")
        self.a_input.setText(str(self._coefficients.A))
        self.b_input.setText(str(self._coefficients.B))
        self.c_input.setValue(self._coefficients.C)

    def _set_calc_func(self) -> None:
        user_func = self.func_input.text()
        if not user_func:
            MessageBox(
                text="This input couldn't be empty!", icon=QMessageBox.Warning
            ).display()
            return None

        expression = self._parse_expression(user_func)
        if not expression:
            MessageBox(
                text="Expression isn't valid!", icon=QMessageBox.Warning
            ).display()
            return None

        self.expression_with_x = expression.subs(
            self.__arg_var, symbols(self.__arg_var)
        )
        self._chosen_func = lambdify(self.__arg_var, self.expression_with_x, "math")
        self._parse_func()

        if self._chosen_func:
            self._plot_rebuild()

    def _parse_func(self) -> None:
        try:
            round(self._chosen_func(1))
        except (TypeError, NameError):
            MessageBox(
                text="Couldn't convert entered string to Python function!",
                icon=QMessageBox.Warning,
            ).display()
            self._chosen_func = None
        except ZeroDivisionError:
            pass

    @staticmethod
    def _parse_expression(user_func: str) -> Optional[Any]:
        try:
            return sympify(user_func)
        except (SympifyError, TypeError):
            return None

    @staticmethod
    def _set_layout(
        box: QGroupBox, layout: QVBoxLayout, *, widgets: List[QWidget]
    ) -> None:
        [layout.addWidget(widget) for widget in widgets]
        box.setLayout(layout)

    @staticmethod
    def get_points(
        func: Callable,
        start_x: float,
        end_x: float,
        step_num: int,
    ) -> PointsTuple:
        step = abs(end_x - start_x) / step_num
        x_values, y_values = [], []
        for i in range(step_num + 1):
            x_values.append(round(start_x, 3))
            y_values.append(round(func(start_x), 3))
            start_x = start_x + step
        return x_values, y_values

    @staticmethod
    def _get_plot(
        points: PointsTuple,
        show_options: QCheckBox,
        *,
        show_points: bool = True,
        points_only: bool = False,
    ) -> Optional[Dict[str, Any]]:
        return (
            asdict(PlotData(points, show_points, points_only))
            if show_options.isChecked()
            else None
        )
