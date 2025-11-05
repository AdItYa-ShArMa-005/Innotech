from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import re

app = FastAPI(title="Emergency Triage Symptom Analyzer")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class SymptomAnalysisRequest(BaseModel):
    complaint: str
    age: Optional[int] = None
    vitals: Optional[dict] = None
    selected_symptoms: Optional[List[str]] = []

# Response model
class SymptomAnalysisResponse(BaseModel):
    priority: str  # red, yellow, green
    priority_label: str  # CRITICAL, URGENT, NON-URGENT
    confidence: float  # 0.0 to 1.0
    detected_symptoms: List[str]
    reasoning: str
    suggested_symptoms: List[str]

# Critical symptoms database
CRITICAL_KEYWORDS = {
    'chest_pain': ['chest pain', 'heart attack', 'cardiac', 'angina', 'chest pressure', 'crushing pain'],
    'breathing': ['difficulty breathing', 'shortness of breath', 'dyspnea', 'cant breathe', 'suffocating', 'respiratory distress', 'gasping'],
    'bleeding': ['severe bleeding', 'hemorrhage', 'blood loss', 'profuse bleeding', 'uncontrolled bleeding'],
    'unconscious': ['unconscious', 'unresponsive', 'passed out', 'collapsed', 'loss of consciousness', 'coma'],
    'stroke': ['stroke', 'paralysis', 'facial drooping', 'slurred speech', 'weakness one side'],
    'seizure': ['seizure', 'convulsion', 'fitting', 'epileptic'],
    'head_injury': ['head injury', 'head trauma', 'skull fracture', 'brain injury'],
    'severe_pain': ['excruciating', 'worst pain ever', 'unbearable pain', '10/10 pain'],
    'jaundice': ['yellowness', 'dark urine']
}

URGENT_KEYWORDS = {
    'fever': ['fever', 'high temperature', 'pyrexia', 'febrile'],
    'pain': ['severe pain', 'intense pain', 'pain', 'ache', 'hurts badly'],
    'vomiting': ['vomiting', 'throwing up', 'emesis', 'severe nausea'],
    'diarrhea': ['diarrhea', 'loose stools', 'gastroenteritis'],
    'infection': ['infection', 'infected', 'pus', 'abscess'],
    'fracture': ['fracture', 'broken bone', 'fractured'],
    'burn': ['burn', 'scalded', 'thermal injury'],
    'allergic': ['allergic reaction', 'allergy', 'anaphylaxis', 'swelling', 'hives'],
}

NON_URGENT_KEYWORDS = {
    'cold': ['cold', 'runny nose', 'sneezing', 'cough'],
    'minor_pain': ['mild pain', 'slight discomfort', 'minor ache'],
    'checkup': ['checkup', 'routine', 'follow up', 'prescription refill'],
    'rash': ['rash', 'skin irritation', 'itching'],
}

# Medical conditions database
CRITICAL_CONDITIONS = ['cancer', 'tumor', 'malignancy', 'carcinoma', 'leukemia', 'lymphoma']
URGENT_CONDITIONS = ['diabetes complication', 'asthma attack', 'kidney stone', 'appendicitis', 'pneumonia']


def analyze_complaint(complaint: str, age: int = None, vitals: dict = None, selected_symptoms: List[str] = []) -> dict:
    """
    Analyze the chief complaint and determine priority
    """
    complaint_lower = complaint.lower()
    detected_symptoms = []
    detected_keywords = []
    priority_score = 0
    
    # Check for critical symptoms in complaint
    for symptom, keywords in CRITICAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in complaint_lower:
                detected_symptoms.append(symptom)
                detected_keywords.append(keyword)
                priority_score += 10
                break
    
    # Check for urgent symptoms
    for symptom, keywords in URGENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in complaint_lower:
                if symptom not in detected_symptoms:
                    detected_symptoms.append(symptom)
                    detected_keywords.append(keyword)
                priority_score += 5
                break
    
    # Check for critical medical conditions
    for condition in CRITICAL_CONDITIONS:
        if condition in complaint_lower:
            priority_score += 15
            detected_keywords.append(condition)
    
    # Check for urgent medical conditions
    for condition in URGENT_CONDITIONS:
        if condition in complaint_lower:
            priority_score += 7
            detected_keywords.append(condition)
    
    # Check selected symptoms
    if selected_symptoms:
        if any(s in ['chest_pain', 'breathing', 'bleeding', 'unconscious'] for s in selected_symptoms):
            priority_score += 10
        elif any(s in ['fever', 'pain'] for s in selected_symptoms):
            priority_score += 5
    
    # Analyze vitals if provided
    vital_concerns = []
    if vitals:
        if vitals.get('pulse'):
            pulse = vitals['pulse']
            if pulse > 120 or pulse < 50:
                priority_score += 5
                vital_concerns.append(f"abnormal pulse ({pulse} bpm)")
        
        if vitals.get('temperature'):
            temp = vitals['temperature']
            if temp > 103 or temp < 95:
                priority_score += 5
                vital_concerns.append(f"critical temperature ({temp}°F)")
    
    # Age consideration
    if age:
        if age < 2 or age > 70:
            priority_score += 2  # Vulnerable populations
    
    # Determine priority based on score
    if priority_score >= 10:
        priority = 'red'
        priority_label = 'CRITICAL'
        confidence = min(priority_score / 15, 1.0)
    elif priority_score >= 5:
        priority = 'yellow'
        priority_label = 'URGENT'
        confidence = min(priority_score / 10, 1.0)
    else:
        priority = 'green'
        priority_label = 'NON-URGENT'
        confidence = 0.7
    
    # Build reasoning
    reasoning_parts = []
    if detected_keywords:
        reasoning_parts.append(f"Detected concerning terms: {', '.join(detected_keywords[:3])}")
    if vital_concerns:
        reasoning_parts.append(f"Vital signs concern: {', '.join(vital_concerns)}")
    if selected_symptoms:
        reasoning_parts.append(f"Selected symptoms indicate {priority_label.lower()} care")
    if not reasoning_parts:
        reasoning_parts.append("Based on general assessment of complaint")
    
    reasoning = ". ".join(reasoning_parts) + "."
    
    # Suggest symptoms to check
    suggested = []
    if 'chest' in complaint_lower or 'heart' in complaint_lower:
        suggested.extend(['chest_pain', 'breathing'])
    if 'breath' in complaint_lower or 'cough' in complaint_lower:
        suggested.append('breathing')
    if 'blood' in complaint_lower or 'wound' in complaint_lower:
        suggested.append('bleeding')
    if 'fever' in complaint_lower or 'temperature' in complaint_lower:
        suggested.append('fever')
    if 'pain' in complaint_lower or 'hurt' in complaint_lower:
        suggested.append('pain')
    
    # Remove duplicates
    detected_symptoms = list(set(detected_symptoms))
    suggested = [s for s in list(set(suggested)) if s not in detected_symptoms]
    
    return {
        'priority': priority,
        'priority_label': priority_label,
        'confidence': round(confidence, 2),
        'detected_symptoms': detected_symptoms,
        'reasoning': reasoning,
        'suggested_symptoms': suggested[:4]  # Max 4 suggestions
    }


@app.get("/")
def read_root():
    return {
        "message": "Emergency Triage Symptom Analyzer API",
        "version": "1.0",
        "endpoints": {
            "/analyze": "POST - Analyze symptoms and determine priority"
        }
    }


@app.post("/analyze", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyze patient complaint and determine triage priority
    """
    try:
        if not request.complaint or len(request.complaint.strip()) < 3:
            raise HTTPException(status_code=400, detail="Chief complaint is too short")
        
        result = analyze_complaint(
            complaint=request.complaint,
            age=request.age,
            vitals=request.vitals,
            selected_symptoms=request.selected_symptoms
        )
        
        return SymptomAnalysisResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "symptom-analyzer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)