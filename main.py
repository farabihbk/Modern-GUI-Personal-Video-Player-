import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QSlider
)
from PyQt6.QtCore import QTimer, Qt
import vlc

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.filename = ""

        # Create a VLC instance and a media player.
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        # Flag to detect if slider is being moved manually.
        self.slider_is_pressed = False

        # Set up the main widget and layout.
        self.widget = QFrame(self)
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Create the video frame where VLC will render the video.
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background: black;")
        self.layout.addWidget(self.video_frame)

        # Create a horizontal layout for control buttons and progress slider.
        self.controls_layout = QHBoxLayout()
        self.layout.addLayout(self.controls_layout)

        # Open button: Open a video file.
        self.open_button = QPushButton("Open Video")
        self.open_button.clicked.connect(self.open_file)
        self.controls_layout.addWidget(self.open_button)

        # Pause button: Pause or resume video playback.
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        self.controls_layout.addWidget(self.pause_button)

        # Stop button: Stop video playback.
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_video)
        self.controls_layout.addWidget(self.stop_button)

        # Progress slider: Display and control the playback progress.
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        # Connect slider events for manual movement.
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        self.controls_layout.addWidget(self.progress_slider)

        # Timer to update the slider based on the video's current position.
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # Update every 100 milliseconds.
        self.timer.timeout.connect(self.update_ui)

    def open_file(self):
        # Open a file dialog to select a video file.
        self.filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if self.filename:
            media = self.instance.media_new(self.filename)
            self.mediaplayer.set_media(media)
            # Embed the VLC video output into our video frame.
            if sys.platform.startswith('linux'):
                self.mediaplayer.set_xwindow(self.video_frame.winId())
            elif sys.platform == "win32":
                self.mediaplayer.set_hwnd(self.video_frame.winId())
            elif sys.platform == "darwin":
                self.mediaplayer.set_nsobject(int(self.video_frame.winId()))
            self.mediaplayer.play()
            # Start the timer to update the progress slider.
            self.timer.start()

    def pause_video(self):
        # Pause or resume video playback.
        self.mediaplayer.pause()

    def stop_video(self):
        # Stop video playback and reset the progress slider.
        self.mediaplayer.stop()
        self.timer.stop()
        self.progress_slider.setValue(0)

    def slider_pressed(self):
        # Set the flag when the slider is being dragged manually.
        self.slider_is_pressed = True

    def slider_released(self):
        # Clear the flag when the slider is released.
        self.slider_is_pressed = False
        self.set_position()
        # If the slider was moved manually and the video isn't playing (ended or stopped),
        # start playing again.
        if self.progress_slider.value() < self.progress_slider.maximum() and not self.mediaplayer.is_playing():
            media = self.instance.media_new(self.filename)
            self.mediaplayer.set_media(media)
            self.mediaplayer.play()
            self.set_position()

    def set_position(self):
        # Seek to the position in the video based on the slider's value.
        pos = self.progress_slider.value() / 1000.0
        self.mediaplayer.set_position(pos)

    def update_ui(self):
        # Update the slider to reflect the current playback position.
        # Only update if the slider is not being moved manually.
        if self.mediaplayer.is_playing() and not self.slider_is_pressed:
            pos = self.mediaplayer.get_position()
            self.progress_slider.setValue(int(pos * 1000))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())