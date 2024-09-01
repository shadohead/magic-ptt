import sys
import pyaudio
import numpy as np
from pynput import keyboard
from collections import deque
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QPushButton, QLabel, QSlider, QProgressBar, QStatusBar, QCheckBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import configparser
import os
import time
import win32api
import win32con
from PyQt6.QtWidgets import QLabel



class ColorProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 10px;
                text-align: center;
                background-color: #333;
                height: 15px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4caf50, stop:0.5 #ffeb3b, stop:1 #f44336);
                border-radius: 10px;
            }
        """)

class MagicPTTApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magic Push-to-Talk")
        self.setGeometry(100, 100, 400, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(15)  # Add more space between widgets

        self.config = configparser.ConfigParser()
        self.config_file = 'magic_ptt_config.ini'

        self.setup_ui()
        self.setup_audio()
        self.load_config()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_audio)
        self.is_running = False
        self.is_calibrating = False
        self.calibration_samples = 0
        self.calibration_total = 100  # Number of samples for calibration

        self.ptt_key = 0x56  # Virtual key code for 'V'
        self.ptt_active = False

        self.test_mode = False
        self.last_active_time = 0


    def setup_ui(self):
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Mic selection
        self.mic_combo = QComboBox()
        self.layout.addWidget(self.create_label("Select Microphone:"))
        self.layout.addWidget(self.mic_combo)

        # Push-to-talk key selection
        self.ptt_key_button = self.create_button("Set Push-to-Talk Key (current: V)")
        self.ptt_key_button.clicked.connect(self.capture_ptt_key)
        self.layout.addWidget(self.ptt_key_button)

        # Threshold offset slider
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(5, 20)
        self.threshold_slider.setValue(10)
        self.threshold_label = self.create_label("Threshold Offset: 10 dB")
        self.layout.addWidget(self.threshold_label)
        self.layout.addWidget(self.threshold_slider)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)

        # Timeout duration slider
        self.timeout_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeout_slider.setRange(0, 2000)  # 0 to 2000 ms
        self.timeout_slider.setValue(500)  # Default 500 ms
        self.timeout_label = self.create_label("Release Delay Duration: 500 ms")
        self.layout.addWidget(self.timeout_label)
        self.layout.addWidget(self.timeout_slider)
        self.timeout_slider.valueChanged.connect(self.update_timeout_label)

        # Manual threshold mode
        self.manual_threshold_checkbox = self.create_checkbox("Use Manual Threshold")
        self.manual_threshold_checkbox.stateChanged.connect(self.toggle_manual_threshold)
        self.layout.addWidget(self.manual_threshold_checkbox)

        # Manual threshold slider
        self.manual_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.manual_threshold_slider.setRange(-60, 0)  # dB range
        self.manual_threshold_slider.setValue(-30)  # Default threshold
        self.manual_threshold_slider.setEnabled(False)
        self.manual_threshold_label = self.create_label("Manual Threshold: -30 dB")
        self.layout.addWidget(self.manual_threshold_label)
        self.layout.addWidget(self.manual_threshold_slider)
        self.manual_threshold_slider.valueChanged.connect(self.update_manual_threshold_label)

        # Start/Stop button
        self.start_stop_button = self.create_button("Start", primary=True)
        self.start_stop_button.clicked.connect(self.toggle_monitoring)
        self.layout.addWidget(self.start_stop_button)

        # Test Mode checkbox
        self.test_mode_checkbox = self.create_checkbox("Test Mode (No Key Press)")
        self.test_mode_checkbox.stateChanged.connect(self.toggle_test_mode)
        self.layout.addWidget(self.test_mode_checkbox)

        # Status message
        self.status_label = self.create_label("Ready to start", large=True)
        self.layout.addWidget(self.status_label)

        # Audio level display
        self.level_label = self.create_label("Current Level: N/A")
        self.threshold_display_label = self.create_label("Current Threshold: N/A")
        self.layout.addWidget(self.level_label)
        self.layout.addWidget(self.threshold_display_label)

        # Visual audio meter
        self.audio_meter = ColorProgressBar()
        self.audio_meter.setRange(-60, 0)  # Typical range for audio levels in dB
        self.layout.addWidget(self.create_label("Audio Level:"))
        self.layout.addWidget(self.audio_meter)

        # Threshold indicator
        self.threshold_indicator = QWidget()
        self.threshold_indicator.setFixedHeight(5)
        self.threshold_indicator.setStyleSheet("background-color: #ff5722;")
        self.layout.addWidget(self.threshold_indicator)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet("background-color: #333; color: #eee;")

    def create_label(self, text, large=False):
        label = QLabel(text)
        label.setStyleSheet("color: #eee;")
        if large:
            label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        return label

    def create_button(self, text, primary=False):
        button = QPushButton(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedHeight(40)
        if primary:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: #fff;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #388e3c;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #555;
                    color: #eee;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #666;
                }
                QPushButton:pressed {
                    background-color: #444;
                }
            """)
        return button

    def create_checkbox(self, text):
        checkbox = QCheckBox(text)
        checkbox.setStyleSheet("color: #eee;")
        checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        return checkbox

    def toggle_manual_threshold(self, state):
        manual_mode = bool(state)
        self.manual_threshold_slider.setEnabled(manual_mode)
        if manual_mode:
            self.statusBar.showMessage("Manual Threshold Mode Active")
        else:
            self.statusBar.showMessage("Automatic Threshold Mode Active")

    def update_manual_threshold_label(self):
        value = self.manual_threshold_slider.value()
        self.manual_threshold_label.setText(f"Manual Threshold: {value} dB")

    # Rest of the methods remain unchanged

    def setup_audio(self):
        self.p = pyaudio.PyAudio()
        self.update_mic_list()
        
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.WINDOW_DURATION = 5
        self.UPDATE_INTERVAL = 50  # ms, increased update frequency for smoother meter

        self.audio_levels = deque(maxlen=int(self.WINDOW_DURATION * self.RATE / self.CHUNK))
        self.threshold = None

    def update_mic_list(self):
        self.mic_combo.clear()
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                self.mic_combo.addItem(dev['name'], i)

    def update_threshold_label(self):
        value = self.threshold_slider.value()
        self.threshold_label.setText(f"Threshold Offset: {value} dB")

    def update_timeout_label(self):
        value = self.timeout_slider.value()
        self.timeout_label.setText(f"Release Delay Duration: {value} ms")

    def capture_ptt_key(self):
        self.ptt_key_button.setText("Press any key...")
        self.ptt_key_button.setEnabled(False)
        
        def on_press(key):
            try:
                if hasattr(key, 'vk'):
                    self.ptt_key = key.vk
                    key_name = key.char if hasattr(key, 'char') else key.name
                else:
                    self.ptt_key = key.value.vk
                    key_name = key.name
                self.ptt_key_button.setText(f"Set Push-to-Talk Key (current: {key_name})")
            except AttributeError:
                self.ptt_key_button.setText(f"Set Push-to-Talk Key (current: {key})")
            self.ptt_key_button.setEnabled(True)
            return False  # Stop listener

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def toggle_monitoring(self):
        if self.is_running:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        device_index = self.mic_combo.currentData()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  input_device_index=device_index,
                                  frames_per_buffer=self.CHUNK)
        self.timer.start(self.UPDATE_INTERVAL)
        self.is_running = True
        self.start_stop_button.setText("Stop")
        
        if self.manual_threshold_checkbox.isChecked():
            self.threshold = self.manual_threshold_slider.value()
            self.status_label.setText(f"Monitoring audio... Manual Threshold: {self.threshold:.2f} dB")
            self.statusBar.showMessage("Monitoring with Manual Threshold")
        else:
            if self.threshold is None:
                self.is_calibrating = True
                self.calibration_samples = 0
                self.status_label.setText("Calibrating noise floor... Please remain silent.")
                self.statusBar.showMessage("Calibrating...")
            else:
                self.status_label.setText("Monitoring audio...")
                self.statusBar.showMessage("Monitoring")

    def stop_monitoring(self):
        self.timer.stop()
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        self.is_running = False
        self.start_stop_button.setText("Start")
        self.status_label.setText("Monitoring stopped")
        self.statusBar.showMessage("Stopped")

    def toggle_test_mode(self, state):
        self.test_mode = bool(state)
        if self.test_mode:
            self.statusBar.showMessage("Test Mode Active - No Key Press")
        else:
            self.statusBar.showMessage("Normal Mode - Key Press Active")

    def get_audio_level(self, data):
        data_float = data.astype(float)
        normalized = np.abs(data_float) / 32768.0
        rms = np.sqrt(np.mean(normalized**2))
        db = 20 * np.log10(max(rms, 1e-10))
        return db

    def update_threshold(self):
        if self.threshold is None:
            return None
        noise_floor = np.median(self.audio_levels)
        return noise_floor + self.threshold_slider.value()

    def update_audio(self):
        data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
        db_level = self.get_audio_level(data)
        self.audio_levels.append(db_level)
        
        if self.manual_threshold_checkbox.isChecked():
            self.threshold = self.manual_threshold_slider.value()
        elif self.is_calibrating:
            self.calibration_samples += 1
            if self.calibration_samples >= self.calibration_total:
                self.threshold = np.median(self.audio_levels) + self.threshold_slider.value()
                self.is_calibrating = False
                self.status_label.setText("Calibration complete. Monitoring audio...")
                self.statusBar.showMessage("Monitoring")
            else:
                progress = int((self.calibration_samples / self.calibration_total) * 100)
                self.statusBar.showMessage(f"Calibrating... {progress}%")
        else:
            self.threshold = self.update_threshold()
        
        self.level_label.setText(f"Current Level: {db_level:.2f} dB")
        if self.threshold is not None:
            self.threshold_display_label.setText(f"Current Threshold: {self.threshold:.2f} dB")
        
        # Update audio meter
        self.audio_meter.setValue(int(db_level))
        
        # Update threshold indicator position
        if self.threshold is not None:
            meter_width = self.audio_meter.width()
            threshold_pos = int((self.threshold - self.audio_meter.minimum()) / (self.audio_meter.maximum() - self.audio_meter.minimum()) * meter_width)
            self.threshold_indicator.setFixedWidth(threshold_pos)
        
        current_time = time.time()
        timeout_duration = self.timeout_slider.value() / 1000  # Convert ms to seconds

        if self.threshold is not None and db_level > self.threshold:
            self.last_active_time = current_time
            if not self.test_mode and not self.ptt_active:
                win32api.keybd_event(self.ptt_key, 0, 0, 0)
                self.ptt_active = True
            self.status_label.setText("Voice detected!" + (" (Test Mode - No Key Press)" if self.test_mode else " Push-to-Talk activated."))
        elif current_time - self.last_active_time < timeout_duration:
            # Keep PTT active during timeout period
            if not self.test_mode and not self.ptt_active:
                win32api.keybd_event(self.ptt_key, 0, 0, 0)
                self.ptt_active = True
            self.status_label.setText("Timeout active" + (" (Test Mode - No Key Press)" if self.test_mode else " - Push-to-Talk still on."))
        else:
            if self.ptt_active and not self.test_mode:
                win32api.keybd_event(self.ptt_key, 0, win32con.KEYEVENTF_KEYUP, 0)
                self.ptt_active = False
            if not self.is_calibrating:
                self.status_label.setText("Monitoring audio..." + (" (Test Mode)" if self.test_mode else ""))

    def save_config(self):
        self.config['Settings'] = {
            'microphone': self.mic_combo.currentText(),
            'ptt_key': str(self.ptt_key),
            'threshold_offset': str(self.threshold_slider.value()),
            'threshold': str(self.threshold) if self.threshold is not None else '',
            'test_mode': str(self.test_mode),
            'timeout_duration': str(self.timeout_slider.value()),
            'manual_threshold': str(self.manual_threshold_checkbox.isChecked()),
            'manual_threshold_value': str(self.manual_threshold_slider.value())
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        print("Configuration saved.")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
                if 'Settings' in self.config:
                    settings = self.config['Settings']
                    
                    # Set microphone
                    mic_name = settings.get('microphone', '')
                    mic_index = self.mic_combo.findText(mic_name)
                    if mic_index >= 0:
                        self.mic_combo.setCurrentIndex(mic_index)
                    else:
                        print(f"Configured microphone '{mic_name}' not found. Using default.")
                    
                    # Set PTT key
                    try:
                        self.ptt_key = int(settings.get('ptt_key', '0x56'), 0)
                    except ValueError:
                        print(f"Invalid ptt_key value in config: {settings.get('ptt_key')}. Using default.")
                        self.ptt_key = 0x56  # Default to 'V'

                    key_name = self.get_key_name(self.ptt_key)
                    self.ptt_key_button.setText(f"Set Push-to-Talk Key (current: {key_name})")
                    
                    # Set threshold offset
                    try:
                        threshold_offset = int(settings.get('threshold_offset', '10'))
                        if 5 <= threshold_offset <= 20:
                            self.threshold_slider.setValue(threshold_offset)
                        else:
                            print(f"Threshold offset {threshold_offset} out of range (5-20). Using default.")
                            self.threshold_slider.setValue(10)
                    except ValueError:
                        print(f"Invalid threshold_offset value: {settings.get('threshold_offset')}. Using default.")
                        self.threshold_slider.setValue(10)
                    self.update_threshold_label()
                    
                    # Set threshold
                    threshold_str = settings.get('threshold', '')
                    if threshold_str:
                        try:
                            self.threshold = float(threshold_str)
                        except ValueError:
                            print(f"Invalid threshold value: {threshold_str}. Will calibrate on start.")
                            self.threshold = None
                    else:
                        self.threshold = None
                    
                    # Load test mode state
                    self.test_mode = settings.getboolean('test_mode', False)
                    self.test_mode_checkbox.setChecked(self.test_mode)

                    # Load timeout duration
                    try:
                        timeout_duration = int(settings.get('timeout_duration', '500'))
                        if 0 <= timeout_duration <= 2000:
                            self.timeout_slider.setValue(timeout_duration)
                        else:
                            print(f"Timeout duration {timeout_duration} out of range (0-2000). Using default.")
                            self.timeout_slider.setValue(500)
                    except ValueError:
                        print(f"Invalid timeout_duration value: {settings.get('timeout_duration')}. Using default.")
                        self.timeout_slider.setValue(500)
                    self.update_timeout_label()

                    # Load manual threshold settings
                    manual_threshold = settings.getboolean('manual_threshold', False)
                    self.manual_threshold_checkbox.setChecked(manual_threshold)
                    if manual_threshold:
                        self.manual_threshold_slider.setEnabled(True)
                        try:
                            manual_threshold_value = int(settings.get('manual_threshold_value', '-30'))
                            if -60 <= manual_threshold_value <= 0:
                                self.manual_threshold_slider.setValue(manual_threshold_value)
                            else:
                                print(f"Manual threshold value {manual_threshold_value} out of range (-60 to 0 dB). Using default.")
                                self.manual_threshold_slider.setValue(-30)
                        except ValueError:
                            print(f"Invalid manual_threshold_value: {settings.get('manual_threshold_value')}. Using default.")
                            self.manual_threshold_slider.setValue(-30)
                        self.update_manual_threshold_label()
                
                print("Configuration loaded successfully.")
                self.status_label.setText("Configuration loaded. Ready to start.")
            except Exception as e:
                print(f"Error loading configuration: {str(e)}")
                self.status_label.setText("Error loading configuration. Using default settings.")
        else: 
            print("No configuration file found. Using default settings.")
            self.status_label.setText("No saved configuration. Will calibrate on start.")

    def get_key_name(self, key_code):
        """Convert a key code to a readable name."""
        if 32 <= key_code <= 126:
            return chr(key_code)
        for name, value in vars(win32con).items():
            if name.startswith('VK_') and value == key_code:
                return name[3:]
        return f"Unknown ({key_code})"
    
    def closeEvent(self, event):
        self.stop_monitoring()
        self.save_config()  # Automatically save config on exit
        self.p.terminate()
        super().closeEvent(event)  # Call the base class closeEvent

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MagicPTTApp()
    window.show()
    sys.exit(app.exec())
