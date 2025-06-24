from typing import Any, List, Dict, Optional, Tuple, Union
import httpx
from mcp.server.fastmcp import FastMCP
import kagglehub
from kagglehub import KaggleDatasetAdapter
import os
import pandas as pd

# Initialize FastMCP server
mcp = FastMCP("pollution-trends")

# load the kaggle dataset 
path = kagglehub.dataset_download("adityaramachandran27/world-air-quality-index-by-city-and-coordinates")
downloaded_files = os.listdir(path)
csv_file = [f for f in downloaded_files if f.endswith('.csv')][0]
df = pd.read_csv(os.path.join(path, csv_file))

# Global variables
AVAILABLE_CITIES = df['City'].unique().tolist()
AVAILABLE_COUNTRIES = df['Country'].unique().tolist()

#mcp tool 1: fetching data for city
@mcp.tool()
def location_tool(df: pd.DataFrame, user_input: str = None, random_count: int = 5) -> List[Dict[str, str]]:
    """
    Select cities based on user input or randomly from the air quality dataset.
    
    Args:
        df: DataFrame containing air quality data with City and Country columns
        user_input: Optional text to search for matching cities or countries
        random_count: Number of random cities to return if no specific match is found
        
    Returns:
        List of dictionaries containing city and country information
    """
    filtered_df = df.copy()
    
    if user_input and len(user_input.strip()) > 0:
        # Try to match either city or country
        city_match = filtered_df['City'].str.contains(user_input, case=False, na=False)
        country_match = filtered_df['Country'].str.contains(user_input, case=False, na=False)
        filtered_df = filtered_df[city_match | country_match]
        
        if filtered_df.empty:
            return [{"error": f"No cities found matching '{user_input}'"}]
    
    # Get unique city-country pairs to avoid duplicates
    unique_locations = filtered_df[['City', 'Country']].drop_duplicates()
    
    # Select random subset if needed or return all matches up to random_count
    if len(unique_locations) > random_count and (user_input is None or len(user_input.strip()) == 0):
        # If no input or empty input, select random cities
        random_indices = random.sample(range(len(unique_locations)), random_count)
        result = unique_locations.iloc[random_indices].to_dict('records')
    else:
        # Return matching cities, limited by count
        result = unique_locations.head(random_count).to_dict('records')
    
    return result

#mcp tool 2: forecasting air pollution
@mcp.tool()
def fetch_tool() 
 # fetches data using the dataframe
 # Fetch Data Tool: Retrieves pollution data for selected cities


#mcp tool 3: analyze trends
@mcp.tool()
def analyze_trends_tool(): 
    # Analyze Trends Tool: Performs analysis on pollution data across cities


#mcp tool 4: compare cities
@mcp.tool()
def compare_cities_tool():
    # Compare Cities Tool: Compares pollution data between multiple cities







if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')