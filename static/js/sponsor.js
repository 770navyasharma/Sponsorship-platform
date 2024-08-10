document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".navbar a, .nav-link");
    const sections = document.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        // Skip the logout link from tab handling
        if (tab.getAttribute("href") === "/logout") {
            return;
        }

        tab.addEventListener("click", event => {
            event.preventDefault();

            // Remove active classes from all tabs and sections
            tabs.forEach(t => t.classList.remove("active"));
            sections.forEach(section => section.style.display = "none");

            // Add active class to the clicked tab
            tab.classList.add("active");

            // Show the corresponding section
            const targetId = tab.getAttribute("href").substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.style.display = 'block';
            } else {
                console.error('Target section not found:', targetId);
            }
        });
    });

    // Set default tab and section to active
    if (tabs.length > 0) {
        tabs[0].classList.add("active");
    }
    sections.forEach(section => section.style.display = "none");
    if (sections.length > 0) {
        sections[0].style.display = "block";
    }

    // Create Campaign Modal functionality
    const createCampaignBtn = document.getElementById("createCampaignBtn");
    const createCampaignModal = document.getElementById("createCampaignModal");
    const createCampaignForm = document.getElementById("createCampaignForm");

    // Function to open the modal
    createCampaignBtn.addEventListener("click", () => {
        createCampaignModal.style.display = "block";
    });

    // Function to close the modal
    window.closeCreateCampaignModal = function() {
        createCampaignModal.style.display = "none";
    }

    // Close the modal if the user clicks outside of it
    window.addEventListener("click", event => {
        if (event.target === createCampaignModal) {
            createCampaignModal.style.display = "none";
        }
    });

    // Handle form submission
    createCampaignForm.addEventListener("submit", event => {
        event.preventDefault();

        const formData = new FormData(createCampaignForm);

        fetch('/create_campaign', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                location.reload();  // Reload the page to reflect the changes
            } else {
                alert(data.message);
            }
            closeCreateCampaignModal();  // Close the modal after form submission
        })
        .catch(error => console.error('Error creating campaign:', error));
    });
    // Load sponsor data
    loadSponsorData();
});


function loadSponsorData() {
    fetch('/sponsor_dashboard')
        .then(response => response.json())
        .then(data => {
            document.getElementById("sponsor-name").textContent = data.sponsor.company_name;
            document.getElementById("company-name").textContent = data.sponsor.company_name;
            document.getElementById("industry").textContent = data.sponsor.industry;
            document.getElementById("budget").textContent = `$${data.sponsor.budget}`;

            const ongoingCampaigns = document.getElementById("ongoing-campaigns");
            ongoingCampaigns.innerHTML = ''; // Clear previous data
            data.ongoing_campaigns.forEach(campaign => {
                const div = document.createElement("div");
                div.textContent = `Campaign: ${campaign.name} - Budget: $${campaign.budget}`;
                const viewButton = document.createElement("button");
                viewButton.textContent = "View";
                viewButton.className = "view-campaign-btn";
                viewButton.dataset.campaignId = campaign.id;
                div.appendChild(viewButton);
                ongoingCampaigns.appendChild(div);
            });

            const newRequests = document.getElementById("new-ad-requests");
            newRequests.innerHTML = ''; // Clear previous data
            data.pending_ad_requests.forEach(request => {
                const div = document.createElement("div");
                div.textContent = `Campaign: ${request.campaign.name} - Influencer: ${request.influencer.user.username}`;
                const viewButton = document.createElement("button");
                viewButton.textContent = "View";
                viewButton.className = "view-influencer-btn";
                viewButton.dataset.adRequestId = request.id;
                div.appendChild(viewButton);
                newRequests.appendChild(div);
            });

            const campaignsContainer = document.getElementById("campaigns-container");
                campaignsContainer.innerHTML = ''; // Clear previous data
                data.campaigns.forEach(campaign => {
                    const campaignCard = document.createElement("div");
                    campaignCard.className = "campaign-card col-md-4";
                    campaignCard.innerHTML = `
                        <h4>${campaign.name}</h4>
                        <p>${campaign.description}</p>
                        <p><strong>Budget:</strong> $${campaign.budget}</p>
                        <p><strong>Start Date:</strong> ${campaign.start_date}</p>
                        <p><strong>End Date:</strong> ${campaign.end_date}</p>
                    `;
                    campaignsContainer.appendChild(campaignCard);
                });
        })
        // .catch(error => console.error('Error loading sponsor data:', error));
}

document.addEventListener("DOMContentLoaded", () => {
    const campaignsContainer = document.getElementById("campaigns-container");
    const updateForm = document.getElementById("updateCampaignForm");
    const updateModal = document.getElementById("updateCampaignModal");
    const closeModalBtn = updateModal.querySelector(".close");

    // Function to open the modal
    function openModal() {
        updateModal.style.display = "block";
    }

    // Function to close the modal
    function closeModal() {
        updateModal.style.display = "none";
    }

    // Close modal when the user clicks on the close button
    closeModalBtn.addEventListener("click", closeModal);

    // Close modal when the user clicks outside of the modal content
    window.addEventListener("click", event => {
        if (event.target === updateModal) {
            closeModal();
        }
    });

    // Event delegation for update and delete buttons
    campaignsContainer.addEventListener("click", event => {
        if (event.target.classList.contains("update-campaign-btn")) {
            const campaignId = event.target.getAttribute("data-campaign-id");
            console.log(`Update button clicked for campaign ID: ${campaignId}`);
            fetch(`/get_campaign/${campaignId}`)
                .then(response => response.json())
                .then(data => {
                    // Populate the form with the campaign's current details
                    document.getElementById("campaignId").value = data.id;
                    document.getElementById("name").value = data.name;
                    document.getElementById("description").value = data.description;
                    document.getElementById("budget").value = data.budget;
                    document.getElementById("start_date").value = data.start_date;
                    document.getElementById("end_date").value = data.end_date;
                    // Show the modal
                    openModal();
                })
                .catch(error => console.error('Error fetching campaign:', error));
        } else if (event.target.classList.contains("delete-campaign-btn")) {
            const campaignId = event.target.getAttribute("data-campaign-id");
            console.log(`Delete button clicked for campaign ID: ${campaignId}`);
            if (confirm("Are you sure you want to delete this campaign?")) {
                fetch(`/delete_campaign/${campaignId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        alert("Campaign deleted successfully.");
                        location.reload();  // Reload the page to reflect the changes
                    } else {
                        alert("Failed to delete campaign.");
                    }
                })
                .catch(error => console.error('Error deleting campaign:', error));
            }
        }
    });

    // Handle the form submission to update the campaign
    updateForm.addEventListener("submit", event => {
        event.preventDefault();

        const formData = new FormData(updateForm);
        const campaignId = formData.get("campaignId");

        // Send the updated campaign data to the server
        fetch(`/update_campaign/${campaignId}`, {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                alert("Campaign updated successfully.");
                closeModal();
                location.reload();  // Reload the page to reflect the changes
            } else {
                alert("Failed to update campaign.");
            }
        })
        .catch(error => console.error('Error updating campaign:', error));
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    const searchButton = document.getElementById("searchButton");
    const influencerResults = document.getElementById("influencerResults");
    const viewInfluencerModal = document.getElementById("viewInfluencerModal");
    const createAdRequestModal = document.getElementById("createAdRequestModal");
    const adRequestForm = document.getElementById("createAdRequestForm");

    // Function to fetch and display influencers based on search
    const searchInfluencers = () => {
        const query = searchInput.value;
        if (query.trim() === "") {
            alert("Please enter a search query.");
            return;
        }
        
        fetch(`/search_influencers?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                influencerResults.innerHTML = '';
                if (data.influencers.length === 0) {
                    influencerResults.innerHTML = '<p>No influencers found.</p>';
                } else {
                    data.influencers.forEach(influencer => {
                        const influencerCard = document.createElement('div');
                        influencerCard.className = 'col-md-4 mb-3';
                        influencerCard.innerHTML = `
                            <div class="card search-result-card">
                                <div class="card-body">
                                    <h5 class="card-title">${influencer.name}</h5>
                                    <p><strong>Niche:</strong> ${influencer.niche}</p>
                                    <button class="btn btn-info view-influencer-btn" data-id="${influencer.id}">View</button>
                                    <button class="btn btn-primary request-ad-btn" data-id="${influencer.id}">Request</button>
                                </div>
                            </div>
                        `;
                        influencerResults.appendChild(influencerCard);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    };

    // Function to fetch and populate campaigns
    const loadCampaigns = () => {
        fetch('/get_campaigns')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch campaigns');
                }
                return response.json();
            })
            .then(data => {
                const campaignSelect = document.getElementById("campaignSelect");
                campaignSelect.innerHTML = '';

                if (!data.campaigns || data.campaigns.length === 0) {
                    campaignSelect.innerHTML = '<option>No campaigns available</option>';
                } else {
                    data.campaigns.forEach(campaign => {
                        const option = document.createElement('option');
                        option.value = campaign.id;
                        option.textContent = campaign.name;
                        campaignSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const campaignSelect = document.getElementById("campaignSelect");
                campaignSelect.innerHTML = '<option>Error loading campaigns</option>';
            });
    };

    // Event listener for search button
    searchButton.addEventListener("click", searchInfluencers);

    // Event delegation for view and request buttons
    influencerResults.addEventListener("click", event => {
        if (event.target.classList.contains("view-influencer-btn")) {
            const influencerId = event.target.getAttribute("data-id");
            fetch(`/get_influencer/${influencerId}`)
                .then(response => response.json())
                .then(data => {
                    const details = `
                        <p><strong>Name:</strong> ${data.name}</p>
                        <p><strong>Email:</strong> ${data.email}</p>
                        <p><strong>Niche:</strong> ${data.niche}</p>
                        <p><strong>Category:</strong> ${data.category}</p>
                        <p><strong>Reach:</strong> ${data.reach}</p>
                    `;
                    document.getElementById("influencerDetails").innerHTML = details;
                    $(viewInfluencerModal).modal('show');
                })
                .catch(error => console.error('Error fetching influencer details:', error));
        } else if (event.target.classList.contains("request-ad-btn")) {
            const influencerId = event.target.getAttribute("data-id");
            document.getElementById("selectedInfluencerId").value = influencerId;
            loadCampaigns(); // Load campaigns when opening the modal
            $(createAdRequestModal).modal('show');
        }
    });

    // Handle form submission for creating ad request
    adRequestForm.addEventListener("submit", event => {
        event.preventDefault();
        const formData = new FormData(adRequestForm);

        fetch("/create_ad_request", {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                alert("Ad request sent successfully.");
                $(createAdRequestModal).modal('hide');
            } else {
                alert("Failed to send ad request.");
            }
        })
        .catch(error => {
            console.error('Error submitting ad request:', error);
            alert("An error occurred while sending the ad request.");
        });
    });

    // Close modals
    const closeModals = () => {
        $(viewInfluencerModal).modal('hide');
        $(createAdRequestModal).modal('hide');
    };

    document.querySelectorAll(".modal .close").forEach(closeBtn => {
        closeBtn.addEventListener("click", closeModals);
    });

    window.addEventListener("click", event => {
        if (event.target === viewInfluencerModal || event.target === createAdRequestModal) {
            closeModals();
        }
    });
});


$(document).ready(function() {
    // Handle view details button click for ad requests
    $('.view-request-btn').on('click', function() {
        var requestId = $(this).data('ad-request-id');
        $.getJSON('/sponsor/request/' + requestId, function(data) {
            if (data.error) {
                alert(data.error);
            } else {
                // Populate modal with ad request details
                $('#ad-request-details').html(`
                    <h3>Request ID: ${data.request_id}</h3>
                    <p><strong>Requirements:</strong> ${data.requirements}</p>
                    <p><strong>Payment Amount:</strong> ${data.payment_amount}</p>
                    <p><strong>Status:</strong> ${data.status}</p>
                    <h4>Influencer Details</h4>
                    <p><strong>Name:</strong> ${data.influencer.name}</p>
                    <p><strong>Category:</strong> ${data.influencer.category}</p>
                    <p><strong>Niche:</strong> ${data.influencer.niche}</p>
                    <p><strong>Reach:</strong> ${data.influencer.reach}</p>
                    <h4>Campaign Details</h4>
                    <p><strong>Name:</strong> ${data.campaign.name}</p>
                    <p><strong>Description:</strong> ${data.campaign.description}</p>
                    <p><strong>Start Date:</strong> ${data.campaign.start_date}</p>
                    <p><strong>End Date:</strong> ${data.campaign.end_date}</p>
                `);
                $('#ad-request-details-modal').modal('show');
            }
        });
    });
});

$(document).ready(function() {
    $('.view-btn').on('click', function() {
        var influencerName = $(this).data('influencer');
        var adRequestId = $(this).data('ad-request-id');
        $.ajax({
            url: '/get_influencer_details',
            method: 'POST',
            data: { ad_request_id: adRequestId },
            success: function(data) {
                $('#influencer-details').html(
                    `<p>Username: ${data.username}</p>
                    <p>Category: ${data.category}</p>
                    <p>Niche: ${data.niche}</p>
                    <p>Reach: ${data.reach}</p>`
                );
                $('#ex1').modal('open');
            }
        });
    });

    $('.view-campaign-btn').on('click', function() {
        var campaignId = $(this).data('campaign-id');
        $.ajax({
            url: '/get_campaign_details',
            method: 'POST',
            data: { campaign_id: campaignId },
            success: function(data) {
                var adRequestsHtml = data.ad_requests.map(function(ad_request) {
                    return `
                        <div>
                            <span>Influencer: ${ad_request.influencer_name}</span>
                            <button class="view-influencer-btn" data-ad-request-id="${ad_request.id}">View</button>
                        </div>
                    `;
                }).join('');

                $('#campaign-details').html(`
                    <p>Name: ${data.name}</p>
                    <p>Description: ${data.description}</p>
                    <p>Start Date: ${data.start_date}</p>
                    <p>End Date: ${data.end_date}</p>
                    <p>Budget: ${data.budget}</p>
                    <p>Visibility: ${data.visibility}</p>
                    <p>Goals: ${data.goals}</p>
                    <h5>Accepted Ad Requests</h5>
                    ${adRequestsHtml}
                `);
                $('#campaign-details-modal').modal('open');
            }
        });
    });

    // Use event delegation to handle dynamically added view-influencer-btn buttons
    $(document).on('click', '.view-influencer-btn', function() {
        var adRequestId = $(this).data('ad-request-id');
        $.ajax({
            url: '/get_influencer_details',
            method: 'POST',
            data: { ad_request_id: adRequestId },
            success: function(data) {
                $('#influencer-details').html(
                    `<p>Username: ${data.username}</p>
                    <p>Category: ${data.category}</p>
                    <p>Niche: ${data.niche}</p>
                    <p>Reach: ${data.reach}</p>`
                );
                $('#influencer-details-modal').modal('open');
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const statsOptions = document.querySelectorAll(".stats-option");
    const statsContent = document.getElementById("statsContent");

    // Function to load stats based on the selected option
    const loadStats = (statType) => {
        let endpoint = '';
        if (statType === 'campaigns') {
            endpoint = '/stats/campaigns';
        } else if (statType === 'influencers') {
            endpoint = '/stats/influencers';
        } else if (statType === 'requests') {
            endpoint = '/stats/requests';
        }
    
        statsContent.innerHTML = '';
        fetch(endpoint)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (statType === 'campaigns') {
                    renderCampaignsChart(data);
                } else if (statType === 'influencers') {
                    renderInfluencersChart(data);
                } else if (statType === 'requests') {
                    renderRequestsChart(data);
                }
            })
            .catch(error => console.error('Error loading stats:', error));
    };
    
    
    const renderCampaignsChart = (data) => {
        const ctx = document.createElement('canvas');
        statsContent.appendChild(ctx);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Campaign Budgets',
                    data: data.budgets,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    };
    
    const renderInfluencersChart = (data) => {
        const ctx = document.createElement('canvas');
        statsContent.appendChild(ctx);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Influencer Reach',
                    data: data.reach,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    };
    
    const renderRequestsChart = (data) => {
        const ctx = document.createElement('canvas');
        statsContent.appendChild(ctx);
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.statuses,
                datasets: [{
                    label: 'Ad Request Statuses',
                    data: data.counts,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    };
    
    
    // Event listeners for stats options
    statsOptions.forEach(option => {
        option.addEventListener("click", (e) => {
            e.preventDefault();
            const statType = option.getAttribute("data-stat");
            loadStats(statType);
        });
    });    
});
