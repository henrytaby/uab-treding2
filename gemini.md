# Gemini Memory - Data Extraction Project

This file serves as my internal memory and reference for the Data Extraction Project, ensuring all context, requirements, and architectural decisions are preserved for future interactions.

## Core Requirements
- **Goal**: Extract data from web systems (initially Yahoo Finance trending stocks).
- **Architecture**: Object-Oriented (OOP), SOLID principles, highly optimal, scalable, robust.
- **Environment**: Use `.env` for secrets/configuration (e.g., username, passwords, general parameters).
- **Execution**: Command Line Interface (CLI) via `main.py` supporting different commands and parameters (e.g., `python main.py top-empresas --parametro1`).
- **Storage**: Output data into directories organized by module and extraction date/time (e.g., `datos/top-empresas/YYYYMMDD_HHMMSS/data.xlsx`).
- **Formats**: JSON or Excel (`.xlsx`), standardizing on Excel for the first requirement.

## Phase 1 Requirement: Yahoo Finance
- **Command**: `top-empresas`
- **Target URL**: `https://finance.yahoo.com/markets/stocks/trending/`
- **Fallback**: Parsing provided exact HTML snippet (table logic with class `.yf-1tpeyy7`).
- **Target Columns**: Symbol, Name, Price, Change, Change %, Volume, Avg Vol(3M), Market Cap, P/E Ratio (TTM), 52 Wk Change %

## Phase 2 Requirement: Individual Quotes
- **Action**: Loop through extracted symbols from Phase 1.
- **Target URL**: `https://finance.yahoo.com/quote/{symbol}`
- **Parsing Targets**: Locate list `ul.yf-6myrf1` and extract text from `span.label` and `span.value` within `li` elements.
- **Data Integration**: Merge the new fields (Previous Close, Open, Bid, Day's Range, etc.) into the main record for the symbol before saving to Excel.

## Technical Stack & Decisions
- **Language**: Python 3.x
- **Configuration**: `python-dotenv` for loading `.env` variables.
- **CLI**: `argparse` built-in module for handling command-line arguments and subparsers cleanly.
- **Extraction/Parsing**: `BeautifulSoup4` for robust HTML parsing.
- **Data Export**: `pandas` and `openpyxl` for easily creating properly typed Excel files.
- **File Structure**:
  - `core/`: Base classes (`BaseExtractor`), configuration manager, storage manager.
  - `modules/`: Specific implementations (e.g., `YahooTrendingExtractor`).
  - `datos/`: Organized output folders.
  - `main.py`: Entrypoint.
  - `gemini.md`: This file (internal context).
  - `README.md`: Project documentation in Spanish.

## Future Scaling
- New websites or modules should be added inside the `modules/` directory, subclassing `core.extractor.BaseExtractor`.
- `main.py` should dynamically or structurally register new commands linking to these modules.
- Ensure the `StorageManager` can accept different formats (`.json`, `.csv`, `.xlsx`).
