from flask import Blueprint, render_template, url_for, redirect, session,  \
                  request, g, flash, abort
from datetime import datetime
from app import app, db
from app.causes.models import Cause, Action
from app.users.models import User

mod = Blueprint('causes', __name__)

@mod.route('/cause/<title>')
@mod.route('/cause/<title>/story')
def story(title):
    #: Campaign being viewed
    #campaign = Campaign.query.filter_by(title=title).first()

    #: These variables are for testing and demo use only
    # TODO: modify cause model to include all of this
    action_1 = {
        'id':1,
        'cause_id':1,
        'title':'Call in',
        'heading':'Call the boss',
        'description':'Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio.',
        'supporters':16,
        'expiration':datetime(2016, 2, 18, 17, 0, 56, 613943),
    }
    action_2 = {
        'id':2,
        'cause_id':1,
        'title':'Show up',
        'heading':'Show up at the factory',
        'description':'Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio.',
        'supporters':64,
        'expiration':datetime(2016, 2, 18, 17, 0, 56, 613943),
    } 
    cause = {
        'id':1,
        'actions':[action_1,action_2],
        'title':'Demo Cause',
        'boss':'Boss',
        'created_on':datetime(2016, 2, 18, 17, 0, 56, 613943),
        'location':'New York City',
        'creators':[User(nickname='pmamontov', full_name='Pavel Mamontov', initials='PM'),
                    User(nickname='dgross', full_name='Daniel Gross', initials='DG'),
                    User(nickname='ctonder', full_name='Carl Tonder', initials='CT')],
        'supporters':[User(nickname='mjones', full_name='Mother Jones', initials='MJ'),
                      User(nickname='jhill', full_name='Joe Hill', initials='JH'),
                      User(nickname='nchomsky', full_name='Noam Chomsky', initials='NC'),
                      User(nickname='tuser', full_name='Test User', initials='TU'),
                      User(nickname='auser', full_name='Anonymous User', initials='AU')],
        'video':None,
        'image':'images/demo-vid.jpg',
        'story_heading':'Heading',
        'story_content':'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.',
    }
    # Render campaign template
    return render_template('causes/index.html', cause=cause)

@mod.route('/cause/<title>/demands')
def demands(title):
    #: Campaign being viewed
    #campaign = Campaign.query.filter_by(title=title).first()

    #: These variables are for testing and demo use only
    # TODO: modify cause model to include all of this
    demand_1 = {
        'id':1,
        'cause_id':1,
        'title':'Demand 1',
        'resolved':False,
        'description':'Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. In euismod ultrices facilisis. Vestibulum porta sapien adipiscing augue congue id pretium lectus molestie. Proin quis dictum nisl. Morbi id quam sapien, sed vestibulum sem.'
    }
    demand_2 = {
        'id':2,
        'cause_id':1,
        'title':'Demand 2',
        'resolved':True,
        'description':'Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. In euismod ultrices facilisis. Vestibulum porta sapien adipiscing augue congue id pretium lectus molestie. Proin quis dictum nisl. Morbi id quam sapien, sed vestibulum sem.'
    }
    action_1 = {
        'id':1,
        'cause_id':1,
        'title':'Call in',
        'heading':'Call the boss',
        'description':'Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio.',
        'supporters':16,
        'expiration':datetime(2016, 2, 18, 17, 0, 56, 613943),
    }
    action_2 = {
        'id':2,
        'cause_id':1,
        'title':'Show up',
        'heading':'Show up at the factory',
        'description':'Vivamus fermentum semper porta. Nunc diam velit, adipiscing ut tristique vitae, sagittis vel odio.',
        'supporters':64,
        'expiration':datetime(2016, 2, 18, 17, 0, 56, 613943),
    } 
    cause = {
        'id':1,
        'actions':[action_1,action_2],
        'demands':[demand_1,demand_2],
        'title':'Demo Cause',
        'boss':'Boss',
        'created_on':datetime(2016, 2, 18, 17, 0, 56, 613943),
        'location':'New York City',
        'creators':[User(nickname='pmamontov', full_name='Pavel Mamontov', initials='PM'),
                    User(nickname='dgross', full_name='Daniel Gross', initials='DG'),
                    User(nickname='ctonder', full_name='Carl Tonder', initials='CT')],
        'supporters':[User(nickname='mjones', full_name='Mother Jones', initials='MJ'),
                      User(nickname='jhill', full_name='Joe Hill', initials='JH'),
                      User(nickname='nchomsky', full_name='Noam Chomsky', initials='NC'),
                      User(nickname='tuser', full_name='Test User', initials='TU'),
                      User(nickname='auser', full_name='Anonymous User', initials='AU')],
        'video':None,
        'image':'images/demo-vid.jpg',
        'story_heading':'Heading',
        'story_content':'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.',
    }

    # Render campaign demands template
    return render_template('causes/demands.html', cause=cause)
