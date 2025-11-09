## Follow these directions to run the code


1. **Clone the repository:**
   ```bash
   git clone https://github.com/dinopapaya/Cheapest-Flight-Finder---Project2---66.git
   cd Cheapest-Flight-Finder---Project2---66
   ```

2. **Create and activate a virtual environment (Command Prompt):**
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Team Name: Aviation

## Team Members: Siddharth Bandaru and Anish Gude

# Project Title: Cheapest Flight Finder

### Problem: Finding the cheapest flight itinerary to a given destination can be time-consuming and confusing due to the large number of airlines, fluctuating prices, and the variety of direct and multi-leg options available. This project automates the process by computing the most cost-effective flight route between two airports in the United States using real flight route data.  


### Motivation: Travelers often spend hours comparing prices across booking platforms. Our project simplifies this process by modeling flights as a **weighted graph** and applying **shortest-path algorithms** to find the optimal (minimum-cost) route.  The goal is to provide an interactive, visual tool that helps users quickly understand the cheapest way to travel across the U.S.  


### Data: All Airline Flight Routes in the US (Kaggle).

### Tools:

### Algorithm implementation: Python

### Visualization: Python(using Streamlist and Folium for interactive map displays)

### Visuals: The system will visualize the algorithm’s pathfinding process and final results using Streamlit and Folium.

### Strategy: We model the flight network as a weighted graph, where cities represent nodes and flights represent edges with associated costs. Using Dijkstra’s algorithm, we will compute the shortest (minimum-cost) path between two cities, ensuring that all edge weights(flight costs) are non-negative.

### Distribution:

#### Anish: Implementing the Dijkstra algorithm.

#### Siddharth: Development of the visualization and the user interface to illustrate the pathfinding process.

#### Anish: Assisting both algorithm development and visualization integration.

### Reference:

All Airline Flight Routes in the US (Kaggle): https://www.kaggle.com/datasets/oleksiimartusiuk/all-airline-fight-routes-in-the-us
