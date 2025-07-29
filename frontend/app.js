const fileUpload = document.getElementById("fileUpload");
const fileText = document.getElementById("fileText");
const analyzeBtn = document.getElementById("analyzeBtn");
const loader = document.getElementById("loader");
const summaryText = document.getElementById("summaryText");
const sentimentText = document.getElementById("sentimentText");
const entitiesList = document.getElementById("entitiesList");
const modeToggle = document.getElementById("modeToggle");
const BACKEND_URL = "http://127.0.0.1:8000/upload"; // ✅ Use FastAPI backend

let entityChart;

// Theme toggle
modeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  modeToggle.textContent = document.body.classList.contains("dark") ? "☀️" : "🌙";
});

// Show selected file name
fileUpload.addEventListener("change", () => {
  if (fileUpload.files.length > 0) {
    fileText.textContent = fileUpload.files[0].name;
  }
});

// Analyze button click
analyzeBtn.addEventListener("click", async () => {
  const file = fileUpload.files[0];
  if (!file) { alert("Please upload a file first!"); return; }

  loader.style.display = "block"; // Show loader
  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(BACKEND_URL, { method: "POST", body: formData });

    if (!response.ok) throw new Error("Failed to analyze document.");
    const data = await response.json();

    // Display results
    summaryText.textContent = data.summary;
    sentimentText.textContent = `${data.sentiment} ${getSentimentEmoji(data.sentiment)}`;
    entitiesList.innerHTML = data.entities.map(e => `<span>${e.Text} (${e.Type})</span>`).join("");
    drawEntityChart(data.entities);
  } catch (e) {
    alert(`Error: ${e.message}`);
  } finally {
    loader.style.display = "none"; // Hide loader
  }
});

// Emoji for sentiment
function getSentimentEmoji(sentiment) {
  switch (sentiment?.toUpperCase()) {
    case "POSITIVE": return "😊";
    case "NEGATIVE": return "😞";
    case "NEUTRAL": return "😐";
    default: return "🤔";
  }
}

// Draw entity chart
function drawEntityChart(entities) {
  const ctx = document.getElementById('entityChart').getContext('2d');
  const typeCounts = {};
  entities.forEach(e => { typeCounts[e.Type] = (typeCounts[e.Type] || 0) + 1; });
  const labels = Object.keys(typeCounts);
  const values = Object.values(typeCounts);
  if (entityChart) entityChart.destroy();
  entityChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        label: 'Entity Types',
        data: values,
        backgroundColor: ['#ff7eb3','#ff758c','#ffb3c6','#ffd1e3','#c9a0dc']
      }]
    }
  });
}

// Particle animation (background)
const canvas = document.getElementById("particles");
const ctx2 = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const particles = Array.from({length:60},()=>({x:Math.random()*canvas.width,y:Math.random()*canvas.height,r:Math.random()*3+1,dx:(Math.random()-0.5)*0.5,dy:(Math.random()-0.5)*0.5}));
function animateParticles() {
  ctx2.clearRect(0,0,canvas.width,canvas.height);
  ctx2.fillStyle="rgba(255,255,255,0.7)";
  particles.forEach(p=>{
    ctx2.beginPath();
    ctx2.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx2.fill();
    p.x+=p.dx;p.y+=p.dy;
    if(p.x<0||p.x>canvas.width) p.dx*=-1;
    if(p.y<0||p.y>canvas.height) p.dy*=-1;
  });
  requestAnimationFrame(animateParticles);
}
animateParticles();
