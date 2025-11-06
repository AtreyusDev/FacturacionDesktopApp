from datetime import datetime
import os
from pathlib import Path

def create_log(origin: str, log_text: str) -> None:
    """
    Registra un log en una carpeta segura del sistema para el día actual.
    En Windows se usa %APPDATA%/FacturacionAwaa/logs
    En Linux/macOS se usa ~/.local/share/facturacion_awaa/logs

    Args:
        origin (str): `Opcional` Nombre del origen del log.
        log_text (str): Texto que se escribirá en el log.

    Raises:
        ValueError: Si el texto del log está vacío.
    """
    if not log_text:
        raise ValueError("No se puede escribir el log. Debe especificar el log_text.")

    dt_now = datetime.now()

    # Ruta segura para logs
    if os.name == "nt":
        base_dir = os.getenv("APPDATA", Path.home())
        logs_dir = Path(base_dir) / "FacturacionAwaa" / "logs"
    else:
        logs_dir = Path.home() / ".local" / "share" / "facturacion_awaa" / "logs"

    logs_dir.mkdir(parents=True, exist_ok=True)

    log_filename = f"log_{dt_now.day}_{dt_now.month}_{dt_now.year}.log"
    log_path = logs_dir / log_filename

    text = f"{dt_now.hour}:{dt_now.minute}:{dt_now.second} | "
    text += log_text if not origin else f"[{origin}] - {log_text}"
    text += "\n"

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(text)