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
    def image(cls, path, size=None, format=None):
        
        # First, open the path
        # TODO: what happens if the file is not an image? It should raise a meaningful exception
        #         Maybe ValueError: Invalid image path / File does not exist / etc. Could be shown to the user
        
        from PIL import Image
        im = Image.open(path)
        original_size = im.size
        
        if size is None and format is None:
            # No need to process anything
            return cls(path)
        
        if format is None:
            basename = os.path.basename(filename)
            dummy, ext = os.path.splitext(basename)
            # TODO: guess file type from mimetypes package, not extension
            format = ext
        
        if size is None:
            # Do not resize
            # Note: do not return because format may be different (transparency, background, etc.)
            size = original_size
        
        # If some processing is necessary, do it now.
        
        import tempfile, os
        
        # Create a temporary file
        fd, temp = tempfile.mkstemp(suffix="."+format)
        
        logger.debug("Image will be saved temporarily to: " + temp)
        
        # Resize the image
        final_im = Image.new("RGB", size, "white")
        im.thumbnail(size, Image.ANTIALIAS)
        
        actual_size = im.size
        paste_pos = tuple((size[i]-actual_size[i])/2 for i in (0, 1))
        final_im.paste(im, paste_pos)
        final_im.save(temp)
        
        # Create the StoredFile instance
        image = cls(temp)
        
        # tempfile.mkstemp does nor delete the file once created
        os.remove(temp)
    
        return image

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
