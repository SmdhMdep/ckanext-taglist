import ckan.tests.factories as factories
import ckan.plugins.toolkit as toolkit
import ckanext.taglist.plugin as plugin

from ckan import model

import pytest

'''
Important notes:
"plugin.tags_helper()" makes ckan step forward once which allows tags
to be added/rename/removed. This is why it is used in some cases
'''

@pytest.mark.ckan_config('ckan.plugins','taglist')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
#Test that list tags works with no tags
def test_api_no_list_tag():
    taglist = toolkit.get_action('listTag')({'ignore_auth': True})
    assert taglist == "no tags"

@pytest.mark.ckan_config('ckan.plugins','taglist')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
#Test that adding a tag works
def test_add_tag():
    admin = factories.Sysadmin()
    context = {'model': model, 'session': model.Session, 'user': admin["name"]}

    data = {'tag': "Test"}
    tag = toolkit.get_action('addTag')(context, data)

    taglist2 = toolkit.get_action('listTag')({'ignore_auth': True},{})

    assert taglist2 != "no tags"

@pytest.mark.ckan_config('ckan.plugins','taglist')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
#Test renaming tags
def test_rename_tag():
    admin = factories.Sysadmin()
    context = {'model': model, 'session': model.Session, 'user': admin["name"]}

    plugin.tags_helper()

    data = {'tag': "Test"}
    tagadd = toolkit.get_action('addTag')(context, data)

    plugin.tags_helper()

    data = {'tagOld': "Test", 'tagNew': "Test2"}
    tag = toolkit.get_action('renameTag')(context, data)

    taglist = toolkit.get_action('listTag')({'ignore_auth': True},{})
    assert taglist[0].tagname == "Test2"

@pytest.mark.ckan_config('ckan.plugins','taglist')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
#test deleing tags
def test_remove_tag():
    admin = factories.Sysadmin()
    context = {'model': model, 'session': model.Session, 'user': admin["name"]}

    plugin.tags_helper()

    data = {'tag': "Test"}
    tagadd = toolkit.get_action('addTag')(context, data)

    plugin.tags_helper()

    taglist = toolkit.get_action('listTag')({'ignore_auth': True},{})
    assert taglist[0].tagname == "Test"

    tag = toolkit.get_action('removeTag')(context, data)

    plugin.tags_helper()

    taglist = toolkit.get_action('listTag')({'ignore_auth': True},{})
    assert taglist != "Test"

@pytest.mark.ckan_config('ckan.plugins','taglist')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
#Test auth is correct
def test_auth_add_tag():
    admin = factories.Sysadmin()
    context = {'model': model, 'session': model.Session, 'user': admin["name"]}
    assert  plugin.auth._user_has_minumum_role(context) == {'success': True}

    user = factories.User()
    context = {'model': model, 'session': model.Session, 'user': user["name"]}
    assert  plugin.auth._user_has_minumum_role(context) == {'success': False}