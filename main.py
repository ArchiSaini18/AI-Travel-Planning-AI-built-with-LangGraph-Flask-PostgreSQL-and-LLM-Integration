from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Conversation, Message, Preference, Itinerary
from auth import auth_bp, init_login_manager
from agent import build_travel_agent
from agent.state import create_initial_state
from agent.tools import weather_api, currency_api, llm_api
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "travel-planner-secret-key-2025")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///travel_planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
init_login_manager(app)
app.register_blueprint(auth_bp)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

agent = build_travel_agent()

with app.app_context():
    db.create_all()
    logger.info("Database initialized successfully")


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('app_page'))
    return render_template('landing.html')


@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('app_page'))
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for('app_page'))
    return render_template('signup.html')


@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')


@app.route('/app')
@login_required
def app_page():
    return render_template('app_enhanced.html')


@app.route('/api/conversations', methods=['GET', 'POST'])
@login_required
def conversations():
    if request.method == 'GET':
        convs = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).all()
        return jsonify([c.to_dict() for c in convs]), 200

    data = request.json
    title = data.get('title', 'Travel Plan')
    
    conv = Conversation(user_id=current_user.id, title=title)
    db.session.add(conv)
    db.session.commit()
    
    return jsonify(conv.to_dict()), 201


@app.route('/api/conversations/<int:conv_id>', methods=['GET', 'DELETE'])
@login_required
def get_conversation(conv_id):
    conv = Conversation.query.get_or_404(conv_id)
    
    if conv.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        return jsonify(conv.to_dict(include_messages=True)), 200
    
    if request.method == 'DELETE':
        db.session.delete(conv)
        db.session.commit()
        return jsonify({'message': 'Conversation deleted'}), 200


@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        conv = Conversation.query.get_or_404(conversation_id)
        if conv.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        user_msg = Message(conversation_id=conversation_id, role='user', content=user_message)
        db.session.add(user_msg)
        db.session.commit()
        
        state = create_initial_state()
        state["user_input"] = user_message
        state["session_id"] = str(conversation_id)
        
        # Load conversation history (all previous messages)
        all_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
        conversation_history = [{"role": msg.role, "content": msg.content} for msg in all_messages]
        state["conversation_history"] = conversation_history
        
        # Load previous preferences for follow-ups
        if conv.preferences:
            state["preferences"] = {
                "budget": conv.preferences.budget,
                "duration": conv.preferences.duration,
                "interests": conv.preferences.interests or [],
                "travel_style": conv.preferences.travel_style,
                "companions": conv.preferences.companions,
                "season": conv.preferences.season
            }
        
        # Load previous itinerary for follow-ups
        if conv.itinerary:
            try:
                state["itinerary"] = {
                    "destination": {"name": conv.itinerary.destination, "country": conv.itinerary.country},
                    "duration": conv.itinerary.duration,
                    "days": json.loads(conv.itinerary.days) if conv.itinerary.days else [],
                    "budget": json.loads(conv.itinerary.budget_breakdown) if conv.itinerary.budget_breakdown else {},
                    "weather": json.loads(conv.itinerary.weather) if conv.itinerary.weather else {}
                }
                state["selected_destination"] = state["itinerary"]["destination"]
                # Important: Set requested_destination for follow-ups to ensure it's used instead of re-scoring
                state["requested_destination"] = conv.itinerary.destination
            except:
                pass
        
        # Mark as follow-up if there are previous messages (before the new user message)
        if len(all_messages) > 1:
            state["is_followup"] = True
        
        result = agent.invoke(state)
        
        logger.info(f"Agent result keys: {result.keys()}")
        logger.info(f"Has itinerary: {bool(result.get('itinerary'))}")
        logger.info(f"Has followup_response: {bool(result.get('followup_response'))}")
        logger.info(f"Is followup: {state.get('is_followup')}")
        logger.info(f"followup_response value: {result.get('followup_response')}")
        logger.info(f"current_node: {result.get('current_node')}")
        
        response_text = ""
        
        # For follow-ups, prioritize followup_response
        # Check if handler ran by looking at current_node
        if state.get('is_followup'):
            followup_resp = result.get('followup_response')
            if followup_resp:
                response_text = followup_resp
                logger.info(f"Using follow-up response: {response_text[:100]}...")
            else:
                logger.warning(f"Follow-up was set but no followup_response in result. Generating response directly.")
                # Fallback: Generate follow-up response directly
                try:
                    from agent.tools import llm_api as llm_tool
                    dest = result.get('selected_destination', {})
                    prefs = result.get('preferences', {})
                    conv_hist = result.get('conversation_history', [])
                    
                    context = f"You are a helpful travel assistant.\nCurrent destination: {dest.get('name', 'Unknown')}\nUser question: {user_message}"
                    messages = [
                        {"role": "system", "content": context},
                        {"role": "user", "content": user_message}
                    ]
                    response_text = llm_tool.generate_completion(messages, temperature=0.7, max_tokens=800)
                    logger.info(f"Generated fallback follow-up response")
                except Exception as e:
                    logger.error(f"Error generating fallback response: {e}")
                    response_text = "I'm here to help! What would you like to know about your travel plans?"
        
        # For new requests with itinerary
        elif result.get('itinerary'):
            response_text = f"Great! I've created a {result['itinerary'].get('duration', 'multi')}-day itinerary for {result.get('selected_destination', {}).get('name', 'your destination')}!"
            
            if result.get('selected_destination') and not conv.preferences:
                pref = Preference(
                    conversation_id=conversation_id,
                    budget=result['preferences'].get('budget'),
                    duration=result['preferences'].get('duration'),
                    interests=result['preferences'].get('interests'),
                    travel_style=result['preferences'].get('travel_style')
                )
                db.session.add(pref)
                
                itin = Itinerary(
                    conversation_id=conversation_id,
                    destination=result['selected_destination'].get('name'),
                    country=result['selected_destination'].get('country'),
                    duration=result['itinerary'].get('duration'),
                    days=json.dumps(result['itinerary'].get('days', [])),
                    budget_total=result.get('budget_breakdown', {}).get('total'),
                    budget_breakdown=json.dumps(result.get('budget_breakdown', {})),
                    weather=json.dumps(result.get('weather_data', {}))
                )
                db.session.add(itin)
        
        else:
            response_text = "I've noted your preferences. Let me find the perfect destination for you!"
            logger.info(f"Default response used")
        
        asst_msg = Message(conversation_id=conversation_id, role='assistant', content=response_text)
        db.session.add(asst_msg)
        
        conv.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'response': response_text,
            'destination': result.get('selected_destination'),
            'weather': result.get('weather_data'),
            'budget': result.get('budget_breakdown'),
            'preferences': result.get('preferences')
        }), 200
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
