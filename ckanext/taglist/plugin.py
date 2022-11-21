import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model

from flask import Blueprint

import ckanext.taglist.actionsapi as actionsapi
import ckanext.taglist.auth as auth
import ckanext.taglist.db as db

import logging
log = logging.getLogger(__name__)
c = toolkit.c

#Used to add page in later get_blueprint()
def tag_show():

    context = {'model': model, 'user': c.user, 'auth_user_obj': c.userobj}
    try:
        toolkit.check_access('sysadmin', context, {})
        return toolkit.render('admin/addTag.html')
    except toolkit.NotAuthorized:
        return toolkit.abort(403, 'Need to be system administrator to administer')


#Only used on first time startup
#Adds the required vocabulary
def create_voc(context):
    try:
        data = {'id': 'tags'}
        toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        data = {'name': 'tags'}
        toolkit.get_action('vocabulary_create')(context, data)

#Adds tags to the vocabulary from the table centraltags
def create_tags():
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}


    tagList = db.centraltags.find(Added=False).all()
    if ( len(tagList) != 0): #check if tags to add
        vocabularyList = toolkit.get_action('vocabulary_list')({'ignore_auth': True}, {})
        for vocabulary in vocabularyList:
            if (vocabulary["name"] == "tags"): #find the correct vocab
                for tag in tagList: #adds tags to vocab
                    if (tag.tagname != ""):
                        try:
                            logging.info("Creating tag for 'tags'")
                            data: dict[str, str] = {'name': tag.tagname, 'vocabulary_id': vocabulary['id']}
                            toolkit.get_action('tag_create')(context, data)
                            db.centraltags.updateAdded(True, id = tag.id)
                        except:
                            log.info("Tag all ready exist")
    create_voc(context)

#HTML helper
#Return the list of tags from the tags vocabulary.
def tags_helper():
    create_tags()
    try:
        tags = toolkit.get_action('tag_list')(
                {}, {'vocabulary_id': 'tags'})
        return tags
    except toolkit.ObjectNotFound:
        return None

class TaglistPlugin(plugins.SingletonPlugin,toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IDatasetForm, inherit=False)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IAuthFunctions, inherit=True)
    plugins.implements(plugins.IBlueprint)

    # IConfigurable
    # Creates DB table
    def configure(self, config):
        if not db.centraltags_table.exists():
            db.centraltags_table.create()

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic','taglist')

    # IDatasetForm
    def _modify_package_schema(self, schema):

        schema['resources'].update({
                'tags': [
                    toolkit.get_validator('ignore_missing'),
                    toolkit.get_converter('convert_to_tags')('tags')
                ]
                })
        return schema

    def show_package_schema(self):
            schema = super(TaglistPlugin, self).show_package_schema()
            schema['resources'].update({
                'tags': [
                    toolkit.get_validator('ignore_missing'),
                    toolkit.get_converter('convert_to_tags')('tags')
                ]
            })
            return schema 

    def create_package_schema(self):
        schema = super(TaglistPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(TaglistPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    
    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # IAuthFunctions
    def get_auth_functions(self):
        auth_dict = {
            'addTag': auth.addTag
        }
        return auth_dict

    # IActions
    def get_actions(self):
        actions_dict = {
            'addTag': actionsapi.addTag,
            'removeTag': actionsapi.removeTag,
            'listTag': actionsapi.listTag,
            'renameTag': actionsapi.renameTag
        }
        return actions_dict

    # ITemplateHelpers
    def get_helpers(self):
        return {'tags': tags_helper}

    # IBlueprint
    def get_blueprint(self):
        u'''Return a Flask Blueprint object to be registered by the app.'''

        # Create Blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        # Add plugin url rules to Blueprint object
        rules = [
            (u'/ckan-admin/tags', u'admin/tags', tag_show),
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
    