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
   
4. **Command-line usage:**
   
   ****You can inspect the cheapest fare between two airports directly from the terminal:****
   ```bash
   python main.py ABE PIE
   ```

6. **Streamlit dashboard:**
   
   ****Launch the interactive dashboard to explore routes visually:****
   
   ```bash
   streamlit run app.py
   ```

## Team Name: Aviation

## Team Members: Siddharth Bandaru and Anish Gude

# Project Title: Cheapest Flight Finder

### Problem: Finding the cheapest flight itinerary to a given destination can be time-consuming and confusing due to the large number of airlines, fluctuating prices, and the variety of direct and multi-leg options available. This project automates the process by computing the most cost-effective flight route between two airports in the United States using real flight route data.  


### Motivation: Travelers often spend hours comparing prices across booking platforms. Our project simplifies this process by modeling flights as a **weighted graph** and applying **shortest-path algorithms** to find the optimal (minimum-cost) route.  The goal is to provide an interactive, visual tool that helps users quickly understand the cheapest way to travel across the U.S.  


### Data: All Airline Flight Routes in the US (Kaggle).

### Tools:

#### Python: Core implementation of Dijkstra’s and Bellman-Ford algorithms for efficient shortest path computation. Used for visualization, data handling, and integration between backend logic and front-end interface.
#### Streamlit: Builds an interactive web application interface.
#### Folium: Generates interactive maps to visualize the shortest flight path.
#### Pandas: Used for efficient data loading and preprocessing of the flight dataset.

### Algorithm implementation: Python

### Visualization: Python(using Streamlist and Folium for interactive map displays)

### Visuals: The system will visualize the algorithm’s pathfinding process and final results using Streamlit and Folium.

### Distribution:

#### Anish: Implementing the Dijkstra algorithm.

#### Siddharth: Designed and implemented the Python-based visualization interface using Streamlit and Folium. Also contributed to algorithm testing and integration between backend and frontend.

#### Anish: Focused on developing and debugging the graph algorithms (Dijkstra and Bellman-Ford) in Python, ensuring efficiency and correctness. Also assisted in data preprocessing and system testing.

### Reference:

All Airline Flight Routes in the US (Kaggle): https://www.kaggle.com/datasets/oleksiimartusiuk/all-airline-fight-routes-in-the-us
