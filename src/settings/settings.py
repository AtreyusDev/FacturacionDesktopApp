import json
import os
import sys
from ..utils.log import create_log
from pathlib import Path

class SettingsManager:
    """
    Manager de la configuracion del programa. Esta programado para
    devolver los valores de la configuracion en todo momento.

    Methods:
        __get_settings_data()
        __get_gui_config()
        get_window_geometry()
    """

    def __init__(self):
        # Ruta base del bundle original
        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        # Carpeta segura para configuración modificable
        if os.name == "nt":
            base_config = os.getenv("APPDATA", Path.home())
            self.CONFIG_DIR = Path(base_config) / "FacturacionAwaa"
        else:
            self.CONFIG_DIR = Path.home() / ".config" / "facturacion_awaa"

        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # settings.json se guarda en AppData
        self.SETTINGS_JSON_FILE = self.CONFIG_DIR / "settings.json"

        # Si no existe, copiar desde el bundle
        default_settings_path = Path(self.BASE_DIR) / "json" / "settings.json"
        if not self.SETTINGS_JSON_FILE.exists():
            try:
                default_settings = {
                    "debug": False,
                    "update_time": 1,
                    "prints_path": ""
                }
                with open(self.SETTINGS_JSON_FILE, "w", encoding="utf-8") as f:
                    json.dump(default_settings, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error creando settings.json por defecto: {e}")
                sys.exit(1)

        # Los demás archivos siguen en el bundle
        self.GUI_JSON_FILE = os.path.join(self.BASE_DIR, "json", "gui_config.json")
        self.INPUTS_GEOMETRY_JSON_FILE = os.path.join(self.BASE_DIR, "json", "inputs_geometry.json")
        self.NO_INVOICE_SELECTED_BACKGROUND_FILEPATH = os.path.join(self.BASE_DIR, 'assets/images', 'no_invoice_selected.png')
        self.ICON_FILEPATH = os.path.join(self.BASE_DIR, 'assets/images', 'icon.ico')

        # Cargar datos
        settings_data = self.__get_settings_data()
        gui_data = self.__get_gui_config()

        self.DEBUG = settings_data.get('debug')
        self.UPDATE_TIME = settings_data.get('update_time')
        defined_prints_path_in_settings = settings_data.get('prints_path')
        self.prints_path = defined_prints_path_in_settings if defined_prints_path_in_settings else ""

        self.INVOICE_WIDTH = gui_data.get('invoice_width')
        self.INVOICE_HEIGHT = gui_data.get('invoice_height')
        self.WINDOW_WIDTH = gui_data.get('window_width')
        self.WINDOW_HEIGHT = gui_data.get('window_height')
        self.INVOICE_BACKGROUND_PATH = os.path.join(self.BASE_DIR, gui_data.get('invoice_background_path'))
        self.APP_TITLE = gui_data.get('app_title')
        self.MARGIN_TOP = gui_data.get('margin_top')
        self.MARGIN_BOTTOM = gui_data.get('margin_bottom')


        
    def __get_settings_data(self)->dict:
        """
        Retorna la configuracion escrita en settings.json

        Returns:
            settings_data (dict): Diccionario con los pares y claves de parametros de configuracion.
        """
        try:
            with open(self.SETTINGS_JSON_FILE, 'r', encoding='utf-8') as config_file:
                return json.load(config_file)
        except Exception as e:
            print(f'Error al obtener los datos de configuración: {e}')
            sys.exit(1)
        
    def __get_gui_config(self)->dict:
        """
        Retorna la configuracion de gui escrita en gui_config.json

        Returns:
            settings_data (dict): Diccionario con los pares y claves de configuraciones del gui.
        """
        try:
            if not os.path.exists(self.GUI_JSON_FILE):
                print(f"Error. No se pudo encontrar el json de gui del programa.")
                sys.exit(1)
            with open(self.GUI_JSON_FILE, 'r', encoding='utf-8') as config_file:
                return json.load(config_file)
        except Exception as e:
            print(f'Error al obtener los datos del gui del programa: {e}')
            sys.exit(1)
        
    def get_window_geometry(self)->str:
        """
        Formula el width y height de la ventana en un formato compatible con Tkinter.

        Returns:
            window_geometry (str): Geometria de la ventana en formato w x h.
        """
        return f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}"
    
    def get_invoices_in_prints_path(self)->list:
        """
        Retorna una lista con los nombres de los archivos .pdf en
        la ruta especificada en self.prints_path.
        """
        files = []
        try:
            files = [
                file for file in os.listdir(self.prints_path)
                if file.lower().endswith(".pdf") and os.path.isfile(os.path.join(self.prints_path, file))
            ]
        except Exception as e:
            print("Error leyendo archivos PDF: ", e)
        return files
    
    def set_prints_path(self, new_path: str) -> bool:
        """
        Actualiza `settings.json` y `self.prints_path` con la nueva
        ruta para las facturas generadas.

        Returns:
            result (bool): Si la operación fue exitosa o no.
        """
        result = False
        old_path = self.prints_path
        try:
            self.prints_path = new_path
            with open(self.SETTINGS_JSON_FILE, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            settings_data['prints_path'] = new_path
            with open(self.SETTINGS_JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4, ensure_ascii=False)
            result = True
        except Exception as e:
            if not self.DEBUG:
                create_log('SettingsManager', f'Error al cambiar la ruta para guardar las facturas generadas: {e}')
            else:
                print(f"Error al cambiar la ruta de las facturas generadas: {e}")
        if result:
            if not self.DEBUG:
                create_log('SettingsManager', f'Se ha actualizado la ruta de guardado de facturas de {old_path} -> {self.prints_path}')
            else:
                print(f'Se ha actualizado la ruta de guardado de facturas de {old_path} -> {self.prints_path}')
        return result

settings_instance = SettingsManager()