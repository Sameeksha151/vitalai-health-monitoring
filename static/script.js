const form = document.getElementById("health-form");
const resultSection = document.getElementById("result-section");
const scoreEl = document.getElementById("health-score");
const summaryText = document.getElementById("summary-text");
const recList = document.getElementById("recommendations-list");
const statusText = document.getElementById("health-status");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const formData = new FormData(form);
    const payload = {};

    formData.forEach((v,k)=>payload[k]=v);

    // Show loading state
    summaryText.textContent = "Analyzing your health data...";
    recList.innerHTML = "";
    scoreEl.textContent = "--";
    statusText.textContent = "";

    try {

        const response = await fetch("/analyze",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(payload)
        });

        if(!response.ok){
            throw new Error("Server error");
        }

        const data = await response.json();

        // Health score
        scoreEl.textContent = data.health_score ?? "--";

        const progressBar = document.getElementById("score-progress");
        progressBar.style.width = data.health_score + "%";

        const scoreCircle = document.getElementById("health-score");

        // Status logic
        if (data.health_score >= 80){
            statusText.textContent = "🟢 Healthy";
            statusText.style.color = "#22c55e";
            scoreCircle.style.borderColor = "#22c55e";
            scoreCircle.style.color = "#22c55e";
        }
        else if (data.health_score >= 60){
            statusText.textContent = "🟡 Moderate";
            statusText.style.color = "#f59e0b";
            scoreCircle.style.borderColor = "#f59e0b";
            scoreCircle.style.color = "#f59e0b";
        }
        else{
            statusText.textContent = "🔴 Risk";
            statusText.style.color = "#ef4444";
            scoreCircle.style.borderColor = "#ef4444";
            scoreCircle.style.color = "#ef4444";
        }

        // Summary
        summaryText.textContent = data.summary || "No summary.";

        // Doctor Advice (ADD THIS)
        document.getElementById("doctor-advice").textContent = data.doctor_advice;

        // Recommendations
        recList.innerHTML = "";

        if(Array.isArray(data.recommendations)){
            data.recommendations.forEach((rec)=>{
                const li = document.createElement("li");
                li.textContent = rec;
                recList.appendChild(li);
            });
        }

        // Tips
        const tipsList = document.getElementById("tips-list");
        tipsList.innerHTML = "";

        if(Array.isArray(data.tips)){
            data.tips.forEach((tip)=>{
                const li = document.createElement("li");
                li.textContent = tip;
                tipsList.appendChild(li);
            });
        }

    } catch(err){

        summaryText.textContent = "Something went wrong. Please try again.";
        recList.innerHTML = "";
        statusText.textContent = "";

        console.error(err);
    }

});