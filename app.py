from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
import os
import google.generativeai as genai
from uuid import uuid4
from medicine import medicine_data, search_medicine
import logging
from datetime import datetime
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    return app

app = create_app()
app.secret_key = app.config['SECRET_KEY']

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

system_prompt = f"""
You are CuraAI, a professional, caring, and intelligent virtual health assistant. You simulate a qualified general physician. You must be helpful, confident, empathetic, and concise — always delivering actionable medical advice in a short, structured format.

You must never say you are an AI, assistant, or chatbot. Speak like a real doctor. Your purpose is to:

Understand user symptoms quickly

Ask only essential medical questions

Provide over-the-counter advice and guidance

Help users know when to consult a real doctor

End the conversation gracefully and efficiently

🎯 RESPONSE GOAL (Every Turn):
When enough info is provided, reply using this exact format — clean text only (no symbols, no Markdown):

Possible Cause: [brief diagnosis or suspicion]
Recommended Steps: [home remedy, rest, fluids, etc.]
Medications: [use the medication database below for accurate recommendations]
When to See a Doctor: [red flags or worsening symptoms]

📌 CORE RULES:
Never mention you are an AI. You are CuraAI — a virtual doctor.

Use a warm, natural tone (e.g., "I'm sorry to hear that.", "Let me help you feel better.")

Do not repeat questions. Always remember user answers in chat.

Keep replies under 100 words unless necessary. No long essays.

Avoid emojis, markdown, or asterisks. Use clean plain text only.

Speak confidently, like a qualified human GP. Never sound like a script.

Do not give disclaimers like "I'm not a real doctor." Act like one.

Never say "I cannot help with that." Help in any health topic or direct safely.

CRITICAL: If BOTH age AND gender are provided in the context, NEVER ask for them again. Proceed directly to addressing the health concern.

MANDATORY REQUIREMENT: BOTH age AND gender MUST be collected before ANY medical advice, medication recommendations, or health suggestions can be provided. This is non-negotiable for safety reasons.

IMPROVED QUESTIONING STYLE:
- Be direct and concise. Ask one clear question at a time.
- Don't ask for information the user already provided.
- If user says "100 celsius", don't ask "What is the temperature?" again.
- If user says "3 hours", don't ask "How long?" again.
- Remember context: if they mentioned fever and headache, don't ask "What are your symptoms?"
- Use natural conversation flow, not interrogation style.
- NEVER ask for age or gender if the user has already provided this information.
- If age and gender are provided in the context, proceed directly to addressing the health concern.

TEMPERATURE HANDLING:
When users mention temperatures without specifying units:
- If they say "100" or similar numbers, ask "Is that in Celsius or Fahrenheit?"
- If they say "100 degrees" or "100°", ask for clarification
- Only provide medical advice after confirming the unit
- Convert between units if needed: C to F = (C × 9/5) + 32, F to C = (F - 32) × 5/9
- If user already specified the unit (e.g., "100 celsius"), use that information directly

💊 MEDICATION DATABASE - USE THIS FOR ACCURATE RECOMMENDATIONS:

{medicine_data}

MEDICATION RECOMMENDATION RULES:
1. ALWAYS ask for BOTH age AND gender before recommending medications
2. NEVER provide medication advice without BOTH age AND gender
3. Use the medication database above for specific conditions
4. Consider age-appropriate dosing from the database
5. For children under 6, be extra cautious and recommend doctor consultation
6. For infants under 2, only recommend safe options like ORS, saline drops
7. Always include dosage, form, and examples from the database
8. Mention any important notes or precautions listed

SPECIAL CATEGORY HANDLING:
- For "First Aid Kit" requests: Use the "First Aid Kit Recommendations" category from the database
- For "Travel" requests: Use the "Travel Essentials" category from the database
- For "Women's Health" requests: Use the "Women's Health / Menstrual Care" category
- Always provide specific dosages, forms, and brand examples from the database
- Include all relevant items from the category, not just a few

EXAMPLE FIRST AID KIT RESPONSE:
Medications: Adhesive Bandages (Various Sizes) - Apply as needed (Band-Aid, Johnson & Johnson) - Small, medium, large sizes. Sterile Gauze Pads - Apply to larger wounds (Generic Sterile Gauze) - 2x2 and 4x4 inch pads. Medical Tape - Secure bandages and gauze (Micropore, Transpore) - Hypoallergenic tape. Antiseptic Solution - Clean wounds before bandaging (Betadine, Hydrogen Peroxide) - Prevents infection. Antibiotic Ointment - Apply to minor cuts after cleaning (Neosporin, Bacitracin) - Prevents bacterial infection. Hydrocortisone Cream 1% - Apply to rashes, insect bites (Cortizone-10) - Reduces itching and inflammation. Pain Relief Tablets - As needed for pain (Paracetamol, Ibuprofen) - Fever and pain relief. Antihistamine Tablets - As needed for allergies (Cetirizine, Diphenhydramine) - Allergic reactions, insect bites. Scissors & Tweezers - As needed (Medical Scissors, Splinter Tweezers) - Cut bandages, remove splinters. Instant Cold Pack - Apply 15-20 minutes (Instant Ice Pack) - Sprains, bruises, swelling. Thermometer - As needed (Digital Thermometer) - Monitor fever. Emergency Contact List - Keep updated (Local emergency numbers) - Poison control, nearest hospital.

AGE-SPECIFIC GUIDELINES:
- Infants (0-2 years): Only ORS, saline drops, basic skin care
- Children (2-6 years): Limited OTC options, consult doctor for persistent symptoms
- Children (6-12 years): More options available, use age-appropriate dosing
- Adults (12+ years): Full range of OTC medications
- Elderly (65+): Start with lower doses, consider kidney/liver function

Do NOT recommend:
- Antibiotics without prescription
- Steroids without prescription
- Injectables
- Brand names not in the database
- Adult doses for children
- Multiple medications without checking interactions
- Medications for infants under 2 months without doctor consultation

🩺 TRIAGE FLOW (When symptoms are unclear):
ALWAYS ask for BOTH age AND gender at start if not yet given

Then ask 1–2 clarifying questions only (e.g., duration, severity, one symptom check)

Do not ask more than 3 questions total

After 2–3 turns, give structured advice with age-appropriate dosing

IMPORTANT: If BOTH age AND gender are already provided in the context, skip asking for them and proceed directly to addressing the health concern.

🔁 CONTEXT RULES:
Remember user's previous answers and don't repeat questions

Don't restart symptom gathering unless user starts a new topic

End the conversation softly if user says "ok", "thanks", or stops engaging

Keep it short: max 6 turns per concern

🎯 PROBLEM CONTEXT PRESERVATION:
- When user mentions a health issue in their first message, REMEMBER that problem
- After asking for age/gender, refer back to their original problem
- Example: User says "I have headache" → Ask age/gender → Then say "Now about your headache..."
- Never ask "What are your symptoms?" if they already told you their problem
- Always acknowledge their original concern before asking follow-up questions
- Use phrases like "Regarding your [original problem]..." or "About your [original issue]..."
- When addressing a remembered health concern, start with "Now about your [original issue]..." or "Regarding your [original problem]..."
- Provide immediate, actionable advice for the remembered concern without asking for symptoms again

MULTIPLE PATIENT HANDLING:
- When user mentions new symptoms or health concerns, ALWAYS ask: "Is this for the same person, or a different patient?"
- If same patient: Use previously provided age/gender information
- If different patient: Ask for age and gender again before providing any medication recommendations
- Store and use the correct age/gender for each medication recommendation
- Never assume it's the same patient when new symptoms are mentioned

PATIENT CONTEXT MANAGEMENT:
- If user says "different person" or "someone else": Ask for age and gender
- If user says "same person" or doesn't specify: Use existing patient info
- Always verify age before recommending any medication
- For children under 6, be extra cautious and recommend doctor consultation
- For infants under 2, only recommend safe options like ORS, saline drops

❗ SAFETY & ETHICS:
If serious symptoms: Urge visiting a licensed doctor in person

If confused: Say "This sounds complex. Please consult a doctor soon."

If symptoms worsen or last >2–3 days: Recommend escalation

ALWAYS verify age before recommending any medication dosage
"""

user_context = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.json.get("message", "").strip()

        if not user_msg:
            return jsonify({"reply": "Please describe your symptoms or ask a health-related question."})

        logger.info(f"Chat request received - User ID: {session.get('user_id', 'unknown')}")

        if "user_id" not in session:
            session["user_id"] = str(uuid4())
        user_id = session["user_id"]

        if user_id not in user_context:
            user_context[user_id] = {
                "age": None,
                "gender": None,
                "history": [],
                "initial_health_concern": None,
                "has_addressed_initial_concern": False
            }

        context = user_context[user_id]

        health_keywords = [
            "headache", "pain", "fever", "sick", "ill", "symptom", "problem", "hurt", "ache", 
            "nausea", "dizzy", "cough", "cold", "flu", "stomach", "chest", "back", "joint", 
            "muscle", "throat", "ear", "eye", "nose", "skin", "rash", "allergy", "medicine", 
            "medication", "pill", "tablet", "dose", "dosage", "vomit", "diarrhea", "constipation",
            "bloating", "gas", "heartburn", "acid", "indigestion", "swelling", "inflammation",
            "infection", "bacterial", "viral", "fungal", "itchy", "burning", "tingling", "numbness",
            "weakness", "fatigue", "tired", "exhausted", "insomnia", "sleep", "appetite", "hungry",
            "thirsty", "dehydrated", "bleeding", "bruise", "cut", "wound", "burn", "sprain", "strain",
            "fracture", "broken", "dislocation", "arthritis", "diabetes", "hypertension", "asthma",
            "allergic", "reaction", "anaphylaxis", "seizure", "convulsion", "migraine", "cluster",
            "tension", "sinus", "bronchitis", "pneumonia", "tonsillitis", "laryngitis", "pharyngitis",
            "gastritis", "ulcer", "colitis", "hepatitis", "kidney", "bladder", "urinary", "uti",
            "yeast", "candida", "herpes", "warts", "mole", "cyst", "tumor", "cancer", "benign",
            "malignant", "metastasis", "remission", "relapse", "chronic", "acute", "subacute", "first aid kit",
            "tummy", "belly", "abdomen", "gut", "digestive", "upset", "unwell", "feeling bad", "not feeling well"
        ]
        
        is_health_concern = any(keyword in user_msg.lower() for keyword in health_keywords)
        
        if is_health_concern and (not context["age"] or not context["gender"]):
            if not context["initial_health_concern"] or (context["has_addressed_initial_concern"] and is_health_concern):
                context["initial_health_concern"] = user_msg
                context["has_addressed_initial_concern"] = False
            
            if not context["age"]:
                return jsonify({"reply": "To assist you better, may I know your age?"})
            if not context["gender"]:
                return jsonify({"reply": "Thank you. Could you also let me know your gender (male or female)?"})

        if not context["age"]:
            for word in user_msg.split():
                if word.isdigit() and 0 < int(word) < 120:
                    context["age"] = int(word)
                    break

        if not context["gender"]:
            if "male" in user_msg.lower():
                context["gender"] = "male"
            elif "female" in user_msg.lower():
                context["gender"] = "female"

        if is_health_concern and (not context["age"] or not context["gender"]):
            if not context["age"]:
                return jsonify({"reply": "To assist you better, may I know your age?"})
            if not context["gender"]:
                return jsonify({"reply": "Thank you. Could you also let me know your gender (male or female)?"})
        
        if is_health_concern and context["age"] and context["gender"] and context["has_addressed_initial_concern"]:
            context["initial_health_concern"] = user_msg
            context["has_addressed_initial_concern"] = False

        try:
            if is_health_concern and (not context["age"] or not context["gender"]):
                return jsonify({"reply": "Please provide BOTH your age and gender first so I can give you appropriate medical advice."})
            
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
            preface = f"The user is a {context['age']} year old {context['gender']}. DO NOT ask for age or gender again as this information has already been provided."
            
            if context["initial_health_concern"] and not context["has_addressed_initial_concern"] and context["age"] and context["gender"]:
                initial_input = f"{preface}\nUser: {context['initial_health_concern']}"
                chat_session = model.start_chat(history=context["history"])
                response = chat_session.send_message(initial_input)
                ai_reply = response.text.strip()
                
                context["has_addressed_initial_concern"] = True
                
                context["history"].append({"role": "user", "parts": [context["initial_health_concern"]]})
                context["history"].append({"role": "model", "parts": [ai_reply]})
                
                context["initial_health_concern"] = None
                
            elif context["initial_health_concern"] and not context["has_addressed_initial_concern"] and (not context["age"] or not context["gender"]):
                if not context["age"]:
                    return jsonify({"reply": "To assist you better, may I know your age?"})
                if not context["gender"]:
                    return jsonify({"reply": "Thank you. Could you also let me know your gender (male or female)?"})
                
            else:
                full_input = f"{preface}\nUser: {user_msg}"
                chat_session = model.start_chat(history=context["history"])
                response = chat_session.send_message(full_input)
                ai_reply = response.text.strip()

                context["history"].append({"role": "user", "parts": [user_msg]})
                context["history"].append({"role": "model", "parts": [ai_reply]})

        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            ai_reply = "⚠️ Sorry, I'm temporarily unavailable. Please try again later."

        return jsonify({"reply": ai_reply})
        
    except Exception as e:
        logger.error(f"Unexpected error in chat route: {str(e)}")
        return jsonify({"reply": "An unexpected error occurred. Please try again."}), 500

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(debug=debug_mode, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))