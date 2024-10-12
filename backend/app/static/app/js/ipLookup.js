document.addEventListener("DOMContentLoaded", function() {
    const currentIp = document.getElementById("currentIp");
    const lookupIpBtn = document.getElementById("lookupIpBtn");
    const customIp = document.getElementById("customIp");
    const ipDetailsList = document.getElementById("ipDetailsList");

    // Fetch user's IP and details on load
    fetch('https://ipapi.co/json/')
        .then(response => response.json())
        .then(data => {
            currentIp.value = data.ip;  // Show the user's IP initially
            populateIpDetails(data);
        })
        .catch(error => {
            currentIp.value = "Error fetching IP";
        });

    // Enable button when custom IP is entered
    customIp.addEventListener("input", function() {
        lookupIpBtn.disabled = !customIp.value.trim();
    });

    // Lookup custom IP details and show the entered IP in the currentIp field
    lookupIpBtn.addEventListener("click", function() {
        const manualIp = customIp.value.trim();
        fetch(`https://ipapi.co/${manualIp}/json/`)
            .then(response => response.json())
            .then(data => {
                currentIp.value = manualIp;  // Display the manual IP entered by the user
                populateIpDetails(data);
            })
            .catch(error => {
                alert("Error fetching IP details");
            });
    });

    // Function to populate IP details in the card
    function populateIpDetails(data) {
        ipDetailsList.innerHTML = `
            <li><strong>IP:</strong> <span>${data.ip}</span></li>
            <li><strong>City:</strong> <span>${data.city}</span></li>
            <li><strong>Region:</strong> <span>${data.region}</span></li>
            <li><strong>Country:</strong> <span>${data.country_name}</span></li>
            <li><strong>Latitude:</strong> <span>${data.latitude}</span></li>
            <li><strong>Longitude:</strong> <span>${data.longitude}</span></li>
            <li><strong>ISP:</strong> <span>${data.org || "N/A"}</span></li>
        `;
    }
});
