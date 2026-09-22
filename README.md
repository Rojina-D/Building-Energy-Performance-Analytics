# Building Energy Performance Analytics

A focused retrofit-decision dashboard: it turns zone-level BAS telemetry into diagnosable HVAC faults, ranked avoided-energy opportunities, and simple-payback recommendations.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Open `http://localhost:5000`. The first run creates `energy_analytics.db` with a deterministic 21-day demonstration data set. It includes a cumulative meter reset, duplicate DST hour, and a one-day sensor-swap gap so the ETL behavior can be inspected.

## Analytics design

1. Clean source records: deduplicate DST intervals, correct cumulative-meter resets, and omit missing-zone hours rather than treating them as zero.
2. Aggregate 15-minute data to zone-hour. The expected-use baseline has heating-degree-day and occupancy terms; the daily roll-up can be added from `hourly_rows()` for portfolio reporting.
3. Detect three transparent faults: simultaneous heat/cool calls, after-hours setback failures, and high energy in unoccupied zones.
4. Rank zones by attributable waste and extrapolate annual kWh, cost, and payback. The dashboard also shows a regression-style expected-versus-actual excess signal as the ML experiment comparator.

## Production data & deployment

The app uses a generated, building-domain demonstration feed so it runs without credentials. In a deployment, replace `seed_readings()` with an adapter for Building Data Genome, NREL ComStock/ResStock, or BAS historian CSVs while retaining the normalized schema.

For AWS: package this Flask service in a container, use RDS PostgreSQL instead of SQLite, schedule ingestion with EventBridge/Lambda or ECS, and deploy the web service through ECS Fargate behind an ALB. Store source credentials in Secrets Manager.

## Rule definitions

- **Simultaneous heating/cooling:** heat and cool call are both active in the same zone-hour.
- **Setback failure:** after-hours heating occurs while the setpoint remains above 18°C.
- **Occupancy-energy mismatch:** an unoccupied zone uses more than 0.18 kWh per hour.

Assumptions are deliberately visible in the UI; tune thresholds and repair costs to the site’s sequence of operations and tariff.
