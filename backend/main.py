from flask import request, jsonify
from config import app, db
from models import User

# GET endpoint to retrieve all users from the database.
@app.route("/users", methods=["GET"])
def get_users():
    try:
        # Retrieve all users from the database
        users = User.query.all()
        # Convert each user record to JSON format using the to_json method.
        json_users = [user.to_json() for user in users]
        return jsonify({"users": json_users}), 200
    except Exception as e:
        # Return a 500 error if something unexpected occurs.
        return jsonify({"message": f"Error retrieving users: {str(e)}"}), 500

# POST endpoint to create a new user.
# Expects a JSON payload with firstName, lastName, and email.
@app.route("/create_user", methods=["POST"])
def create_user():
    # Extract required fields from the incoming JSON data.
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    email = request.json.get("email")

    # Validate that all required fields are provided.
    if not first_name or not last_name or not email:
        return (
            jsonify({"message": "You must include a first name, last name and email"}),
            400,
        )

    # Create a new user instance.
    new_user = User(first_name=first_name, last_name=last_name, email=email)
    try:
        # Add the new user to the database session and commit the transaction.
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        # Rollback the session if an error occurs to keep the database consistent.
        db.session.rollback()
        return jsonify({"message": f"Error creating user: {str(e)}"}), 400

    return jsonify({"message": "User created!"}), 201

# PATCH endpoint to update an existing user.
# Expects a JSON payload that can include firstName, lastName, and/or email.
@app.route("/update_user/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    # Find the user by id; return a 404 if not found.
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.json
    # Update fields if provided in the payload, otherwise retain existing values.
    user.first_name = data.get("firstName", user.first_name)
    user.last_name = data.get("lastName", user.last_name)
    user.email = data.get("email", user.email)

    try:
        # Commit the changes to the database.
        db.session.commit()
    except Exception as e:
        # Rollback the session if an error occurs.
        db.session.rollback()
        return jsonify({"message": f"Error updating user: {str(e)}"}), 400

    return jsonify({"message": "User updated."}), 200

# DELETE endpoint to remove an existing user.
@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    # Find the user by id; return a 404 if not found.
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        # Delete the user and commit the transaction.
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        # Rollback the session if an error occurs during deletion.
        db.session.rollback()
        return jsonify({"message": f"Error deleting user: {str(e)}"}), 400

    return jsonify({"message": "User deleted."}), 200

if __name__ == "__main__":
    # Ensure that the database tables are created before starting the app.
    with app.app_context():
        db.create_all()

    app.run(debug=True)
