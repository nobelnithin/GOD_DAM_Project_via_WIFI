import sys
import openpyxl
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer, QRect
from datetime import datetime
import requests  

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create widgets
        self.username_label = QLabel('Username:', self)
        self.username_input = QLineEdit(self)

        self.password_label = QLabel('Password:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.handle_login)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

        # Window settings
        self.setWindowTitle('Login')
        self.resize(500, 300)

    def handle_login(self):
        # Hardcoded username and password for internal authentication
        valid_username = "admin"
        valid_password = "1234"

        username = self.username_input.text()
        password = self.password_input.text()

        if username == valid_username and password == valid_password:
            self.open_water_level_widget()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password.')

    def open_water_level_widget(self):
        self.water_level_widget = WaterLevelWidget()
        self.water_level_widget.show()
        self.close()  # Close the login window




class WaterLevelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ip_address = "http://192.168.4.1"  # Replace with your ESP32 IP address
        self.initExcel()

    def initUI(self):
        # Create widgets
        self.title_label = QLabel('WATER LEVEL MONITOR', self)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.sensor_label = QLabel('Sensor Reading: N/A', self)

        # Custom widget for water level
        self.water_level_widget = WaterLevelDisplay(self)

        self.settings_button = QPushButton('Open DAM Manually', self)
        self.settings_button.clicked.connect(self.send_toggle_command)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.sensor_label)
        layout.addWidget(self.water_level_widget)
        layout.addWidget(self.settings_button)
        self.setLayout(layout)

        # Window settings
        self.setWindowTitle('Water Level Monitor')
        self.resize(600, 400)

        # Timer to update sensor readings
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_sensor_reading)
        self.timer.start(1000)  # Update every second

    def initExcel(self):
        # Create or load the Excel file
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.sheet.title = "Water Levels"
        self.sheet.append(["Timestamp", "Water Level (%)"])  # Header row
        self.workbook.save("water_levels.xlsx")

    def send_toggle_command(self):
        # This would be the logic to send a command to the ESP32, if needed.
        pass

    def update_sensor_reading(self):
        try:
            response = requests.get(f"{self.ip_address}/")  # Fetch data from ESP32
            if response.status_code == 200:
                water_level = int(response.text.strip())  # Convert response to integer
                self.sensor_label.setText(f'Water Level: {water_level}%')
                self.water_level_widget.set_water_level(water_level)  # Update the water level display
                self.log_to_excel(water_level)  # Log to Excel
            else:
                self.sensor_label.setText('Failed to get data from ESP32')
        except requests.exceptions.RequestException as e:
            self.sensor_label.setText('Error: ' + str(e))

    def log_to_excel(self, water_level):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sheet.append([timestamp, water_level])  # Append new row
        self.workbook.save("water_levels.xlsx")  # Save changes to the file

    def closeEvent(self, event):
        event.accept()


class WaterLevelDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.water_level = 0  # Water level percentage

    def set_water_level(self, level):
        self.water_level = level
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw tank outline
        tank_rect = QRect(10, 10, width - 20, height - 20)  # Rectangular tank with padding
        painter.setPen(QColor(0, 0, 0))  # Black color for the outline
        painter.drawRect(tank_rect)  # Draw tank outline
        
        # Determine color based on the water level
        if self.water_level < 85:
            color = QColor(76, 175, 80)  # Green for water level less than 85%
        else:
            color = QColor(255, 0, 0)  # Red for water level 85% and above
        
        # Calculate water height as an integer
        water_height = int(tank_rect.height() * (self.water_level / 100))
        
        # Fill the inside of the tank with the color
        painter.fillRect(tank_rect.x() + 1, tank_rect.y() + (tank_rect.height() - water_height), 
                         tank_rect.width() - 1, water_height, color)  # Fill rectangle with color



if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_app = LoginApp()
    login_app.show()
    sys.exit(app.exec_())