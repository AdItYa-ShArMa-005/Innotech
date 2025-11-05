// API Service for FastAPI Integration
// Add this as a new file: api-service.js

// Change this to your FastAPI server URL
// If running locally: 'http://localhost:8000'
// If deployed: 'https://your-api-domain.com'
const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Analyze symptoms using FastAPI backend
 * @param {string} complaint - Chief complaint text
 * @param {number} age - Patient age
 * @param {object} vitals - Vital signs object
 * @param {array} selectedSymptoms - Array of selected symptoms
 * @returns {Promise} Analysis result with priority
 */
export async function analyzeSymptoms(complaint, age, vitals, selectedSymptoms = []) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                complaint: complaint,
                age: age,
                vitals: vitals,
                selected_symptoms: selectedSymptoms
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const result = await response.json();
        return {
            success: true,
            data: result
        };
    } catch (error) {
        console.error('Error analyzing symptoms:', error);
        return {
            success: false,
            message: error.message
        };
    }
}

/**
 * Check API health
 */
export async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            return { healthy: false };
        }
        const data = await response.json();
        return { healthy: data.status === 'healthy' };
    } catch (error) {
        console.error('API health check failed:', error);
        return { healthy: false };
    }
}
