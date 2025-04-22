import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QStackedWidget,
    QLineEdit, QPushButton, QTextEdit
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import user

    print("Модуль user успешно импортирован")
except ImportError as e:
    print(f"Ошибка импорта модуля user: {e}")
    sys.exit(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()

        self.text_edit = None

        self.page1 = QWidget()
        self.page2 = QWidget()

        self.setup_page1()
        self.setup_page2()

        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)

        self.setCentralWidget(self.stacked_widget)

    def setup_page1(self):
        self.setWindowTitle("My App")

        self.line_username = QLineEdit()
        self.line_email = QLineEdit()
        self.line_pass = QLineEdit()

        button_edit_note = QPushButton("Изменить заметку")
        button_registration = QPushButton("Зарегистрироваться")

        button_registration.clicked.connect(
            lambda: self.registration_new_user(
                self.line_username.text(),
                self.line_email.text(),
                self.line_pass.text()
            )
        )
        button_edit_note.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout = QVBoxLayout()
        layout.addWidget(self.line_username)
        layout.addWidget(self.line_email)
        layout.addWidget(self.line_pass)
        layout.addWidget(button_registration)
        layout.addWidget(button_edit_note)

        self.page1.setLayout(layout)

    def registration_new_user(self, username, email, password):
        user.newUser(username, email, password)

    def setup_page2(self):
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст заметки")

        button_save = QPushButton("Сохранить")
        button_back_reg = QPushButton("Вернуться назад")
        button_back_reg.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        button_save.clicked.connect(self.the_button_was_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(button_save)
        layout.addWidget(button_back_reg)

        self.page2.setLayout(layout)

    def the_button_was_clicked(self):
        all_text = self.text_edit.toPlainText()
        try:
            with open(r"C:\Users\eldor\Рабочий стол\zam1.txt", "w+") as file:
                file.write(all_text)
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
