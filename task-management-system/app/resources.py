from datetime import datetime
import traceback
from flask import Response, abort, json, jsonify, request
from flask_restful import Resource
from pydantic import ValidationError
from app.models import db, Task
from app.schemas import TaskSchema, TaskCreateSchema

class Tasks(Resource):
    def get(self):
        try:
            tasks = Task.query.all()
            if not tasks:
                return jsonify({"message": "No tasks found, add them"}), 200

            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
                for task in tasks
            ]
            response_json = json.dumps(tasks_data)
            return Response(response_json, status=200, mimetype='application/json')

        except Exception as e:
            print("Error occurred during GET request:")
            traceback.print_exc()
            return jsonify({"error": "An internal error occurred during GET"}), 500

    def post(self):
        print(f"Received HTTP method: {request.method}")
        try:
            tasks = request.get_json()
            print("Received tasks data:", tasks)

            if not isinstance(tasks, list):
                return jsonify({"error": "Expected a list of tasks"}), 400

            validated_tasks = []
            for task_data in tasks:
                if not isinstance(task_data, dict):
                    return jsonify({"error": "Each task must be a dictionary"}), 400

                task_data.pop('id', None)

                if 'due_date' in task_data and isinstance(task_data['due_date'], str):
                    task_data['due_date'] = datetime.strptime(task_data['due_date'], '%Y-%m-%d').date()

                validated_tasks.append(TaskCreateSchema.model_validate(task_data))

            print(f"Validated tasks: {validated_tasks}")

        except ValidationError as e:
            print("Validation error:")
            traceback.print_exc()
            return jsonify({"errors": e.errors()}), 400

        except Exception as e:
            print("An error occurred while processing the POST request:")
            traceback.print_exc()
            return jsonify({"error": "An internal error occurred during POST"}), 500

        task_dicts = [
            {
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date
            }
            for task in validated_tasks
        ]

        try:
            db.session.bulk_insert_mappings(Task, task_dicts)
            db.session.commit()

        except Exception as e:
            print("Database insertion error:")
            traceback.print_exc()
            return jsonify({"error": "Failed to insert tasks into the database"}), 500

        try:
            created_tasks = Task.query.order_by(Task.id.desc()).limit(len(task_dicts)).all()

            created_tasks_serialized = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
                for task in created_tasks
            ]

            response_json = json.dumps(created_tasks_serialized)
            return Response(response_json, status=201, mimetype='application/json')

        except Exception as e:
            print("Error occurred while serializing tasks:")
            traceback.print_exc()
            return jsonify({"error": "Failed to serialize tasks"}), 500


class TaskUpdation(Resource):
    def get(self, task_id):
        try:
            task = Task.query.get(task_id)
            if not task:
                abort(404)

            task_serialized = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
            response_json = json.dumps(task_serialized)
            return Response(response_json, status=200, mimetype='application/json')

        except Exception as e:
            print(f"Error occurred while fetching task {task_id}:")
            traceback.print_exc()
            return jsonify({"error": f"Failed to retrieve task {task_id}"}), 500

    def put(self, task_id):
        try:
            task = Task.query.get(task_id)
            if not task:
                abort(404)

            request_payload = request.get_json()
            updated_fields = ['title', 'description', 'status', 'due_date']
            for field in updated_fields:
                if field in request_payload:
                    if field == 'due_date':
                        request_payload[field] = datetime.strptime(request_payload[field], '%Y-%m-%d').date()
                    setattr(task, field, request_payload[field])

            db.session.commit()

            task_serialized = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
            response_json = json.dumps(task_serialized)
            return Response(response_json, status=200, mimetype='application/json')

        except Exception as e:
            print(f"Error occurred while updating task {task_id}:")
            traceback.print_exc()
            return jsonify({"error": f"Failed to update task {task_id}"}), 500

    def delete(self, task_id):
        try:
            task = Task.query.get(task_id)
            if not task:
                abort(404)

            db.session.delete(task)
            db.session.commit()
            return jsonify({"message": f"Task {task_id} deleted successfully"}), 200

        except Exception as e:
            print(f"Error occurred while deleting task {task_id}:")
            traceback.print_exc()
            return jsonify({"error": f"Failed to delete task {task_id}"}), 500


class FilterByStatus(Resource):
    def get(self):
        try:
            status = request.args.get('status')
            if not status:
                return jsonify({"error": "Missing 'status' query parameter"}), 400

            tasks = Task.query.filter_by(status=status).all()

            tasks_serialized = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
                for task in tasks
            ]

            response_json = json.dumps(tasks_serialized)
            return Response(response_json, status=200, mimetype='application/json')

        except Exception as e:
            print("Error occurred while filtering tasks by status:")
            traceback.print_exc()
            return jsonify({"error": "Failed to filter tasks by status"}), 500
