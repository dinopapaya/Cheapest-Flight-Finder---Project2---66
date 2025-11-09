## Team Name: Aviation

## Team Members: Zhuen Zhong, Siddharth Bandaru, Anish Gude

# Project Title: Cheapest Flight Finder

### Problem: Sometimes it is difficult to find the cheapest flight to a certain place online; the project will find the best path minimizing generalized cost.

### Motivation: We want to be able to find the minimum price for a flight. The project will look at direct flights and multi-leg paths, ultimately outputting the most cost effective path.

### Data: All Airline Flight Routes in the US (Kaggle).

### Tools:

### Algorithm implementation: Python

### Visualization: Python(using Streamlist and Folium for interactive map displays)

### Visuals: The system will visualize the algorithm’s pathfinding process and final results using Streamlit and Folium.

### Strategy: We model the flight network as a weighted graph, where cities represent nodes and flights represent edges with associated costs. Using Dijkstra’s algorithm, we will compute the shortest (minimum-cost) path between two cities, ensuring that all edge weights(flight costs) are non-negative.

### Distribution:

#### Zhuen: Implementing the Dijkstra algorithm.

#### Siddharth: Development of the visualization and the user interface to illustrate the pathfinding process.

#### Anish: Assisting both algorithm development and visualization integration.

### Reference:

All Airline Flight Routes in the US (Kaggle): https://www.kaggle.com/datasets/oleksiimartusiuk/all-airline-fight-routes-in-the-us
