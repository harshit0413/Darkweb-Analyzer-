// Get the relevant DOM elements
const pcapFileInput = document.getElementById('pcapFile');
const analyzeButton = document.getElementById('analyzeButton');
const analysisContent = document.getElementById('analysisContent');
const resultsDiv = document.getElementById('results');
const downloadReportButton = document.getElementById('downloadReportButton');

analyzeButton.addEventListener('click', () => {
    const file = pcapFileInput.files[0];
    if (file) {
        // Prepare FormData with the file to send
        const formData = new FormData();
        formData.append('file', file);

        // Display analyzing text and make results visible
        analysisContent.textContent = 'Analyzing...';
        resultsDiv.classList.remove('hidden');

        // Adjust the fetch URL to communicate with the locally running Flask server
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Handle the response data from Flask (the prediction results)
            analysisContent.textContent = `Analysis complete! Results: ${data.prediction}`;
            downloadReportButton.classList.remove('disabled');
        })
        .catch(error => {
            // Handle any errors that occurred during the fetch
            analysisContent.textContent = 'Error analyzing file. See console for details.';
            console.error('Error:', error);
        });
    } else {
        // Alert the user if no file is selected
        alert('Please select a PCAP file to analyze.');
    }
});

// Functionality for 'Download Report' button
downloadReportButton.addEventListener('click', () => {
    const text = analysisContent.textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'analysis_report.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});
