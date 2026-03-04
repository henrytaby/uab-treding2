# Guía para Desarrolladores: Extractor de Yahoo Finance

Bienvenido al módulo de extracción de datos de **Yahoo Finance** (`modules/yahoo_finance.py`). 

Este documento explica en detalle cómo funciona el motor de extracción para que puedas entenderlo rápidamente, mantenerlo y usarlo como referencia para construir nuevos módulos en el futuro.

## 🎯 1. Propósito del Módulo

El objetivo principal de `yahoo_finance.py` es capturar la información de las empresas con mayor tendencia ("Trending Stocks") en la bolsa de valores estadounidense a través de Yahoo Finance.

Para lograr esto, el proceso se divide en **dos fases** principales:
1. **Extracción Base (Trending Table):** Extraer la tabla principal con la lista de empresas en tendencia.
2. **Deep Scrape (Quote Details):** Navegar individualmente al perfil financiero ("Quote") de cada empresa descubierta para engrosar el dataset con detalles adicionales y datos de mercado en tiempo real.

---

## 🏗️ 2. Arquitectura de Clases

El archivo define dos clases fundamentales. Ambas heredan de `BaseExtractor` (`core/extractor.py`), lo que significa que el proceso de hacer peticiones HTTP (descargar el HTML con `requests`) y el manejo de reintentos automáticos ya está resuelto por la clase padre.

### A. `YahooTrendingExtractor`
Esta es la clase orquestadora y la principal. Se enfoca en la URL: `https://finance.yahoo.com/markets/stocks/trending/`

**Métodos Clave:**
*   `__init__()`: Define la URL objetivo y el nombre lógico del módulo (`top-empresas`).
*   `parse(html_content)`: Recibe el HTML en texto crudo de la página de tendencias, lo lee usando `BeautifulSoup` y busca todas las filas de la tabla principal usando el selector `data-testid="data-table-v2-row"`. Por cada fila, extrae información básica como `Symbol`, `Name`, `Price`, `Volume`, etc., iterando sobre las celdas de la tabla mediante sus localizadores `data-testid-cell`. Devuelve una lista de diccionarios (cada diccionario es una empresa).
*   `execute_with_fallback(test_html_path)`: Un método salvavidas. Si Yahoo Finance nos detecta como bot y rechaza nuestra petición de red (ej. retornando HTML vacío o sin tabla), este método tiene la capacidad de leer un archivo HTML físico (local) proporcionado en su lugar para que el desarrollo no se detenga.
*   `run_deep_scrape(test_html_path)`: **El Orquestador**. Este método llama a `execute_with_fallback()` para obtener la lista de las empresas. Luego, itera sobre cada empresa, lee su símbolo (ej. "CRWD") e instancia un `YahooQuoteExtractor` para buscar información especializada de esa empresa. Por último, une ambos diccionarios para tener una empresa enriquecida y hace una pausa (Delay) para evitar que la IP sea baneada.

### B. `YahooQuoteExtractor`
Esta clase secundaria se encarga de analizar el perfil individual de una única empresa. 
Se enfoca en URLs dinámicas como: `https://finance.yahoo.com/quote/{symbol}/`

**Métodos Clave:**
*   `__init__(symbol)`: Recibe el símbolo de la empresa (ej. `BOX`) y arma dinámicamente la URL.
*   `parse(html_content)`: Analiza el HTML buscando dos secciones:
    1.  **Métricas Financieras Básicas:** Busca las listas `<ul>` de clase `yf-6myrf1` que contienen los pares de etiqueta/valor (ej. "Previous Close", "Bid", "Ask").
    2.  **Métricas Clave en Tiempo Real:** Interroga elementos individuales mediante `data-testid` (ej. `qsp-price`, `qsp-price-change`) para capturar el precio actual ($), la variación nominal en dólares y su equivalente en porcentaje (`%`).
*   `execute()`: En lugar de retornar una lista de diccionarios, sobrescribe la naturaleza de ejecución base para devolver un único diccionario (las métricas extraídas) el cual luego se unirá al registro padre.

---

## 🕵️ 3. ¿Cómo funciona la recolección de datos (Parsing HTML)?

Imagina que Yahoo Finance despliega su información usando etiquetas de HTML como esta:
```html
<td data-testid-cell="intradayprice"><span class="price">23.92</span></td>
```

Para extraer el "23.92", utilizamos la librería `BeautifulSoup` (`bs4`).

### Selector por Atributos (Data-Testid)
En páginas modernas construidas con React o Vue, las clases CSS cambian constantemente. Es por ello que usamos localizadores de pruebas, como `data-testid`.

Ejemplo de cómo los usamos (dentro de `YahooQuoteExtractor`):
```python
price_span = soup.find('span', {'data-testid': 'qsp-price'})
if price_span:
    details["Precio Actual"] = price_span.get_text(strip=True)
```
Esto le dice al analizador: *"Busca un span que tenga el atributo data-testid exacto a 'qsp-price'. Si existe, extrae el puro texto ignorando tabulaciones o espacios residuales (`strip=True`)."*

### Limpieza de Tablas con `_extract_text()`
A veces las celdas de las tablas (`<td>`) no tienen el texto directamente suelto, sino que contienen `<span>` u otros contenedores extra.
El método de apoyo `_extract_text(cell, default="--")` es nuestra trituradora: 
1. Revisa si la celda es nula (Retorna `--` para evitar fallos de python).
2. Intenta buscar los `<span>` anidados. Si tienen algo, usa el texto de dicho control.
3. Si nada funciona, intenta sacar cualquier texto de la raíz de la celda.

---

## 🚦 4. Flujo Completo del Ciclo de Vida (End-To-End)

Te explicaremos el flujo cada vez que se ejecuta `python main.py top-empresas`:

1. El usuario ejecuta el CLI y el sistema cae en el script administrador (`main.py`).
2. Se genera e invoca a `YahooTrendingExtractor().run_deep_scrape()`.
3. `YahooTrendingExtractor` hace una petición HTTP a `https://finance.yahoo.com/markets/stocks/trending/`. Si falla, usa Tenacity para reintentar `X` veces (configurado en `.env`).
4. Descarga el HTML y busca la fila base. Encuentra una empresa, por ejemplo "BOX".
5. Una vez que tiene en memoria el registro de "BOX" ({'Symbol': 'BOX', 'Name': 'Box Inc', ... }), inicia el bucle "Deep Scrape".
6. Se crea al iterar a `YahooQuoteExtractor("BOX")`. 
7. Éste hace la solicitud a `https://finance.yahoo.com/quote/BOX/`.
8. Extrae 19 detalles más (como `Bid`, `Ask` y variaciones en vivo y porcentaje). Retorna este diccionario de 19 ítems.
9. Se fusionan las 10 columnas en bruto del extractor tendencia + los 19 detalles del individual, construyendo un súper-objeto de casi 30 variables para "BOX".
10. Se descansa un lapso dictado por `config.RATE_LIMIT_DELAY` (usualmente un segundo).
11. Se pasa a iterar la siguiente empresa y el ciclo se repite.
12. Al final, se consolida todo en un Listado masivo de JSON y se le manda con formato Excel/Json a `StorageManager` (la clase encargada de escribir archivos).

---

## 🎓 5. Recomendaciones de Escalamiento

Si vas a agregar nuevos extractores para esta API:

1. **Evitar Sobrecarga:** Sé prudente con los retardos de red (`time.sleep()`). Yahoo cuenta con potentes firewalls (`Cloudflare`), y ráfagas inmensas de datos simultáneos desde una IP local pueden ocasionar baneos o el detestado Cloudfare Challenge (CAPTCHA).
2. **Depende lo menos posible de Clases CSS (`class="..."`):** Las páginas cambian su layout estético. Procura buscar por `id` o atributos descriptivos como `data-field` o `data-testid`, ya que los ingenieros Frontend rara vez los modifican.
3. **Control Cauteloso de Errores Crudos:** Ya que cada campo de la web es susceptible a no venir ese día, todos están controlados con `.get_text()` bajo declaraciones seguras `if campo:` o dentro de validaciones de excepciones crudas. Sigue este patrón para no derrumbar un proceso de 100 empresas en fila solo porque a una le faltó un campo de datos.
