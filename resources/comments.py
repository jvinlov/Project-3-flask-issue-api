import models
# import pdb # the python debugger
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required # need this for authorization
from playhouse.shortcuts import model_to_dict
# playhouse is from peewee

# first argument is blueprint's name
# second argument is it's import_name
comment = Blueprint('comments', 'comment')
#blueprint is like the router in express, it records operations


#attach restful CRUD routes to comment blueprint

# Index Route (get)
@comment.route('/', methods=["GET"]) # GET is the default method
def get_all_comments():
    # print(vars(request))
    # print(request.cookies)
    ## find the comments and change each one to a dictionary into a new array
    
    print('Current User:',  current_user, 'line 23', '\n')
    # Send all comments back to client. There is no valid reason for this not to work
    # so we don't use a try -> except.
    # IMPORTANT -> Use max_depth=0 if we want just the comment created_by id and not the entire
    # created_by object sent back to the client. 
    # Could also use exclude=[models.Comment.created_by] to entirely remove ref to created_by
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
    # all_comments = [model_to_dict(d, max_depth=0) for d in models.Comment.select()]

    # we want the entire object, so we are not going to use max_depth=0
    all_comments = [model_to_dict(comment) for comment in models.Comment.select()]

    print(all_comments, 'line 35', '\n')
    return jsonify(data=all_comments, status={'code': 200, 'message': 'Success'})


# Create/New Route (post)
@login_required # <- look this up to save writing some code https://flask-login.readthedocs.io/en/latest/#flask_login.login_required
@comment.route('/', methods=["POST"])
def create_comments():
    ## see request payload anagolous to req.body in express
    payload = request.get_json() # flask gives us a request object (similar to req.body)
    print(type(payload), 'payload')
    
    #######################################################################
    #adding authorization step here...
    # if not current_user.is_authenticated: # Check if user is authenticated and allowed to create a new comment
    #     print(current_user)
    #     return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to create a comment'})
    #######################################################################
    payload['created_by'] = current_user.id # Set the 'created_by' of the comment to the current user
    print(payload['created_by'], 'created by current user id')

    print(payload, 'line 56')
    comment = models.Comment.create(**payload) ## ** spread operator
    # returns the id, see print(comment)

    ## see the object
    # print(comment)
    # print(comment.__dict__)
    ## Look at all the methods
    # print(dir(comment))
    # Change the model to a dict
    print(model_to_dict(comment), 'model to dict')
    comment_dict = model_to_dict(comment)
    return jsonify(data=comment_dict, status={"code": 201, "message": "Success"})


# Show/Read Route (get) <--not using this, yet
@comment.route('/<id>/', methods=["GET"]) # <id> is the params (:id in express)
def get_one_comment(id):
    print(id)
    # Get the comment we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'comment' resource wasn't found.
    one_comment = models.Comment.get(id=id)

    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to edit a comment'})

    if one_comment.created_by.id is not current_user.id: 
        # Checks if created_by (User) of comment has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only update a comment you created'})

    return jsonify(
                data=model_to_dict(one_comment), 
                status={'code': 200, 'message': 'You can update a comment you created'}
            )


# Update/Edit Route (put) <--not using this, yet
@comment.route('/<id>/', methods=["PUT"])
def update_comment(id):
    # print('hi')
    # pdb.set_trace()
    payload = request.get_json()
    # print(payload)

    # Get the comment we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'comment' resource wasn't found.
    comment_to_update = models.Comment.get(id=id)
    print(comment_to_update, 'line106')
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to edit a comment'})

    if comment_to_update.created_by.id is not current_user.id: 
        # Checks if create_by (User) of comment has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only update a comment you created'})

    # Given our form, we only want to update the subject of our comment
    # comment_to_update.update(
    #     subject=payload['subject']
    # ).execute()

    #new code
    comment_to_update.subject = payload['subject']
    comment_to_update.save()

    # Get a dictionary of the updated comment to send back to the client.
    # Use max_depth=0 because we want just the created_by id and not the entire
    # created_by object sent back to the client. 
    # update_comment_dict = model_to_dict(comment_to_update, max_depth=0)

    # we want the entire object, so we are not going to use max_depth=0
    update_comment_dict = model_to_dict(comment_to_update)
    return jsonify(status={'code': 200, 'msg': 'success'}, data=update_comment_dict)    


# Delete Route (delete) <--not using this, yet
@comment.route('/<id>/', methods=["DELETE"])
def delete_comment(id):
    # Get the comment we are trying to delete. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'comment' resource wasn't found.
    comment_to_delete = models.Comment.get(id=id)
    print(comment_to_delete, 'line 141');
    print(current_user, 'line 142');
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to delete a comment'})
    if comment_to_delete.created_by.id is not current_user.id: 
        # Checks if created_by (User) of comment has the same id as the logged in User
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only delete the comment you created'})
    
    # Delete the comment and send success response back to user
    query = models.Comment.delete().where(models.Comment.id==id)
    query.execute()
    print(comment_to_delete, 'line 153');
    return jsonify(data='resource successfully deleted', status={"code": 200, "message": "resource deleted successfully"})
