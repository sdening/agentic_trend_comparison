# Agentic Trend Comparison: Air Pollution Analysis

This project provides a set of agentic tools to fetch, analyze, and visualize global air quality data. It leverages a Kaggle dataset to provide insights into pollution trends for various cities around the world. The system is built using the `FastMCP` framework, allowing an agent to interact with the tools programmatically.

## ✨ Features

- **City Discovery**: Find cities by name or country, or get a random selection of locations.
- **Data Retrieval**: Fetch detailed, time-series pollution data for specified cities.
- **In-depth Analysis**: Calculate overall AQI, identify primary pollutants, and determine long-term trends (improving, worsening, or stable) using linear regression.
- **Data Visualization**: Generate and save time-series plots to visualize AQI trends over time for one or more cities.

## 🛠️ Implemented Tools

This project exposes its functionality through a series of `MCP` tools:

- **`location_tool`**: Selects cities based on user input or randomly from the dataset.
- **`fetch_tool`**: Retrieves the raw pollution data records for the selected cities.
- **`analyze_trends_tool`**: Processes the raw data to generate a summary, including average AQI, primary pollutant, and the pollution trend over time.
- **`plot_trends_tool`**: Creates a `.png` plot of the AQI data over time and saves it to the `~/air_pollution_artefacts` directory.

## 🚀 Getting Started

To run the agentic tool MCP Server, execute the following command from the root directory of the project:

## Overview
MCP (Model Context Protocol) Servers allow AI assistants like Claude and Amazon Q developer CLI to access tools and data sources. This repository includes MCP Servers for data fetching and analysis to help you get started with MCP for air data analysis based on city. 

To use the Application Modernization MCP Servers, two approaches will be covered:
- Claude Desktop


## Prerequisites
#### **1. Clone the current repository:**
```bash
git clone ....
```  

And navigate to the project folder:
```bash
cd pollution_trends
```  

#### **2. Install MCP Python SDK:**
--> [GitHub Repository](https://github.com/modelcontextprotocol/python-sdk)  

For this:  
Install `uv` package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```  
Add project dependencies: 
```bash
cd application_modernization
uv add "mcp[cli]"
```  
If you encounter an error regarding a missing `pyproject.toml` when using `uv add`, you can alternatively install the package using `pip`:
```bash
pip install "mcp[cli]"
```  

This will start the `FastMCP` server, which listens for tool calls via `stdio`.


**Setup Instructions for the custom MCP Servers **
Follow these steps to get the custom Code Modernization MCP server up and running.  

#### **1. Navigate to Project Folder**
```bash
cd pollution_trends 
```

#### **2. Create virtual environment and activate it**
```bash
uv venv
source .venv/bin/activate
```

#### **3. Install dependencies**
```bash
uv add "mcp[cli]" httpx
```

## Using MCP Servers

### Option - Claude Desktop
1. Install Claude Desktop application (https://claude.ai/download)  
2. Configure Claude to use your MCP server:  
Open the configuration file (Mac): `~/Library/Application Support/Claude/claude_desktop_config.json`  
Add your MCP server configuration:
```json
{
  "mcpServers": {
    "code_modernization": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "<full_path_to_code_analysis_modernization/pollution_trends.py>"
      ]
    }
  }
}
```
Ensure that the paths are correctly specified. Incorrect paths will prevent the servers from starting.

**Note:** If `"command": "uv"` doesn't work, use the absolute path to uv instead: `/Users/<username>/.local/bin/uv`  
3. Save json and restart Claude Desktop  
4. Your tool should appear in the chat interface  
5. Start using your tools and interact with them 🚀   

## ✅ Project Status & To-Do

- [x] Implement Kaggle Dataset integration.
- [x] Develop core data analysis logic.
- [x] Set up the agentic tool structure with `FastMCP`.
- [x] Implement `location_tool`, `fetch_tool`, `analyze_trends_tool`, and `plot_trends_tool`.
- [ ] Implement a `comparison_tool` to directly compare the analysis results of multiple cities.
- [ ] Filming and documenting demo of how it works. 

## 📊 Data Source

This project uses the World Air Quality Index by City and Coordinates dataset from Kaggle.
