import json
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow all origins by default

# Configure the API key directly
genai.configure(api_key="AIzaSyAUrtj6xSt9rk9KFnYfGLE7ZXyTefV9LyM")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

def handle_combined_request(prompt):
    response = model.generate_content(prompt)

    # Debug: Log the raw response from the model
    raw_response = response.candidates[0].content.parts[0].text.strip()
    print("Raw response from model:", raw_response)

    try:
        # Parse the response to JSON
        response_json = json.loads(raw_response)
        print("Parsed JSON response:", response_json)

        # Extract details
        intent = response_json.get('intent', '')
        report_type = response_json.get('details', {}).get('report_type', None)
        report_name = response_json.get('details', {}).get('report_name', None)
        description = response_json.get('details', {}).get('description', None)
        schedule = response_json.get('details', {}).get('schedule', {})
        sharing_roles = response_json.get('details', {}).get('sharing', [])
        format = response_json.get('details', {}).get('format', None)

        # Parent object details
        parent = response_json.get('parent', {})
        parent_object_name = parent.get('object', None)
        parent_fields = parent.get('fields', [])
        parent_filters = parent.get('filters', {})
        parent_group_by = parent.get('group_by', {})
        parent_columns = parent.get('columns', [])
        parent_bucket_fields = parent.get('bucket_fields', {})
        parent_formulas = parent.get('formulas', [])

        # Related objects details
        related_objects = response_json.get('related_objects', [])
        processed_related_objects = []

        for obj in related_objects:
            obj_name = obj.get('object', None)
            obj_fields = obj.get('fields', [])
            obj_filters = obj.get('filters', {})
            obj_columns = obj.get('columns', [])
            obj_group_by = obj.get('group_by', {})
            processed_related_objects.append({
                "objectName": obj_name,
                "fields": obj_fields,
                "filters": obj_filters,
                "columns": obj_columns,
                "groupBy": obj_group_by
            })

        # Advanced features
        advanced_features = response_json.get('advanced_features', {})
        bucket_fields = advanced_features.get('bucket_fields', [])
        cross_filters = advanced_features.get('cross_filters', [])
        report_formulas = advanced_features.get('report_formulas', [])

        # Formatted JSON for response
        formatted_json = {
            "intent": intent,
            "reportType": report_type,
            "name": report_name,
            "description": description,
            "parentObject": {
                "objectName": parent_object_name,
                "fields": parent_fields,
                "filters": parent_filters,
                "groupBy": parent_group_by,
                "columns": parent_columns,
                "bucketFields": bucket_fields,
                "formulas": parent_formulas
            },
            "relatedObjects": processed_related_objects,
            "reportSettings": {
                "format": format,
                "schedule": {
                    "frequency": schedule.get('frequency', None),
                    "time": schedule.get('time', None)
                },
                "sharing": {
                    "public": False,  # Assuming sharing is not public by default; adjust if necessary
                    "roles": sharing_roles
                }
            },
            "advancedFeatures": {
                "bucketFields": bucket_fields,
                "crossFilters": cross_filters,
                "reportFormulas": report_formulas
            }
        }
        
        # Debug: Log the formatted JSON
        print("Formatted JSON response:", json.dumps(formatted_json, indent=2))

        return formatted_json

    except json.JSONDecodeError:
        return {
            "intent": "",
            "reportType": None,
            "name": None,
            "description": None,
            "parentObject": {
                "objectName": None,
                "fields": [],
                "filters": {},
                "groupBy": {},
                "columns": [],
                "bucketFields": [],
                "formulas": []
            },
            "relatedObjects": [],
            "reportSettings": {
                "format": None,
                "schedule": {
                    "frequency": None,
                    "time": None
                },
                "sharing": {
                    "public": None,
                    "roles": []
                }
            },
            "advancedFeatures": {
                "bucketFields": [],
                "crossFilters": [],
                "reportFormulas": []
            }
        }

@app.route('/generateReport', methods=['POST'])
def generate_report():
    data = request.json
    prompt = data.get('prompt', None)  # Get user-provided prompt if available
    if not prompt:
        return jsonify({"error": "No prompt provided in the request."}), 400
    response_data = handle_combined_request(prompt)
    return jsonify(response_data)
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
