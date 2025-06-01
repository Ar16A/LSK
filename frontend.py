import re
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QWidget, QStackedWidget, QTextBrowser,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QHBoxLayout, QInputDialog, QSplitter, QMenu,
    QTabWidget, QTabBar, QStyle, QFileDialog, QColorDialog, QStyleOptionTab, QDialog, QComboBox
)
from PyQt6.QtGui import QFont, QAction, QColor, QPainter, QPixmap, QPen, QPalette
from PyQt6.QtCore import Qt, QPoint

from user import (
    login_user, register_user, list_notes, save_note, folder_is_empty, text_note, delete_note, delete_folder,
    new_photo, cur_login, is_sync, logout_user, synchro, giga_photo, get_photos, resize_photo, Section
)
from errors import OccupiedName, UserNotExists, IncorrectPassword, NotChange
from giga import summary, get_help, NotPhoto, TooMany, NotEthical


class ColoredTabBar(QTabBar):
    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            color = self.tabData(index)

            if color and color.isValid():
                option.palette.setColor(QPalette.ColorRole.Button, color)
                option.palette.setColor(QPalette.ColorRole.Window, color)

            self.style().drawControl(QStyle.ControlElement.CE_TabBarTabShape, option, painter)
            self.style().drawControl(QStyle.ControlElement.CE_TabBarTabLabel, option, painter)


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


class GigaChatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GigaChat")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.function_combo = QComboBox()
        self.function_combo.addItems(["Помощь", "Краткое содержание", "Генерация фото"])
        self.function_combo.setStyleSheet("""
            QComboBox {
                background: #8A2BE2;
                color: white;
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
            }
        """)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите ваш запрос для GigaChat...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                color: white;
                background-color: black;
                padding: 8px;
                border: 1px solid black;
                border-radius: 4px;
                font-size: 15px;
            }
        """)

        btn_layout = QHBoxLayout()
        submit_btn = StyledButton("Отправить")
        # noinspection PyUnresolvedReferences
        submit_btn.clicked.connect(self.accept)

        cancel_btn = StyledButton("Отмена")
        # noinspection PyUnresolvedReferences
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(QLabel("Выберите функцию:"))
        layout.addWidget(self.function_combo)
        layout.addWidget(QLabel("Ваш запрос:"))
        layout.addWidget(self.input_text)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_input(self):
        return self.function_combo.currentText(), self.input_text.toPlainText()


class TextResultDialog(QDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.result_text = QTextEdit()
        self.result_text.setPlainText(text)
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                color: white;
                background-color: black;
                padding: 8px;
                border: 1px solid black;
                border-radius: 4px;
                font-size: 15px;
            }
        """)

        btn_layout = QHBoxLayout()
        copy_btn = StyledButton("Скопировать")
        # noinspection PyUnresolvedReferences
        copy_btn.clicked.connect(self.copy_text)

        close_btn = StyledButton("Закрыть")
        # noinspection PyUnresolvedReferences
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(close_btn)

        layout.addWidget(QLabel(f"{title}:"))
        layout.addWidget(self.result_text)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def copy_text(self):
        QApplication.clipboard().setText(self.result_text.toPlainText())


class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите имя пользователя или email")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Логин:", self.login_edit)
        form_layout.addRow("Пароль:", self.password_edit)

        login_btn = StyledButton("Войти")
        # noinspection PyUnresolvedReferences
        login_btn.clicked.connect(self.main_window.ui_login_user)

        to_register_btn = StyledButton("Регистрация")
        # noinspection PyUnresolvedReferences
        to_register_btn.clicked.connect(self._to_registration_page)

        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(to_register_btn)

        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addStretch(1)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _to_registration_page(self):
        self.main_window.stacked_widget.setCurrentIndex(1)


class RegistrationPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

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

        register_btn = StyledButton("Зарегистрироваться")
        # noinspection PyUnresolvedReferences
        register_btn.clicked.connect(self.main_window.ui_register_user)

        to_login_btn = StyledButton("Уже есть аккаунт? Войти")
        # noinspection PyUnresolvedReferences
        to_login_btn.clicked.connect(self._to_login_page)

        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(to_login_btn)

        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addStretch(1)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _to_login_page(self):
        self.main_window.stacked_widget.setCurrentIndex(0)


class SectionsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Мои разделы")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sections_tabs = QTabWidget()
        self.sections_tabs.setTabPosition(QTabWidget.TabPosition.North)
        # noinspection PyUnresolvedReferences
        self.sections_tabs.currentChanged.connect(self.main_window.change_section)
        self.sections_tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.sections_tabs.customContextMenuRequested.connect(self.main_window.show_tab_context_menu)

        btn_layout = QHBoxLayout()

        new_section_btn = StyledButton("Новый раздел")
        # noinspection PyUnresolvedReferences
        new_section_btn.clicked.connect(self.main_window.create_new_section)

        sync_btn = StyledButton("Синхронизировать")
        # noinspection PyUnresolvedReferences
        sync_btn.clicked.connect(self.main_window.synchronize)

        logout_btn = StyledButton("Выйти")
        # noinspection PyUnresolvedReferences
        logout_btn.clicked.connect(self.main_window.ui_logout)

        btn_layout.addWidget(new_section_btn)
        btn_layout.addWidget(sync_btn)
        btn_layout.addWidget(logout_btn)

        layout.addWidget(title)
        layout.addWidget(self.sections_tabs)
        layout.addLayout(btn_layout)

        self.setLayout(layout)


class FolderPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self.folder_notes_list = QListWidget()
        self.folder_notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.folder_notes_list.customContextMenuRequested.connect(self.main_window.show_folder_context_menu)
        # noinspection PyUnresolvedReferences
        self.folder_notes_list.itemDoubleClicked.connect(self.main_window.open_folder_item)

        btn_layout = QHBoxLayout()

        new_note_btn = StyledButton("Новая заметка")
        # noinspection PyUnresolvedReferences
        new_note_btn.clicked.connect(self.main_window.create_new_note)

        back_btn = StyledButton("Назад к разделу")
        # noinspection PyUnresolvedReferences
        back_btn.clicked.connect(self.main_window.go_back_to_sections)

        btn_layout.addWidget(new_note_btn)
        btn_layout.addWidget(back_btn)

        layout.addWidget(self.folder_notes_list)
        layout.addLayout(btn_layout)

        self.setLayout(layout)


class NotePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

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
        self.menu_btn.clicked.connect(self.main_window.show_note_menu)

        title_layout.addWidget(title)
        title_layout.addWidget(self.menu_btn, alignment=Qt.AlignmentFlag.AlignRight)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Введите текст заметки здесь...")
        self.note_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.note_edit.customContextMenuRequested.connect(self.main_window.show_editor_context_menu)

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        self.preview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.preview.customContextMenuRequested.connect(self.main_window.on_preview_context_menu)
        # noinspection PyUnresolvedReferences
        self.note_edit.textChanged.connect(self.main_window.update_preview)

        splitter.addWidget(self.note_edit)
        splitter.addWidget(self.preview)
        splitter.setSizes([400, 200])

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        save_btn = StyledButton("Сохранить")
        # noinspection PyUnresolvedReferences
        save_btn.clicked.connect(self.main_window.save_current_note)

        cancel_btn = StyledButton("Отмена")
        # noinspection PyUnresolvedReferences
        cancel_btn.clicked.connect(self.main_window.return_to_previous_page)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(title_layout)
        layout.addWidget(splitter)
        layout.addLayout(btn_layout)

        self.setLayout(layout)


class DrawingPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setMinimumSize(600, 500)

        self.canvas = QPixmap(800, 600)
        self.canvas.fill(Qt.GlobalColor.white)

        self.last_point = None
        self.drawing = False
        self.pen_color = QColor(Qt.GlobalColor.black)
        self.pen_width = 3
        self.erasing = False
        self.eraser_color = QColor(Qt.GlobalColor.white)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Рисование")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold;
            color: #8A2BE2;
            margin-bottom: 10px;
        """)

        self.drawing_label = QLabel()
        self.drawing_label.setPixmap(self.canvas)
        self.drawing_label.setStyleSheet("background-color: white; border: 2px solid #8A2BE2;")
        self.drawing_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.drawing_label.setScaledContents(False)
        self.drawing_label.setMouseTracking(True)

        tool_layout = QHBoxLayout()
        tool_layout.setSpacing(10)

        self.color_widget = QWidget()
        color_layout = QHBoxLayout(self.color_widget)
        color_layout.setContentsMargins(0, 0, 0, 0)

        self.color_btn = StyledButton("Цвет")
        # noinspection PyUnresolvedReferences
        self.color_btn.clicked.connect(self.choose_color)

        self.color_indicator = QLabel()
        self.color_indicator.setFixedSize(30, 30)
        self.color_indicator.setStyleSheet(
            f"background: {self.pen_color.name()}; border: 1px solid #888; border-radius: 15px;")

        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.color_indicator)

        self.eraser_btn = StyledButton("🧽 Ластик")
        # noinspection PyUnresolvedReferences
        self.eraser_btn.clicked.connect(self.toggle_eraser)
        self.update_eraser_btn_style()

        self.size_combo = QComboBox()
        self.size_combo.addItems(["1", "2", "3", "5", "8", "10", "15", "20"])
        self.size_combo.setCurrentText("3")
        # noinspection PyUnresolvedReferences
        self.size_combo.currentTextChanged.connect(self.change_pen_width)
        self.size_combo.setStyleSheet("""
            QComboBox {
                background: #8A2BE2;
                color: white;
                border-radius: 5px;
                padding: 5px;
                min-width: 60px;
            }
        """)

        self.clear_btn = StyledButton("🧹 Очистить")
        # noinspection PyUnresolvedReferences
        self.clear_btn.clicked.connect(self.clear_canvas)

        tool_layout.addWidget(self.color_widget)
        tool_layout.addWidget(self.eraser_btn)
        tool_layout.addWidget(QLabel("Размер:"))
        tool_layout.addWidget(self.size_combo)
        tool_layout.addWidget(self.clear_btn)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.save_btn = StyledButton("💾 Сохранить")
        # noinspection PyUnresolvedReferences
        self.save_btn.clicked.connect(self.save_drawing)

        self.cancel_btn = StyledButton("❌ Отмена")
        # noinspection PyUnresolvedReferences
        self.cancel_btn.clicked.connect(self.main_window.return_to_previous_page)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addWidget(title)
        layout.addWidget(self.drawing_label, 1)
        layout.addLayout(tool_layout)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def update_eraser_btn_style(self):
        style = """
            QPushButton {
                background: %s;
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-size: 17px;
            }
        """ % ("#462255" if self.erasing else "#8A2BE2")
        self.eraser_btn.setStyleSheet(style)

    def choose_color(self):
        color = QColorDialog.getColor(self.pen_color, self, "Выберите цвет кисти")
        if color.isValid():
            self.pen_color = color
            self.color_indicator.setStyleSheet(
                f"background: {color.name()}; border: 1px solid #888; border-radius: 15px;")
            if self.erasing:
                self.erasing = False
                self.update_eraser_btn_style()

    def toggle_eraser(self):
        self.erasing = not self.erasing
        self.update_eraser_btn_style()

    def change_pen_width(self, width):
        self.pen_width = int(width)

    def clear_canvas(self):
        self.canvas.fill(Qt.GlobalColor.white)
        self.drawing_label.setPixmap(self.canvas)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        label_size = self.drawing_label.size()
        new_canvas = QPixmap(label_size)
        new_canvas.fill(Qt.GlobalColor.white)
        painter = QPainter(new_canvas)
        painter.drawPixmap(0, 0, self.canvas.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        painter.end()
        self.canvas = new_canvas
        self.drawing_label.setPixmap(self.canvas)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = self.get_canvas_position(event.pos())
            self.draw_point(self.last_point)

    def mouseMoveEvent(self, event):
        if self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            current_point = self.get_canvas_position(event.pos())
            if self.last_point:
                self.draw_line(self.last_point, current_point)
            self.last_point = current_point

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.last_point = None

    def get_canvas_position(self, pos):
        global_pos = self.drawing_label.mapToGlobal(QPoint(0, 0))
        canvas_pos = self.mapToGlobal(pos)
        x = canvas_pos.x() - global_pos.x()
        y = canvas_pos.y() - global_pos.y()

        label_size = self.drawing_label.size()
        pixmap_size = self.canvas.size()
        scale_x = pixmap_size.width() / label_size.width() if label_size.width() > 0 else 1
        scale_y = pixmap_size.height() / label_size.height() if label_size.height() > 0 else 1
        x = x * scale_x
        y = y * scale_y

        x = max(0, min(x, self.canvas.width()))
        y = max(0, min(y, self.canvas.height()))
        return QPoint(int(x), int(y))

    def draw_point(self, point):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = self.eraser_color if self.erasing else self.pen_color
        painter.setPen(QPen(color, self.pen_width,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPoint(point)
        painter.end()
        self.drawing_label.setPixmap(self.canvas)

    def draw_line(self, start, end):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = self.eraser_color if self.erasing else self.pen_color
        painter.setPen(QPen(color, self.pen_width,
                            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(start, end)
        painter.end()
        self.drawing_label.setPixmap(self.canvas)

    def save_drawing(self):
        if not self.main_window.current_note_id:
            self.main_window.show_message("Ошибка", "Сначала создайте заметку!")
            return

        drawing_name, ok = QInputDialog.getText(
            self, "Название рисунка", "Введите название рисунка:",
            text=f"Рисунок {len(list_notes(self.main_window.current_folder_id or self.main_window.current_section.id_root)) + 1}"
        )
        if not ok or not drawing_name.strip():
            self.main_window.show_message("Ошибка", "Название рисунка не может быть пустым!")
            return

        drawing_name = drawing_name.replace('_', ' ')
        if not drawing_name.endswith('.png'):
            drawing_name += '.png'

        filename = "last_drawing.png"
        if not self.canvas.save(filename, "PNG"):
            self.main_window.show_message("Ошибка", "Не удалось сохранить рисунок")
            return
        try:
            saved_path = new_photo(self.main_window.current_note_id, filename, 700, drawing_name)
            self.main_window.insert_drawing(saved_path, drawing_name)
            self.main_window.return_to_previous_page()
        except OccupiedName:
            self.main_window.show_message("Ошибка", f"Рисунок с именем '{drawing_name}' уже существует!")
        except Exception as e:
            self.main_window.show_message("Ошибка", f"Не удалось сохранить изображение: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заметки")
        self.setMinimumSize(1000, 800)

        self.current_user = None
        self.current_note_id = None
        self.current_note_name = None
        self.current_folder_id = None
        self.current_section = None
        self.image_sizes = {}
        self._is_programmatic_change = False
        self.is_new_note = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.stacked_widget = QStackedWidget()

        self.login_page = LoginPage(self)
        self.registration_page = RegistrationPage(self)
        self.sections_page = SectionsPage(self)
        self.folder_page = FolderPage(self)
        self.note_page = NotePage(self)
        self.drawing_page = DrawingPage(self)

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.registration_page)
        self.stacked_widget.addWidget(self.sections_page)
        self.stacked_widget.addWidget(self.folder_page)
        self.stacked_widget.addWidget(self.note_page)
        self.stacked_widget.addWidget(self.drawing_page)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.stacked_widget)

        # noinspection PyUnresolvedReferences
        self.note_page.note_edit.cursorPositionChanged.connect(self.update_preview)
        # noinspection PyUnresolvedReferences
        self.note_page.note_edit.textChanged.connect(self.update_preview)

        self.current_user = cur_login()
        if not self.current_user:
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.show_sections()

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
            QTabWidget::pane {
                border: 5px solid #8A2BE2;
                background: #C0C0C0;
            }
            QMessageBox QLabel {
                color: black;
            }
            QMessageBox QPushButton {
                color: #FFFFFF;
            }
        """)

    def clear_login_registration_fields(self):
        self.login_page.login_edit.clear()
        self.login_page.password_edit.clear()
        self.registration_page.username_edit.clear()
        self.registration_page.email_edit.clear()
        self.registration_page.password_edit.clear()
        self.registration_page.confirm_password_edit.clear()

    def synchronize(self):
        if not self.current_user:
            self.show_message("Ошибка", "Вы не вошли в систему!")
            return
        if is_sync():
            self.show_message("Успех", "Данные уже синхронизированы!")
            return
        try:
            if synchro():
                self.show_message("Успех", "Данные успешно синхронизированы!")
            else:
                self.show_message("Ошибка",
                                  "Не удалось синхронизировать данные. Возможно, нет подключения к интернету.")
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка синхронизации: {str(e)}")

    def get_color_name(self, color):
        return color.name()

    def get_color_from_string(self, color_str):
        try:
            return QColor(color_str)
        except ValueError:
            return QColor(138, 43, 226)

    def show_sections(self):
        if not self.current_user:
            self.stacked_widget.setCurrentIndex(0)
            return

        current_section_name = self.current_section.name if self.current_section else None
        self.sections_page.sections_tabs.clear()

        try:
            sections = self.current_user.list_sections()
            if not sections:
                self.sections_page.sections_tabs.addTab(
                    QLabel("У вас пока нет разделов. Создайте первый раздел!"), "Нет разделов")
                self.stacked_widget.setCurrentIndex(2)
                return

            stylesheet = """
                QTabBar::tab {
                    color: black;
                    padding: 12px;
                    margin-right: 2px;
                    min-width: 100px;
                    border-top-left: 5px;
                    border-radius: 2px;
                }
                QTabWidget::pane {
                    border: 5px solid #8A2BE2;
                    background: #C0C0C0;
                }
            """
            tab_bar = ColoredTabBar()
            self.sections_page.sections_tabs.setTabBar(tab_bar)

            current_index = 0
            for index, section in enumerate(sections):
                tab = QWidget()
                tab_layout = QVBoxLayout()
                tab_layout.setSpacing(10)
                tab_layout.setContentsMargins(10, 10, 10, 10)

                label = QLabel(f"Раздел: {section.name}\n")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                contents_list = QListWidget()
                contents_list.setStyleSheet("""
                    QListWidget::item {
                        background-color: #8A2BE2;
                        border-bottom: 2px solid #C0C0C0;
                        border-radius: 10px;
                        padding: 8px;
                        margin-bottom: 2px;
                        min-height: 30px;
                    }
                """)
                contents_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                # noinspection PyUnresolvedReferences
                contents_list.customContextMenuRequested.connect(
                    lambda pos, s=section: self.show_context_menu(pos, s))
                # noinspection PyUnresolvedReferences
                contents_list.itemClicked.connect(
                    lambda items, s=section: self._open_section_item(items, s))

                folders_and_notes = section.menu()
                folders = folders_and_notes[0] if folders_and_notes and len(folders_and_notes) > 0 else []
                notes = folders_and_notes[1] if folders_and_notes and len(folders_and_notes) > 1 else []

                for folder_id, folder_name in folders:
                    item = QListWidgetItem(f"📁 {folder_name}")
                    item.setData(Qt.ItemDataRole.UserRole, folder_id)
                    item.setData(Qt.ItemDataRole.UserRole + 1, "folder")
                    contents_list.addItem(item)

                for note_id, note_name in notes:
                    item = QListWidgetItem(f"📝 {note_name}")
                    item.setData(Qt.ItemDataRole.UserRole, note_id)
                    item.setData(Qt.ItemDataRole.UserRole + 1, "note")
                    contents_list.addItem(item)

                btn_layout = QHBoxLayout()
                btn_layout.setSpacing(10)

                create_folder_btn = StyledButton("Создать папку")
                # noinspection PyUnresolvedReferences
                create_folder_btn.clicked.connect(
                    lambda _, s=section: self._create_folder_in_section(s))

                create_note_btn = StyledButton("Создать заметку")
                # noinspection PyUnresolvedReferences
                create_note_btn.clicked.connect(
                    lambda _, s=section: self._create_note_in_section(s))

                btn_layout.addWidget(create_folder_btn)
                btn_layout.addWidget(create_note_btn)

                tab_layout.addWidget(label)
                tab_layout.addWidget(contents_list)
                tab_layout.addLayout(btn_layout)
                tab.setLayout(tab_layout)

                tab_color = self.get_color_from_string(section.color)
                if not tab_color.isValid():
                    tab_color = QColor(138, 43, 226)

                tab_index = self.sections_page.sections_tabs.addTab(tab, section.name)
                self.sections_page.sections_tabs.tabBar().setTabData(tab_index, tab_color)

                if section.name == current_section_name:
                    current_index = index

            self.sections_page.sections_tabs.setStyleSheet(stylesheet)
            self.stacked_widget.setCurrentIndex(2)
            self.sections_page.sections_tabs.setCurrentIndex(current_index)

        except Exception as e:
            self.show_message("Ошибка", f"Не удалось загрузить разделы: {str(e)}")

    def _create_folder_in_section(self, section):
        self.current_section = section
        self.start_create_folder()

    def _create_note_in_section(self, section):
        self.current_section = section
        self.create_new_note()

    def _open_section_item(self, item, section):
        self.current_section = section
        self.open_section_item(item)

    def show_folder(self):
        if not self.current_user or not self.current_section or not self.current_folder_id:
            self.stacked_widget.setCurrentIndex(2)
            return

        self.folder_page.folder_notes_list.clear()

        try:
            notes = list_notes(self.current_folder_id)
            for note_id, note_name in notes:
                item = QListWidgetItem(f"📝 {note_name}")
                item.setData(Qt.ItemDataRole.UserRole, note_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, "note")
                self.folder_page.folder_notes_list.addItem(item)
            self.stacked_widget.setCurrentIndex(3)
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось загрузить заметки: {str(e)}")

    def show_folder_context_menu(self, position):
        item = self.folder_page.folder_notes_list.itemAt(position)
        if not item:
            return
        menu = QMenu()
        delete_action = QAction("Удалить заметку", self)
        # noinspection PyUnresolvedReferences
        delete_action.triggered.connect(lambda: self.ui_delete_note(item))
        menu.addAction(delete_action)
        menu.exec(self.folder_page.folder_notes_list.mapToGlobal(position))

    def open_folder_item(self, item):
        item_type = item.data(Qt.ItemDataRole.UserRole + 1)
        item_id = item.data(Qt.ItemDataRole.UserRole)
        if item_type == "note":
            self.current_note_id = item_id
            self.is_new_note = False
            try:
                note_text = text_note(item_id)
                self.note_page.note_edit.setText(note_text)
                self.stacked_widget.setCurrentIndex(4)
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось открыть заметку: {str(e)}")

    def open_section_item(self, item):
        item_type = item.data(Qt.ItemDataRole.UserRole + 1)
        item_id = item.data(Qt.ItemDataRole.UserRole)
        if item_type == "folder":
            self.current_folder_id = item_id
            self.show_folder()
        else:
            self.current_note_id = item_id
            self.is_new_note = False
            try:
                note_text = text_note(item_id)
                self.note_page.note_edit.setText(note_text)
                self.stacked_widget.setCurrentIndex(4)
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось открыть заметку: {str(e)}")

    def show_tab_context_menu(self, position):
        if not self.current_user:
            self.show_message("Ошибка", "Пользователь не авторизован!")
            return
        tab_bar = self.sections_page.sections_tabs.tabBar()
        index = tab_bar.tabAt(position)
        if index < 0:
            self.show_message("Ошибка", "Выберите действительную вкладку!")
            return
        try:
            sections = self.current_user.list_sections()
            if index >= len(sections):
                self.show_message("Ошибка", "Выбранный раздел не найден!")
                return
            section = sections[index]
            menu = QMenu(self)
            delete_action = QAction("Удалить раздел", self)
            # noinspection PyUnresolvedReferences
            delete_action.triggered.connect(lambda: self.delete_section(section))
            menu.addAction(delete_action)
            menu.exec(self.sections_page.sections_tabs.tabBar().mapToGlobal(position))
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось открыть контекстное меню: {str(e)}")

    def delete_section(self, section):
        try:
            folders_and_notes = section.menu()
            is_empty = not (folders_and_notes[0] or folders_and_notes[1]) if folders_and_notes else True

            if is_empty:
                section.delete()
                self.show_message("Успех", "Раздел успешно удалён!")
                self.show_sections()
            else:
                reply = QMessageBox.question(
                    self, 'Удаление раздела',
                    f'Раздел "{section.name}" содержит папки или заметки. Вы уверены, что хотите удалить его?'
                    f' Все содержимое будет удалено.',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    section.delete()
                    self.show_message("Успех", "Раздел успешно удалён!")
                    self.show_sections()
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось удалить раздел: {str(e)}")

    def start_create_folder(self):
        self.current_folder_id = None
        self.create_new_folder()

    def create_new_note(self):
        if not self.current_section:
            self.show_message("Ошибка", "Сначала выберите раздел!")
            return
        folder_id = self.current_folder_id if self.current_folder_id is not None else self.current_section.id_root
        while True:
            note_name, ok = QInputDialog.getText(self, "Новая заметка", "Введите название заметки:")
            if not ok:
                return
            if not note_name.strip():
                self.show_message("Ошибка", "Название заметки не может быть пустым!")
                continue
            existing_notes = list_notes(folder_id)
            existing_names = [note[1] for note in existing_notes]
            if note_name in existing_names:
                self.show_message("Ошибка", f"Заметка с именем '{note_name}' уже существует в этой папке!")
                continue
            break
        try:
            self.current_note_id = self.current_section.reserve_note(folder_id)
            self.current_note_name = note_name
            self.is_new_note = True
            self.note_page.note_edit.clear()
            self.stacked_widget.setCurrentIndex(4)
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось создать заметку: {str(e)}")

    def start_drawing(self):
        self.stacked_widget.setCurrentIndex(5)

    def change_section(self, index):
        if index >= 0 and self.current_user:
            sections = self.current_user.list_sections()
            if index < len(sections):
                self.current_section = sections[index]

    def create_new_section(self):
        name, ok = QInputDialog.getText(self, "Новый раздел", "Введите название раздела:")
        if not ok or not name.strip():
            return
        color_dialog = QColorDialog(self)
        color_dialog.setWindowTitle("Выберите цвет для раздела")
        color_dialog.setCurrentColor(QColor(138, 43, 226))
        color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)
        if color_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_color = color_dialog.currentColor()
            color_name = selected_color.name()
            try:
                self.current_user.create_section(name, color_name)
                self.current_section = \
                    [section for section in self.current_user.list_sections() if section.name == name][0]
                self.show_message("Успех", "Раздел успешно создан!")
                self.show_sections()
            except OccupiedName as e:
                self.show_message("Ошибка", str(e))
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось создать раздел: {str(e)}")

    def go_back_to_sections(self):
        self.current_folder_id = None
        self.show_sections()

    def show_note_menu(self):
        menu = QMenu(self)
        insert_image_action = QAction("Вставить фото", self)
        # noinspection PyUnresolvedReferences
        insert_image_action.triggered.connect(self.insert_image)
        menu.addAction(insert_image_action)
        draw_action = QAction("Создать рисунок", self)
        # noinspection PyUnresolvedReferences
        draw_action.triggered.connect(self.start_drawing)
        menu.addAction(draw_action)
        gigachat_action = QAction("GigaChat", self)
        # noinspection PyUnresolvedReferences
        gigachat_action.triggered.connect(self.show_gigachat_dialog)
        menu.addAction(gigachat_action)
        delete_note_action = QAction("Удалить заметку", self)
        # noinspection PyUnresolvedReferences
        delete_note_action.triggered.connect(self.delete_current_note)
        menu.addAction(delete_note_action)
        menu.exec(self.note_page.menu_btn.mapToGlobal(self.note_page.menu_btn.rect().bottomLeft()))

    def show_gigachat_dialog(self):
        if not self.current_note_id:
            self.show_message("Ошибка", "Сначала создайте заметку!")
            return
        dialog = GigaChatDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            function, query = dialog.get_input()
            if not query.strip():
                self.show_message("Ошибка", "Запрос не может быть пустым!")
                return
            self.handle_gigachat_action(function, query)

    def handle_gigachat_action(self, function, query):
        try:
            if function == "Помощь":
                result = get_help(query)
                self.show_text_result_dialog("Результат помощи", result)
            elif function == "Краткое содержание":
                result = summary(query)
                self.show_text_result_dialog("Краткое содержание", result)
            elif function == "Генерация фото":
                photo_name, ok = QInputDialog.getText(
                    self, "Название фото", "Введите название фото:",
                    text=f"Фото {len(list_notes(self.current_folder_id or self.current_section.id_root)) + 1}"
                )
                if not ok or not photo_name.strip():
                    self.show_message("Ошибка", "Название фото не может быть пустым!")
                    return
                if not photo_name.endswith('.png'):
                    photo_name += '.png'
                photo_name_for_markdown = photo_name.replace('_', ' ')
                try:
                    saved_path = giga_photo(self.current_note_id, photo_name, query)
                    self.note_page.note_edit.insertPlainText(f"\n![{photo_name_for_markdown}]({saved_path})\n")
                    self.show_message("Успех", "Фото успешно сгенерировано и добавлено в заметку!")
                except OccupiedName:
                    self.show_message("Ошибка", f"Фото с именем '{photo_name}' уже существует!")
        except NotPhoto:
            self.show_message("Ошибка", "GigaChat не смог сгенерировать изображение по описанию.")
        except TooMany:
            self.show_message("Ошибка", "Слишком много запросов. Попробуйте позже.")
        except NotEthical:
            self.show_message("Ошибка", "GigaChat отказался отвечать по моральным соображениям.")
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка при выполнении запроса: {str(e)}")

    def show_text_result_dialog(self, title, text):
        dialog = TextResultDialog(title, text, self)
        dialog.exec()

    def show_editor_context_menu(self, position):
        self.note_page.note_edit.createStandardContextMenu(position).exec(
            self.note_page.note_edit.mapToGlobal(position))

    def insert_image(self):
        if not self.current_note_id:
            self.show_message("Ошибка", "Сначала создайте заметку!")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            try:
                saved_path = new_photo(self.current_note_id, file_path, 700)
                image_name = file_path.split('/')[-1]
                image_name_for_markdown = image_name.replace('_', ' ')
                self.note_page.note_edit.insertPlainText(f"\n![{image_name_for_markdown}]({saved_path})\n")
            except OccupiedName as e:
                self.show_message("Ошибка", str(e))
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось вставить изображение: {str(e)}")

    def insert_drawing(self, filename, drawing_name="Рисунок"):
        drawing_name_for_markdown = drawing_name.replace('_', ' ')
        self.note_page.note_edit.insertPlainText(f"\n![{drawing_name_for_markdown}]({filename})\n")

    def delete_current_note(self):
        if not self.current_note_id:
            self.show_message("Ошибка", "Нет заметки для удаления")
            return
        reply = QMessageBox.question(
            self, 'Удаление заметки',
            'Вы уверены, что хотите удалить текущую заметку?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_note(self.current_note_id)
                self.current_note_id = None
                self.current_note_name = None
                self.is_new_note = False
                self.return_to_previous_page()
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось удалить заметку: {str(e)}")

    def on_preview_context_menu(self, position):
        anchor = self.note_page.preview.anchorAt(position)
        if anchor.startswith("image:"):
            img_id = anchor.split(":")[1]
            menu = QMenu(self)
            resize_action = QAction("Изменить размер", self)
            # noinspection PyUnresolvedReferences
            resize_action.triggered.connect(lambda: self.resize_image(img_id))
            menu.addAction(resize_action)
            menu.exec(self.note_page.preview.mapToGlobal(position))

    def resize_image(self, img_id):
        photo_sizes = get_photos(self.current_note_id)
        photo_id = None
        for pid, size in photo_sizes:
            if str(pid) == img_id:
                photo_id = pid
                current_size = size
                break
        if photo_id is None:
            self.show_message("Ошибка", "Не удалось найти изображение в базе данных!")
            return
        size, ok = QInputDialog.getInt(
            self, "Изменить размер изображения", "Новый размер (пиксели):", current_size, 50, 1200, 25)
        if ok:
            try:
                resize_photo(photo_id, size)
                self.image_sizes[img_id] = size
                self.update_preview()
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось изменить размер изображения: {str(e)}")

    def update_preview(self):
        if self._is_programmatic_change:
            return

        markdown_text = self.note_page.note_edit.toPlainText()
        if self.current_note_id:
            self.image_sizes = {str(pid): size for pid, size in get_photos(self.current_note_id)}
        html = self.markdown_to_html(markdown_text)

        self._is_programmatic_change = True
        try:
            self.note_page.preview.setHtml(html)
        finally:
            self._is_programmatic_change = False

        cursor = self.note_page.note_edit.textCursor()
        cursor_pos = cursor.position()
        total_length = len(markdown_text)

        scroll_bar = self.note_page.preview.verticalScrollBar()
        if total_length > 0:
            if len(markdown_text.split('\n')) <= 1 and total_length < 100:
                scroll_bar.setValue(0)
            else:
                relative_pos = cursor_pos / total_length
                max_scroll = scroll_bar.maximum()
                target_scroll = int(max_scroll * relative_pos)
                scroll_bar.setValue(target_scroll)
        else:
            scroll_bar.setValue(0)

    def markdown_to_html(self, markdown_text):
        html = """<html>
        <head>
        <style>
            body { line-height: 1; font-size: 16px; color: white; max-width: 800px; margin: 0 auto; padding: 20px; 
            font-family: Consolas, monospace; }
            h1 { font-size: 24px; font-weight: bold; color: white; }
            h2 { font-size: 22px; font-weight: bold; color: white; }
            h3 { font-size: 20px; font-weight: bold; color: white; }
            h4 { font-size: 18px; font-weight: bold; color: white; }
            h5 { font-size: 16px; font-weight: bold; color: white; }
            strong, b { font-weight: bold; }
            em, i { font-style: italic; }
            s, strike, del { text-decoration: line-through; }
            code { background-color: grey; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
            pre { background-color: grey; padding: 10px; border-radius: 5px; overflow-x: auto; }
            a { color: #8A2BE2; text-decoration: underline; }
            a[href^="image:"] { color: #9055a2; text-decoration: none; }
            img { display: block; margin: 10px 0; }
            blockquote { color: #6a737d; font-style: italic; border-left: 3px solid #8A2BE2; padding-left: 10px; 
            margin-left: 0; }
            hr { border: none; border-top: 1px solid darkgrey; margin: 10px 0; }
            table, th, td { color: #8A2BE2; border: 1px solid #ddd; padding: 8px; text-align: left; }
            table { border-collapse: collapse; width: 100%; margin: 15px 0; }
            th { background-color: #f2f2f2; }
            p { margin: 2px 0; }
            br { line-height: 1.0; }
        </style>
        </head>
        <body>
        """
        lines = markdown_text.split('\n')
        in_code_block = False
        img_counter = 0
        paragraph_open = False
        photo_sizes = get_photos(self.current_note_id) if self.current_note_id else []
        photo_id_list = [str(pid) for pid, _ in photo_sizes]

        for line in lines:
            line = line.rstrip()
            if line.strip() == '```':
                if paragraph_open:
                    html += "</p>"
                    paragraph_open = False
                in_code_block = not in_code_block
                html += "<pre><code>" if in_code_block else "</code></pre>"
                continue
            if in_code_block:
                html += line + "\n"
                continue

            if not line.strip():
                if paragraph_open:
                    html += "<br>"
                continue

            if not paragraph_open:
                html += "<p>"
                paragraph_open = True

            img_matches = re.finditer(r"!\[(.*?)\]\((.*?)\)", line)
            for match in img_matches:
                if img_counter < len(photo_id_list):
                    img_id = photo_id_list[img_counter]
                    img_counter += 1
                    alt_text = match.group(1).replace('_', ' ')
                    img_url = match.group(2)
                    img_size = self.image_sizes.get(img_id, 700)
                    img_tag = f'</p><a name="image:{img_id}" href="image:{img_id}"><img src="{img_url}" alt="{alt_text}" style="max-width:{img_size}px; max-height:{img_size}px;"></a><p>'
                    line = line.replace(match.group(0), img_tag)

            line = re.sub(r"^# (.*?)$", r"</p><h1>\1</h1><p>", line)
            line = re.sub(r"^## (.*?)$", r"</p><h2>\1</h2><p>", line)
            line = re.sub(r"^### (.*?)$", r"</p><h3>\1</h3><p>", line)
            line = re.sub(r"^#### (.*?)$", r"</p><h4>\1</h4><p>", line)
            line = re.sub(r"^##### (.*?)$", r"</p><h5>\1</h5><p>", line)
            line = re.sub(r"^###### (.*?)$", r"</p><h6>\1</h6><p>", line)
            line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            line = re.sub(r"__(.*?)__", r"<strong>\1</strong>", line)
            line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)
            line = re.sub(r"_(.*?)_", r"<em>\1</em>", line)
            line = re.sub(r"~~(.*?)~~", r"<s>\1</s>", line)
            line = re.sub(r"`(.+?)`", r"<code>\1</code>", line)
            line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)
            line = re.sub(r"^>\s(.*?)$", r"</p><blockquote>\1</blockquote><p>", line)
            line = re.sub(r"^[-*_]{3,}$", r"</p><hr><p>", line)

            if "|" in line and "-" not in line:
                cells = [cell.strip() for cell in line.split("|") if cell.strip()]
                line = "</p><table><tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr></table><p>"
            elif "|" in line and "-" in line:
                continue

            html += line + "<br>"

        if paragraph_open:
            html += "</p>"
        html += "</body></html>"
        return html

    def show_context_menu(self, position, section):
        sender = self.sender()
        if not isinstance(sender, QListWidget):
            return
        item = sender.itemAt(position)
        if not item:
            return
        menu = QMenu()
        if item.data(Qt.ItemDataRole.UserRole + 1) == "folder":
            delete_action = QAction("Удалить папку", self)
            # noinspection PyUnresolvedReferences
            delete_action.triggered.connect(lambda: self.ui_delete_folder(item, section))
            menu.addAction(delete_action)
        else:
            delete_action = QAction("Удалить заметку", self)
            # noinspection PyUnresolvedReferences
            delete_action.triggered.connect(lambda: self.ui_delete_note(item))
            menu.addAction(delete_action)
        menu.exec(self.sender().mapToGlobal(position))

    def ui_delete_folder(self, item, section):
        folder_id = item.data(Qt.ItemDataRole.UserRole)
        if not folder_is_empty(folder_id):
            reply = QMessageBox.question(
                self, 'Удаление папки',
                'Внутри папки есть заметки, которые будут удалены при удалении папки. Продолжить?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    delete_folder(folder_id)
                    self.show_sections()
                except Exception as e:
                    self.show_message("Ошибка", f"Не удалось удалить папку: {str(e)}")
        else:
            try:
                delete_folder(folder_id)
                self.show_sections()
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось удалить папку: {str(e)}")

    def ui_delete_note(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, 'Удаление заметки',
            'Вы уверены, что хотите удалить заметку?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_note(note_id)
                if self.current_folder_id:
                    self.show_folder()
                else:
                    self.show_sections()
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось удалить заметку: {str(e)}")

    def ui_login_user(self):
        login = self.login_page.login_edit.text()
        password = self.login_page.password_edit.text()
        if not all([login, password]):
            self.show_message("Ошибка", "Все поля должны быть заполнены!")
            return
        try:
            self.current_user = login_user(login, password)
            self.current_folder_id = None
            self.show_message("Успех", "Вы успешно вошли!")
            self.show_sections()
        except UserNotExists as e:
            self.show_message("Ошибка входа", str(e))
        except IncorrectPassword as e:
            self.show_message("Ошибка входа", str(e))
        except Exception as e:
            self.show_message("Ошибка", f"Неизвестная ошибка: {str(e)}")

    def ui_register_user(self):
        username = self.registration_page.username_edit.text().strip()
        email = self.registration_page.email_edit.text().strip()
        password = self.registration_page.password_edit.text()
        confirm_password = self.registration_page.confirm_password_edit.text()
        if not all([username, email, password, confirm_password]):
            self.show_message("Ошибка", "Все поля должны быть заполнены!")
            return
        for x in '<>@"\'/\\|{}[]()~:;,#$%^&*+=`!?':
            if x in username:
                self.show_message("Ошибка",
                                  "Имя пользователя содержит запрещенные символы: <>@\"\'/\\|{}[]()~:;,#$%^&*+=`!?")
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

    def create_new_folder(self):
        if not self.current_section:
            self.show_message("Ошибка", "Сначала выберите раздел!")
            return
        folder_name, ok = QInputDialog.getText(self, "Новая папка", "Введите название папки:")
        if not ok:
            return
        if not folder_name.strip():
            self.show_message("Ошибка", "Название папки не может быть пустым!")
            return
        try:
            self.current_section.create_folder(folder_name)
            self.show_sections()
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось создать папку: {str(e)}")

    def return_to_previous_page(self):
        if self.stacked_widget.currentIndex() == 5:
            self.stacked_widget.setCurrentIndex(4)
        elif self.stacked_widget.currentIndex() == 4 and self.is_new_note and self.current_note_id:
            try:
                delete_note(self.current_note_id)
                self.current_note_id = None
                self.current_note_name = None
                self.is_new_note = False
            except Exception as e:
                self.show_message("Ошибка", f"Не удалось удалить несохранённую заметку: {str(e)}")
            if self.current_folder_id:
                self.show_folder()
            else:
                self.show_sections()
        elif self.current_folder_id:
            self.show_folder()
        else:
            self.show_sections()

    def save_current_note(self):
        text = self.note_page.note_edit.toPlainText()
        if not text.strip():
            self.show_message("Ошибка", "Заметка не может быть пустой!")
            return
        try:
            if not self.current_note_id:
                self.show_message("Ошибка", "Заметка не создана!")
                return
            save_note(self.current_note_id, text,
                      self.current_note_name if hasattr(self, 'current_note_name') and self.current_note_name else "")
            self.show_message("Успех", "Заметка успешно создана!" if self.is_new_note else "Заметка успешно сохранена!")
            self.is_new_note = False
            self.current_note_name = None
            self.return_to_previous_page()
        except OccupiedName as e:
            self.show_message("Ошибка", str(e))
        except NotChange:
            self.show_message("Предупреждение", "Заметка не была изменена.")
        except Exception as e:
            self.show_message("Ошибка", f"Ошибка сохранения: {str(e)}")

    def ui_logout(self):
        if not self.current_user:
            self.stacked_widget.setCurrentIndex(1)
            self.clear_login_registration_fields()
            return

        sync_result = is_sync()

        if not sync_result:
            reply = QMessageBox.question(
                self, 'Выход',
                'Данные не синхронизированы с сервером. Попытаться синхронизировать перед выходом?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    sync_result = synchro()
                    if not sync_result:
                        self.show_message("Ошибка",
                                          "Не удалось синхронизировать с сервером."
                                          " Возможно, нет соединения с интернетом.")
                        reply = QMessageBox.question(
                            self, 'Выход',
                            'Синхронизация не удалась. Выйти без синхронизации?',
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        sync_result = (reply == QMessageBox.StandardButton.Yes)
                except Exception as e:
                    self.show_message("Ошибка", f"Ошибка синхронизации: {str(e)}")
                    reply = QMessageBox.question(
                        self, 'Выход',
                        'Синхронизация не удалась. Выйти без синхронизации?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    sync_result = (reply == QMessageBox.StandardButton.Yes)
            elif reply == QMessageBox.StandardButton.No:
                sync_result = True
            else:
                return

        if sync_result:
            try:
                logout_user()
                self.current_user = None
                self.current_note_id = None
                self.current_folder_id = None
                self.stacked_widget.setCurrentIndex(0)
                self.clear_login_registration_fields()
            except Exception as e:
                self.show_message("Ошибка", f"Ошибка при выходе: {str(e)}")

    def closeEvent(self, event):
        if self.current_user and not is_sync():
            reply = QMessageBox.question(
                self, 'Выход из приложения',
                'Данные не синхронизированы с сервером. Попытаться синхронизировать перед выходом?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if not synchro():
                        self.show_message("Ошибка", "Не удалось синхронизировать с сервером. Возможно, нет соединения.")
                        reply = QMessageBox.question(
                            self, 'Выход из приложения',
                            'Синхронизация не удалась. Закрыть приложение без синхронизации?',
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply != QMessageBox.StandardButton.Yes:
                            event.ignore()
                            return
                except Exception as e:
                    self.show_message("Ошибка", f"Ошибка синхронизации: {str(e)}")
                    reply = QMessageBox.question(
                        self, 'Выход из приложения',
                        'Синхронизация не удалась. Закрыть приложение без синхронизации?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        event.ignore()
                        return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        event.accept()

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()


app = QApplication(sys.argv)
app.setFont(QFont("Consolas", 10))
app.setStyle("Fusion")
window = MainWindow()
window.show()
app.exec()
