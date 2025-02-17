### NBA Shot Insights: Trends, Efficiency & Court Hotspots

#### Design Rationale
This visualization provides an interactive exploration of NBA players' shooting trends, efficiency under defensive pressure, and shot distribution on the court.

#### Visual Encoding Choices
Each chart was designed to highlight a different aspect of shooting performance
1. Shooting Trends Over the Seasons
    - Encoding
        - X-axis: Seasons (Categorical)
        - Y-axis: Shot % and Contested Shot % (Quantitative)
        - Colors: Blue for Shot % and Orange for Contested Shot %
    - Rationale
        - A line chart effectively represents trends over time
        - Dots on the lines allow for better granular insights at each season
        - Dual lines allow comparison between general shot efficiency and defensive contest rate
2. Shot Efficiency vs Defensive Pressure
    - Encoding
        - X-axis: Shot Efficiency (Quantitative)
        - Y-axis: Contest Percentage (Quantitative)
        - Circle Size: Consistent
    - Rationale
        - A scatter plot is ideal for analyzing correlations
        - This chart allows users to understand if contested shots significantly impact efficiency
3. Shot Hotspots Across the Court
    - Encoding
        - X-axis: Court coordinates of shots (Location)
        - Y-axis: Court coordinates of shots (Location)
        - Color: Red to Blue (Indicating shooting accuracy)
    - Rationale
        - Hexbin heatmaps efficiently summarize thousands of data points.
        - The color gradient provides an intuitive sense of high-efficiency zones (blue) vs low-efficiency zones (red).
        - The court outline preserves spatial awareness.

#### Interaction Techniques
1. Search & Filter by Player / Team / Year  
Users can quickly explore individual player tendencies, team shooting styles, or season
2. Smooth Transitions for Data Updates  
This helps maintain visual continuity, preventing sudden jumps in the data
3. Hover Interactions for Data Tooltips  
This provides detailed information without cluttering the charts

#### Alternatives Considered
1. Bar Charts for Trends
    - Line charts showcase trends better over time
2. Shot Location as Scatter Dots
    - Too much clutter with raw shot data, hexbin aggregation makes trends more interpretable
3. Static Filters Instead of Search
    - Searchable player/team selector improves usability over dropdowns

#### References
Data Sources
- https://www.nba.com/stats
- https://github.com/swar/nba_api
- https://github.com/shufinskiy/nba_data

#### Development Process
The development of NBA Shot Insights: Trends, Efficiency & Court Hotspots was a collaborative effort between Kun and James, with work divided based on data preparation, initial implementation, and final refinements. We collaborated asynchronously to work as both of us had time. 

Team Contributions  
- Kun:
    - Collected and cleaned the NBA shooting data.
    - Conducted data preprocessing to ensure accuracy.
    - Implemented initial versions of the three charts.
    - Implemented initial version of the search bar.
    - Implemented interactive features such as hover
- James:
    - Refactored the initial chart implementations and finalized the visualizations.
    - Polished interactive features, including:
        - Search & filter functionality for players, teams, and year.
        - Smooth transitions for updated data.
    - Designed styling, layout, and UI polish for the final visualization.

The project took approximately 18 hours in total
- Data collection & cleaning - 4 hours
- Initial chart implementation - 5 hours
- Interactivity - 5 hours
- Final polishing & refactor - 4 hours

Challenges
1. Data Cleaning & Preprocessing
    - Although all data were queried through nba.com/stats, datasets from various subsections (e.g., hustle vs. NBA league) might have been collected using different methods. Thus, we need to handle discrepancies between these datasets.
    - Some datasets were summarized and pre-aggregated offline to reduce the amount of data needed to be fetched during the initial visualization.
2. Interactivity
    - Given the large dataset, we needed to ensure that filtering and rendering of charts was smooth
3. Layout & Alignment
    - Proper spacing between charts, titles, and other UI elements was challenging