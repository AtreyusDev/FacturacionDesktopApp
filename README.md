# 🧾 Facturación Desktop App

Es una aplicación de escritorio desarrollada en Python con PyQt6 que permite generar facturas personalizadas en formato PDF, alineando dinámicamente los datos ingresados sobre una plantilla visual. Está diseñada para ser robusta, multiplataforma y fácil de usar, incluso sin conexión a internet. Fue desarrollada para solucionar un problema especifico de la empresa ELEVACION AWAA 4D S.A

---

## 🚀 Características principales

- 🖋️ **Editor visual de facturas** con campos configurables
- 📄 **Generación de PDF** con alineación precisa sobre una plantilla
- 🧩 **Configuración modular** desde archivos JSON
- 🗂️ **Ruta de guardado personalizable** para las facturas generadas
- 🧠 **Logs automáticos** en `%APPDATA%` para trazabilidad
- 🧱 **Empaquetado profesional** con PyInstaller e Inno Setup
- 🖥️ **Interfaz moderna** con PyQt6

---

## 🖼️ Interfaz

La interfaz está dividida en dos vistas:

- **Editor**: permite ingresar datos en campos alineados con la plantilla de factura.
- **Visualizador**: muestra la factura generada en PDF.

---

## 🛠️ Tecnologías utilizadas

- Python 3.12+
- PyQt6
- ReportLab (para generación de PDFs)
- Pillow, lxml, pikepdf

## ⚙️ Instalación y ejecución

### 🔧 Requisitos

- Python 3.12+
- `pip install -r requirements.txt`

### ▶️ Ejecutar en desarrollo

```bash
python main.py

