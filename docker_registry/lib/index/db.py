# -*- coding: utf-8 -*-

"""An SQLAlchemy backend for the search endpoint
"""
import logging

from ... import storage
from .. import config
from . import Index
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.sql.functions
import time

from docker_registry.core import compat
json = compat.json


Base = sqlalchemy.ext.declarative.declarative_base()

logger = logging.getLogger(__name__)

class Version (Base):
    "Schema version for the search-index database"
    __tablename__ = 'version'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    def __repr__(self):
        return '<{0}(id={1})>'.format(type(self).__name__, self.id)


class Repository (Base):
    "Repository description"
    __tablename__ = 'repository'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(
        sqlalchemy.String(length=30 + 1 + 64),  # namespace / respository
        nullable=False, unique=True)
    description = sqlalchemy.Column(
        sqlalchemy.String(length=100))

    def __repr__(self):
        return "<{0}(name='{1}', description='{2}')>".format(
            type(self).__name__, self.name, self.description)

def retry(f):
    def _retry(self, *args, **kwargs):
        retry_times = 2
        i = 0
        while True:
            try:
                return f(self, *args, **kwargs)
            except sqlalchemy.exc.DBAPIError as e:
                if i < retry_times:
                    logger.warn("DB is disconnected. Reconnect to it.")
                    self.reconnect_db()
                    i += 1
                else:
                    raise e

    return _retry


class Layer (Base):
    "layer cnt description"
    __tablename__ = 'layer'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(
        sqlalchemy.String(length=128), 
        nullable=False, unique=True,primary_key=True)
    cnt =  sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)
    description = sqlalchemy.Column(
        sqlalchemy.String(length=100))

    def __repr__(self):
        return "<{0}(name='{1}', cnt='{2}')>".format(
            type(self).__name__, self.name,self.cnt)

class Tag (Base):
    "tag description"
    __tablename__ = 'tag'

    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
    namespace = sqlalchemy.Column(sqlalchemy.String(length=128), nullable=False)
    imagename = sqlalchemy.Column(sqlalchemy.String(length=128), nullable=False)
    tagname = sqlalchemy.Column(sqlalchemy.String(length=56), nullable=False)
    value =  sqlalchemy.Column(sqlalchemy.String(length=128), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String(length=512))

    def __repr__(self):
        return "<{0}(namespace='{1}', imagename='{2}',tagname='{3}',value='{4}')>".format(type(self).__name__, self.namespace,self.imagename,self.tagname,self.value)


class SQLAlchemyIndex (Index):
    """Maintain an index of repository data

    The index is a dictionary.  The keys are
    '{namespace}/{repository}' strings, and the values are description
    strings.  For example:

      index['library/ubuntu'] = 'An ubuntu image...'
    """
    def __init__(self, database=None):
        if database is None:
            cfg = config.load()
            database = cfg.sqlalchemy_index_database
        self._database = database
        self._engine = sqlalchemy.create_engine(database)
        self._session = sqlalchemy.orm.sessionmaker(bind=self._engine)
        self.version = 1
        self._setup_database()
        super(SQLAlchemyIndex, self).__init__()

    def reconnect_db(self):
        self._engine = sqlalchemy.create_engine(self._database)
        self._session = sqlalchemy.orm.sessionmaker(bind=self._engine)

    def _setup_database(self):
        session = self._session()
        if self._engine.has_table(table_name=Version.__tablename__):
            version = session.query(
                sqlalchemy.sql.functions.max(Version.id)).first()[0]
        else:
            version = None
        if version:
            if version != self.version:
                raise NotImplementedError(
                    'unrecognized search index version {0}'.format(version))
        else:
            self._generate_index(session=session)
        session.close()

    @retry
    def _generate_index(self, session):
        #store = storage.load()
        Base.metadata.create_all(self._engine)
        #session.add(Version(id=self.version))
        #for repository in self._walk_storage(store=store):
            #session.add(Repository(**repository))
        #add by zxc for create layer table
        #session.add(Layer(name="demolayer",cnt=0))
        #session.add(Tag(namespace="demo", imagename="demo", tagname="1.0", value="xxxxxxxx"))
        session.commit()

    @retry
    def _handle_repository_created(
            self, sender, namespace, repository, value):
        logger.debug("DB _handle_repository_created ...")
        name = '{0}/{1}'.format(namespace, repository)
        description = ''  # TODO(wking): store descriptions
        session = self._session()
        session.add(Repository(name=name, description=description))
        session.commit()
        session.close()

    @retry
    def _handle_repository_updated(
            self, sender, namespace, repository, value):
        logger.debug("DB _handle_repository_updated ...")
        name = '{0}/{1}'.format(namespace, repository)
        description = ''  # TODO(wking): store descriptions
        session = self._session()
        session.query(Repository).filter(
            Repository.name == name
        ).update(
            values={'description': description},
            synchronize_session=False
        )
        session.commit()
        session.close()

    @retry
    def _handle_repository_deleted(self, sender, namespace, repository):
        logger.debug("DB _handle_repository_deleted ...")
        name = '{0}/{1}'.format(namespace, repository)
        session = self._session()
        session.query(Repository).filter(Repository.name == name).delete()
        session.commit()
        session.close()


    @retry
    def _handle_layer_increased(
            self, sender, layer):
        logger.debug("DB _handle_layer_increased ...")
        name = layer
        description = ''  # TODO(wking): store descriptions
        session = self._session()

        layerID="'%s'"%layer
        #time.sleep(1)
        cmd="INSERT INTO layer (name,cnt) VALUES (%s,1) ON DUPLICATE KEY UPDATE cnt=cnt+1;"%layerID
        session.execute(cmd)
        session.commit()
        session.close()

    @retry
    def _handle_layer_decreased(
            self, sender, layer):
        logger.debug("DB _handle_layer_decreased ...")
        name = layer
        layerID="'%s'"%layer
        description = ''  # TODO(wking): store descriptions
        session = self._session()
        cmd="UPDATE layer SET cnt = IF(cnt<1, 0, cnt-1) WHERE name=%s;"%layerID
        session.execute(cmd)
        cmd="DELETE from layer where cnt = 0"
        session.execute(cmd)
        session.commit()
        session.close()

    @retry
    def _handle_tag_created(self, sender, namespace, imagename, tagname, value ,jsondata):
        logger.debug("DB _handle_tag_created ...")
        description = ''  # TODO(wking): store descriptions
        session = self._session()
        session.add(Tag(namespace=namespace, imagename=imagename, tagname=tagname, value=value ,description=jsondata))
        session.commit()
        session.close()

    @retry
    def _handle_tag_deleted(self, sender, namespace, imagename, tagname, value):
        logger.debug("DB _handle_tag_deleted ...")
        session = self._session()
        session.query(Tag).filter(Tag.namespace == namespace , Tag.imagename == imagename , Tag.tagname==tagname).delete()
        session.commit()
        session.close()

    @retry
    def results(self, search_term):
        session = self._session()
        like_term = '%%%s%%' % search_term
        repositories = session.query(Repository).filter(
            sqlalchemy.sql.or_(
                Repository.name.like(like_term),
                Repository.description.like(like_term)))
        return [
            {
                'name': repo.name,
                'description': repo.description,
            }
            for repo in repositories]



    @retry
    def get_allnamespaces(self):
        session = self._session()
        Tags = session.query(Tag).group_by(Tag.namespace).all()
        return [
            {
                'namespaces': repo.namespace,
            }
            for repo in Tags]

    @retry
    def get_tags(self,select_term):
        session = self._session()
        Tags = session.query(Tag).filter(Tag.namespace==select_term).all()

        results = []

        for repo in Tags :
            taginfo = {}
            taginfo['tag'] = repo.namespace + '/' + repo.imagename + ':' + repo.tagname
            taginfo['id'] = repo.value
            if repo.description :
                jsondata = json.loads(repo.description)
                taginfo['created'] = jsondata.get('created','null')
                taginfo['Size'] = jsondata.get('Size','null')
                taginfo['arch'] = jsondata.get('arch','null')
                taginfo['os'] = jsondata.get('os','null')
            else:
                taginfo['created'] = "null"
                taginfo['Size'] = "null"
                taginfo['arch'] = "null"
                taginfo['os'] = "null"

            results.append(taginfo)


        return results

    @retry
    def get_layer_info(self, search_term):
        session = self._session()
        like_term = '%%%s%%' % search_term
        repositories = session.query(Layer).filter(Layer.name==search_term).all()

        return [
            {
                'name': repo.name,
                'cnt': repo.cnt,
            }
            for repo in repositories]

    @retry
    def get_layer_cnt(self, layer_id):
        session = self._session()
        layer_cnt = session.query(Layer).filter(Layer.name == layer_id).first().cnt
        return layer_cnt

