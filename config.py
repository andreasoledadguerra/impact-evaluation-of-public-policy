from pathlib import Path

ROOT_DIR = Path(__file__).parent
RAW_DIR = ROOT_DIR / "data" / "raw"


# Specific files
MUNICIPIOS_PATH  = RAW_DIR / "base_municipios.xlsx"
INSCRIPTOS_PATH  = RAW_DIR / "ficha_inscriptos.xlsx"
FORMULARIOS_PATH = RAW_DIR / "formularios_curso.xlsx"

MEJORES_RESULTADOS = RAW_DIR / "mejores_resultados.xlsx"
NUEVA_ENCUESTA     = RAW_DIR / "nueva_encuesta_situacion_hogar.xlsx"