from pathlib import Path

# Directorio raíz del repositorio
BASE_DIR = Path(__file__).resolve().parent.parent

# Subcarpetas principales
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"
PLOTS_DIR = BASE_DIR / "plots"
DOCS_DIR = BASE_DIR / "docs"

# Archivo oficial de escalas del Grupo 8
DATA_G08_CSV = DATA_DIR / "PuertoSur_escalas_G08.csv"
# Fallback por si alguien tiene el CSV directamente en la raíz
if not DATA_G08_CSV.exists() and (BASE_DIR / "PuertoSur_escalas_G08.csv").exists():
    DATA_G08_CSV = BASE_DIR / "PuertoSur_escalas_G08.csv"

# Archivo de parámetros de distribuciones ajustadas
DISTRIBUTIONS_JSON = DATA_DIR / "distribuciones_g08.json"

# Asegurar que existan directorios de salida
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
