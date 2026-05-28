"""
run_pipeline.py
Orquesta el pipeline ETL completo: Extract → Transform → Load
Uso:  python run_pipeline.py
"""

import sys
import time
from pathlib import Path

# Agrega la raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from etl import extract, transform, load


def main():
    start = time.time()
    print("=" * 50)
    print("  PIPELINE ETL — Datamart Residuos Sólidos")
    print("=" * 50)

    try:
        extract.run()
        transform.run()
        load.run()

        elapsed = time.time() - start
        print("=" * 50)
        print(f"  Pipeline completado en {elapsed:.1f}s ✓")
        print("=" * 50)

    except Exception as e:
        print(f"\n[ERROR] Pipeline fallido: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
