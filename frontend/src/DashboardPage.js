import React from "react";
import "./DashboardPage.css"

function DashboardPage() {
        return (
          <div className="dashboard-container">
            <h2>NBA 3-PT Analysis Dashboard</h2>
            <div className="iframe-wrapper">
                <iframe 
                title="NBA 3-PT Analysis" 
                src="https://app.powerbi.com/reportEmbed?reportId=71c2ed4c-b32e-4ad4-8151-fec20492b6e2&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf"  
                allowFullScreen
                ></iframe>
            </div>
          </div>
        );
      }
      
      export default DashboardPage;