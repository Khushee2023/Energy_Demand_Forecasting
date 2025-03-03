document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-forecast');
    const loadingEl = document.getElementById('loading');
    const errorMsgEl = document.getElementById('error-message');
    const forecastResultsEl = document.getElementById('forecast-results');
    const forecastPlotEl = document.getElementById('forecast-plot');
    const peakDemandInfoEl = document.getElementById('peak-demand-info');
    const showHourlyDataBtn = document.getElementById('show-hourly-data');
    const hourlyDataTableEl = document.getElementById('hourly-data-table');

    const today = new Date();
    const dateInput = document.getElementById('start-date');
    dateInput.valueAsDate = today;

    generateBtn.addEventListener('click', generateForecast);
    showHourlyDataBtn.addEventListener('click', toggleHourlyData);

    async function generateForecast() {
       
        loadingEl.classList.remove('hidden');
        forecastResultsEl.classList.add('hidden');
        errorMsgEl.classList.add('hidden');
        
        const days = document.getElementById('forecast-days').value;
        const startDate = document.getElementById('start-date').value;
    
        const formData = new FormData();
        formData.append('days', days);
        if (startDate) {
            formData.append('start_date', startDate);
        }
        
        try {
    
            const response = await fetch('/forecast', {
                method: 'POST',
                body: formData
            });
        
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate forecast');
            }

            displayResults(data.forecast);
            
        } catch (error) {
            errorMsgEl.textContent = error.message;
            errorMsgEl.classList.remove('hidden');
        } finally {
            loadingEl.classList.add('hidden');
        }
    }
    function displayResults(data) {
        forecastResultsEl.classList.remove('hidden');
        forecastPlotEl.innerHTML = `<img src="data:image/png;base64,${data.plot}" alt="Forecast Plot" class="forecast-image">`;
        displayPeakDemand(data.peak_demand);
        createHourlyDataTable(data.forecast);
    }
    function displayPeakDemand(peakData) {
        peakDemandInfoEl.innerHTML = '';
        
        peakData.forEach(peak => {
            const peakDate = new Date(peak.datetime);
            const formattedDate = peakDate.toLocaleDateString('en-US', { 
                weekday: 'long', 
                month: 'short', 
                day: 'numeric' 
            });
            
            const peakCard = document.createElement('div');
            peakCard.className = 'peak-card glow-card';
        
            const prediction = Math.round(peak.prediction);
            
            peakCard.innerHTML = `
                <div class="peak-date">${formattedDate}</div>
                <div class="peak-value">${prediction} MW</div>
                <div class="peak-time">at ${peak.hour}:00</div>
                <div class="tooltip">Based on historical usage patterns and time-based features</div>
            `;
            
            peakDemandInfoEl.appendChild(peakCard);
        });
    }
    
    // Create hourly data table
    function createHourlyDataTable(forecastData) {
        hourlyDataTableEl.innerHTML = '';
        
        // Create table
        const table = document.createElement('table');
        table.className = 'hourly-table';
        
        // Create header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Energy Demand (MW)</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Create body
        const tbody = document.createElement('tbody');
        
        forecastData.forEach(item => {
            const datetime = new Date(item.datetime);
            const date = datetime.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric' 
            });
            const time = datetime.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: true 
            });
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${date}</td>
                <td>${time}</td>
                <td>${item.prediction.toFixed(2)}</td>
            `;
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        hourlyDataTableEl.appendChild(table);
    }
    
    // Toggle hourly data visibility
    function toggleHourlyData() {
        hourlyDataTableEl.classList.toggle('hidden');
        
        if (hourlyDataTableEl.classList.contains('hidden')) {
            showHourlyDataBtn.textContent = 'Show Hourly Data';
        } else {
            showHourlyDataBtn.textContent = 'Hide Hourly Data';
        }
    }
});