# EDA CLI - Dataset Quality API

HTTP-сервис для оценки готовности датасета к обучению модели. Использует простые эвристики качества данных из EDA-ядра (HW03).

## Установка и запуск

```bash
uv sync
uv run uvicorn eda_cli.api:app --port 8000
```

Сервис будет доступен по адресу `http://127.0.0.1:8000`

Интерактивная документация API доступна по адресу: `http://127.0.0.1:8000/docs`

## Эндпоинты API

### `GET /health`

Проверка работоспособности сервиса.

**Ответ:**
```json
{
  "status": "ok",
  "service": "dataset-quality",
  "version": "0.2.0"
}
```

**Пример запроса:**
```bash
curl http://127.0.0.1:8000/health
```

---

### `POST /quality`

Оценка качества датасета по агрегированным признакам (без загрузки файла).

**Параметры запроса (JSON):**
- `n_rows` (int): Число строк в датасете
- `n_cols` (int): Число колонок
- `max_missing_share` (float): Максимальная доля пропусков среди всех колонок (0..1)
- `numeric_cols` (int): Количество числовых колонок
- `categorical_cols` (int): Количество категориальных колонок

**Ответ:**
```json
{
  "ok_for_model": true,
  "quality_score": 0.85,
  "message": "Данных достаточно, модель можно обучать (по текущим эвристикам).",
  "latency_ms": 0.5,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "no_numeric_columns": false,
    "no_categorical_columns": false
  },
  "dataset_shape": {
    "n_rows": 1000,
    "n_cols": 10
  }
}
```

**Пример запроса:**
```bash
curl -X POST http://127.0.0.1:8000/quality \
  -H "Content-Type: application/json" \
  -d '{
    "n_rows": 1000,
    "n_cols": 10,
    "max_missing_share": 0.1,
    "numeric_cols": 5,
    "categorical_cols": 5
  }'
```

---

### `POST /quality-from-csv`

Оценка качества датасета по CSV-файлу с использованием EDA-ядра (summarize_dataset, missing_table, compute_quality_flags).

**Параметры запроса:**
- `file` (multipart/form-data): CSV-файл для анализа

**Ответ:**
```json
{
  "ok_for_model": true,
  "quality_score": 0.82,
  "message": "CSV выглядит достаточно качественным для обучения модели (по текущим эвристикам).",
  "latency_ms": 15.3,
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_high_cardinality_categoricals": false,
    "has_suspicious_id_duplicates": false
  },
  "dataset_shape": {
    "n_rows": 1000,
    "n_cols": 10
  }
}
```

**Обработка ошибок:**
- `400` - если файл не является CSV или пустой
- `400` - если не удалось прочитать CSV

**Пример запроса:**
```bash
curl -F "file=@data/example.csv" http://127.0.0.1:8000/quality-from-csv
```

---

### `POST /quality-flags-from-csv`

Вывод всех флагов качества по CSV-файлу. Использует EDA-ядро из HW03 (summarize_dataset, missing_table, compute_quality_flags) и возвращает полный набор флагов, включая числовые метрики (quality_score, max_missing_share, has_many_skipping_values) и булевы флаги (too_few_rows, too_many_columns, has_constant_columns, has_high_cardinality_categoricals, has_suspicious_id_duplicates).

**Параметры запроса:**
- `file` (multipart/form-data): CSV-файл для анализа

**Ответ:**
```json
{
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "has_many_skipping_values": 0,
    "max_missing_share": 0.05,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_high_cardinality_categoricals": false,
    "has_suspicious_id_duplicates": false,
    "quality_score": 0.85
  }
}
```

**Обработка ошибок:**
- `400` - если файл не является CSV или пустой
- `400` - если не удалось прочитать CSV

**Пример запроса:**
```bash
curl -F "file=@data/example.csv" http://127.0.0.1:8000/quality-flags-from-csv
```

---

## CLI команды

### Генерация отчёта

```bash
uv run eda-cli report data/example.csv --out-dir reports_example
```

### Обзор датасета

```bash
uv run eda-cli overview data/example.csv
```

## Тестирование

```bash
uv run pytest -q
```

## Структура проекта

```
eda-cli/
├── src/
│   └── eda_cli/
│       ├── api.py          # FastAPI эндпоинты
│       ├── cli.py           # CLI команды
│       ├── core.py          # EDA-ядро (summarize_dataset, missing_table, compute_quality_flags)
│       └── viz.py           # Визуализация
├── tests/
│   └── test_core.py         # Тесты для EDA-ядра
├── data/
│   └── example.csv         # Пример CSV-файла
└── pyproject.toml           # Зависимости проекта
```

