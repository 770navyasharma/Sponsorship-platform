$(document).ready(function() {
    // Load Active Campaigns and New Requests on page load
    loadActiveCampaigns();
    loadNewRequests();

    function loadActiveCampaigns() {
        $.ajax({
            url: "/load_active_campaigns",
            type: "GET",
            success: function(data) {
                $('#active-campaigns-container').empty();
                data.campaigns.forEach(campaign => {
                    const campaignHTML = `
                        <div class="campaign-bar">
                            <h5>${campaign.name}</h5>
                            <button onclick="viewDetails(${campaign.id})">View</button>
                        </div>
                    `;
                    $('#active-campaigns-container').append(campaignHTML);
                });
            }
        });
    }

    function loadNewRequests() {
        $.ajax({
            url: "/load_new_requests",
            type: "GET",
            success: function(data) {
                $('#new-requests-container').empty();
                data.requests.forEach(request => {
                    const requestHTML = `
                        <div class="campaign-bar">
                            <h5>${request.campaign_name}</h5>
                            <button onclick="viewDetails(${request.campaign_id})">View</button>
                        </div>
                    `;
                    $('#new-requests-container').append(requestHTML);
                });
            }
        });
    }   

    window.viewDetails = function(campaignId) {
        $.ajax({
            url: `/campaign_details/${campaignId}`,
            type: "GET",
            success: function(data) {
                $('.modal-body').html(`
                    <p><strong>Name:</strong> ${data.name}</p>
                    <p><strong>Description:</strong> ${data.description}</p>
                    <p><strong>Budget:</strong> ${data.budget}</p>
                    <p><strong>Goals:</strong> ${data.goals}</p>
                    <p><strong>Sponsor:</strong> ${data.sponsor_name}</p>
                `);
                $('#detailsModal').modal('show');
            }
        });
    };
});

$(document).ready(function() {
    // Handle View button clicks
    $(document).on('click', '.view-btn', function() {
        var campaignId = $(this).data('campaign-id');
        viewCampaignDetails(campaignId);
    });

    // Handle Accept button clicks
    $(document).on('click', '.accept-btn', function() {
        var campaignId = $(this).data('campaign-id');
        updateRequestStatus(campaignId, 'Accepted');
    });

    // Handle Reject button clicks
    $(document).on('click', '.reject-btn', function() {
        var campaignId = $(this).data('campaign-id');
        updateRequestStatus(campaignId, 'Rejected');
    });
});

function updateRequestStatus(campaignId, status) {
    $.ajax({
        url: '/update_request_status',
        type: 'POST',
        data: JSON.stringify({ campaign_id: campaignId, status: status }),
        contentType: 'application/json',
        success: function(response) {
            alert(response.message);
            // Optionally, remove or update the request item from the UI
            $('#request-' + campaignId).remove();
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            alert('Failed to update the request status. Please try again.');
        }
    });
}


function viewCampaignDetails(campaignId) {
    $.ajax({
        url: '/campaign_details/' + campaignId,
        type: 'GET',
        success: function(response) {
            $('#detailsModal .modal-body').html(
                '<p><strong>Name:</strong> ' + response.name + '</p>' +
                '<p><strong>Description:</strong> ' + response.description + '</p>' +
                '<p><strong>Budget:</strong> ' + response.budget + '</p>' +
                '<p><strong>Goals:</strong> ' + response.goals + '</p>' +
                '<p><strong>Sponsor:</strong> ' + response.sponsor_name + '</p>'
            );
            $('#detailsModal').modal('show');
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
            alert('Failed to fetch campaign details. Please try again.');
        }
    });
}

function loadNewRequests() {
    $.ajax({
        url: "/load_new_requests",
        method: "GET",
        success: function (data) {
            let container = $("#new-requests-container");
            container.empty(); // Clear previous content

            data.requests.forEach(request => {
                let html = `
                    <div class="request-bar">
                        <span>Campaign Name: ${request.campaign_name}</span>
                        <button class="btn btn-primary" onclick="viewCampaignDetails(${request.campaign_id})">View</button>
                        <button class="btn btn-success" onclick="updateRequestStatus(${request.campaign_id}, 'Accepted')">Accept</button>
                        <button class="btn btn-danger" onclick="updateRequestStatus(${request.campaign_id}, 'Rejected')">Reject</button>
                    </div>
                `;
                container.append(html);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error loading new requests:", error);
        }
    });
}

$(document).ready(function () {
    loadNewRequests();
});

$(document).ready(function() {
    let influencerId = null;

    // Fetch influencer ID from server
    $.ajax({
        url: '/get_influencer_id',
        type: 'GET',
        success: function(data) {
            if (data.influencer_id) {
                influencerId = data.influencer_id;
            } else {
                console.error('Influencer ID not found');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error fetching influencer ID:', status, error);
        }
    });

    // Search form submission
    $('#influencer-search-form').on('submit', function(event) {
        event.preventDefault();
        const query = $('#influencer-search-query').val();

        $.ajax({
            url: '/influencer_search_campaigns',
            type: 'GET',
            data: { query: query },
            success: function(data) {
                if (data.campaigns) {
                    $('#influencer-campaign-results').empty();
                    data.campaigns.forEach(function(campaign) {
                        $('#influencer-campaign-results').append(`
                            <div class="influencer-campaign-card">
                                <h5>${campaign.name}</h5>
                                <button class="btn btn-info influencer-view-btn" data-id="${campaign.id}">View</button>
                                <button class="btn btn-success influencer-request-btn" data-id="${campaign.id}">Request</button>
                            </div>
                        `);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error('Error searching campaigns:', status, error);
            }
        });
    });

    // View campaign button click
    $(document).on('click', '.influencer-view-btn', function() {
        const campaignId = $(this).data('id');

        $.ajax({
            url: `/influencer_campaign_details/${campaignId}`,
            type: 'GET',
            success: function(data) {
                if (data.error) {
                    console.error('Error fetching campaign details:', data.error);
                } else {
                    $('#influencer-campaign-description').text(data.description);
                    $('#influencer-campaign-goals').text(data.goals);
                    $('#influencer-campaign-modal').modal('show');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching campaign details:', status, error);
            }
        });
    });

    // Request button click
    $(document).on('click', '.influencer-request-btn', function() {
        const campaignId = $(this).data('id');
        $('#influencer-request-campaign-id').val(campaignId);
        $('#influencer-request-modal').modal('show');
    });

    // Submit request form
    $('#influencer-submit-request').on('click', function() {
        const campaignId = $('#influencer-request-campaign-id').val();
        console.log(campaignId)
        const message = $('#influencer-request-message').val();
        const requirements = $('#influencer-request-requirements').val();
        const payment = $('#influencer-request-payment').val();

        $.ajax({
            url: '/influencer_request_collaboration',
            type: 'POST',
            data: {
                campaign_id: campaignId,
                message: message,
                requirements: requirements,
                payment: payment,
                influencer_id: influencerId
            },
            success: function(data) {
                if (data.success) {
                    alert('Request sent successfully!');
                    $('#influencer-request-modal').modal('hide');
                } else {
                    console.error('Error sending request:', data.error);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error sending request:', status, error);
            }
        });
    });
});

$(document).ready(function() {
    // Function to show the selected section and hide others
    function showSection(sectionId) {
        $('.tab-content').addClass('d-none');  // Hide all sections
        $(sectionId).removeClass('d-none');   // Show the selected section
    }

    // Handle click event on navbar links
    $('.navbar-nav a').on('click', function(e) {
        e.preventDefault();  // Prevent default link behavior
        const targetId = $(this).attr('href');  // Get the href attribute of the clicked link

        if (targetId === '#inf-logout') {
            // Handle logout
            window.location.href = '/inf-logout';  // Redirect to logout route
        } else {
            showSection(targetId);  // Show the selected section
        }
    });

    // Optionally, show the profile section by default on page load
    showSection('#profile-section');
});
