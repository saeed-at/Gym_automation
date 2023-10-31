from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QLineEdit, QCheckBox
from styles import label_style, line_edit_style, btn_style, checkbox_style, header_style, day_label_style
from checkbox_inputs import week_sessions
from PyQt5.QtWidgets import QGridLayout
from utils import encrypt_credentials, store_preferred_sessions
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class LoginWindow(QWidget):
    """
    Represents the login window for the gym auto reservation.
    User will type username and password related to his/her samad.aut.ac.ir's account.
    By clicking on the Next button the schedule page will show up.
    """
    def __init__(self):
        super().__init__()
        self.logo = None
        self.header = None
        self.username_input = None
        self.username_label = None
        self.password_input = None
        self.password_label = None
        self.next_button = None
        self.schedule_page = None
        self.init_ui()

    def init_ui(self):
        """
        Initializes the widgets for the main page and configures them.
        :return: None
        """
        # setting main page schema
        self.setWindowTitle("Configurations")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background: #000000;")


        # header configuration
        image = QPixmap("images_gui/cover.png")
        self.header = QLabel()
        self.header.setPixmap(image)
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.header.setStyleSheet(header_style)

        # logo configurations
        image = QPixmap("images_gui/logo.png")
        self.logo = QLabel()
        self.logo.setPixmap(image.scaled(200, 200))
        self.logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.logo.setStyleSheet("margin-bottom: 0px")
        self.logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        self.logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # username input and label configurations
        self.username_label = QLabel("Enter your username:")
        self.username_label.setStyleSheet(label_style)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(line_edit_style)
        # password input and label configurations
        self.password_label = QLabel("Enter your password:")
        self.password_label.setStyleSheet(label_style)
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(line_edit_style)
        self.password_input.setEchoMode(QLineEdit.Password)
        # next button configurations
        self.next_button = QPushButton("Proceed to Schedule")
        self.next_button.clicked.connect(self.show_schedule_page)
        self.next_button.setStyleSheet(btn_style)

        # adding widgets to the main page layout
        layout = QVBoxLayout()
        layout.addWidget(self.header)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.next_button)
        layout.addWidget(self.logo)
        layout.addStretch()

        self.setLayout(layout)

    def show_schedule_page(self):
        """
        By clicking on the next button on the main page, schedule page will show up with the method.
        :return: None
        """
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:
            self.hide()
            self.schedule_page = SchedulePage(username, password)
            self.schedule_page.show()


class SchedulePage(QWidget):
    """
    Represents the page for selecting preferred gym sessions.
    """
    def __init__(self, username, password):
        """
        Initializes schedule page according to the username and password received from the main page window.
        :param username: username for samad.aut.ac.ir
        :param password: password for samad.aut.ac.ir
        """
        super().__init__()
        self.username = username
        self.password = password
        self.schedule = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday', 'Sunday']}
        self.checkbox_dict = None
        self.done_button = None
        self.preferred_session = None
        self.checkbox_dict = {}
        self.preferred_session = {
            'saturday': [],
            'sunday': [],
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
        }
        self.init_ui()

    def init_ui(self):
        # schedule page main configurations
        self.setWindowTitle("Configurations")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background: #000000;")

        self.done_button = QPushButton("Done")
        self.done_button.setStyleSheet(btn_style)
        self.done_button.clicked.connect(self.save_schedule)

        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # show asking label to the users to choose preferred session.
        info_label = QLabel("Choose your preferred gym sessions:")
        info_label.setStyleSheet("color: #ffffff; margin-top: 0px;font-size: 35px;")
        layout.addWidget(info_label)
        # adding checkbox for each available sessions in the gym with QGridLayout in pyqt
        grid_layout = QGridLayout()

        row = 1
        for day in week_sessions.keys():
            day_label = QLabel(day.capitalize())
            day_label.setAlignment(QtCore.Qt.AlignCenter)
            day_label.setStyleSheet(day_label_style)


            grid_layout.addWidget(day_label, row, 0)
            col = 1
            for session in week_sessions[day].keys():
                checkbox = QCheckBox(session)
                checkbox.setStyleSheet(checkbox_style)
                grid_layout.addWidget(checkbox, row, col)
                self.checkbox_dict[(day, session)] = checkbox
                col += 1
            row += 1
        # adding grid layout to the QvBoxLayout
        layout.addLayout(grid_layout)
        layout.addWidget(self.done_button)

        self.setLayout(layout)

    def save_schedule(self):
        """
        Saves preferred session in preferred_session dictionary in this format:
        preferred_sessions = { 'sunday': ['8-9:35', '15-16:35'], 'monday': ['15-16:35'], 'saturday':[], ...}
        :return: None
        """
        for day in week_sessions.keys():
            for session in week_sessions[day].keys():
                if self.checkbox_dict[(day, session)].isChecked():
                    self.preferred_session[day].append(session)

        encrypt_credentials(self.username, self.password)
        store_preferred_sessions(self.preferred_session)
        self.close()


