from typing import Any, List, Dict, Optional, Tuple, Union
import httpx
from mcp.server.fastmcp import FastMCP
import random
import kagglehub
import os
import pandas as pd
from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("pollution-trends")

# load the kaggle dataset 
path = kagglehub.dataset_download("adityaramachandran27/world-air-quality-index-by-city-and-coordinates")
downloaded_files = os.listdir(path)
csv_file = [f for f in downloaded_files if f.endswith('.csv')][0]
# The 'Date' column in this dataset is not uniformly formatted, causing parsing errors.
# We will read it as a string and handle conversions within the analysis tool.
# For a real-world scenario, cleaning this column upon loading would be ideal.
df = pd.read_csv(os.path.join(path, csv_file))

# Global variables
AVAILABLE_CITIES = df['City'].unique().tolist()
AVAILABLE_COUNTRIES = df['Country'].unique().tolist()

#mcp tool 1: fetching data for city
@mcp.tool()
def location_tool(user_input: str = None, random_count: int = 5) -> List[Dict[str, str]]:
    """
    Select cities based on user input or randomly from the air quality dataset.
    
    Args:
        user_input: Optional text to search for matching cities or countries
        random_count: Number of random cities to return if no specific match is found
        
    Returns:
        List of dictionaries containing city and country information
    """
    if user_input and len(user_input.strip()) > 0:
        filtered_df = df.copy()
        # Try to match either city or country
        city_match = filtered_df['City'].str.contains(user_input, case=False, na=False)
        country_match = filtered_df['Country'].str.contains(user_input, case=False, na=False)
        filtered_df = filtered_df[city_match | country_match]

        if filtered_df.empty:
            return [{"error": f"No cities found matching '{user_input}'"}]
    else:
        # If no user input, select random cities from the entire dataset
        unique_locations = df[['City', 'Country']].drop_duplicates() # Use the original df for random selection
        if len(unique_locations) <= random_count:
            return unique_locations.to_dict('records')
        else:
            random_indices = random.sample(range(len(unique_locations)), random_count)
            return unique_locations.iloc[random_indices].to_dict('records')

    # For user_input case, return all unique matches
    unique_locations = filtered_df[['City', 'Country']].drop_duplicates()
    return unique_locations.to_dict('records')

#mcp tool 2: forecasting air pollution
@mcp.tool()
def fetch_tool(cities_info: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Fetches pollution data for the specified cities.

    Args:
        cities_info: A list of dictionaries, where each dictionary contains 'City' and 'Country' keys,
                     typically obtained from the location_tool. Example: [{'City': 'London', 'Country': 'United Kingdom'}]

    Returns:
        A list of dictionaries, where each dictionary represents a row of pollution data
        for the specified cities. Returns an empty list if no data is found or an error message.
    """
    if not cities_info:
        return []

    # Extract city names from the input, handling potential error messages from location_tool
    valid_cities_info = [info for info in cities_info if 'City' in info and 'error' not in info]
    if not valid_cities_info:
        # If the input was just an error message from location_tool, propagate it or handle
        if cities_info and 'error' in cities_info[0]:
            return cities_info # Propagate the error message
        return [] # No valid cities to process

    city_names = [info['City'] for info in valid_cities_info]

    # Filter the global DataFrame 'df' based on the extracted city names
    # Assuming 'City' column exists in df
    filtered_data = df[df['City'].isin(city_names)]

    if filtered_data.empty:
        # If no data found for the given cities, return an informative message
        return [{"error": f"No detailed pollution data found for cities: {', '.join(city_names)}. "
                           "The dataset might not contain detailed pollution metrics for these locations."}]

    # Convert the filtered DataFrame to a list of dictionaries
    # This will include all columns for the matched rows
    return filtered_data.to_dict(orient='records')


#mcp tool 3: analyze trends
@mcp.tool()
def analyze_trends_tool(pollution_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes pollution data to provide a summary and time-series trend for each city.
    If a 'Date' column is available, it calculates the trend. Otherwise, it provides a snapshot summary.

    Args:
        pollution_data: A list of dictionaries, with each dictionary representing a row of pollution data,
                        typically from the fetch_tool.

    Returns:
        A dictionary containing the analysis summary for each city, including trend information if available.
        Example: {'London': {'Overall AQI': 55, 'AQI Category': 'Moderate', 'Primary Pollutant': 'Ozone', 'Trend': 'Improving', 'Note': 'Trend based on 15 data points.'}}
    """
    if not pollution_data or ('error' in pollution_data[0]):
        return {"error": "No data available to analyze. Please fetch data for a city first.", "details": pollution_data}

    analysis_df = pd.DataFrame(pollution_data)
    results = {}

    # Check if a date column exists for time-series analysis
    has_date_column = 'Date' in analysis_df.columns and analysis_df['Date'].notna().any()

    if has_date_column:
        # Attempt to convert 'Date' to datetime, coercing errors to NaT (Not a Time)
        analysis_df['Date'] = pd.to_datetime(analysis_df['Date'], errors='coerce')
        # Drop rows where date conversion failed
        analysis_df.dropna(subset=['Date'], inplace=True)

    pollutant_cols = {
        'PM2.5': 'PM2.5 AQI Value', 'Ozone': 'Ozone AQI Value',
        'NO2': 'NO2 AQI Value', 'CO': 'CO AQI Value'
    }

    for city, group in analysis_df.groupby('City'):
        city_results = {}
        city_results['Overall AQI'] = round(group['AQI Value'].mean(), 2)
        city_results['AQI Category'] = group['AQI Category'].mode()[0] if not group['AQI Category'].mode().empty else 'N/A'

        max_pollutant_val = -1
        primary_pollutant = 'N/A'
        for pollutant_name, col_name in pollutant_cols.items():
            if col_name in group and not group[col_name].isnull().all():
                current_val = group[col_name].mean()
                if current_val > max_pollutant_val:
                    max_pollutant_val = current_val
                    primary_pollutant = pollutant_name
        city_results['Primary Pollutant'] = primary_pollutant

        #analyse data over time
        if has_date_column and len(group) > 2:
            # Sort by date and prepare data for regression
            sorted_group = group.sort_values('Date').dropna(subset=['AQI Value'])
            if len(sorted_group) > 2:
                # Convert dates to numerical values (days from the start) for regression
                days = (sorted_group['Date'] - sorted_group['Date'].min()).dt.days
                aqi_values = sorted_group['AQI Value']
                
                # Perform linear regression
                slope, _, r_value, p_value, _ = linregress(days, aqi_values)
                
                # Determine trend based on slope and statistical significance (p-value < 0.05)
                if p_value < 0.05:
                    city_results['Trend'] = 'Improving' if slope < 0 else 'Worsening'
                else:
                    city_results['Trend'] = 'Stable'
                city_results['Note'] = f"Trend based on {len(sorted_group)} data points (r-squared: {r_value**2:.2f})."
        else:
            city_results['Note'] = "Snapshot summary; not enough data for trend analysis."
        
        results[city] = city_results

    if not results:
        return {"error": "Could not generate analysis from the provided data."}

    return results


#mcp tool 4: compare cities
#@mcp.tool()
#def compare_cities_tool():
    # Compare Cities Tool: Compares pollution data between multiple cities


#mcp tool 5: plot results
@mcp.tool()
def plot_trends_tool(pollution_data: List[Dict[str, Any]], output_dir: str = "air_pollution_artefacts") -> Dict[str, str]:
    """
    Generates and saves a time-series plot of AQI values for the given city data.
    The plot is saved to a directory in the user's home folder.

    Args:
        pollution_data: A list of dictionaries containing pollution data from fetch_tool.
        output_dir: The directory under the user's home folder to save the plot image.

    Returns:
        A dictionary with the path to the saved plot or an error message.
    """
    if not pollution_data or ('error' in pollution_data[0]):
        return {"error": "No data available to plot.", "details": pollution_data}

    plot_df = pd.DataFrame(pollution_data)

    #get data
    if 'Date' not in plot_df.columns or plot_df['Date'].notna().sum() < 2:
        return {"error": "Cannot generate plot. Data does not contain sufficient date information."}

    plot_df['Date'] = pd.to_datetime(plot_df['Date'], errors='coerce')
    plot_df.dropna(subset=['Date', 'AQI Value'], inplace=True)
    plot_df.sort_values('Date', inplace=True)

    if plot_df.empty:
        return {"error": "No valid data points remaining after cleaning for plotting."}

    #save here
    home_dir = os.path.expanduser("~")
    save_path = os.path.join(home_dir, output_dir)
    os.makedirs(save_path, exist_ok=True)

    #plot
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 8))
    cities = plot_df['City'].unique()
    sns.lineplot(data=plot_df, x='Date', y='AQI Value', hue='City', marker='o', ax=ax)
    ax.set_title(f'Air Quality Index (AQI) Trend for {", ".join(cities)}', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('AQI Value', fontsize=12)
    ax.legend(title='City')
    fig.autofmt_xdate()
    plt.tight_layout()

    #save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aqi_trend_{'_'.join(cities).replace(' ', '_')}_{timestamp}.png"
    full_path = os.path.join(save_path, filename)
    plt.savefig(full_path)
    plt.close(fig)

    return {"status": f"Plot successfully generated for {', '.join(cities)}.", "plot_path": full_path}



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')