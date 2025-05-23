import sys
import re
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QStackedWidget, QTextBrowser,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QHBoxLayout, QInputDialog, QSplitter, QMenu,
    QTabWidget
)
from PyQt6.QtGui import QFont, QAction, QColor
from PyQt6.QtCore import Qt

from user import (
    login_user, register_user, list_notes, save_note, folder_is_empty, text_note, delete_note, delete_folder
)
from errors import (
    OccupiedName, UserNotExists, IncorrectPassword, NotChange
)


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
        self.current_section = None
        self.image_sizes = {}

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.stacked_widget = QStackedWidget()

        self.create_login_page()
        self.create_registration_page()
        self.create_sections_page()
        self.create_notes_list_page()
        self.create_note_page()

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.registration_page)
        self.stacked_widget.addWidget(self.sections_page)
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
            QMessageBox {
                background-color: #C0C0C0;
            }
            QInputDialog {
                background-color: #C0C0C0;
            }
            QTabWidget::pane {
                border: 1px solid #8A2BE2;
                background: #C0C0C0;
            }
            QTabBar::tab {
                background: #8A2BE2;
                color: white;
                padding: 8px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #6A0DAD;
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

    def create_sections_page(self):
        self.sections_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Мои разделы")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sections_tabs = QTabWidget()
        self.sections_tabs.setTabPosition(QTabWidget.TabPosition.North)
        # noinspection PyUnresolvedReferences
        self.sections_tabs.currentChanged.connect(self.change_section)

        btn_layout = QHBoxLayout()

        self.new_section_btn = StyledButton("Новый раздел")
        # noinspection PyUnresolvedReferences
        self.new_section_btn.clicked.connect(self.create_new_section)

        self.logout_btn = StyledButton("Выйти")
        # noinspection PyUnresolvedReferences
        self.logout_btn.clicked.connect(self.logout)

        btn_layout.addWidget(self.new_section_btn)
        btn_layout.addWidget(self.logout_btn)

        layout.addWidget(title)
        layout.addWidget(self.sections_tabs)
        layout.addLayout(btn_layout)

        self.sections_page.setLayout(layout)

    def create_notes_list_page(self):
        self.notes_list_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self.section_title = QLabel()
        self.section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.new_folder_btn.setVisible(True)

        self.back_btn = StyledButton("Назад")
        # noinspection PyUnresolvedReferences
        self.back_btn.clicked.connect(self.go_back_to_sections)
        self.back_btn.setVisible(False)

        self.to_sections_btn = StyledButton("К разделам")
        # noinspection PyUnresolvedReferences
        self.to_sections_btn.clicked.connect(self.go_back_to_sections)

        btn_layout.addWidget(self.new_note_btn)
        btn_layout.addWidget(self.new_folder_btn)
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.to_sections_btn)

        layout.addWidget(self.section_title)
        layout.addWidget(self.notes_list)
        layout.addLayout(btn_layout)

        self.notes_list_page.setLayout(layout)

    def create_note_page(self):
        self.note_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title_layout = QHBoxLayout()
        title = QLabel("Редактор заметок")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.menu_btn = QPushButton("☰")
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8A2BE2;
                font-size: 20px;
                padding: 5px;
            }
        """)
        self.menu_btn.setFixedSize(40, 40)
        # noinspection PyUnresolvedReferences
        self.menu_btn.clicked.connect(self.show_note_menu)

        title_layout.addWidget(title)
        title_layout.addWidget(self.menu_btn, alignment=Qt.AlignmentFlag.AlignRight)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Введите текст заметки здесь...")
        self.note_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.note_edit.customContextMenuRequested.connect(self.show_editor_context_menu)

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        self.preview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.preview.customContextMenuRequested.connect(self.on_preview_context_menu)
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

        layout.addLayout(title_layout)
        layout.addWidget(splitter)
        layout.addLayout(btn_layout)

        self.note_page.setLayout(layout)

    def show_sections(self):
        if not self.current_user:
            self.stacked_widget.setCurrentIndex(0)
            return

        self.sections_tabs.clear()

        try:
            sections = self.current_user.list_sections()
            if not sections:
                self.sections_tabs.addTab(QLabel("У вас пока нет разделов. Создайте первый раздел!"), "Нет разделов")
                return

            for section in sections:
                tab = QWidget()
                tab_layout = QVBoxLayout()

                label = QLabel(f"Раздел: {section.name}\nЦвет: {section.color}")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                open_btn = StyledButton("Открыть раздел")
                # noinspection PyUnresolvedReferences
                open_btn.clicked.connect(lambda _, s=section: self.open_section(s))

                tab_layout.addWidget(label)
                tab_layout.addWidget(open_btn)
                tab.setLayout(tab_layout)

                self.sections_tabs.addTab(tab, section.name)

            self.stacked_widget.setCurrentIndex(2)

        except Exception as e:
            self.show_message("Ошибка", f"Не удалось загрузить разделы: {str(e)}")

    def open_section(self, section):
        self.current_section = section
        self.current_folder_id = None
        self.show_notes_list()

    def change_section(self, index):
        pass

    def create_new_section(self):
        name, ok = QInputDialog.getText(
            self, "Новый раздел", "Введите название раздела:"
        )
        if not ok or not name.strip():
            return

        color, ok = QInputDialog.getItem(
            self, "Выбор цвета", "Выберите цвет для раздела:",
            ["Фиолетовый", "Синий", "Зеленый", "Красный", "Желтый"], 0, False
        )
        if not ok:
            return

        try:
            self.current_user.create_section(name, color)
            self.show_message("Успех", "Раздел успешно создан!")
            self.show_sections()
        except OccupiedName as e:
            self.show_message("Ошибка", str(e))
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось создать раздел: {str(e)}")

    def go_back_to_sections(self):
        self.current_section = None
        self.current_folder_id = None
        self.show_sections()

    def show_note_menu(self):
        menu = QMenu(self)

        insert_image_action = QAction("Вставить фото", self)
        # noinspection PyUnresolvedReferences
        insert_image_action.triggered.connect(self.insert_image)
        menu.addAction(insert_image_action)

        delete_note_action = QAction("Удалить заметку", self)
        # noinspection PyUnresolvedReferences
        delete_note_action.triggered.connect(self.delete_current_note)
        menu.addAction(delete_note_action)

        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def show_editor_context_menu(self, position):
        self.note_edit.createStandardContextMenu(position).exec(self.note_edit.mapToGlobal(position))

    def insert_image(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            image_name = file_path.split('/')[-1]
            self.note_edit.insertPlainText(f"![{image_name}]({file_path})")

    def delete_current_note(self):
        if self.current_note_id:
            reply = QMessageBox.question(
                self, 'Удаление заметки',
                'Вы уверены, что хотите удалить текущую заметку?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    delete_note(self.current_note_id)
                    self.show_notes_list()
                except Exception as e:
                    self.show_message("Ошибка", f"Не удалось удалить заметку: {str(e)}")
        else:
            self.show_message("Ошибка", "Нет заметки для удаления")

    def on_preview_context_menu(self, position):
        anchor = self.preview.anchorAt(position)
        if anchor.startswith("image:"):
            img_id = anchor.split(":")[1]
            menu = QMenu(self)
            resize_action = QAction("Изменить размер", self)
            # noinspection PyUnresolvedReferences
            resize_action.triggered.connect(lambda: self.resize_image(img_id))
            menu.addAction(resize_action)

            menu.exec(self.preview.mapToGlobal(position))

    def resize_image(self, img_id):
        current_size = self.image_sizes.get(img_id, 300)
        size, ok = QInputDialog.getInt(
            self,
            "Изменить размер изображения",
            "Новый размер (пикселей):",
            current_size,
            50, 1000, 25
        )

        if ok:
            self.image_sizes[img_id] = size
            self.update_preview()

    def update_preview(self):
        markdown_text = self.note_edit.toPlainText()
        html = self.markdown_to_html(markdown_text)
        self.preview.setHtml(html)

    def markdown_to_html(self, markdown_text):
        html = """<html>
        <head>
        <style>
            body {
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 { font-size: 2em; color: white; }
            h2 { font-size: 1.75em; color: white; }
            h3 { font-size: 1.5em; color: white; }
            h4 { font-size: 1.25em; color: white; }
            h5 { font-size: 1.1em; color: white; }
            strong, b { font-weight: bold; }
            em, i { font-style: italic; }
            s, strike, del { text-decoration: line-through; }
            code {
                background-color: #f0f0f0;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: monospace;
            }
            pre {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            a {
                color: #8A2BE2;
                text-decoration: underline;
            }
            blockquote {
                border-left: 3px solid #8A2BE2;
                padding-left: 10px;
                color: #6a737d;
                font-style: italic;
                margin-left: 0;
            }
            ul, ol {
                padding-left: 20px;
            }
            li {
                margin: 5px 0;
            }
            hr {
                border: none;
                border-top: 1px solid #8A2BE2;
                margin: 20px 0;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
        </head>
        <body>
        """

        lines = markdown_text.split('\n')
        in_code_block = False
        in_list = False
        list_type = None
        current_indent = 0
        img_counter = 0

        for line in lines:
            if line.strip() == '```':
                in_code_block = not in_code_block
                html += "<pre><code>" if in_code_block else "</code></pre>"
                continue

            if in_code_block:
                html += line + "\n"
                continue

            img_matches = re.finditer(r"!\[(.*?)\]\((.*?)\)", line)
            for match in img_matches:
                img_id = f"img{img_counter}"
                img_counter += 1
                alt_text = match.group(1)
                img_url = match.group(2)
                img_size = self.image_sizes.get(img_id, 300)

                img_tag = f'<a name="image:{img_id}" href="image:{img_id}">' \
                          f'<img src="{img_url}" alt="{alt_text}" style="max-width:{img_size}px; max-height:{img_size}px;"></a>'
                line = line.replace(match.group(0), img_tag)

            line = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", line)
            line = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", line)
            line = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", line)
            line = re.sub(r"^#### (.*?)$", r"<h4>\1</h4>", line)
            line = re.sub(r"^##### (.*?)$", r"<h5>\1</h5>", line)

            line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            line = re.sub(r"__(.*?)__", r"<strong>\1</strong>", line)

            line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)
            line = re.sub(r"_(.*?)_", r"<em>\1</em>", line)

            line = re.sub(r"~~(.*?)~~", r"<s>\1</s>", line)

            line = re.sub(r"`(.+?)`", r"<code>\1</code>", line)

            line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)

            line = re.sub(r"^>\s(.*?)$", r"<blockquote>\1</blockquote>", line)

            line = re.sub(r"^[-*_]{3,}$", r"<hr>", line)

            m = re.match(r"^(\s*)([-*+])\s(.*)", line)
            if m:
                indent = len(m.group(1))
                if not in_list:
                    html += "<ul>\n"
                    in_list = True
                    list_type = 'ul'
                elif indent > current_indent:
                    html += "<ul>\n"
                elif indent < current_indent:
                    html += "</ul>\n"

                current_indent = indent
                html += "  " * (indent // 2) + f"<li>{m.group(3)}</li>\n"
                continue

            m = re.match(r"^(\s*)(\d+)\.\s(.*)", line)
            if m:
                indent = len(m.group(1))
                if not in_list:
                    html += "<ol>\n"
                    in_list = True
                    list_type = 'ol'
                elif indent > current_indent:
                    html += "<ol>\n"
                elif indent < current_indent:
                    html += "</ol>\n"

                current_indent = indent
                html += "  " * (indent // 2) + f"<li>{m.group(3)}</li>\n"
                continue

            if in_list:
                html += f"</{list_type}>\n"
                in_list = False
                current_indent = 0

            if "|" in line and "-" not in line:
                cells = [cell.strip() for cell in line.split("|") if cell.strip()]
                line = "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"
            elif "|" in line and "-" in line:
                continue

            html += line + "\n"

        if in_list:
            html += f"</{list_type}>"

        html += "</body></html>"

        return html

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
        if not folder_is_empty(folder_id):
            reply = QMessageBox.question(self, 'Удаление папки',
                                    'Внутри папки есть заметки, которые будут удалены при удалении папки. Продолжить?',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                delete_folder(folder_id)
                self.show_notes_list()
        else:
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

        except OccupiedName as e:
            self.show_message("Ошибка регистрации", str(e))
        except Exception as e:
            self.show_message("Ошибка", f"Неизвестная ошибка: {str(e)}")

    def show_notes_list(self):
        if not self.current_user or not self.current_section:
            self.stacked_widget.setCurrentIndex(2)
            return

        self.notes_list.clear()
        self.section_title.setText(f"Раздел: {self.current_section.name}")

        try:
            folders_and_notes = self.current_section.menu()

            folders = []
            notes = []

            if self.current_folder_id is not None:
                notes = list_notes(self.current_folder_id)
                self.back_btn.setVisible(True)
                self.new_folder_btn.setVisible(False)
            else:
                if folders_and_notes and len(folders_and_notes) > 0:
                    folders = folders_and_notes[0]
                if len(folders_and_notes) > 1:
                    notes = folders_and_notes[1]
                self.back_btn.setVisible(False)
                self.new_folder_btn.setVisible(True)

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

            self.stacked_widget.setCurrentIndex(3)  # Переключаемся на страницу заметок

        except Exception as e:
            self.show_message("Ошибка", f"Не удалось загрузить заметки: {str(e)}")

    def create_new_note(self):
        if not self.current_section:
            self.show_message("Ошибка", "Сначала выберите раздел!")
            return

        self.current_note_id = None
        self.note_edit.clear()
        self.stacked_widget.setCurrentIndex(4)  # Переключаемся на редактор заметок

    def create_new_folder(self):
        if not self.current_section:
            self.show_message("Ошибка", "Сначала выберите раздел!")
            return

        folder_name, ok = QInputDialog.getText(
            self, "Новая папка", "Введите название папки:"
        )
        if ok and folder_name.strip():
            try:
                self.current_section.create_folder(folder_name)
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
                note_text = text_note(item_id)
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

                folder_id = self.current_folder_id if self.current_folder_id is not None else self.current_section.id_root
                self.current_section.create_note(note_name, text, folder_id)
                self.show_message("Успех", "Заметка успешно создана!")
            else:
                try:
                    save_note(self.current_note_id, text)
                    self.show_message("Успех", "Заметка успешно сохранена!")
                except NotChange as e:
                    self.show_message("Предупреждение", str(e))
                except OccupiedName as e:
                    self.show_message("Ошибка", str(e))

            self.show_notes_list()

        except OccupiedName as e:
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
