import React from "react";
import "./UserPage.css"
import { Link } from "react-router-dom";

function User({favoriteTeam = "Atlanta Hawks"}) {

    const teamDashboards = {
        "Atlanta Hawks": "https://app.powerbi.com/reportEmbed?reportId=a05b2eed-3429-4052-9881-d05df802b153&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf", 
        "Boston Celtics": "https://app.powerbi.com/reportEmbed?reportId=743e8d38-e622-4330-9b27-8f200ff4b8c8&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Brooklyn Nets": "https://app.powerbi.com/reportEmbed?reportId=9a430350-dc42-4926-990a-ae244f853dfe&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Charlotte Hornets": "https://app.powerbi.com/reportEmbed?reportId=a5ed183e-e5a0-4ffd-80f1-b2e5dabc64e4&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Chicago Bulls": "https://app.powerbi.com/reportEmbed?reportId=288d3b37-a168-45e7-a9b3-cfffca035b3b&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Cleveland Cavaliers": "https://app.powerbi.com/reportEmbed?reportId=029f1e2e-bd09-4a10-9427-4a88cb96af1f&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Dallas Mavericks": "https://app.powerbi.com/reportEmbed?reportId=98d4d39f-04ce-4349-a01e-6a4f01798ba9&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Denver Nuggets": "https://app.powerbi.com/reportEmbed?reportId=c9b4454c-69da-4b03-94eb-6037434ef35f&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Detroit Pistons": "https://app.powerbi.com/reportEmbed?reportId=37705011-7641-4cd1-bca4-4bfc648a6afb&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Golden State Warriors": "https://app.powerbi.com/reportEmbed?reportId=5316298a-a58b-470d-b7c7-13afd569b97d&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Houston Rockets": "https://app.powerbi.com/reportEmbed?reportId=6b81c746-ea26-40fa-9146-90539b4f45dc&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Indiana Pacers": "https://app.powerbi.com/reportEmbed?reportId=b953e6cd-ba2f-40c3-bf1d-507aa6ee3c32&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "LA Clippers": "https://app.powerbi.com/reportEmbed?reportId=96a0b9f0-e993-4c07-bd63-8a62d8502798&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Los Angeles Lakers": "https://app.powerbi.com/reportEmbed?reportId=e075e088-b4cf-453e-9f36-7b09af0efdce&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Memphis Grizzlies": "https://app.powerbi.com/reportEmbed?reportId=de88168d-73c5-4440-b3f2-9fc4c0ce2e0f&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Miami Heat": "https://app.powerbi.com/reportEmbed?reportId=01d6fcdd-a0ef-4bc1-bd03-76d8dbe0c368&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Milwaukee Bucks": "https://app.powerbi.com/reportEmbed?reportId=3d2ec1ec-e853-4806-b574-af13f6ac73b9&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Minnesota Timberwolves": "https://app.powerbi.com/reportEmbed?reportId=7481d957-71af-4eaa-ba12-62358d6cca48&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "New Orleans Pelicans": "https://app.powerbi.com/reportEmbed?reportId=ca89c456-eaee-449c-90f1-6cc4738a4db5&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "New York Knicks": "https://app.powerbi.com/reportEmbed?reportId=1acb3f08-6a75-4e29-a4aa-267477df3724&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Oklahoma City Thunder": "https://app.powerbi.com/reportEmbed?reportId=6ea468a6-b5f3-446c-9bbc-2ff248d4b74e&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Orlando Magic": "https://app.powerbi.com/reportEmbed?reportId=81e3bc11-1fbc-47b6-9267-217e346aa327&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Philadelphia 76ers": "https://app.powerbi.com/reportEmbed?reportId=25f8c2ee-b257-4f2e-b67c-f36967d0e7a5&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Phoenix Suns": "https://app.powerbi.com/reportEmbed?reportId=e17a5cf9-30f8-4c35-97ef-b52895669982&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Portland Trail Blazers": "https://app.powerbi.com/reportEmbed?reportId=fcde58a1-5dec-4192-8a59-7483dc1b21e6&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Sacramento Kings": "https://app.powerbi.com/reportEmbed?reportId=df6c3294-1c0e-40e3-a984-4953f6bd2743&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "San Antonio Spurs": "https://app.powerbi.com/reportEmbed?reportId=36913a32-5363-4fbd-9a94-c672be55ecac&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Toronto Raptors": "https://app.powerbi.com/reportEmbed?reportId=a85312a9-bde0-4f46-a651-97e9f7d1bf08&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Utah Jazz": "https://app.powerbi.com/reportEmbed?reportId=138a238f-ec45-4d0b-9d62-022e3fd17a8e&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf",
        "Washington Wizards": "https://app.powerbi.com/reportEmbed?reportId=883becd5-6c32-47fb-a8f9-a8253e8e223e&autoAuth=true&ctid=19d57598-97b0-442c-b74e-c855b0d87caf"   
    };

    // add debug output
    console.log("Received favoriteTeam:", favoriteTeam);

    // normalize team names 
    const selectedTeam = Object.keys(teamDashboards).find(
        team => team.toLowerCase() === favoriteTeam?.toLowerCase() 
    ) || "Atlanta Hawks";
        
    console.log("Resolved team:", selectedTeam);

    const publicUrl = teamDashboards[selectedTeam];

    console.log("Selected dashboard URL:", publicUrl);

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h2>{selectedTeam} 3-PT Analysis Dashboard</h2>
                <Link to="/dashboard" className="nba-dashboard-link">
                    View Full NBA Dashboard
                </Link>
            </div>
            <div className="iframe-wrapper">
                <iframe
                title={`${selectedTeam} 3-PT Analysis`}
                src={publicUrl}
                allowFullScreen
                sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
                ></iframe>
            </div>
        </div>
    );
}
      export default User;