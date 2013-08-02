import os

import cbpos

logger = cbpos.get_logger(__name__)

from cbpos.mod.base.models import Item

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, LargeBinary, Enum, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class StoredFile(cbpos.database.Base, Item):
    __tablename__ = 'storedfiles'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), default='')
    filetype = Column(String(5), default='')
    content = deferred(Column("content", LargeBinary(2**32-1)))

    def __init__(self, filename):
        basename = os.path.basename(filename)
        dummy, ext = os.path.splitext(basename)
        # TODO: guess file type from mimetypes package, not extension
        filetype = ext[1:]
        with open(filename, 'rb') as f:
            content = f.read()
        
        super(StoredFile, self).__init__(filetype=filetype, content=content, filename=basename)

    @classmethod
    def image(cls, path):
        # TODO: process the image with PIL and accept additional arguments for image size, format, etc.
        return cls(path)

    @hybrid_property
    def display(self):
        return self.filename
    
    @display.expression
    def display(self):
        return self.filename

    @hybrid_property
    def path(self):
        cache = self.cached()
        if not os.path.isfile(cache):
            with open(cache, 'wb') as f:
                f.write(self.content)
        return cache

    def cached(self):
        # TODO: do not use resources, use data (userdata) for files which can be modified
        return cbpos.res.base('cache/{}.{}'.format(self.id, self.filetype))

    def __repr__(self):
        return "<StoredFile %s>" % (self.filename,)
