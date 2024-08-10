from .database import db
from sqlalchemy import CheckConstraint
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    flagged = db.Column(db.String, default="Active")

    __table_args__ = (
        CheckConstraint("role IN ('Admin', 'Sponsor', 'Influencer')", name='check_role'),
    )

    sponsor = db.relationship('Sponsor', uselist=False, backref='user')
    influencer = db.relationship('Influencer', uselist=False, backref='user')

class Sponsor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_name = db.Column(db.String)
    industry = db.Column(db.String)
    budget = db.Column(db.Float)

    campaigns = db.relationship('Campaign', backref='sponsor')

class Influencer(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    category = db.Column(db.String)
    niche = db.Column(db.String)
    reach = db.Column(db.Integer)

    ad_requests = db.relationship('AdRequest', backref='influencer')
    def to_dict(self):
        return {
        'id': self.id,
        'name': self.user.username,
        'niche': self.niche,
        'category': self.category,
        'reach': self.reach
    }

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    budget = db.Column(db.Float)
    visibility = db.Column(db.String)
    goals = db.Column(db.String)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'))
    flagged = db.Column(db.String, default="Active")

    __table_args__ = (
        CheckConstraint("visibility IN ('public', 'private')", name='check_visibility'),
    )

    ad_requests = db.relationship('AdRequest', backref='campaign')

class AdRequest(db.Model):
    __tablename__ = 'AdRequest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    messages = db.Column(db.String)
    requirements = db.Column(db.String)
    payment_amount = db.Column(db.Float)
    status = db.Column(db.String,default='Pending')
    __table_args__ = (
        CheckConstraint("status IN ('Pending', 'Accepted', 'Rejected')", name='check_status'),
        CheckConstraint("Completed IN ('False', 'True')",name = 'completion_status')
    )

class SponsorAdRequest(db.Model):
    __tablename__ = 'SponsorAdRequest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    requirements = db.Column(db.String, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, default='Pending')  # Pending, Accepted, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    influencer = db.relationship('Influencer', backref='sponsor_ad_requests')
    campaign = db.relationship('Campaign', backref='sponsor_ad_requests')

    __table_args__ = (
        CheckConstraint("status IN ('Pending', 'Accepted', 'Rejected')", name='check_status'),
        CheckConstraint("Completed IN ('False', 'True')",name = 'completion_status')
    )
    
    def __repr__(self):
        return f'<SponsorAdRequest {self.id} - {self.status}>'