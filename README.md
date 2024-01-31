# NBA Assist Leaders Analysis Web Application

## Overview
This web application provides an interactive analysis of NBA assist leaders over the last 40 years. It fetches and displays game-by-game assist and turnover data for the top assist leaders each season, presenting the information in a series of insightful boxplots.

## Features
- **Data Fetching**: Automatically updates the database with the latest game logs for the top assist leaders every night.
- **Data Visualization**: Generates boxplots showing the distribution of assists and turnovers for each of the top 20 NBA assist leaders.
- **Historical Analysis**: Offers a 40-year retrospective view of assist leaders in the NBA, with detailed game log data.

## Installation

### Prerequisites
- Python 3.x
- Pip (Python package manager)
- PostgreSQL

### Setup
1. **Clone the Repository**
   ```bash
   git clone [repository_url]
   cd [repository_name]

2. **Set Up a Virtual Environment (Optional but recommended)**
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install Dependencies**
   ```bash
    pip install -r requirements.txt

4. **Database Configuration**
    - Set up a PostgreSQL database.
    - Configure the SQLALCHEMY_DATABASE_URI in the application's settings.

5. **Initialize Database**
    ```bash
    flask db upgrade

6. **Run the Application**
    ```bash
    flask run

### Usage
    - Access the web application via http://localhost:5000 or the configured port.
    - Navigate through the application to view different visualizations and analyses.

### Data Fetching
    - The script for fetching and updating the database is scheduled to run every night at 2 AM using a cron job.
    - Manual execution can be done by running the data_fetcher.py script.

### Contributing
    - Contributions to this project are welcome. Please fork the repository and open a pull request with your features or fixes.

### Contact
    Developer: Umar Arshid
    Email: umarsabirvancity@gmail.com





