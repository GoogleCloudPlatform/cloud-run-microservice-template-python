columns_to_remove = [
        'engine_speed_50909', 
        'fuel_5l_consumed_50909', 
        'boost_pressure_50909', 
        'boost_pressure_54909', 
        'fuel_5l_consumed_54909', 
        'engine_speed_54909', 
        'fuel_5l_consumed_55909', 
        'engine_speed_55909', 
        'boost_pressure_55909', 
        'boost_pressure_56909', 
        'fuel_5l_consumed_56909',
        'engine_speed_56909',
        'fuel_5l_consumed_56912',
        'engine_speed_56912',
        'boost_pressure_56912',
        'boost_pressure_59909',
        'fuel_5l_consumed_59909',
        'engine_speed_59909',
        'fuel_5l_consumed_59912',
        'engine_speed_59912',
        'Unnamed: 30',
        'Standard Deviation:',
        'Unnamed: 31',
        'engine_speed_54912',
        'boost_pressure_54912',
        'fuel_5l_consumed_54912',
        'boost_pressure_59912',
        'boost_pressure_50912',
        'engine_speed_50912',
        'fuel_5l_consumed_50912',
        'engine_speed_55912',
        'boost_pressure_55912',
        'fuel_5l_consumed_55912'
    ]

from sqlalchemy import create_engine
import pandas as pd
import numpy as np

import logging

logging.basicConfig(level=logging.DEBUG)

db_host = "34.147.179.203"
db_port = "5432"
db_user = "postgres"
db_password = "Amygda123"

def get_data_from_db_func(data):
    equipment_number = data['equipment_number']
    date = data['date']
    mav_period = data['mavg_period']

    # Database connection config

    table_name = "RAW_DATA"

    # Database engine

    db_name = "ATL"
    db_engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', echo=False)

    # SQL query for fetching the data

    query = """
    SELECT * FROM "RAW_DATA"
    WHERE timestamp BETWEEN %s AND %s
    AND "engine_number" = %s;
    """

    params = (f'{date} 00:00:00', f'{date} 23:59:59', equipment_number)

    df = pd.read_sql(query, db_engine, params=params)

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Remove the columns from the DataFrame if they exist

    df_sample_cleaned = df.drop(columns=[col for col in columns_to_remove if col in df.columns])
    return df_sample_cleaned

def rsmp_and_create_mavg_for_the_data_func(df, mav_period):
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # Resample only the numeric columns and calculate the mean and mavg
    df_resampled_numeric = df[numeric_cols].resample('1T').mean()

    for col in numeric_cols:
        df_resampled_numeric[f'{col}_mavg'] = df_resampled_numeric[col].rolling(window=f"{mav_period}T").mean()

    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    df_resampled = df[non_numeric_cols].join(df_resampled_numeric, how='right')

    df_resampled = df_resampled.rename(columns={col: f"{col}_rsmpl" for col in numeric_cols})

    df_resampled.reset_index(inplace=True)
    
    return df_resampled

def store_proc_data_in_db_func(df, target_table_name):
    # Database engine

    db_name = "ATL"
    db_engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', echo=False)

    # 
    df.to_sql(target_table_name, db_engine, if_exists='append', index=False)

    return 0