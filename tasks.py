from flask import Blueprint, request, jsonify
from src.models.user import db, Task
from src.routes.auth import verify_token
from datetime import datetime, date

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user can access these tasks
        if user.id != user_id and user.caregiver_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        
        query = Task.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if priority:
            query = query.filter_by(priority=priority)
        
        tasks = query.order_by(Task.due_date, Task.due_time).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if 'task_description' not in data:
            return jsonify({'error': 'task_description is required'}), 400
        
        task = Task(
            user_id=data.get('user_id', user.id),
            task_description=data['task_description'],
            priority=data.get('priority', 'medium'),
            category=data.get('category')
        )
        
        if 'due_date' in data:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        if 'due_time' in data:
            task.due_time = datetime.strptime(data['due_time'], '%H:%M').time()
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user can update this task
        if user.id != task.user_id and user.caregiver_id != task.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'task_description' in data:
            task.task_description = data['task_description']
        if 'due_date' in data:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if 'due_time' in data:
            task.due_time = datetime.strptime(data['due_time'], '%H:%M').time()
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
        if 'category' in data:
            task.category = data['category']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        token = request.headers.get('Authorization')
        user = verify_token(token) if token else None
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user can delete this task
        if user.id != task.user_id and user.caregiver_id != task.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

