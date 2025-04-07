import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QSlider, QMainWindow, QFrame, QSpacerItem, QSizePolicy
)

from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import QPainter, QPen, QBrush, QPixmap, QGuiApplication
import datetime
import pandas as pd
import math

class CrossWidget(QWidget):
    def __init__(self, size_cm=15):
        super().__init__()
        screen = QGuiApplication.primaryScreen()
        self.dpi = screen.physicalDotsPerInch()  # real DPI of the screen
        self.pixels_per_cm = self.dpi / 2.54
        size_in_pixels = int(self.pixels_per_cm * size_cm)  # 20 cm  # 10 cm
        self.setFixedSize(size_in_pixels, size_in_pixels)

        self.v_step = 0
        self.h_step = 0
        self.viewing_distance_cm = 30

    def angle_to_pixels(self, degrees):
        radians = math.radians(degrees)
        cm = math.tan(radians) * self.viewing_distance_cm
        return cm * self.pixels_per_cm

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate spacing based on 0.1° steps
        v_spacing = self.angle_to_pixels(self.v_step * 0.01)
        h_spacing = self.angle_to_pixels(self.h_step * 0.01)

        # Draw vertical dotted line
        pen = QPen(Qt.black, 3)
        if self.v_step == 0:
            pen.setStyle(Qt.SolidLine)
        else:
            pen.setDashPattern([1, v_spacing])
        painter.setPen(pen)
        center_x = self.width() // 2
        center_y = self.height() // 2
        painter.drawLine(center_x, center_y, center_x, 0)
        painter.drawLine(center_x, center_y, center_x, self.height())

        # Draw horizontal dotted line
        pen = QPen(Qt.black, 3)
        if self.h_step == 0:
            pen.setStyle(Qt.SolidLine)
        else:
            pen.setDashPattern([1, h_spacing])
        painter.setPen(pen)
        painter.drawLine(center_x, center_y, 0, center_y)
        painter.drawLine(center_x, center_y, self.width(), center_y)

        # Draw central fixation point (3x dot size)
        dot_radius = 5
        painter.setBrush(QBrush(Qt.red))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            int(self.width() // 2 - dot_radius * 1.5),
            int(self.height() // 2 - dot_radius * 1.5),
            int(dot_radius * 3),
            int(dot_radius * 3)
        )

class MChartApp(QMainWindow):        

    def __init__(self):
        super().__init__()
        self.init_main_ui()

    def init_main_ui(self):
        self.setWindowTitle("M-Chart Cross Simulator")
        
        # Initialize widgets here (cross, sliders, etc.)
        self.cross_widget = CrossWidget()  # Your cross and sliders setup
        self.setCentralWidget(self.cross_widget)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        
        self.cross = CrossWidget(size_cm=15)
        self.cross.setStyleSheet("background-color: white;")

        # Frame to contain and center the cross
        self.cross_container = QFrame()
        self.cross_container.setStyleSheet("background-color: white; border: 2px solid gray;")
        self.cross_container.setFrameStyle(QFrame.Box)
        self.cross_container.setLineWidth(2)
        cross_layout = QVBoxLayout()
        cross_layout.setContentsMargins(0, 0, 0, 0)
        cross_layout.addWidget(self.cross)
        self.cross_container.setLayout(cross_layout)
        self.logs = []

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Close + Toggle Fullscreen buttons (top-left)
        close_button = QPushButton("X")
        button_size = int(self.cross.pixels_per_cm * 0.6)
        close_button.setFixedSize(button_size, button_size)
        close_button.setStyleSheet("font-size: 20px; background-color: white; color: black; border: none;")
        close_button.clicked.connect(self.close)

        close_layout = QHBoxLayout()
        close_layout.addWidget(close_button)
        close_layout.addWidget(close_button)
        close_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(80)

        # Left vertical slider
        self.v_slider = QSlider(Qt.Vertical)
        self.v_slider.setMinimum(0)
        self.v_slider.setMaximum(200)
        self.v_slider.setValue(0)
        self.v_slider.setTickInterval(1)
        self.v_slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: gray;
                width: 8px;
                border-radius: 4px;
                border: none;
            }
            QSlider::handle:vertical {
                background: #2c3e50;
                height: 30px;
                margin: 0 -4px;
                border-radius: 6px;
                border: none;
            }
            QSlider::sub-page:vertical {
                background: #3498db;
                border-radius: 4px;
            }
        """)
        self.v_slider.valueChanged.connect(self.update_v_dash)
        v_slider_box = QFrame()
        v_slider_box.setFixedWidth(100)
        v_slider_box.setStyleSheet("background-color: lightgray; border: 2px solid gray;")
        v_slider_layout = QVBoxLayout()
        v_slider_layout.setAlignment(Qt.AlignCenter)
        v_slider_layout.setAlignment(Qt.AlignCenter)
        v_slider_label = QLabel("Vertical")
        v_slider_label.setStyleSheet("border: none;")
        v_slider_label.setAlignment(Qt.AlignCenter)
        v_slider_layout.addWidget(v_slider_label)
        self.v_value_label = QLabel("0.00°")
        self.v_value_label.setAlignment(Qt.AlignCenter)
        self.v_value_label.setStyleSheet("border: none;")
        v_slider_layout.addWidget(self.v_value_label)
        v_slider_layout.addWidget(self.v_slider)
        v_slider_box.setLayout(v_slider_layout)
        layout.addWidget(v_slider_box)

        # Center canvas
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        center_layout.addWidget(self.cross_container)

        #Confirm button
        self.confirm_button = QPushButton("Confirm Adjustment")
        self.confirm_button.setStyleSheet(
            "background-color: white; color: black; font-size: 16px; padding: 8px 16px;"
                )
        self.score_label = QLabel("Score: V 0.0 | H 0.0")
        self.score_label.setStyleSheet("color: white; font-size: 18px;")
        self.score_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.score_label)
        self.confirm_button.clicked.connect(self.record_adjustment)
        center_layout.addWidget(self.confirm_button)

        layout.addLayout(center_layout)
        center_layout.addSpacing(5)

        # Right horizontal slider (rotated)
        self.h_slider = QSlider(Qt.Vertical)
        self.h_slider.setMinimum(0)
        self.h_slider.setMaximum(200)
        self.h_slider.setValue(0)
        self.h_slider.setTickInterval(1)
        self.h_slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: gray;
                width: 8px;
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background: #2c3e50;
                height: 30px;
                margin: 0 -4px;
                border-radius: 6px;
            }
            QSlider::sub-page:vertical {
                background: #3498db;
                border-radius: 4px;
            }
        """)
        self.h_slider.valueChanged.connect(self.update_h_dash)
        h_slider_box = QFrame()
        h_slider_box.setFixedWidth(100)
        h_slider_box.setStyleSheet("background-color: lightgray; border: 2px solid gray;")
        h_slider_layout = QVBoxLayout()
        h_slider_layout.setAlignment(Qt.AlignCenter)
        h_slider_layout.setAlignment(Qt.AlignCenter)
        h_slider_label = QLabel("Horizontal")
        h_slider_label.setStyleSheet("border: none;")
        h_slider_label.setAlignment(Qt.AlignCenter)
        h_slider_layout.addWidget(h_slider_label)
        self.h_value_label = QLabel("0.00°")
        self.h_value_label.setAlignment(Qt.AlignCenter)
        self.h_value_label.setStyleSheet("border: none;")
        h_slider_layout.addWidget(self.h_value_label)
        h_slider_layout.addWidget(self.h_slider)
        h_slider_box.setLayout(h_slider_layout)
        layout.addWidget(h_slider_box)

        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addLayout(close_layout)
        main_layout.addLayout(layout)
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

    def update_v_dash(self, value):
        self.cross.v_step = value
        self.v_value_label.setText(f"{value * 0.01:.2f}°")
        self.cross.update()

    def update_h_dash(self, value):
        self.cross.h_step = value
        self.h_value_label.setText(f"{value * 0.01:.2f}°")
        self.cross.update()

    def record_adjustment(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        v_angle = round(self.cross.v_step * 0.01, 2)
        h_angle = round(self.cross.h_step * 0.01, 2)
        v_score = round((2.0 - v_angle) * 50, 1)
        h_score = round((2.0 - h_angle) * 50, 1)
        self.logs.append({
            "Timestamp": timestamp,
            "Vertical Dash (°)": v_angle,
            "Vertical Score": v_score,
            "Horizontal Dash (°)": h_angle,
            "Horizontal Score": h_score
        })
        self.score_label.setText(f"Score: V {v_score:.1f} | H {h_score:.1f}")

        df = pd.DataFrame(self.logs)
        df.to_csv("mchart_logs.csv", index=False)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MChartApp()
    window.show()
    sys.exit(app.exec_())
