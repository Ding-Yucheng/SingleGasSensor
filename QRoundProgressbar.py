from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import math

normal_threshold = 67
bad_threshold = 80

class RoundProgressbar(QWidget):
	def __init__(
			self,
			parent=None,
			color: QColor = QColor(100, 255, 100),
			size: int = 100,
			thickness: int = 30,
			value: int = 1,
			maximum: int = 200,
			round_edge: bool = True,
			bg_circle_color: QColor = QColor(200, 200, 200, 255),
			fill_bg_circle: bool = False
	):
		if parent is not None:
			super().__init__(parent=parent)
		elif parent is None:
			super().__init__()
		self._circular_size = size
		self._thickness = thickness
		self._color = color
		self._maximum = maximum
		self._value = value
		self._alen = (self._value / self._maximum) * 180
		self._a = -(self._alen + 180)
		self._round_edge = round_edge
		self._bg_circle_color = bg_circle_color
		self._fill_bg_circle = fill_bg_circle

	def paintEvent(self, paint_event):
		painter = QPainter()
		painter.begin(self)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.setPen(QPen(QColor(255, 150, 0), self._thickness / 4, Qt.SolidLine, Qt.RoundCap))
		painter.drawLine(self.width() / 2.42 * (1.21 - math.cos(math.radians(normal_threshold/200*180))),
						 self.width() / 2.42 * (1.21 - math.sin(math.radians(normal_threshold/200*180))),
						 self.width() / 2 * (1 - math.cos(math.radians(normal_threshold/200*180))),
						 self.width() / 2 * (1 - math.sin(math.radians(normal_threshold/200*180))))
		painter.setPen(QPen(QColor(255, 0, 0), self._thickness / 4, Qt.SolidLine, Qt.RoundCap))
		painter.drawLine(self.width() / 2.42 * (1.21 - math.cos(math.radians(bad_threshold/200*180))),
						 self.width() / 2.42 * (1.21 - math.sin(math.radians(bad_threshold/200*180))),
						 self.width() / 2 * (1 - math.cos(math.radians(bad_threshold/200*180))),
						 self.width() / 2 * (1 - math.sin(math.radians(bad_threshold/200*180))))
		painter.setPen(QPen(self._bg_circle_color, self._thickness - 1, Qt.SolidLine, Qt.RoundCap))
		if self._fill_bg_circle:
			painter.setBrush(QBrush(self._bg_circle_color, Qt.SolidPattern))
		elif not self._fill_bg_circle:
			painter.setBrush(Qt.NoBrush)
		painter.drawArc(self._thickness,self._thickness,self._circular_size,self._circular_size, 0,180*16)

		if self._round_edge:
			painter.setPen(QPen(self._color, self._thickness, Qt.SolidLine, Qt.RoundCap))
		elif not self._round_edge:
			painter.setPen(QPen(self._color, self._thickness, Qt.SolidLine, Qt.FlatCap))
		painter.setBrush(Qt.NoBrush)
		painter.drawArc(
			self._thickness,
			self._thickness,
			self._circular_size,
			self._circular_size,
			self._a * 16,
			self._alen * 16
		)
		painter.setPen(QPen(self._color, self._thickness / 2, Qt.SolidLine, Qt.RoundCap))
		painter.drawLine(self.width() / 2, self.width() / 2,
						 self.width() / 3 * (1.5 - math.cos(math.radians(self._alen))),
						 self.width() / 3 * (1.5 - math.sin(math.radians(self._alen))))
		painter.end()

	def resizeEvent(self, event):
		super().resizeEvent(event)
		self._circular_size = (self.width() - (self._thickness * 2))

	def get_value(self):
		return self._value

	@pyqtSlot(int)
	def set_value(self, value: int):
		self._value = value
		self._alen = (self._value / self._maximum) * 180
		self._a = -(self._alen +180)
		self.update()

	value = pyqtProperty(int, get_value, set_value)

	def get_maximum(self):
		return self._maximum

	@pyqtSlot(int)
	def set_maximum(self, value: int):
		self._maximum = value
		self._alen = (self._value / self._maximum) * 180
		self._a = -(self._alen +180)
		self.update()

	maximum = pyqtProperty(int, get_maximum, set_maximum)

	def get_thickness(self):
		return self._thickness

	@pyqtSlot(int)
	def set_thickness(self, value: int):
		self._thickness = value
		self._circular_size = (self.width() - (self._thickness * 2)) if self.width() < self.height() else (
				self.height() - (self._thickness * 2))
		self.update()

	thickness = pyqtProperty(int, get_thickness, set_thickness)

	def get_color(self):
		return self._color

	@pyqtSlot(QColor)
	def set_color(self, color: QColor):
		self._color = color
		self.update()

	color = pyqtProperty(QColor, get_color, set_color)

	def get_bg_circle_color(self):
		return self._bg_circle_color

	@pyqtSlot(QColor)
	def set_bg_circle_color(self, color: QColor):
		self._bg_circle_color = color
		self.update()

	background_circle_color = pyqtProperty(QColor, get_bg_circle_color, set_bg_circle_color)

	def get_round_edge(self):
		return self._round_edge

	@pyqtSlot(bool)
	def set_round_edge(self, value: bool):
		self._round_edge = value
		self.update()

	round_edge = pyqtProperty(bool, get_round_edge, set_round_edge)

	def get_fill_bg_circle(self):
		return self._fill_bg_circle

	@pyqtSlot(bool)
	def set_fill_bg_circle(self, value: bool):
		self._fill_bg_circle = value
		self.update()

	fill_background_circle = pyqtProperty(bool, get_fill_bg_circle, set_fill_bg_circle)
