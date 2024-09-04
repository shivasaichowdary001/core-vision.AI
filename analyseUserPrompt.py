import json

def handle_combined_request(prompt):
    response = model.generate_content(prompt)

    # Debug: Log the raw response from the model
    raw_response = response.candidates[0].content.parts[0].text.strip()
    print("Raw response from model:", raw_response)

    try:
        # Parse the response to JSON
        response_json = json.loads(raw_response)
        print("Parsed JSON response:", response_json)

        # Ensure response_json is a dictionary
        if not isinstance(response_json, dict):
            raise ValueError("Expected JSON object, got a different format")

        # Extract intent
        intent = response_json.get('intent', None)

        # Handle details based on its type
        details = response_json.get('details', {})
        if isinstance(details, str):
            report_type = details  # If details is a string, use it as report_type
        else:
            report_type = details.get('report_type', None)
            # Handle other fields in details if necessary

        # Extract parent object details
        parent = response_json.get('parent', {})
        parent_object_name = parent.get('object', None)
        parent_fields = parent.get('fields', [])

        # Extract related objects details
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

        # Formatted JSON for response
        formatted_json = {
            "intent": intent,
            "reportType": report_type,
            "parentObject": {
                "objectName": parent_object_name,
                "fields": parent_fields
            },
            "relatedObjects": processed_related_objects
        }
        
        # Debug: Log the formatted JSON
        print("Formatted JSON response:", json.dumps(formatted_json, indent=2))

        return formatted_json

    except json.JSONDecodeError:
        print("Error decoding JSON from response:", raw_response)
        return {
            "intent": None,
            "reportType": None,
            "parentObject": {
                "objectName": None,
                "fields": []
            },
            "relatedObjects": []
        }
    except Exception as e:
        print("Unhandled exception:", str(e))
        return {
            "intent": None,
            "reportType": None,
            "parentObject": {
                "objectName": None,
                "fields": []
            },
            "relatedObjects": []
        }
