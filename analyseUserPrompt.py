from flask import Flask, request, jsonify
import google.generativeai as genai
import json

from flask_cors import CORS

app = Flask(__name__)  # Corrected the variable name
CORS(app)  # Allow all origins by default

# Configure the API key directly
genai.configure(api_key="AIzaSyAUrtj6xSt9rk9KFnYfGLE7ZXyTefV9LyM")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

# Function to handle the combined API call
def handle_combined_request(prompt):
    response = model.generate_content(prompt)
    
    try:
        # Load and process the JSON response
        response_json = json.loads(response.candidates[0].content.parts[0].text.strip())
        if isinstance(response_json, dict):
            intent = response_json.get("intent", "")
            details = response_json.get("details", {})
            
            # Extract parent and related objects with fields
            parent = response_json.get("parent", {"object": "", "fields": []})
            related_objects = response_json.get("related_objects", [])
            
            parent_name = parent.get("object", "")
            parent_fields = parent.get("fields", [])
            
            related_objects_with_fields = []
            for obj in related_objects:
                obj_name = obj.get("object", "")
                obj_fields = obj.get("fields", [])
                related_objects_with_fields.append({"object": obj_name, "fields": obj_fields})

            return {
                "intent": intent,
                "details": details,
                "parent": {
                    "object": parent_name,
                    "fields": parent_fields
                },
                "related_objects": related_objects_with_fields
            }
        else:
            return {
                "intent": "",
                "details": {},
                "parent": {
                    "object": "",
                    "fields": []
                },
                "related_objects": []
            }
    except json.JSONDecodeError:
        return {
            "intent": "",
            "details": {},
            "parent": {
                "object": "",
                "fields": []
            },
            "related_objects": []
        }

@app.route('/generateReport', methods=['POST'])
def generate_report():
    data = request.json
    prompt = data.get('prompt', None)  # Get user-provided prompt if available
    if not prompt:
        return jsonify({"error": "No prompt provided in the request."}), 400
    response_data = handle_combined_request(prompt)
    return jsonify(response_data)

if __name__ == '__main__':  # Corrected the variable name
    app.run(debug=True)
