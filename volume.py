import sys
import pulsectl
import pyaudio
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QComboBox, QHBoxLayout, QPushButton
import pyqtgraph as pg
from pyqtgraph import PlotWidget

class VolumeControl(QWidget):
    def __init__(self):
        super().__init__()

        self.pulse = pulsectl.Pulse('volume-control')
        self.sinks = self.pulse.sink_list()
        self.sources = self.pulse.source_list()

        self.selected_sink = self.sinks[0] if self.sinks else None
        self.selected_source = self.sources[0] if self.sources else None

        self.init_ui()

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)  # Update every 50 ms

    def init_ui(self):
        self.setWindowTitle('Volume Control')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #222;")

        layout = QVBoxLayout()

        self.sink_combo = QComboBox()
        self.sink_combo.setStyleSheet("font-size: 14px; color: white;")
        self.sink_combo.currentIndexChanged.connect(self.select_sink)
        for sink in self.sinks:
            self.sink_combo.addItem(sink.description, sink)
        layout.addWidget(self.sink_combo)

        self.output_slider = QSlider(Qt.Horizontal)
        self.output_slider.setRange(0, 100)
        self.output_slider.setValue(int(self.selected_sink.volume.value_flat * 100))
        self.output_slider.setStyleSheet(
            "QSlider::groove:horizontal { background-color: #444; height: 8px; border: none; }"
            "QSlider::handle:horizontal { background-color: gold; width: 16px; border: none; }"
        )
        self.output_slider.valueChanged.connect(self.set_output_volume)
        layout.addWidget(self.output_slider)

        self.output_label = QLabel(f'Audio Output Volume: {self.selected_sink.volume.value_flat:.0%}')
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setStyleSheet("color: gold; font-size: 16px;")
        layout.addWidget(self.output_label)

        self.source_combo = QComboBox()
        self.source_combo.setStyleSheet("font-size: 14px; color: white;")
        self.source_combo.currentIndexChanged.connect(self.select_source)
        for source in self.sources:
            self.source_combo.addItem(source.description, source)
        layout.addWidget(self.source_combo)

        self.input_slider = QSlider(Qt.Horizontal)
        self.input_slider.setRange(0, 100)
        self.input_slider.setValue(int(self.selected_source.volume.value_flat * 100))
        self.input_slider.setStyleSheet(
            "QSlider::groove:horizontal { background-color: #444; height: 8px; border: none; }"
            "QSlider::handle:horizontal { background-color: gold; width: 16px; border: none; }"
        )
        self.input_slider.valueChanged.connect(self.set_input_volume)
        layout.addWidget(self.input_slider)

        self.input_label = QLabel(f'microphone sensitivity: {self.selected_source.volume.value_flat:.0%}')
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.setStyleSheet("color: gold; font-size: 16px;")
        layout.addWidget(self.input_label)

        self.plot_widget = PlotWidget()
        self.plot_widget.setYRange(-30000, 30000)
        self.plot_widget.setBackground('#222')
        self.plot_data = self.plot_widget.plot(pen=pg.mkPen('y', width=2))
        layout.addWidget(self.plot_widget)

        controls_layout = QHBoxLayout()

        self.y_range_slider = QSlider(Qt.Horizontal)
        self.y_range_slider.setRange(5000, 50000)
        self.y_range_slider.setValue(30000)
        self.y_range_slider.setStyleSheet(
            "QSlider::groove:horizontal { background-color: #444; height: 8px; border: none; }"
            "QSlider::handle:horizontal { background-color: gold; width: 16px; border: none; }"
        )
        self.y_range_slider.valueChanged.connect(self.adjust_y_range)
        controls_layout.addWidget(QLabel("Y-Range:"))
        controls_layout.addWidget(self.y_range_slider)

        self.db_label = QLabel('Level: 0 dB')
        self.db_label.setAlignment(Qt.AlignCenter)
        self.db_label.setStyleSheet("color: gold; font-size: 16px;")
        controls_layout.addWidget(self.db_label)

        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def select_sink(self, index):
        self.selected_sink = self.sinks[index]
        self.output_slider.setValue(int(self.selected_sink.volume.value_flat * 100))
        self.output_label.setText(f'Volume: {self.selected_sink.volume.value_flat:.0%}')

    def set_output_volume(self, value):
        if self.selected_sink:
            volume = min(max(0.0, value / 100.0), 1.0)
            self.pulse.volume_set_all_chans(self.selected_sink, volume)
            self.output_label.setText(f'Audio Output Volume: {volume:.0%}')

    def select_source(self, index):
        self.selected_source = self.sources[index]
        self.input_slider.setValue(int(self.selected_source.volume.value_flat * 100))
        self.input_label.setText(f'Audio Volume: {self.selected_source.volume.value_flat:.0%}')

    def set_input_volume(self, value):
        if self.selected_source:
            volume = min(max(0.0, value / 100.0), 1.0)
            self.pulse.volume_set_all_chans(self.selected_source, volume)
            self.input_label.setText(f'microphone sensitivity: {volume:.0%}')

    def update_plot(self):
        try:
            data = self.stream.read(1024, exception_on_overflow=False)
            data_int = np.frombuffer(data, dtype=np.int16)
            self.plot_data.setData(data_int)

            # Update the dB level
            rms = np.sqrt(np.mean(data_int**2))
            db = 20 * np.log10(rms) if rms > 0 else -np.inf
            self.db_label.setText(f'Level: {db:.2f} dB')
        except IOError as e:
            print(f"Error reading audio stream: {e}")

    def adjust_y_range(self, value):
        self.plot_widget.setYRange(-value, value)

    def closeEvent(self, event):
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VolumeControl()
    window.show()
    sys.exit(app.exec_())
