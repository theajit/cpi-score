# CPI Score API

Public REST API for Corruption Perceptions Index 2025 scores.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/countries` | All countries (`?region=&min_score=&max_score=`) |
| GET | `/countries/{code}` | Lookup by ISO2/ISO3 |
| GET | `/regions` | Region summaries |
| GET | `/regions/{region}` | Countries in region |
| GET | `/rankings` | Ranked list (`?order=desc&limit=10`) |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
