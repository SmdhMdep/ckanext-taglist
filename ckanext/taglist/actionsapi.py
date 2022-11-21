import ckanext.taglist.db as db

import ckan.model as model

import ckan.plugins.toolkit as toolkit

import logging
log = logging.getLogger(__name__)

#Action API command
#Adds a tag to the centraltags table for adding to the tags table later
def addTag(context, data_dict):
    toolkit.check_access("addTag", context, data_dict)

    data, errors = toolkit.navl_validate(
        data_dict,
        {"tag": [toolkit.get_validator('ignore_empty'), str]},
    )

    if errors:
        raise toolkit.ValidationError(errors)

    newTag = db.centraltags()
    newTag.tagname = data['tag']
    newTag.user_id = model.User.get(context['user']).id
    newTag.Added = False
    newTag.save()

    session = context['session']
    session.add(newTag)
    session.commit()

    return newTag.id

#Action API command
#removes a tag from the centraltags table
def removeTag(context, data_dict):
    toolkit.check_access("addTag", context, data_dict)

    data, errors = toolkit.navl_validate(
        data_dict,
        {"tag": [toolkit.get_validator('ignore_empty'), str]},
    )

    if errors:
        raise toolkit.ValidationError(errors)

    tag = db.centraltags.get(tagname=data['tag'])
    if tag is None:
        return "no tag with name stated"

    log.debug(tag)

    session = context['session']
    session.delete(tag)

    try:
        toolkit.get_action('tag_delete')(
                {}, {'vocabulary_id': 'tags', 'id': data['tag'] })
    except:
        return "mis-match error"

    session.commit()

    return True

#Action API command
#Renames a tag
def renameTag(context, data_dict):
    toolkit.check_access("addTag", context, data_dict)

    data, errors = toolkit.navl_validate(
        data_dict,
        {"tagOld": [toolkit.get_validator('ignore_empty'), str],
        "tagNew": [toolkit.get_validator('ignore_empty'), str]},
    )
    if errors:
        raise toolkit.ValidationError(errors)

    log.debug(data_dict)

    centraltTag = db.centraltags.get(tagname=data['tagOld'])
    if centraltTag is None:
        return "no tag with name stated"

    vocab = model.Vocabulary.get(id_or_name="tags")
    if vocab is None:
        return "no vocab with name stated"

    tag = model.Tag.by_name(data['tagOld'],vocab=vocab)
    if tag is None:
        return "no tag with name stated"

    tag.name = data["tagNew"]
    centraltTag.tagname = data["tagNew"]

    session = context['session']
    session.commit()

    return True

#Action API command
#Dev command to list tags.
def listTag(context, data_dict):
    tag = db.centraltags.find().all()
    if tag is None:
        return "no tag with name stated"

    log.debug(tag)

    return True