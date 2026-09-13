import glob

import pandas as pd
from netCDF4 import Dataset
from wrf import getvar, ll_to_xy, extract_times, ALL_TIMES


# Coordenadas RAMM

STATIONS = {
    "R00": (19.04181986, -98.19477367),
    "R01": (19.16336266, -98.30937849),
    "R02": (19.15223057, -98.19846150),
    "R03": (19.15279169, -98.09364025),
    "R05": (19.05121120, -98.30416073),
    "R06": (19.04746122, -98.09389055),
    "R07": (19.00487892, -98.20361627),
    "R08": (18.98066668, -98.23965815),
    "R09": (18.94354964, -98.30607067),
    "R10": (18.93788801, -98.13511047),
    "R12": (19.04328301, -98.19665770),
    "R13": (19.00348124, -98.18358605),
    "R15": (18.91011483, -98.24207605),
    "R16": (19.09947160, -98.26294917),
    "R17": (19.10402894, -98.13478293),
    "R20": (18.98741415, -98.21934545),
    "R22": (19.06674086, -98.15376630),
    "R23": (19.07447244, -98.22051641),
    "R24": (19.02540595, -98.23016195),
    "RCU": (18.93703624, -98.15619774),
}


# Encontrar los archivos output en el periodo de tiempo establecido

files = sorted(
    glob.glob("wrfout_d02_2024-0[3-5]-*_00:00:00")
)

if not files:
    raise FileNotFoundError(
        "No WRF output files were found in the current directory."
    )

print(f"Processing {len(files)} WRF files...")


# Extraer variables en las ubicaciones de las estaciones

records = []

for file_path in files:

    with Dataset(file_path) as nc:

        wind = getvar(
            nc,
            "uvmet10_wspd_wdir",
            timeidx=ALL_TIMES
        )

        times = pd.to_datetime(
            extract_times(
                nc,
                timeidx=ALL_TIMES
            )
        )

        if isinstance(times, pd.Timestamp):
            times = [times]

        for station, (lat, lon) in STATIONS.items():

            xy = ll_to_xy(nc, lat, lon)

            ix = int(xy[0])
            iy = int(xy[1])

            for t_idx, timestamp in enumerate(times):

                if wind.ndim == 3:
                    wind_speed = float(
                        wind[0, iy, ix]
                    )
                    wind_direction = float(
                        wind[1, iy, ix]
                    )

                else:
                    wind_speed = float(
                        wind.values[
                            0,
                            t_idx,
                            iy,
                            ix
                        ]
                    )

                    wind_direction = float(
                        wind.values[
                            1,
                            t_idx,
                            iy,
                            ix
                        ]
                    )

                records.append({
                    "station": station,
                    "timestamp": timestamp,
                    "wind_sim": round(wind_speed, 2),
                    "dir_sim": round(wind_direction, 2),
                })

    print(f"Processed: {file_path}")


# Exportar

simulation_df = pd.DataFrame(records)

simulation_df = (
    simulation_df
    .sort_values(["station", "timestamp"])
    .reset_index(drop=True)
)

output_file = "viento_red_ramm_2024.csv"

simulation_df.to_csv(
    output_file,
    index=False
)

print()
print("Extraction completed successfully.")
print(f"Records: {len(simulation_df):,}")
print(f"Output: {output_file}")
