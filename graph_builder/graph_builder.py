########################################################################################################################
#                                               Тарас - 5 букв, A = -0.5                                               #
#                                               Гевліч - 6 букв, B = 0.6                                               #
#                                             Вікторович - 10 букв, C = 10                                             #
########################################################################################################################
import json
import math
import os
from dataclasses import dataclass, asdict
from typing import Callable, Tuple, Optional, Any, Generator, List, Dict, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
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
    QMenu,
    QAction,
    QGraphicsScene,
    QCheckBox,
    QGraphicsPixmapItem,
    QFileDialog,
    QMessageBox,
)

from .lsm_calculator import LinearCalculator, ParabolicCalculator
from .messagebox import MessageBox
from .plot_widget import MatplotlibWidget
from .zoomable_graphic_view import ZoomableGraphView


@dataclass
class Coefficients:
    A: float = -0.5
    B: float = 0.6
    C: int = 10

    def __iter__(self) -> Generator[Any, Any, None]:
        return (getattr(self, attr) for attr in vars(self))


@dataclass
class PlotData:
    points: Tuple[List[float], List[float]]
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
        self._coefficients = None
        self._chosen_action = None
        self._chosen_func = None
        self._matplotlib_widget = None

        self._init_ui()
        self._make_layout()

        self._create_actions()
        self._create_menu_bar()
        self._click_on_buttons()
        self._trigger_actions()
        self._create_tool_bar()

    def _init_ui(self) -> None:
        self.central_widget = QWidget()
        self.main_grid_layout = QGridLayout()

        self.scene = QGraphicsScene(self)
        self.graph_pixmap_image = QGraphicsPixmapItem()
        self.scene.addItem(self.graph_pixmap_image)
        self.graph_view = ZoomableGraphView(self.scene)

        self.box = QGroupBox()
        self.box_layout = QVBoxLayout()

        self.coordinates_box = QGroupBox("Enter x")
        self.coordinates_box_layout = QVBoxLayout()
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("x")
        self.calculate_funcs_button = QPushButton("Calculate")

        self.coefficients_box = QGroupBox("Enter coefficients")
        self.coefficients_box_layout = QVBoxLayout()
        self.a_input = QLineEdit()
        self.a_input.setPlaceholderText("A")
        self.b_input = QLineEdit()
        self.b_input.setPlaceholderText("B")
        self.c_input = QLineEdit()
        self.c_input.setPlaceholderText("C")
        self.update_button = QPushButton("Update view")

        self.checker_box = QGroupBox()
        self.checker_box_layout = QVBoxLayout()
        self.show_linear = QCheckBox("Straight line")
        self.show_parabola = QCheckBox("Parabola")
        self.show_points = QCheckBox("Points")
        self.show_linear.setChecked(True)
        self.show_parabola.setChecked(True)
        self.show_points.setChecked(True)

        self.buttons_box = QGroupBox()
        self.buttons_box_layout = QVBoxLayout()
        self.calculate_funcs_res = QLabel("")
        self.clear_button = QPushButton("Clear view")

    def _make_layout(self) -> None:
        self.coordinates_box_layout.addWidget(self.x_input)
        self.coordinates_box_layout.addWidget(self.calculate_funcs_button)
        self.coordinates_box.setLayout(self.coordinates_box_layout)

        self.coefficients_box_layout.addWidget(self.a_input)
        self.coefficients_box_layout.addWidget(self.b_input)
        self.coefficients_box_layout.addWidget(self.c_input)
        self.coefficients_box_layout.addWidget(self.update_button)
        self.coefficients_box.setLayout(self.coefficients_box_layout)

        self.checker_box_layout.addWidget(self.show_linear)
        self.checker_box_layout.addWidget(self.show_parabola)
        self.checker_box_layout.addWidget(self.show_points)
        self.checker_box.setLayout(self.checker_box_layout)

        self.buttons_box_layout.addWidget(self.clear_button)
        self.buttons_box_layout.addWidget(self.calculate_funcs_res)
        self.buttons_box.setLayout(self.buttons_box_layout)

        self.box_layout.addWidget(self.coordinates_box)
        self.box_layout.addWidget(self.coefficients_box)
        self.box_layout.addWidget(self.checker_box)
        self.box_layout.addWidget(self.buttons_box)
        self.box.setLayout(self.box_layout)

        self.main_grid_layout.addWidget(self.graph_view, 0, 0)
        self.central_widget.setLayout(self.main_grid_layout)
        self.setCentralWidget(self.central_widget)

    def _create_actions(self) -> None:
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+Alt+S")
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.exit_action = QAction("&Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.clear_action = QAction("&Clear everything", self)
        self.clear_action.setShortcut("Ctrl+D")
        self._create_func_actions()

    def _create_func_actions(self) -> None:
        for attr in dir(self):
            if attr.startswith(self.__func_prefix):
                setattr(
                    self,
                    f"{attr}_action",
                    QAction(f"&{attr.removeprefix(self.__func_prefix)}", self),
                )

    def _fill_menu_with_func_actions(self, menu: QMenu) -> None:
        for attr in dir(self):
            if attr.startswith(self.__func_prefix) and attr.endswith(self.__action_suffix):
                func = getattr(self, attr)
                func.triggered.connect(
                    lambda checked, action_name=attr: self._process_func_menu(
                        action_name
                    )
                )
                menu.addAction(func)

    def _create_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        self.setMenuBar(menu_bar)

        file_menu = QMenu("&File", self)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.exit_action)
        menu_bar.addMenu(file_menu)

        edit_menu = menu_bar.addMenu("&Edit")
        func_menu = QMenu("&Function", self)
        edit_menu.addMenu(func_menu)
        self._fill_menu_with_func_actions(func_menu)
        self._chosen_action = self.__func_prefix + func_menu.actions()[0].text()[1:] + self.__action_suffix
        edit_menu.addAction(self.clear_action)

    def _click_on_buttons(self) -> None:
        self.calculate_funcs_button.clicked.connect(self._calculate_funcs)
        self.update_button.clicked.connect(self._update_scene)
        self.show_linear.clicked.connect(self._plot_rebuild)
        self.show_parabola.clicked.connect(self._plot_rebuild)
        self.show_points.clicked.connect(self._plot_rebuild)
        self.clear_button.clicked.connect(self._clear_scene)

    def _trigger_actions(self) -> None:
        self.open_action.triggered.connect(self._process_open_action)
        self.save_action.triggered.connect(self._process_save_action)
        self.clear_action.triggered.connect(self._process_clear_action)
        self.exit_action.triggered.connect(self._process_exit_action)

    def _process_open_action(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "Text files (*.json *.txt);;All files(*)",
            options=options,
        )

        data = self._open_parse_file(file_path)
        if data:
            self._coefficients = Coefficients(data[0][0], data[0][-1], len(data[0]) - 1)
            self.a_input.setText(str(self._coefficients.A))
            self.b_input.setText(str(self._coefficients.B))
            self.c_input.setText(str(self._coefficients.C))

    def _process_save_action(self) -> None:
        if self._matplotlib_widget:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save graph",
                "",
                "Image files(*.png *.jpg *.jpeg);;All files(*)",
                options=options,
            )

            if os.path.exists(os.path.dirname(file_path)):
                self._matplotlib_widget.fig.savefig(file_path)
                MessageBox(
                    title="Save graph",
                    text="Image was successfully saved!",
                    detailed_text=f"Image was saved to path:\n{file_path}",
                ).display()

    def _process_clear_action(self) -> None:
        self._clear_scene()
        self.x_input.setText("")
        self.a_input.setText("")
        self.b_input.setText("")
        self.c_input.setText("")
        self.calculate_funcs_res.setText("")
        self.show_linear.setChecked(False)
        self.show_parabola.setChecked(False)
        self.show_points.setChecked(False)

    def _process_exit_action(self) -> None:
        self.close()

    def _process_func_menu(self, action_name: str) -> None:
        self._chosen_action = action_name
        self._coefficients = self._get_coeffs()
        if self._coefficients:
            self._build_plot(self._chosen_action)
            self._reload_scene()

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

    def _build_plot(self, action_name: str) -> None:
        self._chosen_func = getattr(self, action_name.removesuffix(self.__action_suffix))

        if self._chosen_func:
            self._generate_plot(
                [
                    (
                        asdict(
                            PlotData(
                                points=self.get_points(self._chosen_func, *self._coefficients),
                                points_only=True,
                            ),
                        )
                        if self.show_points.isChecked()
                        else None
                    ),
                    (
                        asdict(
                            PlotData(
                                points=LinearCalculator(
                                    self.get_points(self._chosen_func, *self._coefficients)
                                ).find_lsm_points(),
                                show_points=False,
                            )
                        )
                        if self.show_linear.isChecked()
                        else None
                    ),
                    (
                        asdict(
                            PlotData(
                                points=ParabolicCalculator(
                                    self.get_points(self._chosen_func, *self._coefficients)
                                ).find_lsm_points(),
                                show_points=False,
                            ),
                        )
                        if self.show_parabola.isChecked()
                        else None
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

        lin_calc = LinearCalculator(self.get_points(self._chosen_func, *self._coefficients))
        par_calc = ParabolicCalculator(self.get_points(self._chosen_func, *self._coefficients))
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

    def _clear_scene(self) -> None:
        self.scene.clear()

    def _reload_scene(self) -> None:
        self._clear_scene()
        image_path = os.path.join("graph_builder", "temp_generate_plot.png")
        self.graph_pixmap_image = QGraphicsPixmapItem(QPixmap(image_path))
        self.scene.addItem(self.graph_pixmap_image)
        os.remove(image_path)

    def _create_tool_bar(self) -> None:
        tool_bar = QDockWidget("Options")
        tool_bar.setWidget(self.box)
        self.addDockWidget(Qt.RightDockWidgetArea, tool_bar)

    def _plot_rebuild(self) -> None:
        if self._chosen_action and self._coefficients:
            self._build_plot(self._chosen_action)
            self._reload_scene()

    def _generate_plot(
            self,
            graphs_values: List[Dict[str, Union[Tuple[List[float], List[float]], bool]]],
    ) -> None:
        self._matplotlib_widget = MatplotlibWidget()
        for graph_data, color in zip(graphs_values, ("blue", "red", "green")):
            if graph_data is None:
                continue
            x, y = graph_data["points"]
            self._matplotlib_widget.plot(
                x, y,
                show_points=graph_data["show_points"],
                points_only=graph_data["points_only"],
                color=color,
            )

        temp_file = f"temp_generate_plot.png"
        temp_image_path = os.path.join("graph_builder", temp_file)
        self._matplotlib_widget.fig.savefig(temp_image_path)

    @staticmethod
    def calc_sin_3x_squared(x: float) -> float:
        return math.sin(3 * (x ** 2))

    @staticmethod
    def calc_atan_4x_plus_2(x: float) -> float:
        return math.atan(4 * x + 2)

    @staticmethod
    def calc_sin_x(x: float) -> float:
        return math.sin(x)

    @staticmethod
    def calc_eps_power_x(x: float) -> float:
        return math.e ** x

    @staticmethod
    def get_points(
            func: Callable,
            start_x: float,
            end_x: float,
            step_num: int,
    ) -> Tuple[List[float], List[float]]:
        step = abs(end_x - start_x) / step_num
        x_values, y_values = [], []
        for i in range(step_num + 1):
            x_values.append(round(start_x, 3))
            y_values.append(round(func(start_x), 3))
            start_x = start_x + step
        return x_values, y_values

    @staticmethod
    def _open_parse_file(path: str) -> Optional[Tuple[List[float], List[float]]]:
        try:
            with open(path, "r") as file:
                data = json.load(file)
            if len(data) != 2 or len(data[0]) != len(data[1]):
                MessageBox(
                    title="Format error",
                    text="File must consist of two lists of the same size!",
                    icon=QMessageBox.Warning,
                ).display()
                return None
            return data
        except json.JSONDecodeError:
            MessageBox(
                title="File error",
                text="Invalid or empty file! Couldn't be parsed.",
                icon=QMessageBox.Warning,
            ).display()
