import sys
import os
import user
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QStackedWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize

# from LSK.errors import OccupiedEmail


class StyledButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setFont(QFont("Arial", 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметки")
        self.setMinimumSize(400, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.stacked_widget = QStackedWidget()

        self.create_registration_page()
        self.create_note_page()

        self.stacked_widget.addWidget(self.registration_page)
        self.stacked_widget.addWidget(self.note_page)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.stacked_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)

    def create_registration_page(self):
        self.registration_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Регистрация")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите имя пользователя")

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Введите email")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Имя пользователя:", self.username_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)

        self.register_btn = StyledButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.register_user)

        self.edit_note_btn = StyledButton("Изменить заметку")
        self.edit_note_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addStretch(1)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.edit_note_btn)

        self.registration_page.setLayout(layout)

    def create_note_page(self):
        self.note_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Редактор заметок")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Введите текст заметки здесь...")

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        self.save_btn = StyledButton("Сохранить заметку")
        self.save_btn.clicked.connect(self.save_note)

        self.back_btn = StyledButton("Назад к регистрации")
        self.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        layout.addWidget(title)
        layout.addWidget(self.note_edit)
        layout.addLayout(btn_layout)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.back_btn)

        self.note_page.setLayout(layout)

    def register_user(self):
        username = self.username_edit.text()
        email = self.email_edit.text()
        password = self.password_edit.text()

        if not all([username, email, password]):
            self.show_message("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            user.newUser(username, email, password)
            self.show_message("Успех", "Пользователь успешно зарегистрирован!")
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка регистрации: {str(e)}")

    def save_note(self):
        text = self.note_edit.toPlainText()
        if not text.strip():
            self.show_message("Ошибка", "Заметка не может быть пустой!")
            return

        try:
            with open(os.path.expanduser(r"C:\Users\eldor\Рабочий стол\zam1.txt"), "w", encoding="utf-8") as f:
                f.write(text)
            self.show_message("Успех", "Заметка успешно сохранена!")
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка сохранения: {str(e)}")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()


app = QApplication(sys.argv)
app.setStyle("Fusion")

window = MainWindow()
window.show()

sys.exit(app.exec())
