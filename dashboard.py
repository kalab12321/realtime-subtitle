from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QComboBox, QLineEdit, 
                             QTabWidget, QSpinBox, QDoubleSpinBox, QGridLayout,
                             QScrollArea, QSizePolicy, QSpacerItem, QFormLayout, QApplication)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QColor
import sys
import sounddevice as sd
from config import config

# Modern QSS Styles
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Helvetica Neue', 'Segoe UI', Arial, sans-serif;
}
QTabWidget::pane {
    border: 1px solid #313244;
    background: #1e1e2e;
    border-radius: 8px;
}
QTabBar::tab {
    background: #313244;
    color: #a6adc8;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
}
QLabel {
    font-size: 14px;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px;
    color: #cdd6f4;
    selection-background-color: #585b70;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton#StopButton {
    background-color: #f38ba8;
}
QPushButton#StopButton:hover {
    background-color: #eba0ac;
}
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #fab387;
}
"""

class Dashboard(QWidget):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def closeEvent(self, event):
        """Ensure total program quit when dashboard is closed"""
        self.status_label.setText("Stopping...")
        self.on_stop()
        # Force application exit
        QApplication.quit()
        event.accept()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Translator - Control Center")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(STYLESHEET)
        
        # Main Layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)
        
        # Header
        header = QLabel("🎙️ Real-Time Translator")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #89b4fa;")
        self.layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.init_home_tab()
        self.init_audio_tab()
        self.init_transcription_tab()
        self.init_translation_tab()
        
        # Footer Actions
        footer = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_config)
        self.save_btn.setStyleSheet("""
            background-color: #a6e3a1; color: #1e1e2e;
        """)
        footer.addStretch()
        footer.addWidget(self.save_btn)
        self.layout.addLayout(footer)

    def init_home_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 18px; color: #a6e3a1;")
        layout.addWidget(self.status_label)
        
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Launch Translator")
        self.start_btn.setFixedSize(200, 60)
        self.start_btn.setStyleSheet("font-size: 16px; background-color: #89b4fa; border-radius: 10px;")
        self.start_btn.clicked.connect(self.on_start)
        
        self.stop_btn = QPushButton("⏹ Stop Translator")
        self.stop_btn.setFixedSize(200, 60)
        self.stop_btn.setStyleSheet("font-size: 16px; background-color: #f38ba8; border-radius: 10px;")
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.hide()
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        
        info = QLabel("The translator will open as an overlay window.\nYou can minimize this dashboard.")
        info.setStyleSheet("color: #6c7086; font-style: italic;")
        layout.addWidget(info)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🏠 Home")

    def init_audio_tab(self):
        tab = QWidget()
        layout = QGridLayout() # Use Grid for organized form
        layout.setSpacing(15)
        
        # Device Selection
        layout.addWidget(QLabel("Input Device:"), 0, 0)
        self.device_combo = QComboBox()
        self.populate_devices()
        layout.addWidget(self.device_combo, 0, 1)
        
        # Refresh Button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedWidth(40)
        refresh_btn.clicked.connect(self.populate_devices)
        layout.addWidget(refresh_btn, 0, 2)
        
        # Sample Rate
        layout.addWidget(QLabel("Sample Rate:"), 1, 0)
        self.sample_rate = QSpinBox()
        self.sample_rate.setRange(8000, 48000)
        self.sample_rate.setValue(config.sample_rate)
        layout.addWidget(self.sample_rate, 1, 1)

        # Silence Threshold
        layout.addWidget(QLabel("Silence Threshold:"), 2, 0)
        self.silence_thresh = QDoubleSpinBox()
        self.silence_thresh.setRange(0.001, 1.0)
        self.silence_thresh.setSingleStep(0.001)
        self.silence_thresh.setDecimals(3)
        self.silence_thresh.setValue(config.silence_threshold)
        layout.addWidget(self.silence_thresh, 2, 1)
        
        layout.addWidget(QLabel("Silence Duration (s):"), 3, 0)
        self.silence_dur = QDoubleSpinBox()
        self.silence_dur.setValue(config.silence_duration)
        layout.addWidget(self.silence_dur, 3, 1)
        
        layout.setRowStretch(4, 1) # Push to top
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🎤 Audio")

    def init_transcription_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        self.whisper_model = QComboBox()
        self.whisper_model.addItems(["tiny", "base", "small", "medium", "large-v3", "turbo"])
        self.whisper_model.setCurrentText(config.whisper_model)
        layout.addRow("Whisper Model:", self.whisper_model)
        
        self.device_type = QComboBox()
        self.device_type.addItems(["cpu", "cuda", "mps", "auto"])
        self.device_type.setCurrentText(config.whisper_device)
        layout.addRow("Compute Device:", self.device_type)
        
        self.compute_type = QComboBox()
        self.compute_type.addItems(["int8", "float16", "float32"])
        self.compute_type.setCurrentText(config.whisper_compute_type)
        layout.addRow("Quantization:", self.compute_type)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "📝 Transcription")

    def init_translation_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        self.api_key = QLineEdit(config.api_key)
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-...")
        layout.addRow("API Key:", self.api_key)
        
        self.base_url = QLineEdit(config.api_base_url or "")
        self.base_url.setPlaceholderText("https://api.openai.com/v1")
        layout.addRow("Base URL:", self.base_url)
        
        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.addItem(config.model)
        layout.addRow("Model:", self.model)
        
        self.target_lang = QComboBox()
        self.target_lang.addItems(["Chinese", "English", "Japanese", "French", "Spanish", "German", "Korean"])
        self.target_lang.setEditable(True)
        self.target_lang.setCurrentText(config.target_lang)
        layout.addRow("Target Language:", self.target_lang)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🈵 Translation")

    def populate_devices(self):
        self.device_combo.clear()
        self.device_combo.addItem("Auto (Default)", "auto")
        
        try:
            devices = sd.query_devices()
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0:
                    name = f"[{i}] {d['name']}"
                    self.device_combo.addItem(name, i) # Store index as data
            
            # Select current
            if config.device_index is not None:
                index = self.device_combo.findData(config.device_index)
                if index >= 0:
                    self.device_combo.setCurrentIndex(index)
        except Exception as e:
            self.device_combo.addItem(f"Error: {e}")

    def save_config(self):
        import configparser
        import os
        
        # Update config object logic would go here, 
        # For now, we write directly to config.ini similarly to settings_window.py
        
        cp = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        cp.read(config_path)
        
        if not cp.has_section("audio"): cp.add_section("audio")
        if not cp.has_section("api"): cp.add_section("api")
        if not cp.has_section("translation"): cp.add_section("translation")
        if not cp.has_section("transcription"): cp.add_section("transcription")
        
        # Audio
        idx = self.device_combo.currentData()
        cp.set("audio", "device_index", str(idx) if idx is not None else "auto")
        cp.set("audio", "sample_rate", str(self.sample_rate.value()))
        cp.set("audio", "silence_threshold", str(self.silence_thresh.value()))
        cp.set("audio", "silence_duration", str(self.silence_dur.value()))
        
        # Transcription
        cp.set("transcription", "whisper_model", self.whisper_model.currentText())
        cp.set("transcription", "device", self.device_type.currentText())
        cp.set("transcription", "compute_type", self.compute_type.currentText())
        
        # Translation
        cp.set("api", "api_key", self.api_key.text())
        cp.set("api", "base_url", self.base_url.text())
        cp.set("translation", "model", self.model.currentText())
        cp.set("translation", "target_lang", self.target_lang.currentText())
        
        with open(config_path, 'w') as f:
            cp.write(f)
            
        self.status_label.setText("Saved! Please restart.")

    def on_start(self):
        # 1. Update UI to Loading State
        self.status_label.setText("Initializing Pipeline... (This may take a moment)")
        self.status_label.setStyleSheet("font-size: 18px; color: #fab387;") # Orange for loading
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Loading...")
        
        # 2. Start Worker Thread
        from PyQt6.QtCore import QThread, pyqtSignal
        self.startup_worker = StartupWorker()
        self.startup_worker.finished.connect(self.on_pipeline_ready)
        self.startup_worker.start()

    def on_pipeline_ready(self, _, pipeline):
        # Create Window on Main Thread
        from main import OverlayWindow
        from config import config
        
        if not pipeline:
             self.status_label.setText("Initialization Failed Check Console")
             self.start_btn.setEnabled(True)
             self.start_btn.setText("▶ Launch Translator")
             return

        self.pipeline = pipeline
        self.overlay_window = OverlayWindow(
            display_duration=config.display_duration,
            window_width=config.window_width
        )
        self.overlay_window.show()

        # Connect Signals
        self.pipeline.signals.update_text.connect(self.overlay_window.update_text)
        if hasattr(self.overlay_window, 'stop_requested'):
             self.overlay_window.stop_requested.connect(self.on_stop)

        # Start Pipeline Thread
        self.pipeline.start()

        self.status_label.setText("Running...")
        self.status_label.setStyleSheet("font-size: 18px; color: #a6e3a1;")
        
        self.start_btn.hide()
        self.stop_btn.show()
        
        self.showMinimized()

    def on_stop(self):
        if hasattr(self, 'pipeline') and self.pipeline:
            self.pipeline.stop()
            self.pipeline = None
            
        if hasattr(self, 'overlay_window') and self.overlay_window:
            self.overlay_window.close()
            self.overlay_window = None
            
        self.status_label.setText("Stopped")
        self.stop_btn.hide()
        self.start_btn.show()
        self.start_btn.setEnabled(True)
        self.start_btn.setText("▶ Launch Translator")
        self.showNormal()

class StartupWorker(QThread):
    finished = pyqtSignal(object, object) # window(None), pipeline

    def run(self):
        try:
            from main import Pipeline
            pipeline = Pipeline()
            self.finished.emit(None, pipeline)
        except Exception as e:
            print(f"Startup Error: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit(None, None)

if __name__ == "__main__":
    def exception_hook(exctype, value, traceback_obj):
        import traceback
        traceback_str = ''.join(traceback.format_tb(traceback_obj))
        error_msg = f"Unhandled Exception: {value}\n\n{traceback_str}"
        print(error_msg)
        from PyQt6.QtWidgets import QMessageBox
        if QApplication.instance():
            QMessageBox.critical(None, "Crash", error_msg)
        else:
            # If no app, just print (already done)
            pass
        sys.exit(1)

    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    w = Dashboard()
    w.show()
    sys.exit(app.exec())
