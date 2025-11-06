from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
import json
from src.utils.log import create_log
from src.utils.modal import *
from ..settings.settings import SettingsManager
from .styles import APP_GLOBAL_STYLES
import platform
import subprocess

class App(QWidget):

    def __init__(self, settings_instance:SettingsManager):
        super().__init__()
        create_log('App', 'Inicializando app')
        self._settings = settings_instance
        self._selected_invoice = ""
        self._editor_inputs = {}
        self._openUI()
        self.setStyleSheet(APP_GLOBAL_STYLES)
        self.setWindowIcon(QIcon(self._settings.ICON_FILEPATH))
        # Verificar si la ruta de facturas está vacía
        if not self._settings.prints_path.strip():
            if not self._prompt_for_initial_prints_path():
                QTimer.singleShot(0, QApplication.instance().quit)
                return

    def _openUI(self) -> None:
        self.setGeometry(0, 0, self._settings.WINDOW_WIDTH, self._settings.WINDOW_HEIGHT)
        self.setWindowTitle(self._settings.APP_TITLE)
        self._center_on_screen()

        main_layout = QHBoxLayout(self)

        # 🔹 Sección de lista de facturas
        generated_invoices_layout = QVBoxLayout()
        label_generated_invoices = QLabel('Facturas generadas')
        label_generated_invoices.setProperty('class', 'main-text')
        generated_invoices_layout.addWidget(label_generated_invoices)

        self._generated_invoices_list_widget = QListWidget()
        self._generated_invoices_list_widget.setFixedWidth(300)
        generated_invoices_layout.addWidget(self._generated_invoices_list_widget)

        self.selected_prints_path_label = QLabel(f'Ruta seleccionada: {self._settings.prints_path}')
        self.selected_prints_path_label.setFixedWidth(300)
        self.selected_prints_path_label.setWordWrap(True)
        generated_invoices_layout.addWidget(self.selected_prints_path_label)

        change_prints_path_btn = QPushButton('Cambiar carpeta')
        open_prints_path_folder_btn = QPushButton('Abrir carpeta')
        generated_invoices_layout.addWidget(change_prints_path_btn)
        generated_invoices_layout.addWidget(open_prints_path_folder_btn)

        # 🔹 Sección de visualizador/editor
        invoices_viewer_layout = QVBoxLayout()

        invoices_viewer_navbar = QHBoxLayout()
        self._btn_editor = QPushButton('Editor')
        self._btn_viewer = QPushButton('Visualizador')
        invoices_viewer_navbar.addWidget(self._btn_editor)
        invoices_viewer_navbar.addWidget(self._btn_viewer)
        invoices_viewer_layout.addLayout(invoices_viewer_navbar)

        self.stack = QStackedWidget()
        invoices_viewer_layout.addWidget(self.stack)

        # 🔹 Vista Editor
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)

        editor_top_section = QHBoxLayout()
        editor_top_title_label = QLabel("Constructor de facturas.")
        editor_top_title_label.setProperty('class', 'main-text')
        editor_top_section.addWidget(editor_top_title_label)

        editor_top_section_right_container = QVBoxLayout()
        editor_top_section_right_container.addWidget(QLabel("Opacidad de la factura"), alignment=Qt.AlignmentFlag.AlignCenter)
        editor_invoice_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        editor_invoice_opacity_slider.setFixedWidth(150)
        editor_invoice_opacity_slider.setRange(0, 100)
        editor_invoice_opacity_slider.setSingleStep(1)
        editor_invoice_opacity_slider.setValue(100)
        editor_top_section_right_container.addWidget(editor_invoice_opacity_slider)
        editor_top_section.addLayout(editor_top_section_right_container)
        editor_layout.addLayout(editor_top_section)

        editor_scroll_area = QScrollArea()
        editor_scroll_area.setWidgetResizable(True)

        editor_invoice_background_container = QWidget()
        editor_invoice_background_container.setFixedSize(
            self._settings.INVOICE_WIDTH,
            self._settings.INVOICE_HEIGHT
        )

        self._editor_invoice_label = QLabel(editor_invoice_background_container)
        self._editor_invoice_label.setPixmap(QPixmap(self._settings.INVOICE_BACKGROUND_PATH).scaled(
            self._settings.INVOICE_WIDTH,
            self._settings.INVOICE_HEIGHT,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self._editor_invoice_label.setGeometry(0, 0, self._settings.INVOICE_WIDTH, self._settings.INVOICE_HEIGHT)

        self._load_editor_inputs(parent=editor_invoice_background_container)

        editor_center_wrapper = QWidget()
        editor_center_layout = QHBoxLayout(editor_center_wrapper)
        editor_center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor_center_layout.setContentsMargins(0, 0, 0, 40)
        editor_center_layout.addWidget(editor_invoice_background_container)

        editor_scroll_area.setWidget(editor_center_wrapper)
        editor_layout.addWidget(editor_scroll_area)

        editor_action_buttons_bar = QHBoxLayout()
        clear_all_inputs_btn = QPushButton('Vaciar todos los campos')
        generate_pdf_btn = QPushButton('Generar PDF')
        editor_action_buttons_bar.addWidget(clear_all_inputs_btn)
        editor_action_buttons_bar.addWidget(generate_pdf_btn)
        editor_layout.addLayout(editor_action_buttons_bar)

        self.stack.addWidget(editor_container)

        # 🔹 Vista Visualizador
        viewer_container = QWidget()
        viewer_layout = QVBoxLayout(viewer_container)

        # Top bar horizontal
        viewer_top_container = QHBoxLayout()

        # Nombre del archivo seleccionado
        self._viewer_invoice_file_name_label = QLabel()
        self._viewer_invoice_file_name_label.setProperty('class', 'main-text')
        viewer_top_container.addWidget(self._viewer_invoice_file_name_label)

        # Contenedor vertical para etiqueta + slider
        viewer_top_section_right_container = QVBoxLayout()
        viewer_top_section_right_container.addWidget(QLabel("Opacidad de la factura"), alignment=Qt.AlignmentFlag.AlignCenter)

        viewer_invoice_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        viewer_invoice_opacity_slider.setFixedWidth(150)
        viewer_invoice_opacity_slider.setRange(0, 100)
        viewer_invoice_opacity_slider.setSingleStep(1)
        viewer_invoice_opacity_slider.setValue(100)
        viewer_top_section_right_container.addWidget(viewer_invoice_opacity_slider)

        viewer_top_container.addLayout(viewer_top_section_right_container)
        viewer_layout.addLayout(viewer_top_container)
                
        viewer_scroll_area = QScrollArea()
        viewer_scroll_area.setWidgetResizable(True)

        image_holder = QWidget()
        image_holder.setFixedSize(self._settings.INVOICE_WIDTH, self._settings.INVOICE_HEIGHT)

        self._viewer_invoice_background_label = QLabel(image_holder)
        self._viewer_invoice_background_label.setPixmap(QPixmap(self._settings.INVOICE_BACKGROUND_PATH).scaled(
            self._settings.INVOICE_WIDTH,
            self._settings.INVOICE_HEIGHT,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self._viewer_invoice_background_label.setGeometry(0, 0, self._settings.INVOICE_WIDTH, self._settings.INVOICE_HEIGHT)

        self._viewer_invoice_overlay_label = QLabel(image_holder)
        self._viewer_invoice_overlay_label.setGeometry(0, 0, self._settings.INVOICE_WIDTH, self._settings.INVOICE_HEIGHT)
        self._viewer_invoice_overlay_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._viewer_invoice_overlay_label.setStyleSheet("background: transparent;")
        self._viewer_invoice_overlay_label.setPixmap(QPixmap())

        viewer_center_wrapper = QWidget()
        viewer_center_layout = QHBoxLayout(viewer_center_wrapper)
        viewer_center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        viewer_center_layout.setContentsMargins(0, 0, 0, 40)
        viewer_center_layout.addWidget(image_holder)

        viewer_scroll_area.setWidget(viewer_center_wrapper)
        viewer_layout.addWidget(viewer_scroll_area)

        viewer_action_buttons_bar = QHBoxLayout()
        delete_invoice_btn = QPushButton('Eliminar Factura')
        print_invoice_btn = QPushButton('Imprimir Factura')
        viewer_action_buttons_bar.addWidget(delete_invoice_btn)
        viewer_action_buttons_bar.addWidget(print_invoice_btn)
        viewer_layout.addLayout(viewer_action_buttons_bar)

        self.stack.addWidget(viewer_container)

        self._btn_editor.setCheckable(True)
        self._btn_viewer.setCheckable(True)

        self._tab_button_group = QButtonGroup()
        self._tab_button_group.setExclusive(True)
        self._tab_button_group.addButton(self._btn_editor, 0)
        self._tab_button_group.addButton(self._btn_viewer, 1)

        self._tab_button_group.idClicked.connect(self._on_tab_switched)

        self._btn_editor.setChecked(True)
        self.stack.setCurrentIndex(0)

        # 🔹 Conectar signals
        editor_invoice_opacity_slider.valueChanged.connect(self._on_invoice_opacity_changed)
        viewer_invoice_opacity_slider.valueChanged.connect(self._on_viewer_invoice_opacity_changed)
        clear_all_inputs_btn.clicked.connect(self._on_clear_all_inputs_btn_pressed)
        generate_pdf_btn.clicked.connect(self._on_generate_pdf_btn_pressed)
        delete_invoice_btn.clicked.connect(self._on_delete_invoice_btn_pressed)
        print_invoice_btn.clicked.connect(self._on_print_invoice_btn_pressed)
        change_prints_path_btn.clicked.connect(self._on_change_prints_path_btn_pressed)
        open_prints_path_folder_btn.clicked.connect(self._on_open_prints_path_folder_btn_pressed)
        self._generated_invoices_list_widget.itemClicked.connect(self._on_invoice_selected)

        main_layout.addLayout(generated_invoices_layout)
        main_layout.addLayout(invoices_viewer_layout)

        self.setLayout(main_layout)
        self.show()

        if self._settings.DEBUG:
            self._geometry_update_timer = QTimer(self)
            self._geometry_update_timer.timeout.connect(self._update_inputs_geometry)
            self._geometry_update_timer.start(1000)

        self._update_prints_in_prints_path()

    def _on_open_prints_path_folder_btn_pressed(self)->None:
        """
        Abre la carpeta de facturas especificada.
        """
        if not os.path.isdir(self._settings.prints_path):
            if self._settings.DEBUG:
                print("Ruta inválida o no existe:", self._settings.prints_path)
            else:
                create_log('App', f'No se pudo abrir la carpeta especificada de las facturas porque no es una ruta valida. Ruta: {self._settings.prints_path}')
            return

        sistema = platform.system()

        try:
            if sistema == "Windows":
                os.startfile(self._settings.prints_path)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", self._settings.prints_path])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", self._settings.prints_path])
            else:
                if self._settings.DEBUG:
                    print("Sistema operativo no soportado:", sistema)
                else:
                    modal = InfoModal(self, 'Abrir Carpeta', f'Tu sistema operativo ({sistema}) no es soportado por nuestra app para abrir la carpeta {self._settings.prints_path}.\nLe invitamos a abrirla manualmente.')
                    modal.exec()
                    create_log('App', f'Sistema operativo no soportado ({sistema}) para abrir la carpeta de facturas.')
        except Exception as e:
            if self._settings.DEBUG:
                print("Error al abrir la carpeta:", e)
            else:
                create_log('App', f'Error al tratar de abrir la carpeta de la ruta de facturas: {e}')

    def _on_viewer_invoice_opacity_changed(self, value: int) -> None:
        effect = QGraphicsOpacityEffect()
        if value > 0:
            opacity = value/100
            if opacity < 0:
                opacity = 0
            elif opacity > 1:
                opacity = 1
            effect.setOpacity(opacity)
        else:
            effect.setOpacity(0.0)
        self._viewer_invoice_background_label.setGraphicsEffect(effect)

    def _on_invoice_selected(self, item: QListWidgetItem, skip_tab_switch=False) -> None:
        """
        Signal `itemClicked` para la lista de facturas en el UI.

        Args:
            item (QListWidgetItem): Item seleccionado.
            skip_tab_switch (bool): Se utiliza en el caso especifico en que se necesita
            omitir el cambio a la seccion de Visualizador de facturas.
        """
        invoice_path = os.path.join(self._settings.prints_path, item.text())
        pixmap = QPixmap(invoice_path).scaled(
            self._settings.INVOICE_WIDTH,
            self._settings.INVOICE_HEIGHT,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._viewer_invoice_overlay_label.setPixmap(pixmap)
        self._viewer_invoice_file_name_label.setText(item.text())
        if not skip_tab_switch:
            self._btn_viewer.click()
        self._selected_invoice = item.text()

    def _on_change_prints_path_btn_pressed(self)->None:
        """
        Signal `clicked` para el boton de `Cambiar ruta`.

        - Deshabilita la app.
        - Muestra un modal para cambiar el directorio de guardado de las facturas.
        - Si ese modal se confirma, se muestra un modal adicional para asegurar que
          el usuario desea realizar el cambio.
        - De ser asi, se utiliza `self._settings` para actualizar la ruta, y si el 
          resultado es correcto, se actualiza la lista de documentos en el UI y el
          label que indica la ruta seleccionada.
        """
        self.setEnabled(False)
        modal = DirectoryModal(parent=self, confirm_btn_text="Actualizar ruta",
                           body="Por favor, seleccione la nueva ruta en la que desea guardar sus facturas.", title="Actualizar ruta de facturas",
                            default_path=self._settings.prints_path)
        modal.exec()
        confirmed, new_path = modal.get_result()
        if confirmed:
            confirm_modal = ConfirmModal(self, body="¿Estás seguro que deseas cambiar la ruta de las facturas generadas? \n Puedes volver a la ruta anterior en cualquier momento...",
            confirm_btn_text='Si', cancel_btn_text='No')
            confirmed = confirm_modal.exec()
            if confirmed == QDialog.DialogCode.Accepted:
                result = self._settings.set_prints_path(new_path)
                if result:
                    self._update_prints_in_prints_path()
                    self.selected_prints_path_label.setText(f"Ruta seleccionada: {new_path}")
        self.setEnabled(True) 

    def _prompt_for_initial_prints_path(self) -> bool:
        """
        Solicita al usuario que configure la ruta de guardado de facturas si no está definida.

        Si la ruta actual está vacía, se propone automáticamente la carpeta `docs/` en la raíz del proyecto
        usando `self._settings.BASE_DIR`.

        Returns:
            bool: True si se configuró correctamente, False si el usuario canceló.
        """
        self.setEnabled(False)

        modal = DirectoryModal(
            parent=self,
            confirm_btn_text="Seleccionar ruta",
            body="Debes seleccionar una ruta para guardar tus facturas antes de continuar.",
            title="Ruta de guardado requerida",
        )
        modal.exec()
        confirmed, new_path = modal.get_result()

        if confirmed and new_path.strip():
            result = self._settings.set_prints_path(new_path)
            if result:
                self._update_prints_in_prints_path()
                self.selected_prints_path_label.setText(f"Ruta seleccionada: {new_path}")
                self.setEnabled(True)
                return True

        # Mostrar modal de cierre
        close_modal = InfoModal(
            self,
            title="Aplicación cerrada",
            body="No se ha seleccionado una ruta de guardado. La aplicación se cerrará.",
        )
        close_modal.exec()
        return False

    def _on_delete_invoice_btn_pressed(self) -> None:
        """
        Elimina la factura seleccionada y actualiza la lista de facturas en el UI.
        """
        if not hasattr(self, "_selected_invoice") or not self._selected_invoice\
            or self._selected_invoice == "":
            return
        self.setEnabled(False)
        confirm_modal = ConfirmModal(self, 'Eliminar Factura', 
        f"¿Estás seguro que deseas eliminar la factura {self._selected_invoice}? \n No podrás recuperar el documento luego de su eliminación.",
        'Eliminar')
        confirm_result = confirm_modal.exec()
        if confirm_result == QDialog.DialogCode.Accepted:
            self.setEnabled(True)
            invoice_path = os.path.join(self._settings.prints_path, self._selected_invoice)
            try:
                if os.path.exists(invoice_path):
                    os.remove(invoice_path)
                    if self._settings.DEBUG:
                        print("✅ Factura eliminada correctamente.")
                    else:
                        create_log('App', f'Se ha eliminado la factura {invoice_path}')
                else:
                    if self._settings.DEBUG:
                        print(f"Se trato de eliminar la factura {invoice_path} pero el archivo no existe.")
                    else:
                        create_log('App', f"Se trato de eliminar la factura {invoice_path} pero el archivo no existe.")
            except Exception as e:
                if self._settings.DEBUG:
                    print(f"Se trato de eliminar la factura {invoice_path} pero hubo un error: {e}.")
                else:
                    create_log('App', f"Se trato de eliminar la factura {invoice_path} pero hubo un error: {e}.")
                return
            self._update_prints_in_prints_path()
        else:
            self.setEnabled(True)


    def _on_print_invoice_btn_pressed(self) -> None:
        """
        Abre el diálogo de impresión del sistema operativo para imprimir la factura seleccionada.
        El archivo PDF se obtiene desde `self._settings.prints_path` + `self._selected_invoice`.
        """
        if not hasattr(self, "_selected_invoice") or not self._selected_invoice:
            self.setEnabled(False)
            info_modal = InfoModal(self, f"Debe seleccionar una factura para imprimir.")
            info_modal.exec()
            self.setEnabled(True)
            return
        invoice_path = os.path.join(self._settings.prints_path, self._selected_invoice)
        if not os.path.exists(invoice_path):
            if self._settings.DEBUG:
                print(f"Error al imprimir el documento {invoice_path}: El archivo no fue encontrado.")
            else:
                create_log('App', f"Error al imprimir el documento {invoice_path}: El archivo no fue encontrado.")
            self.setEnabled(False)
            info_modal = InfoModal(self, f"Error al imprimir el documento {invoice_path}: El archivo no fue encontrado. \n Por favor, contacte con un administrador.")
            info_modal.exec()
            self.setEnabled(True)
            return
        system = platform.system()
        try:
            if system == "Windows":
                # Usa el comando nativo de impresión
                os.startfile(invoice_path, "print")
            elif system == "Darwin":
                # macOS: usa el comando 'open' con opción de impresión
                subprocess.run(["open", "-a", "Preview", invoice_path])
            elif system == "Linux":
                # Linux: usa 'lp' o 'lpr' si están disponibles
                subprocess.run(["lp", invoice_path])
            else:
                self.setEnabled(False)
                info_modal = InfoModal(self, "Imprimir PDF", f'Tu sistema operativo ({system}) no esta soportado para impresion en nuestra App. \n Te invitamos a buscar el documento e imprimirlo manualmente.')
                info_modal.exec()
                self.setEnabled(True)
        except Exception as e:
            if self._settings.DEBUG:
                print(f'Error al imprimir el documento {invoice_path}: {e}')
            else:
                create_log('App', f'Error al imprimir el documento {invoice_path}: {e}')
            self.setEnabled(False)
            info_modal = InfoModal(self, "Imprimir PDF", f'Error al imprimir el documento.\n Por favor, intente imprimirlo manualmente.')
            info_modal.exec()
            ruta_pdf = os.path.join(self._settings.prints_path, self._selected_invoice)
            subprocess.Popen(f'explorer /select,"{ruta_pdf}"')
            self.setEnabled(True)

    def _on_generate_pdf_btn_pressed(self) -> None:
        """
        Genera un archivo PDF con los valores ingresados en los inputs del editor,
        posicionando cada texto según su geometría, escala y alineación definida en el archivo JSON.

        Solo se genera el PDF si al menos un campo ha sido rellenado (texto ingresado o selección activa).
        También imprime el símbolo ✔ en el campo correspondiente a la forma de pago seleccionada.

        El archivo se guarda en `self._settings.prints_path` con nombre basado en timestamp.
        """
        if not self._settings.prints_path or not os.path.isdir(self._settings.prints_path):
            info_modal = InfoModal(self, "Ruta inválida", "La ruta de guardado de facturas no está definida o no existe.")
            info_modal.exec()
            return
        try:
            width_pt = 8.5 * inch
            height_pt = 11 * inch

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"factura_{timestamp}.pdf"
            filepath = os.path.join(self._settings.prints_path, filename)

            c = canvas.Canvas(filepath, pagesize=(width_pt, height_pt))
            c.setFont("Helvetica", 10)

            scale_x = width_pt / self._settings.INVOICE_WIDTH
            scale_y = height_pt / self._settings.INVOICE_HEIGHT

            try:
                with open(self._settings.INPUTS_GEOMETRY_JSON_FILE, "r", encoding="utf-8") as f:
                    inputs_data = json.load(f)
            except Exception as e:
                if self._settings.DEBUG:
                    print("Error cargando inputs_geometry.json en _on_generate_pdf_btn_pressed:", e)
                else:
                    create_log('App', f"Error cargando inputs_geometry.json en _on_generate_pdf_btn_pressed: {e}")
                return

            campos_rellenados = 0

            for key, values in inputs_data.items():
                x, y, w, h, max_len, tipo, *rest = values
                alignment = rest[0] if rest else "left"

                widget = self._editor_inputs.get(key)
                if widget is None:
                    continue

                # Forma de pago se maneja aparte
                if tipo == "radio_button" and key.startswith("forma_pago_"):
                    continue

                if tipo == "radio_button":
                    value = "✔" if widget.isChecked() else ""
                elif tipo == "checkbox":
                    value = "✔" if widget.isChecked() else ""
                elif isinstance(widget, QLineEdit):
                    value = widget.text().strip()
                elif isinstance(widget, QTextEdit):
                    value = widget.toPlainText().strip()
                elif isinstance(widget, QComboBox):
                    value = widget.currentText().strip()
                elif isinstance(widget, QSpinBox):
                    value = str(widget.value())
                else:
                    value = ""

                if value:
                    campos_rellenados += 1
                    text_y = height_pt - ((y + 16) * scale_y)

                    # Alineación horizontal
                    if alignment == "center":
                        text_x = (x + w / 2) * scale_x
                        c.drawCentredString(text_x, text_y, value)
                    elif alignment == "right":
                        text_x = (x + w - 2) * scale_x
                        c.drawRightString(text_x, text_y, value)
                    else:  # left o default
                        text_x = (x + 2) * scale_x
                        c.drawString(text_x, text_y, value)

            # ✔ Imprimir símbolo en forma de pago seleccionada
            forma_pago = getattr(self, "forma_pago_selected", None)

            if forma_pago:
                key = f"forma_pago_{forma_pago}"
                if key in inputs_data:
                    x, y, w, h, *_ = inputs_data[key]
                    text_x = (x + 1) * scale_x
                    text_y = height_pt - ((y + 11) * scale_y)
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(text_x, text_y, "✔")
                    campos_rellenados += 1

            if campos_rellenados == 0:
                self.setEnabled(False)
                info_modal = InfoModal(self, "Generar PDF", 'Debes llenar al menos un campo para generar un documento.')
                info_modal.exec()
                self.setEnabled(True)
                return

            c.save()
            if self._settings.DEBUG:
                print(f"📄 Factura generada para impresión: {filepath}")
            else:
                create_log('App', f"📄 Factura generada para impresión: {filepath}")
            self._update_prints_in_prints_path()
        except Exception as e:
            if self._settings.DEBUG:
                print(f"No se pudo generar el pdf. Error: {e}")
            else:
                modal = InfoModal(self, 'Generar PDF', f'Error al generar el PDF: {e}\n Por favor, pongase en contacto con un administrador.')
                modal.exec()
                create_log('App', f'No se pudo generar el pdf {filepath}: {e}')


    def _on_clear_all_inputs_btn_pressed(self) -> None:
        self.setEnabled(False)
        modal = ConfirmModal(
            parent=self,
            title="Limpiar campos",
            body="¿Estás seguro de continuar? \nEsta accion borrara el contenido de todos los campos.",
            confirm_btn_text='Si', cancel_btn_text='No'
        )
        result = modal.exec()
        if result == QDialog.DialogCode.Accepted:
            parent = self._editor_invoice_label.parent()
            for child in parent.children():
                if isinstance(child, QLineEdit):
                    child.clear()
                elif isinstance(child, QComboBox):
                    child.setCurrentIndex(0)
                elif isinstance(child, QSpinBox):
                    child.setValue(child.minimum())
                elif isinstance(child, QTextEdit):
                    child.clear()
                elif isinstance(child, QRadioButton):
                    child.setAutoExclusive(False)
                    child.setChecked(False)
                    child.setAutoExclusive(True)
                elif isinstance(child, QButtonGroup):
                    child.setExclusive(False)
                    for btn in child.buttons():
                        btn.setChecked(False)
                    child.setExclusive(True)
        self.setEnabled(True)

    def _on_invoice_opacity_changed(self, value:int)->None:
        """
        Actualiza la opacidad de la factura en el editor segun el valor seleccionado
        en el slider de opacidad.
        """
        opacity_effect = QGraphicsOpacityEffect()
        if value > 0:
            opacity = value/100
            if opacity < 0:
                opacity = 0
            elif opacity > 1:
                opacity = 1
            opacity_effect.setOpacity(value/100)
        else:
            opacity_effect.setOpacity(0.0)
        self._editor_invoice_label.setGraphicsEffect(opacity_effect)

    def _on_tab_switched(self, tab_index:int)->None:
        """
        Signal para cambiar de tab.
        """
        self.stack.setCurrentIndex(tab_index)

    def _update_prints_in_prints_path(self)->None:
        """
        Actualiza la lista de archivos en la ruta
        especificada en `self._settings.prints_path`
        """
        self._generated_invoices_list_widget.clear()
        archivos = self._settings.get_invoices_in_prints_path()
        self._generated_invoices_list_widget.addItems(archivos)

        if archivos:
            self._generated_invoices_list_widget.setCurrentRow(0)
            self._on_invoice_selected(self._generated_invoices_list_widget.currentItem(), skip_tab_switch=True)
        else:
            pixmap = QPixmap(self._settings.NO_INVOICE_SELECTED_BACKGROUND_FILEPATH).scaled(
                self._settings.INVOICE_WIDTH,
                self._settings.INVOICE_HEIGHT,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._viewer_invoice_overlay_label.setPixmap(pixmap)
            self._viewer_invoice_file_name_label.setText("No hay ninguna factura seleccionada.")

    def _center_on_screen(self) -> None:
        """
        Centra la APP en el medio de la pantalla.
        """
        app = QApplication.instance()
        if app is None:
            return
        screen = app.primaryScreen()
        if screen is None:
            return
        screen_center = screen.availableGeometry().center()
        frame_geom = self.frameGeometry()
        frame_geom.moveCenter(screen_center)
        self.move(frame_geom.topLeft())

    def _update_inputs_geometry(self):
        """
        Actualiza la geometría y propiedades de los widgets existentes según el archivo JSON.

        Si el widget ya existe en `self._editor_inputs`, se actualiza su posición, tamaño, longitud máxima y alineación.
        Si no existe, se crea y se agrega al contenedor `self._editor_invoice_label`.

        El archivo debe tener entradas con la forma:
            [x, y, width, height, max_length, tipo, alignment?]
        Donde `alignment` puede ser "left", "center" o "right" (opcional, por defecto "left").
        """
        try:
            with open(self._settings.INPUTS_GEOMETRY_JSON_FILE, "r", encoding="utf-8") as f:
                updated_data = json.load(f)
        except Exception as e:
            if self._settings.DEBUG:
                print("Error leyendo geometría:", e)
            else:
                create_log('App', f'Error leyendo la geometria en _upodate_inputs_geometry: {e}')
            return

        for key, values in updated_data.items():
            x, y, w, h, max_len, tipo, *rest = values
            alignment = rest[0] if rest else "left"

            if key in self._editor_inputs:
                widget = self._editor_inputs[key]
                widget.setGeometry(x, y, w, h)

                if tipo == "text" and isinstance(widget, QLineEdit):
                    widget.setMaxLength(max_len)
                    if alignment == "center":
                        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    elif alignment == "right":
                        widget.setAlignment(Qt.AlignmentFlag.AlignRight)
                    else:
                        widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
                continue

            # Crear nuevo widget si no existe
            if tipo == "text":
                widget = QLineEdit(self._editor_invoice_label)
                widget.setMaxLength(max_len)
                if alignment == "center":
                    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                elif alignment == "right":
                    widget.setAlignment(Qt.AlignmentFlag.AlignRight)
                else:
                    widget.setAlignment(Qt.AlignmentFlag.AlignLeft)

            elif tipo == "checkbox":
                widget = QCheckBox(self._editor_invoice_label)

            elif tipo == "radio_button":
                widget = QRadioButton(self._editor_invoice_label)
                self._radio_button_group.addButton(widget)

            else:
                continue

            widget.setGeometry(x, y, w, h)
            widget.setStyleSheet("background-color: rgba(255,255,255,180); border: 1px solid #888;")
            widget.show()
            self._editor_inputs[key] = widget

    def _load_editor_inputs(self, parent: QWidget):
        """
        Carga los widgets de entrada en el editor según la geometría definida en el archivo JSON.

        Este método crea los widgets (QLineEdit, QCheckBox, QRadioButton) y los posiciona en el contenedor `parent`.
        También aplica estilos visuales y alineación de texto si está especificada en el JSON.

        El archivo debe tener entradas con la forma:
            [x, y, width, height, max_length, tipo, alignment?]
        Donde `alignment` puede ser "left", "center" o "right" (opcional, por defecto "left").
        """
        try:
            with open(self._settings.INPUTS_GEOMETRY_JSON_FILE, "r", encoding="utf-8") as f:
                inputs_data = json.load(f)
        except Exception as e:
            if self._settings.DEBUG:
                print("Error cargando inputs_geometry.json en _load_editor_inputs:", e)
            else:
                create_log('App', f"Error cargando inputs_geometry.json en _load_editor_inputs: {e}")
            return

        self._editor_inputs = {}
        self._radio_button_group = QButtonGroup(parent)

        for key, values in inputs_data.items():
            x, y, w, h, max_len, tipo, *rest = values
            alignment = rest[0] if rest else "left"

            if tipo == "text":
                widget = QLineEdit(parent)
                widget.setMaxLength(max_len)

                if alignment == "center":
                    widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                elif alignment == "right":
                    widget.setAlignment(Qt.AlignmentFlag.AlignRight)
                else:
                    widget.setAlignment(Qt.AlignmentFlag.AlignLeft)

            elif tipo == "checkbox":
                widget = QCheckBox(parent)

            elif tipo == "radio_button":
                widget = QRadioButton(parent)
                self._radio_button_group.addButton(widget)

                if key.startswith("forma_pago_"):
                    valor = key.replace("forma_pago_", "")
                    widget.toggled.connect(lambda checked, v=valor: setattr(self, "forma_pago_selected", v) if checked else None)

            else:
                continue

            widget.move(x, y)
            widget.resize(w, h)
            widget.setStyleSheet("background-color: rgba(255,255,255,180); border: 1px solid #888;")
            widget.show()
            self._editor_inputs[key] = widget


