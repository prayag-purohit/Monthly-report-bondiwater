# Monthly Report - Bondi Water

This repository contains modules for interacting with **AlertLab** and **SimpleSub** APIs, fetching sensor data, and generating monthly water usage reports.

## 📂 Project Structure

- `alertlabapi.py` — Manages API interactions with AlertLab.
- `simplesubapi.py` — Manages API interactions with SimpleSub.
- `common_functions.py` — Provides utility functions for data processing.
- Other `.py` files — Examples demonstrating the usage of main modules.

---

## ⚙️ Installation

1. **Clone the Repository**

```bash
git clone https://github.com/prayag-purohit/Monthly-report-bondiwater.git
cd Monthly-report-bondiwater
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Set Environment Variables for API Authentication**

Linux/MacOS:

```bash
export ALERTLAB_USER="your_username"
export ALERTLAB_PASSWORD="your_password"
export SIMPLESUB_USERNAME="your_username"
export SIMPLESUB_PASSWORD="your_password"
export SIMPLESUB_CLIENT_ID="your_client_id"
```

Windows (PowerShell):

```powershell
$env:ALERTLAB_USER="your_username"
$env:ALERTLAB_PASSWORD="your_password"
$env:SIMPLESUB_USERNAME="your_username"
$env:SIMPLESUB_PASSWORD="your_password"
$env:SIMPLESUB_CLIENT_ID="your_client_id"
```

---

## 📦 Modules

### `alertlabapi.py`
Interacts with the AlertLab API to retrieve sensor data.

#### Functions

- `get_token()` — Retrieves authentication token.
- `get_property_name_list(token)` — Fetches and saves property names.
- `get_property_id(token, property_name)` — Retrieves property ID by name.
- `get_sensorlist(token, property_id)` — Fetches Flowie-O and Flowie sensors.
- `get_timeseries_data(token, sensor_id, sensorstoquery, month_start, month_end)` — Fetches and processes timeseries data.

---

### `simplesubapi.py`
Interacts with the SimpleSub API to fetch water usage data.

#### Functions

- `get_token()` — Retrieves authentication token.
- `get_property_list(token)` — Fetches list of properties.
- `get_unit_ids_for_property(data, property_name)` — Retrieves unit IDs for a property.
- `get_timeseries_data(unit_id, auth_token, month_start, month_end)` — Fetches water usage data.

---

### `common_functions.py`
Provides shared utilities for data processing.

#### Functions

- `get_firstandlastdayofpreviousmonth()` — Calculates the start and end dates of the previous month.
- `get_master_df()` — Creates a master DataFrame for water usage data.
- `mergewithmasterdf(master_df, timeseries_df)` — Merges timeseries data with the master DataFrame.
- `add_summary_rows(master_df, cost_per_m3=4.8401)` — Adds summary rows including total liters, cost, and daily usage.

---

## 🚀 Usage Example

To generate the monthly water usage report, run:

```bash
python SSandAL_local_run.py
```

The report will be saved as a CSV file in the `csvs/` directory.

---

## 📌 Notes
- Ensure API credentials are correctly set before running the script.
- The cost per cubic meter (`cost_per_m3`) is set to **4.8401** by default but can be modified in the `add_summary_rows()` function.
- The project is designed to process one request per second to comply with API rate limits.

Happy Reporting! 💧

