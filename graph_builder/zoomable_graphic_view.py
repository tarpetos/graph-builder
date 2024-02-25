from PyQt5.QtGui import QPainter, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene


class ZoomableGraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene) -> None:
        super(ZoomableGraphView, self).__init__(scene)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor

        self.scale(factor, factor)
