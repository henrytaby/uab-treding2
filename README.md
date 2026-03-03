# Proyecto de Extracción de Datos Web (Yahoo Finance Trending)

Este proyecto es una herramienta robusta, escalable y orientada a objetos desarrollada en Python para la extracción de datos de sistemas web. Utiliza principios SOLID para garantizar que el código sea fácil de mantener y extender.

## Características

- **Arquitectura OOP**: Basado en clases abstractas y managers especializados.
- **Escalabilidad**: Fácil de añadir nuevas fuentes de datos creando nuevos módulos extractor.
- **Configuración Segura**: Manejo de variables de entorno mediante archivos `.env`.
- **CLI Amigable**: Interfaz de línea de comandos para ejecutar diferentes tipos de extracciones.
- **Almacenamiento Organizado**: Los resultados se guardan en subcarpetas por módulo y fecha/hora.
- **Formatos de Salida**: Soporte para Excel (`.xlsx`) y JSON.
- **Deep Scrape (Fase 2)**: Al extraer tendencias, el sistema navega dinámicamente ("scrape profundo") a los perfiles individuales de las empresas para fusionar datos estadísticos (Bid, Ask, Rango diario, Cap. de Mercado, etc.) en un único archivo enriquecido.

## Estructura del Proyecto

- `core/`: Clases base y lógica central (configuración, extractores base, almacenamiento).
- `modules/`: Implementaciones específicas de extracción (ej. Yahoo Finance).
- `datos/`: Carpeta donde se almacenan los resultados de las extracciones.
- `main.py`: Punto de entrada del programa.
- `gemini.md`: Memoria interna del proyecto (en inglés).

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt` (o instaladas manualmente: `requests`, `beautifulsoup4`, `pandas`, `openpyxl`, `python-dotenv`).

## Instalación

1. Clona o descarga el proyecto.
2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura tu archivo `.env` (opcional):
   ```
   OUTPUT_BASE_DIR=datos
   DEFAULT_FORMAT=excel
   ```

## Ejecución

Para extraer el top de empresas de Yahoo Finance:

```bash
python main.py top-empresas
```

### Parámetros Adicionales

- `--format [excel|json]`: Especifica el formato de salida.
- `--test-html [ruta_al_archivo]`: Permite usar un archivo HTML local en caso de que la web bloquee la petición (útil para pruebas).

Ejemplo con formato JSON:
```bash
python main.py top-empresas --format json
```

Ejemplo con fallback local:
```bash
python main.py top-empresas --test-html datos/test_html.html
```

## Desarrollo de Nuevos Módulos

Para añadir un nuevo sistema de extracción:
1. Crea un nuevo archivo en `modules/`.
2. Hereda de `core.extractor.BaseExtractor`.
3. Implementa el método `parse(html_content)`.
4. Registra el nuevo comando en `main.py`.
