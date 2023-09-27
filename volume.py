import sys
import os
import pulsectl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton, QComboBox

class VolumeControl(QWidget):
    def __init__(self):
        super().__init__()

        self.pulse = pulsectl.Pulse('volume-control')  # Create a PulseAudio context
        self.sinks = self.pulse.sink_list()  # Get a list of audio output sinks
        self.sources = self.pulse.source_list()  # Get a list of audio input sources

        self.selected_sink = self.sinks[0] if self.sinks else None
        self.selected_source = self.sources[0] if self.sources else None

        # Initialize attributes
        self.output_slider = None
        self.output_label = None
        self.input_slider = None
        self.input_label = None

        self.init_ui()

    def init_ui(self):
        # Configure the main window
        self.setWindowTitle('Volume Control')
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #222;")

        # Create a layout
        layout = QVBoxLayout()

        # Output Sink Combo Box
        self.sink_combo = QComboBox()
        self.sink_combo.setStyleSheet("font-size: 14px; color: white;")
        self.sink_combo.currentIndexChanged.connect(self.select_sink)
        for sink in self.sinks:
            self.sink_combo.addItem(sink.description, sink)
        layout.addWidget(self.sink_combo)

        # Volume slider for the selected output sink
        self.output_slider = QSlider(Qt.Horizontal)
        self.output_slider.setRange(0, 100)
        self.output_slider.setValue(int(self.selected_sink.volume.value_flat * 100))
        self.output_slider.setStyleSheet(
            "QSlider::groove:horizontal { background-color: #444; height: 8px; border: none; }"
            "QSlider::handle:horizontal { background-color: gold; width: 16px; border: none; }"
        )
        self.output_slider.valueChanged.connect(self.set_output_volume)
        layout.addWidget(self.output_slider)

        # Volume label for the selected output sink
        self.output_label = QLabel(f'Volume: {self.selected_sink.volume.value_flat:.0%}')
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setStyleSheet("color: gold; font-size: 16px;")
        layout.addWidget(self.output_label)

        # Input Source Combo Box
        self.source_combo = QComboBox()
        self.source_combo.setStyleSheet("font-size: 14px; color: white;")
        self.source_combo.currentIndexChanged.connect(self.select_source)
        for source in self.sources:
            self.source_combo.addItem(source.description, source)
        layout.addWidget(self.source_combo)

        # Volume slider for the selected input source
        self.input_slider = QSlider(Qt.Horizontal)
        self.input_slider.setRange(0, 100)
        self.input_slider.setValue(int(self.selected_source.volume.value_flat * 100))
        self.input_slider.setStyleSheet(
            "QSlider::groove:horizontal { background-color: #444; height: 8px; border: none; }"
            "QSlider::handle:horizontal { background-color: gold; width: 16px; border: none; }"
        )
        self.input_slider.valueChanged.connect(self.set_input_volume)
        layout.addWidget(self.input_slider)

        # Volume label for the selected input source
        self.input_label = QLabel(f'Volume: {self.selected_source.volume.value_flat:.0%}')
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.setStyleSheet("color: gold; font-size: 16px;")
        layout.addWidget(self.input_label)

        # Microphone input strength indicator (light)
        self.input_light = QLabel()
        self.input_light.setFixedSize(24, 24)
        self.input_light.setStyleSheet("background-color: red; border-radius: 12px;")
        layout.addWidget(self.input_light, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def select_sink(self, index):
        self.selected_sink = self.sinks[index]
        if self.output_slider:
            self.output_slider.setValue(int(self.selected_sink.volume.value_flat * 100))
        if self.output_label:
            self.output_label.setText(f'Volume: {self.selected_sink.volume.value_flat:.0%}')

    def set_output_volume(self, value):
        if self.selected_sink:
            # Calculate left and right channel volumes
            volume = min(max(0.0, value / 100.0), 1.0)
            self.pulse.volume_set_all_chans(self.selected_sink, volume)
            if self.output_label:
                self.output_label.setText(f'Volume: {volume:.0%}')

    def select_source(self, index):
        self.selected_source = self.sources[index]
        if self.input_slider:
            self.input_slider.setValue(int(self.selected_source.volume.value_flat * 100))
        if self.input_label:
            self.input_label.setText(f'Volume: {self.selected_source.volume.value_flat:.0%}')

    def set_input_volume(self, value):
        if self.selected_source:
            # Calculate left and right channel volumes
            volume = min(max(0.0, value / 100.0), 1.0)
            self.pulse.volume_set_all_chans(self.selected_source, volume)
            if self.input_label:
                self.input_label.setText(f'Volume: {volume:.0%}')

            # Update microphone input strength indicator (light)
            input_strength = int(volume * 255)
            self.input_light.setStyleSheet(f"background-color: rgb({255 - input_strength}, {input_strength}, 0);")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VolumeControl()
    window.show()
    sys.exit(app.exec_())
