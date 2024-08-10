from flask import Flask, request, redirect, url_for, flash, session,send_from_directory
from flask import render_template
from flask import current_app as app
from application.models import User,Campaign,AdRequest,Sponsor,Influencer,SponsorAdRequest
from datetime import datetime
from flask import jsonify
from .database import db

UPLOAD_FOLDER = 'static/profile_pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def home():
    # users = User.query.all()
    return render_template('home.html')

@app.route("/admin",methods=['GET','POST'])

def admin():
    if request.method == 'GET':
        return render_template('admin_login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            flash('Login Successful')
            return redirect('/admin_dashboard')
        else:
            flash('Invalid Credentials')
            return redirect(url_for('admin'))
        
@app.route("/admin_dashboard", methods=['GET', 'POST'])
def admin_dashboard():
    current_date = datetime.now().date()

    # Fetch ongoing campaigns
    ongoing_campaigns = Campaign.query.filter(
        Campaign.start_date <= current_date,
        Campaign.end_date >= current_date
    ).all()
    
    all_campaigns = Campaign.query.all()   

    # Fetch flagged users if applicable
    flagged_users = User.query.filter(User.role.in_(['Sponsor', 'Influencer'])).all()
    admin_user = User.query.filter_by(role='admin').first()
    admin_name = admin_user.username if admin_user else 'Admin'
    
    return render_template('admin_dashboard.html', ongoing_campaigns=ongoing_campaigns, flagged_users=flagged_users,all_campaigns=all_campaigns,admin_name=admin_name)

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get('query').strip()
    search_type = request.args.get('type').strip()
    if search_type == 'campaigns':
        results = Campaign.query.filter(
            (Campaign.name.ilike(f'%{query}%')) |
            (Campaign.description.ilike(f'%{query}%')) |
            (Campaign.budget.ilike(f'%{query}%')) |
            (Campaign.visibility.ilike(f'%{query}%')) |
            (Campaign.start_date.ilike(f'%{query}%')) |
            (Campaign.end_date.ilike(f'%{query}%'))
        ).all()
    elif search_type == 'sponsors':
        results = Sponsor.query.join(User).filter(
            (User.username.ilike(f'%{query}%')) |
            (Sponsor.company_name.ilike(f'%{query}%')) |
            (Sponsor.industry.ilike(f'%{query}%')) |
            (Sponsor.budget.ilike(f'%{query}%'))
        ).all()
    elif search_type == 'influencers':
        results = Influencer.query.join(User).filter(
            (User.username.ilike(f'%{query}%')) |
            (Influencer.category.ilike(f'%{query}%')) |
            (Influencer.niche.ilike(f'%{query}%')) |
            (Influencer.reach.ilike(f'%{query}%'))
        ).all()

    return render_template('admin_dashboard_find.html', campaigns=results, search_type=search_type)

@app.route('/stats_data')
def stats_data():
    # Fetch campaign data
    campaigns = Campaign.query.all()
    campaign_labels = [campaign.name for campaign in campaigns]
    campaign_data = [campaign.budget for campaign in campaigns]

    # Fetch user data
    users = User.query.all()
    user_roles = [user.role for user in users]
    role_counts = {role: user_roles.count(role) for role in set(user_roles)}
    user_labels = list(role_counts.keys())
    user_data = list(role_counts.values())

    return jsonify({'campaign_data': {'labels': campaign_labels, 'data': campaign_data}, 
                    'user_data': {'labels': user_labels, 'data': user_data}})

@app.route('/stats/campaign_trends')
def campaign_trends():
    campaigns = Campaign.query.all()
    campaign_trends = {}

    for campaign in campaigns:
        try:
            if campaign.start_date:
                start_date = datetime.strptime(str(campaign.start_date), '%Y-%m-%d')
                month = start_date.strftime('%B')
                if month in campaign_trends:
                    campaign_trends[month] += campaign.budget
                else:
                    campaign_trends[month] = campaign.budget
            else:
                print(f"Campaign {campaign.id} has no start date.")
        except Exception as e:
            print(f"Error processing campaign {campaign.id}: {e}")

    print(campaign_trends)

    trend_labels = list(campaign_trends.keys())
    trend_data = list(campaign_trends.values())

    return jsonify({'labels': trend_labels, 'data': trend_data})

@app.route('/stats/user_distribution')
def user_distribution():
    # Fetch user data
    users = User.query.all()
    user_roles = [user.role for user in users]
    role_counts = {role: user_roles.count(role) for role in set(user_roles)}
    distribution_labels = list(role_counts.keys())
    distribution_data = list(role_counts.values())

    return jsonify({'labels': distribution_labels, 'data': distribution_data})

@app.route('/admin/flag_user/<int:user_id>', methods=['POST'])
def flag_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.flagged = "Flagged"
    db.session.commit()
    return jsonify({'message': 'User flagged successfully'})

@app.route('/admin/unflag_user/<int:user_id>', methods=['POST'])
def unflag_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.flagged = "Active"
    db.session.commit()
    return jsonify({'message': 'User unflagged successfully'})

@app.route('/admin/flag_campaign/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'message': 'Campaign not found'}), 404
    
    campaign.flagged = "Flagged"
    db.session.commit()
    return jsonify({'message': 'Campaign flagged successfully'})

@app.route('/admin/unflag_campaign/<int:campaign_id>', methods=['POST'])
def unflag_camapign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'message': 'Campaign not found'}), 404
    
    campaign.flagged = "Active"
    db.session.commit()
    return jsonify({'message': 'Campaign unflagged successfully'})

@app.route('/admin/remove_user/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # If the user is a sponsor, delete their campaigns first
    if user.role == 'Sponsor' and user.sponsor:
        campaigns = Campaign.query.filter_by(sponsor_id=user.sponsor.id).all()
        for campaign in campaigns:
            db.session.delete(campaign)
        db.session.delete(user.sponsor)

    # If the user is an influencer, delete their ad requests first
    if user.role == 'Influencer' and user.influencer:
        ad_requests = AdRequest.query.filter_by(influencer_id=user.influencer.id).all()
        for ad_request in ad_requests:
            db.session.delete(ad_request)
        db.session.delete(user.influencer)

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User removed successfully'})

@app.route('/admin/remove_campaign/<int:campaign_id>', methods=['POST'])
def remove_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'message': 'Campaign not found'}), 404

    # Remove all related ad requests
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign.id).all()
    for ad_request in ad_requests:
        db.session.delete(ad_request)
        
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({'message': 'Campaign removed successfully'})


@app.route("/user", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        session['sponsor_name'] = username
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            if user.role == 'Sponsor':
                return redirect('/sponsor_dashboard')
            elif user.role == 'Influencer':
                return redirect('/influencer_dashboard')
        else:
            flash('Invalid username or password.')
    
    return render_template('user_login.html')

@app.route("/register_sponsor", methods=["GET", "POST"])
def register_sponsor():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")
        industry = request.form.get("industry")
        budget = request.form.get("budget")

        new_user = User(username=username, email=email, password=password, role='Sponsor')
        db.session.add(new_user)
        db.session.commit()

        sponsor = Sponsor(id=new_user.id, company_name=company_name, industry=industry, budget=budget)
        db.session.add(sponsor)
        db.session.commit()

        return render_template('user_login.html',message='User registered successfully', message_type='success')

    return render_template('register_sponsor.html')

@app.route("/register_influencer", methods=["GET", "POST"])
def register_influencer():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        category = request.form.get("category")
        niche = request.form.get("niche")
        reach = request.form.get("reach")

        new_user = User(username=username, email=email, password=password, role='Influencer')
        db.session.add(new_user)
        db.session.commit()

        influencer = Influencer(id=new_user.id, category=category, niche=niche, reach=reach)
        db.session.add(influencer)
        db.session.commit()

        flash('Influencer registered successfully!')
        return redirect('/user')

    return render_template('register_influencer.html')

@app.route("/sponsor_dashboard", methods=["GET", "POST"])
def sponsor_dashboard():
    if request.method == "GET":
        sponsor_name = session.get('sponsor_name')
        if not sponsor_name:
            return jsonify({"error": "Sponsor not logged in!"}), 401

        sponsor_user = User.query.filter_by(username=sponsor_name, role='Sponsor').first()
        if not sponsor_user:
            return jsonify({"error": "Sponsor not found!"}), 404

        sponsor = sponsor_user.sponsor
        if not sponsor:
            return jsonify({"error": "Sponsor details not found!"}), 404

        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        pending_ad_requests = AdRequest.query.join(Campaign).filter(
            Campaign.sponsor_id == sponsor.id,
            AdRequest.status == 'Pending'
        ).all()
        print(pending_ad_requests)


        ongoing_campaigns = [
            {
                "id": campaign.id,
                "name": campaign.name,
                "budget": campaign.budget,
                "ad_requests": [
                    {
                        "id": ad_request.id,
                        "influencer_name": ad_request.influencer.user.username,
                        "status": ad_request.status
                    }
                    for ad_request in campaign.ad_requests if ad_request.status == 'Accepted'
                ]
            }
            for campaign in campaigns
        ]

        data = {
            "sponsor": {
                "company_name": sponsor.company_name,
                "industry": sponsor.industry,
                "budget": sponsor.budget,
            },
            "ongoing_campaigns": ongoing_campaigns,
            "pending_ad_requests": [
                {
                    "id": ad_request.id,
                    "campaign": {
                        "id": ad_request.campaign.id,
                        "name": ad_request.campaign.name,
                    },
                    "influencer": {
                        "id": ad_request.influencer.id,
                        "username": ad_request.influencer.user.username,
                        "requirements": ad_request.requirements,
                        "payment_amount":ad_request.payment_amount
                    }
                }
                for ad_request in pending_ad_requests
            ],
            "campaigns": [
                {
                    "id": campaign.id,
                    "name": campaign.name,
                    "description": campaign.description,
                    "budget": campaign.budget,
                    "start_date": campaign.start_date,
                    "end_date": campaign.end_date
                }
                for campaign in campaigns
            ]
        }
        
        your_requests = SponsorAdRequest.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id).all()

        
        return render_template(
            'sponsor_dashboard.html',
            sponsor_name=sponsor.company_name,
            sponsor_industry=sponsor.industry,
            sponsor_budget=sponsor.budget,
            ongoing_campaigns=ongoing_campaigns,
            pending_ad_requests=pending_ad_requests,
            campaigns=campaigns,
            data=jsonify(data),
            your_requests=your_requests
        )
            
        
    elif request.method == "POST":
        ad_request_id = request.form.get('ad_request_id')
        action = request.form.get('action')

        ad_request = AdRequest.query.get(ad_request_id)
        if not ad_request:
            flash('Ad request not found!', 'danger')
            return redirect(url_for('sponsor_dashboard'))

        if action == 'accept':
            ad_request.status = 'Accepted'
            db.session.commit()
            flash('Ad request accepted!', 'success')
        elif action == 'reject':
            ad_request.status = 'Rejected'
            db.session.commit()
            flash('Ad request rejected!', 'danger')
        elif action == 'remove' and ad_request.status == 'Rejected':
            db.session.delete(ad_request)
            db.session.commit()
            flash('Ad request removed!', 'info')

        return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/request/<int:request_id>', methods=['GET'])
def request_details(request_id):
    request = SponsorAdRequest.query.get(request_id)
    if request:
        influencer = Influencer.query.get(request.influencer_id)
        campaign = Campaign.query.get(request.campaign_id)
        return jsonify({
            'request_id': request.id,
            'requirements': request.requirements,
            'payment_amount': request.payment_amount,
            'status': request.status,
            'influencer': {
                'name': influencer.user.username,
                'category': influencer.category,
                'niche': influencer.niche,
                'reach': influencer.reach
            },
            'campaign': {
                'name': campaign.name,
                'description': campaign.description,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date
            }
        })
    else:
        return jsonify({'error': 'Request not found'}), 404
    
# Route to get campaign details for the update form
@app.route('/get_campaign/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if campaign:
        campaign_data = {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'budget': campaign.budget,
            'start_date': campaign.start_date,
            'end_date': campaign.end_date
        }
        print(campaign_data)
        return jsonify(campaign_data)
    return jsonify({'error': 'Campaign not found'}), 404

# Route to update campaign details
@app.route('/update_campaign/<int:campaign_id>', methods=['POST'])
def update_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    # Update campaign fields with data from the form
    campaign.name = request.form['name']
    campaign.description = request.form['description']
    campaign.budget = float(request.form['budget'])
    campaign.start_date = request.form['start_date']
    campaign.end_date = request.form['end_date']
    
    db.session.commit()  # Save changes to the database
    return jsonify({'message': 'Campaign updated successfully'}), 200

# Route to delete a campaign
@app.route('/delete_campaign/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    db.session.delete(campaign)
    db.session.commit()  # Save changes to the database
    return jsonify({'message': 'Campaign deleted successfully'}), 200

@app.route('/create_campaign', methods=['POST'])
def create_campaign():
    name = request.form['name']
    description = request.form['description']
    goals = request.form['goals']
    budget = float(request.form['budget'])
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    sponsor_name = session.get('sponsor_name')
    if not sponsor_name:
        return jsonify({"error": "Sponsor not logged in!"}), 401

    sponsor_user = User.query.filter_by(username=sponsor_name, role='Sponsor').first()
    if not sponsor_user:
        return jsonify({"error": "Sponsor not found!"}), 404

    sponsor = sponsor_user.sponsor
    if not sponsor:
        return jsonify({"error": "Sponsor details not found!"}), 404
    # Create a new Campaign instance
    new_campaign = Campaign(
        name=name,
        description=description,
        budget=budget,
        start_date=start_date,
        end_date=end_date,
        visibility='public',  # Default visibility or based on your logic
        goals=goals,
        sponsor_id=sponsor.id,  # Set sponsor_id based on your application logic
        flagged='Active'  # Default flagged value
    )
    
    try:
        # Add and commit to the database
        db.session.add(new_campaign)
        db.session.commit()
        response = {'status': 'success', 'message': 'Campaign created successfully.'}
    except Exception as e:
        db.session.rollback()
        response = {'status': 'error', 'message': str(e)}
    
    return jsonify(response)

@app.route('/search_influencers')
def search_influencers():
    query = request.args.get('query', '')
    influencers = db.session.query(User, Influencer).join(Influencer).filter(
        User.id == Influencer.id,
        (User.username.ilike(f'%{query}%')) | (Influencer.niche.ilike(f'%{query}%'))
    ).all()
    results = [{'id': influencer.id, 'name': user.username, 'niche': influencer.niche, 'category': influencer.category, 'reach': influencer.reach} for user, influencer in influencers]
    return jsonify({'influencers': results})


@app.route('/get_influencer/<int:id>')
def get_influencer(id):
    influencer = db.session.query(User, Influencer).join(Influencer).filter(User.id == id).first()
    if influencer:
        user, influencer = influencer
        result = {
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'niche': influencer.niche,
            'category': influencer.category,
            'reach': influencer.reach
        }
        return jsonify(result)
    else:
        return jsonify({'error': 'Influencer not found'}), 404


@app.route('/create_ad_request', methods=['POST'])
def create_ad_request():
    influencer_id = request.form.get('influencer_id')
    campaign_id = request.form.get('campaign_id')
    requirements = request.form.get('requirements')
    payment_amount = request.form.get('payment_amount')

    # Validate data
    if not influencer_id or not campaign_id or not requirements or not payment_amount:
        return jsonify({'error': 'Missing required fields'}), 400


    try:
        ad_request = SponsorAdRequest(
            influencer_id=influencer_id,
            campaign_id=campaign_id,
            requirements=requirements,
            payment_amount=payment_amount
        )
        db.session.add(ad_request)
        db.session.commit()
        return jsonify({'message': 'Ad request created successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error creating ad request: {e}")
        return jsonify({'error': 'Failed to create ad request'}), 500


@app.route('/get_campaigns')
def get_campaigns():
    sponsor_name = session.get('sponsor_name')
    if not sponsor_name:
        return jsonify({"error": "Sponsor not logged in!"}), 401

    sponsor_user = User.query.filter_by(username=sponsor_name, role='Sponsor').first()
    if not sponsor_user:
        return jsonify({"error": "Sponsor not found!"}), 404

    sponsor = sponsor_user.sponsor
    if not sponsor:
        return jsonify({"error": "Sponsor details not found!"}), 404

    campaigns = db.session.query(Campaign).filter_by(sponsor_id=sponsor.id).all()
    results = [{'id': campaign.id, 'name': campaign.name} for campaign in campaigns]
    return jsonify({'campaigns': results})


@app.route("/get_campaign_details", methods=["POST"])
def get_campaign_details():
    campaign_id = request.form.get('campaign_id')
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found!"}), 404

    ad_requests = [
        {
            "id": ad_request.id,
            "influencer_name": ad_request.influencer.user.username,
            "influencer_id": ad_request.influencer.id
        }
        for ad_request in campaign.ad_requests if ad_request.status == 'Accepted'
    ]

    return jsonify({
        "name": campaign.name,
        "description": campaign.description,
        "start_date": campaign.start_date,
        "end_date": campaign.end_date,
        "budget": campaign.budget,
        "visibility": campaign.visibility,
        "goals": campaign.goals,
        "ad_requests": ad_requests
    })

@app.route("/get_influencer_details", methods=["POST"])
def get_influencer_details():
    ad_request_id = request.form.get('ad_request_id')
    ad_request = AdRequest.query.get(ad_request_id)
    
    if not ad_request:
        return jsonify({"error": "Ad request not found!"}), 404

    influencer = ad_request.influencer
    
    if not influencer:
        return jsonify({"error": "Influencer not found!"}), 404

    # Perform a join to get user details
    result = db.session.query(Influencer, User).join(User, User.id == Influencer.id).filter(Influencer.id == influencer.id).first()

    if not result:
        return jsonify({"error": "Influencer or User details not found!"}), 404
    
    influencer, user = result

    return jsonify({
        "username": user.username,
        "category": influencer.category,
        "niche": influencer.niche,
        "reach": influencer.reach
    })
    
@app.route('/stats/campaigns')
def stats_campaigns():
    try:
        sponsor_name = session.get('sponsor_name')
        if not sponsor_name:
            raise ValueError("Sponsor not logged in!")

        sponsor_user = User.query.filter_by(username=sponsor_name, role='Sponsor').first()
        if not sponsor_user:
            raise ValueError("Sponsor not found!")

        sponsor = sponsor_user.sponsor
        if not sponsor:
            raise ValueError("Sponsor details not found!")

        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        labels = [campaign.name for campaign in campaigns]
        budgets = [campaign.budget for campaign in campaigns]
        
        return jsonify({'labels': labels, 'budgets': budgets})

    except Exception as e:
        app.logger.error(f"Error in /stats/campaigns: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats/influencers')
def stats_influencers():
    try:
        sponsor_name = session.get('sponsor_name')
        if not sponsor_name:
            raise ValueError("Sponsor not logged in!")

        sponsor_user = User.query.filter_by(username=sponsor_name, role='Sponsor').first()
        if not sponsor_user:
            raise ValueError("Sponsor not found!")

        sponsor = sponsor_user.sponsor
        if not sponsor:
            raise ValueError("Sponsor details not found!")

        ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id).all()
        influencer_reach = {}
        for ad_request in ad_requests:
            influencer_name = ad_request.influencer.user.username
            influencer_reach[influencer_name] = influencer_reach.get(influencer_name, 0) + ad_request.influencer.reach

        labels = list(influencer_reach.keys())
        reach = list(influencer_reach.values())

        return jsonify({'labels': labels, 'reach': reach})

    except Exception as e:
        app.logger.error(f"Error in /stats/influencers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats/requests')
def stats_requests():
    try:
        sponsor_name = session.get('sponsor_name')
        if not sponsor_name:
            raise ValueError("Sponsor not logged in!")

        sponsor_user = User.query.filter_by(username=sponsor_name, role='Sponsor').first()
        if not sponsor_user:
            raise ValueError("Sponsor not found!")

        sponsor = sponsor_user.sponsor
        if not sponsor:
            raise ValueError("Sponsor details not found!")

        ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id).all()
        statuses = {
            'Pending': 0,
            'Accepted': 0,
            'Rejected': 0
        }

        for ad_request in ad_requests:
            statuses[ad_request.status] += 1

        return jsonify({'statuses': list(statuses.keys()), 'counts': list(statuses.values())})

    except Exception as e:
        app.logger.error(f"Error in /stats/requests: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/logout")
def logout():
    # Clear session or handle logout logic here
    session.clear()  # Example to clear the session
    return redirect("/")

@app.route("/influencer_dashboard", methods=["GET", "POST"])
def influencer_dashboard():
    if request.method == "GET":
        username = session.get('sponsor_name')
        if not username:
            return redirect(url_for('user_login'))

        user = User.query.filter_by(username=username).first()
        if not user or user.role != 'Influencer':
            return redirect(url_for('user_login'))

        influencer = user.influencer
        if not influencer:
            return jsonify({"error": "Influencer details not found!"}), 404
        influencer_name = session.get('sponsor_name')  # Retrieve influencer_name from session
        if influencer_name:
            user = User.query.filter_by(username=influencer_name).first()
            if user and user.influencer:
                influencer_id = user.influencer.id
        # Fetch active campaigns
        return render_template("influencer_dashboard.html", 
                           name=influencer.user.username, 
                           influencer_id=influencer_id,
                           influencer=influencer,
                           influencer_name=influencer_name)


@app.route("/load_active_campaigns", methods=["GET"])
def load_active_campaigns():

    # Fetch the influencer's active campaigns
    username = session['sponsor_name']
    influencer = Influencer.query.filter_by(id=User.query.filter_by(username=username).first().id).first()
    
    if influencer:
        ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id, status="Accepted").all()
        ad_requestsm = SponsorAdRequest.query.filter_by(influencer_id=influencer.id,status="Accepted").all()
        ad_requests = ad_requests+ad_requestsm
        campaigns = [{"id": ar.campaign.id, "name": ar.campaign.name} for ar in ad_requests]
    else:
        campaigns = []

    return jsonify({"campaigns": campaigns})


@app.route("/load_new_requests", methods=["GET"])
def load_new_requests():
    # Ensure the user is logged in
    username = session['sponsor_name']
    influencer = Influencer.query.filter_by(id=User.query.filter_by(username=username).first().id).first()
    
    if influencer:
        new_requests = SponsorAdRequest.query.filter_by(influencer_id=influencer.id, status="Pending").all()
        requests = [{"campaign_id": nr.campaign.id, "campaign_name": nr.campaign.name} for nr in new_requests]
    else:
        requests = []

    return jsonify({"requests": requests})


@app.route("/campaign_details/<int:campaign_id>", methods=["GET"])
def campaign_details(campaign_id):
    # Fetch detailed campaign information
    campaign = Campaign.query.get(campaign_id)
    
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    
    sponsor = User.query.get(campaign.sponsor_id)
    
    if not sponsor:
        return jsonify({"error": "Sponsor not found"}), 404
    
    details = {
        "name": campaign.name,
        "description": campaign.description,
        "budget": campaign.budget,
        "goals": campaign.goals,
        "sponsor_name": sponsor.username
    }
    
    return jsonify(details)

@app.route("/update_request_status", methods=["POST"])
def update_request_status():
    data = request.get_json()
    print("Received data:", data)  # Debug print
    campaign_id = data.get('campaign_id')
    status = data.get('status')

    # Ensure session user is correct
    username = session.get('sponsor_name')
    user = User.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(id=user.id).first()

    if not influencer:
        return jsonify({"message": "Influencer not found."}), 404

    ad_request = SponsorAdRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer.id, status="Pending").first()

    if not ad_request:
        return jsonify({"message": "Request not found or already processed."}), 404

    ad_request.status = status
    db.session.commit()

    return jsonify({"message": f"Request has been {status.lower()}."})

@app.route('/influencer_search_campaigns', methods=['GET'])
def influencer_search_campaigns():
    query = request.args.get('query', '')
    campaigns = Campaign.query.filter(
        (Campaign.name.ilike(f'%{query}%')) |
        (Campaign.description.ilike(f'%{query}%')) |
        (Campaign.goals.ilike(f'%{query}%'))
    ).all()
    result = [{'id': c.id, 'name': c.name} for c in campaigns]
    return jsonify({'campaigns': result})

@app.route('/influencer_campaign_details/<int:campaign_id>', methods=['GET'])
def influencer_campaign_details(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if campaign:
        return jsonify({
            'description': campaign.description,
            'goals': campaign.goals
        })
    return jsonify({'error': 'Campaign not found'}), 404

@app.route('/influencer_request_collaboration', methods=['POST'])
def influencer_request_collaboration():
    data = request.form
    print(data)
    campaign_id = data.get('campaign_id')
    message = data.get('message')
    requirements = data.get('requirements')
    payment = data.get('payment')
    influencer_id = data.get('influencer_id')
    
    ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        messages=message,
        requirements=requirements,
        payment_amount=payment,
        status='Pending'
    )
    db.session.add(ad_request)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/get_influencer_id')
def get_influencer_id():
    influencer_name = session.get('sponsor_name')  # Retrieve influencer_name from session
    if influencer_name:
        user = User.query.filter_by(username=influencer_name).first()
        if user and user.influencer:
            influencer_id = user.influencer.id
            return jsonify({'influencer_id': influencer_id})
    return jsonify({'error': 'Influencer not found'}), 404
    

@app.route('/inf-logout')
def inf_logout():
    return redirect('/')

