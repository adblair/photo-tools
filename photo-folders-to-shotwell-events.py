#!/usr/bin/env python3

import logging
import os
import shutil

import sqlalchemy.ext.automap
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.schema

log = logging.getLogger(__name__)


def get_database_path():
    xdg_data_dir = os.environ.get('XDG_DATA_DIR', '~/.local/share')
    return os.path.expanduser(os.path.join(
        xdg_data_dir, 'shotwell', 'data', 'photo.db'
    ))


def backup_database(filepath):
    shutil.copy(filepath, filepath + '.bak')


def get_or_create_event(name):
    try:
        return session.query(Event).filter(Event.name == name).one()
    except sqlalchemy.orm.exc.NoResultFound:
        log.info('Creating event "{}"'.format(name))
        event = Event(name=name)
        session.add(event)
        session.flush()
        return event


def convert_folder_names_to_events(model):
    for obj in session.query(model):
        event_name = os.path.basename(os.path.dirname(obj.filename))
        event = get_or_create_event(event_name)
        obj.event_id = event.id


def delete_empty_events():
    empty_events = (
        session.query(Event.id)
        .outerjoin((Photo, Photo.event_id == Event.id))
        .filter(Photo.id == None)  # noqa
    )

    (
        session.query(Event)
        .filter(Event.id.in_(empty_events))
        .delete(synchronize_session='fetch')
    )


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    database_path = get_database_path()
    database_uri = 'sqlite:///{}'.format(database_path)

    backup_database(database_path)

    engine = sqlalchemy.create_engine(database_uri)
    session = sqlalchemy.orm.Session(engine)

    Base = sqlalchemy.ext.automap.automap_base()
    Base.prepare(engine, reflect=True)

    Event = Base.classes.EventTable
    Photo = Base.classes.PhotoTable
    Video = Base.classes.VideoTable

    convert_folder_names_to_events(Photo)
    convert_folder_names_to_events(Video)
    delete_empty_events()

    session.commit()
    session.close()
