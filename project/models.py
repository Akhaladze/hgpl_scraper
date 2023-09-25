from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declarative_base



db = SQLAlchemy()
Base = declarative_base(metadata=db.metadata)

class Connectors(db.Model):
    ''' Connectors table \n
        id: int, primary_key \n
        name: str, unique, nullable=False \n
        status: bool, default=True, nullable=False \n
        created_at: datetime, default=db.func.now(), nullable=False \n
        updated_at: datetime, default=db.func.now(), nullable=False \n
    '''
    __tablename__ = "connectors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False, nullable=False)
    status = db.Column(db.Boolean(), default=True, nullable=False)
    created_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())
    updated_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())

    def __init__(self, name, status:bool=True):
        self.name = name
        self.status = status

class ConnectorId():
    1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    
    def __int__(self):
        return int(self.value)
    

#def create_partition(target, connection, **kw) -> None:
#    """ creating partition by hand"""
#    connection.execute(
#        """CREATE TABLE IF NOT EXISTS "dow" PARTITION OF "main_sds_store" FOR VALUES IN (1)"""
#    )
#    connection.execute(
#        """CREATE TABLE IF NOT EXISTS "basf" PARTITION OF "main_sds_store" FOR VALUES IN (2)"""
#    )

class MainSDSstore(Base):
    __tablename__ = 'main_sds_store'
    __table_args__ = (
        UniqueConstraint("id", "connector_id"),
        {
            "postgresql_partition_by": "LIST (connector_id)",
            #"postgresql_partition_ ": lambda target: target.connector_id,  
        }
    )


    id = db.Column(db.Integer, primary_key=True)
    connector_id = db.Column(db.Integer, db.ForeignKey('connectors.id'), primary_key=True)
    language= db.Column(db.String(256), unique=False, nullable=False, default='NotSet')
    region = db.Column(db.String(256), unique=False, nullable=False, default='NotSet')
    country = db.Column(db.String(256), unique=False, nullable=True, default=None)
    product_id = db.Column(db.String(256), unique=False, nullable=False, default='NotSet')
    title = db.Column(db.String(256), unique=False, nullable=False, default='NotSet')
    description = db.Column(db.String(256), unique=False, nullable=True, default=None)
    url = db.Column(db.String(256), unique=False, nullable=True, default=None)
    filename = db.Column(db.String(256), unique=False, nullable=True, default=None)
    conectors_metadata = db.Column(JSONB(), unique=False, nullable=True, default=None)
    version = db.Column(db.String(255), unique=False, nullable=False, default='new')
    status = db.Column(db.String(20), unique=False, nullable=False, default='new')
    filesize = db.Column(db.Integer, unique=False, nullable=True, default=None)
    filehashes = db.Column(db.String(255), unique=False, nullable=True, default=None)
    created_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())
    updated_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())

    def __init__(self, connector_id, language, region, country, product_id, title, description, url, filename, conectors_metadata, version, status, filesize, filehashes):
        self.connector_id = connector_id
        self.language = language
        self.region = region
        self.country = country
        self.product_id = product_id
        self.title = title
        self.description = description
        self.url = url
        self.filename = filename
        self.conectors_metadata = conectors_metadata
        self.version = version
        self.status = status
        self.filesize = filesize
        self.filehashes = filehashes

    def __repr__(self):
        return '<MainSDSstore %r>' % self.id
    
    def addNewPartition(self, connector_id):
        self.connector_id = connector_id
        db.session.add(self)
        db.session.commit()
        db.session.close()
        return self

# class DowList(db.Model) and class BasfList(db.Model) are the same - DEPRECATED ELEMENTS, NOT USED IN THE PROJECT SOON, TO BE DELETED

class BasfList(db.Model):
    __tablename__ = "basf_list"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=True, default=None)
    url = db.Column(db.String(256), unique=False, nullable=True, default=None)
    filename = db.Column(db.String(256), unique=False, nullable=True, default=None)
    language= db.Column(db.String(256), unique=False, nullable=True, default=None)
    region = db.Column(db.String(256), unique=False, nullable=True, default=None)
    product_id = db.Column(db.String(250), unique=False, nullable=True, default=None)
    trade_productCode = db.Column(db.String(250), unique=False, nullable=True, default=None)
    record_number = db.Column(db.String(250), unique=False, nullable=True,default=None)
    created_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())
    updated_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())
    page = db.Column(db.Integer, unique=False, nullable=True, default=None)
    status = db.Column(db.String(20), unique=False, nullable=False, default='new')
    connector_id = db.Column(db.Integer, db.ForeignKey('connectors.id'), nullable=False, default=1)
    filesize = db.Column(db.Integer, unique=False, nullable=True, default=None)
    filehashes = db.Column(JSONB, unique=False, nullable=True, default=None)
    
    def __init__(self, title, description, url, url_pdf, filename, language, region, product_id, trade_productCode, record_number, page, connector_id=0, filesize=0, filehashes='', status='new'):
        self.title = title
        self.description = description
        self.url = url
        self.url_pdf = url_pdf
        self.filename = filename
        self.language = language
        self.region = region
        self.product_id = product_id
        self.trade_productCode = trade_productCode
        self.record_number = record_number
        self.page = page
        self.connector_id = connector_id
        self.filesize = filesize
        self.filehashes = filehashes
        self.status = status

class DowList(db.Model):
    __tablename__ = "dow_list"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=True, default=None)
    url = db.Column(db.String(256), unique=False, nullable=True, default=None)
    url_pdf = db.Column(db.String(256), unique=False, nullable=True, default=None)
    filename = db.Column(db.String(256), unique=False, nullable=True, default=None)
    language= db.Column(db.String(256), unique=False, nullable=True, default=None)
    region = db.Column(db.String(256), unique=False, nullable=True, default=None)
    product_id = db.Column(db.String(20), unique=False, nullable=True, default=None)
    trade_productCode = db.Column(db.String(20), unique=False, nullable=True, default=None)
    record_number = db.Column(db.String(20), unique=False, nullable=True,default=None)
    created_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())
    updated_at = db.Column(TIMESTAMP, unique=False, nullable=False, default=db.func.now())
    page = db.Column(db.Integer, unique=False, nullable=True, default=None)
    status = db.Column(db.String(20), unique=False, nullable=False, default='new')
    connector_id = db.Column(db.Integer, db.ForeignKey('connectors.id'), nullable=False, default=1)
    filesize = db.Column(db.Integer, unique=False, nullable=True, default=None)
    filehashes = db.Column(JSONB, unique=False, nullable=True, default=None)

    def __init__(self, title, description, url, url_pdf, filename, language, region, product_id, trade_productCode, record_number, page, connector_id=1, filesize=None, filehashes=None):
        self.title = title
        self.description = description
        self.url = url
        self.url_pdf = url_pdf
        self.filename = filename
        self.language = language
        self.region = region
        self.product_id = product_id
        self.trade_productCode = trade_productCode
        self.record_number = record_number
        self.page = page
        self.status = 'new'
        self.connector_id = connector_id
        self.filesize = filesize
        self.filehashes = filehashes