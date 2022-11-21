import logging

import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.authz as authz

#Auth check
#Checks if user is a sysadmin before allowing the creation of a new tag
def _user_has_minumum_role(context):

    user = context['user']

    # Always let sysadmins do their thing.
    if authz.is_sysadmin(user):
        return {'success': True}
    else:
        return {'success': False}

def addTag(context, data_dict):
    return _user_has_minumum_role(context)