from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

class BaseModal(QDialog):
    """
    Clase base para modales en la app.

    Aplica configuración común a todos los modales:
    - Título de la ventana
    - Modalidad de aplicación
    - Flags de ventana tipo diálogo
    - Tamaño mínimo
    - Posicionamiento centrado sobre el padre

    Args:
        parent (QWidget): Ventana padre del modal.
        title (str): Título de la ventana. Default: "Modal"
        width (int): Ancho mínimo de la ventana. Default: 300
    """

    def __init__(self, parent=None, title="Modal", width=300, max_width=500):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(width)
        self.setMaximumWidth(max_width)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Centrar sobre el padre si existe
        if parent:
            self.adjustSize()
            geom = parent.frameGeometry()
            center = geom.center()
            self.move(center - self.rect().center())
class ConfirmModal(BaseModal):
    """
    Modal de confirmación con dos botones.

    Para usarlo se debe crear la instancia y llamar el método exec(),
    el cual retorna el resultado de la confirmación.

    Args:
        parent (QWidget): Ventana padre del modal.
        title (str): Título del modal. Default: "Confirmar"
        body (str): Texto del cuerpo del mensaje. Default: "¿Estás seguro de continuar?"
        confirm_btn_text (str): Texto del botón de confirmar. Default: "Aceptar"
        cancel_btn_text (str): Texto del botón de cancelar. Default: "Cancelar"

    Returns:
        result (QDialog.DialogCode): Código de resultado (Accepted o Rejected).
    """

    def __init__(self, parent=None, title="Confirmar", body="¿Estás seguro de continuar?", confirm_btn_text="Aceptar", cancel_btn_text="Cancelar"):
        super().__init__(parent, title)

        layout = QVBoxLayout()

        label = QLabel(body)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_ok = QPushButton(confirm_btn_text)
        btn_cancel = QPushButton(cancel_btn_text)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)


class InfoModal(BaseModal):
    """
    Modal de información con un solo botón.

    Para usarlo se debe crear la instancia y llamar el método exec(),
    el cual retorna el click del usuario en el botón Ok.

    Args:
        parent (QWidget): Ventana padre del modal.
        title (str): Título del modal. Default: "Aviso"
        body (str): Texto del cuerpo del mensaje. Default: "Esto es un aviso"
        btn_text (str): Texto del botón Ok. Default: "Ok"

    Returns:
        result (QDialog.DialogCode.Accepted): Código de resultado si se presiona Ok.
    """

    def __init__(self, parent=None, title="Aviso", body="Esto es un aviso", btn_text="Ok"):
        super().__init__(parent, title)

        layout = QVBoxLayout()

        label = QLabel(body)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_ok = QPushButton(btn_text)
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


class InputModal(BaseModal):
    """
    Modal con campo de texto y dos botones.

    Devuelve una tupla con el estado de confirmación y el texto ingresado.

    Args:
        parent (QWidget): Ventana padre del modal.
        title (str): Título del modal. Default: "Ingresar texto"
        body (str): Texto del cuerpo del mensaje. Default: "Escribe algo:"
        confirm_btn_text (str): Texto del botón de confirmar. Default: "Confirmar"
        cancel_btn_text (str): Texto del botón de cancelar. Default: "Cancelar"

    Returns:
        tuple[bool, str]: 
            - bool: True si se confirmó, False si se canceló.
            - str: Texto ingresado en el campo.
    """

    def __init__(self, parent=None, title="Ingresar texto", body="Escribe algo:", confirm_btn_text="Confirmar", cancel_btn_text="Cancelar"):
        super().__init__(parent, title)
        self.result = (False, "")

        layout = QVBoxLayout()

        label = QLabel(body)
        label.setWordWrap()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        btn_confirm = QPushButton(confirm_btn_text)
        btn_cancel = QPushButton(cancel_btn_text)
        btn_confirm.clicked.connect(self.on_confirm)
        btn_cancel.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_confirm)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def on_confirm(self):
        self.result = (True, self.input_field.text())
        self.accept()

    def get_result(self) -> tuple[bool, str]:
        return self.result
    
class DirectoryModal(BaseModal):
    """
    Modal para seleccionar un directorio.

    Devuelve una tupla: (confirmado: bool, ruta: str)

    Args:
        parent (QWidget): Ventana padre del modal.
        title (str): Título del modal. Default: "Seleccionar directorio"
        body (str): Texto del cuerpo del mensaje. Default: "Selecciona una carpeta:"
        default_path (str): Ruta inicial que se muestra al abrir el modal.
        confirm_btn_text (str): Texto del botón de confirmar. Default: "Confirmar"
        cancel_btn_text (str): Texto del botón de cancelar. Default: "Cancelar"

    Returns:
        tuple[bool, str]:
            - bool: True si se confirmó, False si se canceló.
            - str: Ruta seleccionada.
    """
    def __init__(
        self,
        parent=None,
        title="Seleccionar directorio",
        body="Selecciona una carpeta:",
        default_path="",
        confirm_btn_text="Confirmar",
        cancel_btn_text="Cancelar"
    ):
        super().__init__(parent, title)
        self.result = (False, "")
        self.default_path = default_path

        layout = QVBoxLayout()

        label = QLabel(body)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setText(default_path)
        layout.addWidget(self.path_display)

        btn_select = QPushButton("Buscar carpeta...")
        btn_select.clicked.connect(self.select_directory)
        layout.addWidget(btn_select)

        btn_confirm = QPushButton(confirm_btn_text)
        btn_cancel = QPushButton(cancel_btn_text)
        btn_confirm.clicked.connect(self.on_confirm)
        btn_cancel.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_confirm)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def select_directory(self):
        from PyQt6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", self.default_path)
        if directory:
            self.path_display.setText(directory)

    def on_confirm(self):
        self.result = (True, self.path_display.text())
        self.accept()

    def get_result(self) -> tuple[bool, str]:
        return self.result
