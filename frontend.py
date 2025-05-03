import sys
import os
import user
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QStackedWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QHBoxLayout, QInputDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class StyledButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setFont(QFont("Consolas", 13))
        self.setStyleSheet("""
            QPushButton {
                background: #8A2BE2;
                color: white;
                border: 5px;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #462255;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметки")
        self.setMinimumSize(600, 600)
        self.notes_dir = r"C:\Users\eldor\Рабочий стол\nodes"
        os.makedirs(self.notes_dir, exist_ok=True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.stacked_widget = QStackedWidget()

        self.create_registration_page()
        self.create_notes_list_page()
        self.create_note_page()

        self.stacked_widget.addWidget(self.registration_page)
        self.stacked_widget.addWidget(self.notes_list_page)
        self.stacked_widget.addWidget(self.note_page)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.stacked_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #C0C0C0;
            }
            QLineEdit, QTextEdit {
                color: white;
                background-color: black;
                padding: 8px;
                border: 1px solid black;
                border-radius: 4px;
                font-size: 15px;
                font-family: Consolas;
            }
            QLabel {
                font-family: Consolas;
                font-size: 17px;
                color: black;
            }
            QFormLayout {
                font-family: Consolas;
            }
            QListWidget {
                color: white;
                background-color: #C0C0C0;
                border: 1px solid black;
                border-radius: 4px;
                font-family: Consolas;
            }
            QListWidget::item {
                 background-color: #8A2BE2;
                 border-bottom: 1px solid #C0C0C0;
                 border-radius: 4px;
                 font-family: Consolas;
            }
            QListWidget::item:hover {
                background-color: #462255;
            }
            QMessageBox {
                font-family: Consolas;
            }
            QInputDialog {
                font-family: Consolas;
            }
        """)

    def create_registration_page(self):
        self.registration_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Регистрация")
        title.setFont(QFont("Consolas", 19, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите имя пользователя")
        self.username_edit.setFont(QFont("Consolas"))

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Введите email")
        self.email_edit.setFont(QFont("Consolas"))

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setFont(QFont("Consolas"))

        form_layout.addRow("Имя пользователя:", self.username_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)

        self.register_btn = StyledButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.register_user)

        self.view_notes_btn = StyledButton("Мои заметки")
        self.view_notes_btn.clicked.connect(lambda: self.show_notes_list())

        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addStretch(1)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.view_notes_btn)

        self.registration_page.setLayout(layout)

    def create_notes_list_page(self):
        self.notes_list_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Мои заметки")
        title.setFont(QFont("Consolas", 19, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.notes_list = QListWidget()
        self.notes_list.setFont(QFont("Consolas"))
        self.notes_list.itemDoubleClicked.connect(self.open_note)

        btn_layout = QHBoxLayout()

        self.new_note_btn = StyledButton("Новая заметка")
        self.new_note_btn.clicked.connect(self.create_new_note)

        self.back_to_reg_btn = StyledButton("Назад")
        self.back_to_reg_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        btn_layout.addWidget(self.new_note_btn)
        btn_layout.addWidget(self.back_to_reg_btn)

        layout.addWidget(title)
        layout.addWidget(self.notes_list)
        layout.addLayout(btn_layout)

        self.notes_list_page.setLayout(layout)

    def create_note_page(self):
        self.note_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Редактор заметок")
        title.setFont(QFont("Consolas", 19, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Введите текст заметки здесь...")
        self.note_edit.setFont(QFont("Consolas"))

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.save_btn = StyledButton("Сохранить")
        self.save_btn.clicked.connect(self.save_note)

        self.cancel_btn = StyledButton("Отмена")
        self.cancel_btn.clicked.connect(lambda: self.show_notes_list())

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addWidget(title)
        layout.addWidget(self.note_edit)
        layout.addLayout(btn_layout)

        self.note_page.setLayout(layout)

    def register_user(self):
        username = self.username_edit.text()
        email = self.email_edit.text()
        password = self.password_edit.text()

        if not all([username, email, password]):
            self.show_message("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            user.registerUser(username, email, password)
            self.show_message("Успех", "Пользователь успешно зарегистрирован!")
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка регистрации: {str(e)}")

    def show_notes_list(self):
        self.notes_list.clear()

        notes = [f for f in os.listdir(self.notes_dir) if f.endswith('.txt')]

        for note in sorted(notes):
            item = QListWidgetItem(note[:-4])
            item.setFont(QFont("Consolas"))
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)

        self.stacked_widget.setCurrentIndex(1)

    def create_new_note(self):
        self.current_note_file = None
        self.note_edit.clear()
        self.stacked_widget.setCurrentIndex(2)

    def open_note(self, item):
        note_file = item.data(Qt.ItemDataRole.UserRole)
        self.current_note_file = os.path.join(self.notes_dir, note_file)

        try:
            with open(self.current_note_file, 'r', encoding='utf-8') as f:
                self.note_edit.setText(f.read())
            self.stacked_widget.setCurrentIndex(2)
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось открыть заметку: {str(e)}")

    def save_note(self):
        text = self.note_edit.toPlainText()
        if not text.strip():
            self.show_message("Ошибка", "Заметка не может быть пустой!")
            return

        try:
            if not hasattr(self, 'current_note_file') or not self.current_note_file:
                note_name, ok = QInputDialog.getText(
                    self, "Новая заметка", "Введите название заметки:"
                )
                if not ok or not note_name.strip():
                    return

                self.current_note_file = os.path.join(
                    self.notes_dir,
                    f"{note_name}.txt"
                )

            with open(self.current_note_file, 'w', encoding='utf-8') as f:
                f.write(text)

            self.show_message("Успех", "Заметка успешно сохранена!")
            self.show_notes_list()
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка сохранения: {str(e)}")

    def show_message(self, title, message) -> None:
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(QFont("Consolas"))
        msg_box.exec()


app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setFont(QFont("Consolas"))

window = MainWindow()
window.show()

sys.exit(app.exec())
