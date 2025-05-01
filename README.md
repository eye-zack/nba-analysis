## NBA Threee-Point Analysis System

The NBA Three-point Analysis system is a machine learning based tool designed to analyze and predict trends in NBA three point shooting. It utilizes historical data and current (real-time) data to evaluate the three point attempts and its impact on team success. 

## Features:

## Data Collection and Integration 
    * Retrieves game statistics using NBA API.
    * Structures and stores data in a relational database.
    * Perfroms data cleaning and validation to ensure integrity.
      
## Statistical Analysis
    * Identifies historical trends in three-point attempts.
    * Analyzes the correlation between three-point atttempts and team success.
    * Generates summary reports and visual analytics.
      
## Machine Learning
    * Trains predictive models to forecast future trends in three-point shooting.
    * Allows for input to filter custom analysis. 
    * Continuously updates models with new data.
   
## User Interface
    * Provides an interactive web dashboard for analytics.
    * Supports downloadable reports and graphical visualizations. 
    
## Getting Started
  1. Clone the repo.
     'git clone https://github.com/cwestrichScholar/nba-analysis.git'
  2. change to the repo directory
     'cd nba-analysis'
  3. run the command to setup a virtual environment.
     'python -m venv venv'
     or for windows run
     'source venv/bin/activate' 
  4. install requirements.txt
     'pip install -r requirements.txt'
  5. start the backend seerver
     'uvicorn main:app --reload'
  6. start the frontend service
     'cd fronteend'
     'npm install'
     'npm start'
   7. Optional testing
      'cd testing'
      'pytest'

## Structure Overview
   backend/ contains FastApi server & ML Pipeline
   frontend/ contains React app UI
   testing/ contains test scripts
   models/ contains saved models

## Notes:
  * Developed as a capstone project for CS499.
  * Designed to support future enhancements.  
