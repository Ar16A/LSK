import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QStackedWidget, QTextBrowser,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QHBoxLayout, QInputDialog, QSplitter, QMenu
)
from PyQt6.QtGui import QFont, QTextCharFormat, QSyntaxHighlighter, QColor, QAction
from PyQt6.QtCore import Qt, QRegularExpression

from user import login_user, register_user

from errors import (
    OccupiedEmail, OccupiedUsername, OccupiedUsernameAndEmail,
    OccupiedNameNote, UserNotExists, IncorrectPassword, NotChange
)


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        header_formats = []
        for level in range(1, 7):
            form = QTextCharFormat()
            form.setFontWeight(QFont.Weight.Bold)
            form.setFontPointSize(24 - level * 2)
            header_formats.append(form)

        self.highlighting_rules.append((QRegularExpression(r"^#\s.+$"), header_formats[0]))
        self.highlighting_rules.append((QRegularExpression(r"^##\s.+$"), header_formats[1]))
        self.highlighting_rules.append((QRegularExpression(r"^###\s.+$"), header_formats[2]))
        self.highlighting_rules.append((QRegularExpression(r"^####\s.+$"), header_formats[3]))
        self.highlighting_rules.append((QRegularExpression(r"^#####\s.+$"), header_formats[4]))
        self.highlighting_rules.append((QRegularExpression(r"^######\s.+$"), header_formats[5]))

        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r"\*\*(.*?)\*\*"), bold_format))
        self.highlighting_rules.append((QRegularExpression(r"__(.*?)__"), bold_format))

        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r"\*(.*?)\*"), italic_format))
        self.highlighting_rules.append((QRegularExpression(r"_(.*?)_"), italic_format))

        strike_format = QTextCharFormat()
        strike_format.setFontStrikeOut(True)
        self.highlighting_rules.append((QRegularExpression(r"~~(.*?)~~"), strike_format))

        inline_code_format = QTextCharFormat()
        inline_code_format.setBackground(QColor("grey"))
        self.highlighting_rules.append((QRegularExpression(r"`(.+?)`"), inline_code_format))

        block_code_format = QTextCharFormat()
        block_code_format.setBackground(QColor("grey"))
        pattern = QRegularExpression(r"```.*?```")
        pattern.setPatternOptions(QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, block_code_format))

        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#8A2BE2"))
        link_format.setFontUnderline(True)
        self.highlighting_rules.append((QRegularExpression(r"\[(.+?)\]\(.+?\)"), link_format))

        image_format = QTextCharFormat()
        image_format.setForeground(QColor("#9055a2"))
        self.highlighting_rules.append((QRegularExpression(r"!\[(.+?)\]\(.+?\)"), image_format))

        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#6a737d"))
        quote_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r"^>\s.+$"), quote_format))

        hr_format = QTextCharFormat()
        hr_format.setForeground(QColor("darkgrey"))
        self.highlighting_rules.append((QRegularExpression(r"^[-*_]{3,}$"), hr_format))

        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#8A2BE2"))
        self.highlighting_rules.append((QRegularExpression(r"^(\s*)[-*+]\s.+$"), list_format))
        self.highlighting_rules.append((QRegularExpression(r"^(\s*)\d+\.\s.+$"), list_format))

        table_format = QTextCharFormat()
        table_format.setForeground(QColor("#8A2BE2"))
        self.highlighting_rules.append((QRegularExpression(r"^\|.+\|$"), table_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class StyledButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background: #8A2BE2;
                color: white;
                border: 5px;
                border-radius: 5px;
                padding: 5px;
                font-size: 17px;
            }
            QPushButton:hover {
                background-color: #462255;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметки")
        self.setMinimumSize(800, 800)

        self.current_user = None
        self.current_note_id = None
        self.current_folder_id = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.stacked_widget = QStackedWidget()

        self.create_login_page()
        self.create_registration_page()
        self.create_notes_list_page()
        self.create_note_page()

        self.stacked_widget.addWidget(self.login_page)
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
            }
            QLabel {
                font-size: 17px;
                color: black;
            }
            QListWidget {
                color: white;
                background-color: #C0C0C0;
                border-radius: 4px;
                font-size: 16px;
            }
            QListWidget::item {
                background-color: #8A2BE2;
                border-bottom: 4px solid #C0C0C0;
                border-radius: 10px;
                padding: 8px;
                margin: 2px;
                min-height: 30px;
            }
            QListWidget::item:hover {
                background-color: #462255;
            }
            QListWidget::item:selected {
                background-color: #6A0DAD;
            }
        """)

    def create_login_page(self):
        self.login_page = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите имя пользователя или email")

        self.login_password_edit = QLineEdit()
        self.login_password_edit.setPlaceholderText("Введите пароль")
        self.login_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Логин:", self.login_edit)
        form_layout.addRow("Пароль:", self.login_password_edit)

        self.login_btn = StyledButton("Войти")
        # noinspection PyUnresolvedReferences
        self.login_btn.clicked.connect(self.login_user)

        self.to_register_btn = StyledButton("Регистрация")
        # noinspection PyUnresolvedReferences
        self.to_register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.to_register_btn)

        main_layout.addWidget(title)
        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.login_page.setLayout(main_layout)

    def create_registration_page(self):
        self.registration_page = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        title = QLabel("Регистрация")
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

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Повторите пароль")
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Имя пользователя:", self.username_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        form_layout.addRow("Подтверждение пароля:", self.confirm_password_edit)

        self.register_btn = StyledButton("Зарегистрироваться")
        # noinspection PyUnresolvedReferences
        self.register_btn.clicked.connect(self.register_users)

        self.to_login_btn = StyledButton("Уже есть аккаунт? Войти")
        # noinspection PyUnresolvedReferences
        self.to_login_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        btn_layout.addWidget(self.register_btn)
        btn_layout.addWidget(self.to_login_btn)

        main_layout.addWidget(title)
        main_layout.addLayout(form_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.registration_page.setLayout(main_layout)

    def create_notes_list_page(self):
        self.notes_list_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Мои заметки")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.notes_list = QListWidget()
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.notes_list.customContextMenuRequested.connect(self.show_context_menu)
        # noinspection PyUnresolvedReferences
        self.notes_list.itemDoubleClicked.connect(self.open_item)

        btn_layout = QHBoxLayout()

        self.new_note_btn = StyledButton("Новая заметка")
        # noinspection PyUnresolvedReferences
        self.new_note_btn.clicked.connect(self.create_new_note)

        self.new_folder_btn = StyledButton("Новая папка")
        # noinspection PyUnresolvedReferences
        self.new_folder_btn.clicked.connect(self.create_new_folder)

        self.back_btn = StyledButton("Назад")
        # noinspection PyUnresolvedReferences
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)

        self.logout_btn = StyledButton("Выйти")
        # noinspection PyUnresolvedReferences
        self.logout_btn.clicked.connect(self.logout)

        btn_layout.addWidget(self.new_note_btn)
        btn_layout.addWidget(self.new_folder_btn)
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.logout_btn)

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
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Введите текст заметки здесь...")

        self.highlighter = MarkdownHighlighter(self.note_edit.document())

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        # noinspection PyUnresolvedReferences
        self.note_edit.textChanged.connect(self.update_preview)

        splitter.addWidget(self.note_edit)
        splitter.addWidget(self.preview)
        splitter.setSizes([400, 200])

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.save_btn = StyledButton("Сохранить")
        # noinspection PyUnresolvedReferences
        self.save_btn.clicked.connect(self.save_note)

        self.cancel_btn = StyledButton("Отмена")
        # noinspection PyUnresolvedReferences
        self.cancel_btn.clicked.connect(lambda: self.show_notes_list())

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addWidget(title)
        layout.addWidget(splitter)
        layout.addLayout(btn_layout)

        self.note_page.setLayout(layout)

    def show_context_menu(self, position):
        item = self.notes_list.itemAt(position)
        if not item:
            return

        menu = QMenu()

        if item.data(Qt.ItemDataRole.UserRole + 1) == "folder":
            delete_action = QAction("Удалить папку", self)
            # noinspection PyUnresolvedReferences
            delete_action.triggered.connect(lambda: self.delete_folder(item))
            menu.addAction(delete_action)
        else:
            delete_action = QAction("Удалить заметку", self)
            # noinspection PyUnresolvedReferences
            delete_action.triggered.connect(lambda: self.delete_note(item))
            menu.addAction(delete_action)

        menu.exec(self.notes_list.mapToGlobal(position))

    def delete_folder(self, item):
        folder_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, 'Удаление папки',
                                     'Вы уверены, что хотите удалить папку и все заметки внутри?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.current_user.delete_folder(folder_id)
            self.show_notes_list()

    def delete_note(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, 'Удаление заметки',
                                     'Вы уверены, что хотите удалить заметку?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.current_user.delete_note(note_id)
            self.show_notes_list()

    def login_user(self):
        login = self.login_edit.text()
        password = self.login_password_edit.text()

        if not all([login, password]):
            self.show_message("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            self.current_user = login_user(login, password)
            self.current_folder_id = None
            self.show_message("Успех", "Вы успешно вошли в систему!")
            self.show_notes_list()

        except UserNotExists as e:
            self.show_message("Ошибка входа", str(e))
        except IncorrectPassword as e:
            self.show_message("Ошибка входа", str(e))
        except Exception as e:
            self.show_message("Ошибка", f"Неизвестная ошибка: {str(e)}")

    def register_users(self):
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not all([username, email, password, confirm_password]):
            self.show_message("Ошибка", "Все поля должны быть заполнены!")
            return
        for x in '<>@"\'/\\|{}[]()~:;,#$%^&*+=`!?':
            if x in username:
                self.show_message("Ошибка", "Имя пользователя содержит запрещенные символы: "
                                            "<>@\"\'/\\|{}[]()~:;,#$%^&*+=`!?!")
                return

        if '@' not in email or '.' not in email:
            self.show_message("Ошибка", "Пожалуйста, введите корректный email!")
            return

        if password != confirm_password:
            self.show_message("Ошибка", "Пароли не совпадают!")
            return

        try:
            register_user(username, email, password)
            self.show_message("Успех", "Пользователь успешно зарегистрирован!")
            self.stacked_widget.setCurrentIndex(0)

        except OccupiedUsernameAndEmail as e:
            self.show_message("Ошибка регистрации", str(e))
        except OccupiedUsername as e:
            self.show_message("Ошибка регистрации", str(e))
        except OccupiedEmail as e:
            self.show_message("Ошибка регистрации", str(e))
        except Exception as e:
            self.show_message("Ошибка", f"Неизвестная ошибка: {str(e)}")

    def show_notes_list(self):
        if not self.current_user:
            self.stacked_widget.setCurrentIndex(0)
            return

        self.notes_list.clear()

        try:
            folders_and_notes = self.current_user.list_notes()

            folders = []
            notes = []

            if self.current_folder_id is not None:
                notes = self.current_user.list_folder(self.current_folder_id)
                self.back_btn.setVisible(True)
            else:
                if folders_and_notes and len(folders_and_notes) > 0:
                    folders = folders_and_notes[0]
                if len(folders_and_notes) > 1:
                    notes = folders_and_notes[1]
                self.back_btn.setVisible(False)

            if self.current_folder_id is None:
                for folder_id, folder_name in folders:
                    item = QListWidgetItem(f"📁 {folder_name}")
                    item.setData(Qt.ItemDataRole.UserRole, folder_id)
                    item.setData(Qt.ItemDataRole.UserRole + 1, "folder")
                    self.notes_list.addItem(item)

            for note_id, note_name in notes:
                item = QListWidgetItem(f"📝 {note_name}")
                item.setData(Qt.ItemDataRole.UserRole, note_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, "note")
                self.notes_list.addItem(item)

            self.stacked_widget.setCurrentIndex(2)

        except Exception as e:
            self.show_message("Ошибка", f"Не удалось загрузить заметки: {str(e)}")

    def update_preview(self):
        markdown_text = self.note_edit.toPlainText()
        self.preview.setMarkdown(markdown_text)

    def create_new_note(self):
        self.current_note_id = None
        self.note_edit.clear()
        self.stacked_widget.setCurrentIndex(3)

    def create_new_folder(self):
        folder_name, ok = QInputDialog.getText(
            self, "Новая папка", "Введите название папки:"
        )
        if ok and folder_name.strip():
            try:
                self.current_user.create_folder(folder_name)
                self.show_notes_list()
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось создать папку: {str(e)}")

    def open_item(self, item):
        item_type = item.data(Qt.ItemDataRole.UserRole + 1)
        item_id = item.data(Qt.ItemDataRole.UserRole)

        if item_type == "folder":
            self.current_folder_id = item_id
            self.show_notes_list()
        else:
            self.current_note_id = item_id
            try:
                note_text = self.current_user.text_note(item_id)
                self.note_edit.setText(note_text)
                self.stacked_widget.setCurrentIndex(3)
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось открыть заметку: {str(e)}")

    def go_back(self):
        self.current_folder_id = None
        self.show_notes_list()

    def save_note(self):
        text = self.note_edit.toPlainText()
        if not text.strip():
            self.show_message("Ошибка", "Заметка не может быть пустой!")
            return

        try:
            if not self.current_note_id:
                note_name, ok = QInputDialog.getText(
                    self, "Новая заметка", "Введите название заметки:"
                )
                if not ok or not note_name.strip():
                    return

                folder_id = self.current_folder_id if self.current_folder_id is not None else self.current_user.id_root
                self.current_user.create_note(note_name, text, folder_id)
                self.show_message("Успех", "Заметка успешно создана!")
            else:
                try:
                    self.current_user.save_note(self.current_note_id, text)
                    self.show_message("Успех", "Заметка успешно сохранена!")
                except NotChange as e:
                    self.show_message("Предупреждение", str(e))
                except OccupiedNameNote as e:
                    self.show_message("Ошибка", str(e))

            self.show_notes_list()

        except OccupiedNameNote as e:
            self.show_message("Ошибка", str(e))
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка сохранения: {str(e)}")

    def logout(self):
        self.current_user = None
        self.current_note_id = None
        self.current_folder_id = None
        self.stacked_widget.setCurrentIndex(0)

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()


app = QApplication(sys.argv)
app.setFont(QFont("Consolas"))
app.setStyle("Fusion")
window = MainWindow()
window.show()

sys.exit(app.exec())
