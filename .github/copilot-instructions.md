# SMEAR Estonia IoT Data Analysis - Copilot Instructions

## Project Overview
This is an environmental monitoring analysis project tracking groundwater levels and meteorological data at SMEAR Estonia research station. The project correlates rainfall events with groundwater level fluctuations using time-series analysis.

## Architecture & Data Flow

### Data Sources (Remote)
- **Water Level**: `smear@smeartartu.emu.ee:DataLog/IOT/WATER-SCT1-GR/` - hourly water level measurements (JSON-L format)
- **CO2 Sensors**: `smear@smeartartu.emu.ee:DataLog/IOT/CO2-SCT1-2M/` - CO2 concentration data
- **Weather Data**: `smear@smeartartu.emu.ee:DataLog/GR/GR_WeatherInformation_NEW` - raw meteorological data

### Data Processing Pipeline
1. **Sync Stage** (`syncData.sh`): Uses rsync to pull remote data into local directories
2. **Transform Stage** (`meteo/makeMeteoCsv.sh`): Converts raw weather format to CSV (extracts 13 columns: wind, temperature, humidity, pressure, rain, etc.)
3. **Analysis Stage** (`water.ipynb`, `rain.ipynb`): Pandas-based Jupyter notebooks process and visualize

### Local Directory Structure
```
water_level/        # JSON-L files, one per hour (water_level.json-YYYY-MM-DDTHH-MM-SS.xxxZ)
CO2/               # SCD41 sensor data files
meteo/             # weather.csv (processed from GR_WeatherInformation_NEW)
```

## Key Data Patterns

### Water Level Data Format
- **Files**: `water_level.json-*` (newline-delimited JSON)
- **Fields**: `{"time": "M/D/YYYY H:MM:SS AM/PM", "level": <float>}`
- **Values**: Raw sensor readings in cm, typically 84-90cm range; > 200cm indicates sensor errors to filter

### Processing Workflow in water.ipynb
1. Load all JSON files with `glob.glob('water_level/*.json-*')`
2. Use `pd.read_json(file, lines=True)` for each file (newline-delimited format)
3. Concatenate with `pd.concat(..., ignore_index=True)`
4. Parse time with `pd.to_datetime(df['time'], format='mixed')` (handles AM/PM format)
5. Filter: `df[df['datetime'] >= '2024-10-23 00:00:00']` (project start date)
6. Resample to hourly: `df.resample('h').mean()`
7. Convert to depth: `depth = -1.2 + level/100` (calibration: -1.2m offset, cm to m)

### Visualization Patterns
- **Twin axes plots**: Water level depth (left) vs rainfall accumulation (right, inverted)
- **Outlier handling**: Filter `level < 200` to remove sensor glitches
- **Time slicing**: Use `.loc['2025-09-21 20:40:00':'2025-09-24 01:00:00']` for event inspection

## Critical Conventions

### Dates & Timezones
- Data uses UTC timestamps (Z suffix)
- Working date range: 2024-10-23 onward
- Times in raw JSON alternate between AM/PM format and ISO 8601

### Data Validation
- Remove duplicates: `df.drop_duplicates()`
- Require both 'time' and 'level': `df.dropna(subset=['time', 'level'])`
- Flag outliers: level > 200cm indicates sensor malfunction

### File I/O
- All data files are in project root or subdirectories (no absolute paths in notebooks)
- Use `glob.glob()` for batch file operations (relative paths from notebook location)
- Meteorological CSV has fixed 13-column structure from `makeMeteoCsv.sh`

## Development Workflow

### Data Sync
```bash
./syncData.sh  # Pulls latest data, processes meteo CSV
```

### Analysis Iteration
1. Run notebook cells sequentially (dependencies on `df` DataFrame)
2. Each cell builds on prior transformations
3. Restart kernel if encountering stale data references

### Testing Data Quality
- Check `df.describe()` for range validation
- Verify datetime parsing: `df.index` should be DatetimeIndex
- Validate resampling: `df_hourly.shape[0]` should be ~24 × days

## Integration Points

### Cross-Notebook References
- `rain.ipynb` likely uses similar data loading pattern for rainfall analysis
- Both notebooks use same water_level/ directory structure

### External Tools
- rsync for remote data sync (requires SSH credentials to SMEAR server)
- Bash scripts for data transformation (sed in makeMeteoCsv.sh)

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| `ValueError: time data does not match format` | Use `format='mixed'` in `pd.to_datetime()` |
| Memory overload (1000+ JSON files) | Process in batches or filter files by date range before loading |
| Duplicate rows across files | Use `df.drop_duplicates()` after concatenation |
| Timezone confusion | All data is UTC; no conversion needed for time slicing |
| NaN values in resampling | Use `.mean()` aggregation; handles gaps gracefully |
