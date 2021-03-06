import models
# import pdb # the python debugger
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required # need this for authorization
from playhouse.shortcuts import model_to_dict
# playhouse is from peewee

# first argument is blueprint's name
# second argument is it's import_name
issue = Blueprint('issues', 'issue')
#blueprint is like the router in express, it records operations


#attach restful CRUD routes to issue blueprint

# Index Route (get)
@issue.route('/', methods=["GET"]) # GET is the default method
def get_all_issues():
    # print(vars(request))
    # print(request.cookies)
    ## find the issues and change each one to a dictionary into a new array
    
    print('Current User:',  current_user, "line 23", '\n')
    # Send all issues back to client. There is no valid reason for this not to work
    # so we don't use a try -> except.
    # IMPORTANT -> Use max_depth=0 if we want just the issue created_by id and not the entire
    # created_by object sent back to the client. 
    # Could also use exclude=[models.Issue.created_by] to entirely remove ref to created_by
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
    # all_issues = [model_to_dict(d, max_depth=0) for d in models.Issue.select()]

    # we want the entire object, so we are not going to use max_depth=0
    all_issues = [model_to_dict(issue) for issue in models.Issue.select()]

    print(all_issues, 'line 35', '\n')
    return jsonify(data=all_issues, status={'code': 200, 'message': 'Success'})

    ######################################################################
    # old way of doing it before adding authorization...
    # try:
    #     issues = [model_to_dict(issue) for issue in models.Issue.select()]
    #     print(issues)
    #     return jsonify(data=issues, status={"code": 200, "message": "Success"})
    # except models.DoesNotExist:
    #     return jsonify(data={}, status={"code": 401, "message": "Error getting the resources"})
    ######################################################################


# Create/New Route (post)
# @login_required <- look this up to save writing some code https://flask-login.readthedocs.io/en/latest/#flask_login.login_required
@issue.route('/', methods=["POST"])
def create_issues():
    ## see request payload anagolous to req.body in express
    payload = request.get_json() # flask gives us a request object (similar to req.body)
    print(type(payload), 'payload')
    
    #######################################################################
    #adding authorization step here...
    if not current_user.is_authenticated: # Check if user is authenticated and allowed to create a new issue
        print(current_user)
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to create an issue'})

    payload['created_by'] = current_user.id # Set the 'created_by' of the issue to the current user
    print(payload['created_by'], 'created by current user id')
    #######################################################################
    print(payload, 'line 63')
    issue = models.Issue.create(**payload) ## ** spread operator
    # returns the id, see print(issue)

    ## see the object
    # print(issue)
    # print(issue.__dict__)
    ## Look at all the methods
    # print(dir(issue))
    # Change the model to a dict
    print(model_to_dict(issue), 'model to dict')
    issue_dict = model_to_dict(issue)
    return jsonify(data=issue_dict, status={"code": 201, "message": "Success"})


# Show/Read Route (get)
@issue.route('/<id>/', methods=["GET"]) # <id> is the params (:id in express)
def get_one_issue(id):
    print(id)
    # Get the issue we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'issue' resource wasn't found.
    one_issue = models.Issue.get(id=id)

    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to edit an issue'})

    if one_issue.created_by.id is not current_user.id: 
        # Checks if created_by (User) of issue has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only update an issue you created'})

    return jsonify(
                data=model_to_dict(one_issue), 
                status={'code': 200, 'message': 'You can update an issue you created'}
            )
    #######################################################################
    # old way of doing it before adding authorization...
    # print(id, 'reserved word?')
    # issue = models.Issue.get_by_id(id)
    # print(issue.__dict__)
    # return jsonify(data=model_to_dict(issue), status={"code": 200, "message": "Success"})
    #######################################################################


# Update/Edit Route (put)
@issue.route('/<id>/', methods=["PUT"])
def update_issue(id):
    # print('hi')
    # pdb.set_trace()
    payload = request.get_json()
    # print(payload)

    # Get the issue we are trying to update. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'issue' resource wasn't found.
    issue_to_update = models.Issue.get(id=id)
    print(issue_to_update, "line122")
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to edit an issue'})

    if issue_to_update.created_by.id is not current_user.id: 
        # Checks if create_by (User) of issue has the same id as the logged in User.
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only update an issue you created'})

    # Given our form, we only want to update the subject of our issue
    # issue_to_update.update(
    #     subject=payload['subject']
    # ).execute()

    #new code
    issue_to_update.subject = payload['subject']
    issue_to_update.save()

    # Get a dictionary of the updated issue to send back to the client.
    # Use max_depth=0 because we want just the created_by id and not the entire
    # created_by object sent back to the client. 
    # update_issue_dict = model_to_dict(issue_to_update, max_depth=0)

    # we want the entire object, so we are not going to use max_depth=0
    update_issue_dict = model_to_dict(issue_to_update)
    return jsonify(status={'code': 200, 'msg': 'success'}, data=update_issue_dict)    

    #######################################################################
    # old way of doing it before adding authorization...
    # payload = request.get_json()
    # # print(payload)

    # query = models.Issue.update(**payload).where(models.Issue.id == id)
    # query.execute()

    # # print(type(query))
    # # find the issue again
    # issue = models.Issue.get_by_id(id)

    # issue_dict = model_to_dict(issue)
    # # updated_issue = model_to_dict(query)
    # # print(updated_issue, type(update_issue))
    # return jsonify(data=issue_dict, status={"code": 200, "message": "resource updated successfully"})
    #######################################################################


# Delete Route (delete)
@issue.route('/<id>/', methods=["DELETE"])
def delete_issue(id):
    # Get the issue we are trying to delete. Could put in try -> except because
    # if we try to get an id that doesn't exist a 500 error will occur. Would 
    # send back a 404 error because the 'issue' resource wasn't found.
    issue_to_delete = models.Issue.get(id=id)
    print(issue_to_delete, 'line 161');
    print(current_user, 'line 162');
    if not current_user.is_authenticated: # Checks if user is logged in
        return jsonify(data={}, status={'code': 401, 'message': 'You must be logged in to create an issue'})
    if issue_to_delete.created_by.id is not current_user.id: 
        # Checks if created_by (User) of issue has the same id as the logged in User
        # If the ids don't match send 401 - unauthorized back to user
        return jsonify(data={}, status={'code': 401, 'message': 'You can only delete the issue you created'})
    
    # Delete the issue and send success response back to user
    query = models.Issue.delete().where(models.Issue.id==id)
    query.execute()
    print(issue_to_delete, 'line 174');
    return jsonify(data='resource successfully deleted', status={"code": 200, "message": "resource deleted successfully"})

    #######################################################################
    # old way of doing it before adding authorization...
    # query = models.Issue.delete().where(models.Issue.id==id)
    # query.execute()
    # return jsonify(data='resource successfully deleted', status={"code": 200, "message": "resource deleted successfully"})
    #######################################################################


