"""
 DBManager.py

 This module is a thin wrapper over sqlalchemy, an sql client library based on
 object relational mapping. It also responsible for creating database and
 inititalizing all arep tables.
"""
import uuid
from sqlalchemy import Column, Integer, BigInteger, Float, String, \
    Boolean, Enum, create_engine, ForeignKey, UniqueConstraint, exc, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from dbconf import *

#for creating database
DBCONN_FMT = "mysql://{user}:{password}@{host}:{port}"

#for regular usage
DBCONN_DEFAULT_FMT = "mysql://{user}:{password}@{host}:{port}/{database}"

#base class from which all mapped classes should inherit
Base = declarative_base()

# SQLAlchemy object-relational configuration for Arep tables
# http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html
class PhotoModel(Base):
    """
       arep session table for session information from replicator
    """
    __tablename__ = 'PhotoTable'
    UUID  = Column(String(uuidLen), primary_key=True)
    Name  = Column(String(stringLen), nullable=False)
    Year  = Column(Integer, nullable=False)
    Month = Column(Integer, nullable=False)
    Day   = Column(Integer, nullable=False)
    NameSpace  = Column(String(stringLen), nullable=False)
    Location = Column(String(stringLen), nullable=False)
    Description = Column(String(stringLen), nullable=True)

    def __repr__(self):
        return "<%s(UUID : %s, Name :%s Year : %d, Month : %d " \
            "Day : %d NameSpace : %s Loc : %s Description :%s)" % (self.__tablename__, \
            self.UUID, self.Name, self.Year, self.Month, self.Day, self.NameSpace,
            self.Location, self.Description)

# Model Queries
def DBGetPhotos(_dbSession):
    """
        fetches all records
    """
    return _dbSession.query(PhotoModel).all()

def DBGetPhoto(_dbSession, imgUUID):
    """
        fetch a row for the imgUUID
    """
    return _dbSession.query(PhotoModel).filter \
        (PhotoModel.UUID==UUID).first()

def DBAddPhoto(_dbSession, UUID, Name, Year, Month, Day, NameSpace, Location='', Description=''):
    """
        insert record
    """
    photo = PhotoModel(UUID=UUID, \
                       Name=Name, \
                       Year=Year, \
                       Month=Month, \
                       Day=Day, \
                       NameSpace=NameSpace, \
                       Location=Location, \
                       Description=Description)
    _dbSession.add(photo)
    return photo

class DBManager():

    def __init__(self):
        """
        loads db configuration for establishing connection
        """
        DB_URL_DEFAULT = (DBCONN_DEFAULT_FMT.format(**DBCONFIG_DICT))
        self._engine = create_engine(DB_URL_DEFAULT)
        self._sessionMaker = sessionmaker(bind=self._engine)

    def __enter__(self):
        """
        opens connection to the specified database
        :returns Database Handle
        """
        self._session = self._sessionMaker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close Connection to the specified database
        """
        self._session.close()

    def getSession(self):
        """
        returns the underlying session object of sql client
        """
        return self._session

    def createDb(self):
        """
        Create arep Database
        """
        assert self.create
        conn = self._engine.connect()
        conn.execute("CREATE DATABASE IF NOT EXISTS %s" % 'Photos')
        conn.execute("COMMIT")

    def dropDb(self):
        """
        Create arep Database
        """
        assert self.create
        conn = self._engine.connect()
        conn.execute("DROP DATABASE IF EXISTS %s" % 'Photos')
        conn.execute("COMMIT")

    def createTables(self):
        """
        Create arep Tables
        """
        Base.metadata.create_all(self._engine)

def InitPhotosDb():
    """
      Initializes the arep db and tables
    """
    with DBManager() as db:
        db.createTables()

def NukePhotosDb():
    """
      Initializes the arep db and tables
    """
    with DBManager(default=True) as db:
        db.dropDb()

def DumpTables(session):
    """
       Dump Tables
    """
    result = []
    photos = session.query(PhotoModel).all()
    for photo in photos:
        print (photo)
        result.append(photo)
    return result
'''
InitPhotosDb();
with DBManager() as db: 
    _dbSession = db.getSession()
    DBAddPhoto(_dbSession, "sample.jpg", uuid.uuid4(), 2017, 01, 01, "/tmp/path/")
    _dbSession.commit()
    DumpTables(_dbSession)
'''
