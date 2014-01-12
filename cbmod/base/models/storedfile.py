import tempfile, os
from cStringIO import StringIO
from PIL import Image

import cbpos

logger = cbpos.get_logger(__name__)

from cbmod.base.models import Item

from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, LargeBinary, Enum, MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator

class StoredFile(cbpos.database.Base, Item):
    __tablename__ = 'storedfiles'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), default='')
    filetype = Column(String(5), default='')
    content = deferred(Column("content", LargeBinary(2**32-1)))

    def __init__(self, path, content_file=None):
        basename = os.path.basename(path)
        filename, filetype = os.path.splitext(basename)
        # TODO: guess file type from mimetypes package, not extension
        if content_file is None:
            try:
                with open(path, 'rb') as f:
                    content = f.read()
            except IOError as e:
                logger.error("Could not read file")
                logger.error(e)
                content = u""
        elif isinstance(content_file, basestring):
            content = content_file
        else:
            content_file.seek(0)
            content = content_file.read()
        
        super(StoredFile, self).__init__(filetype=filetype, content=content, filename=filename)

    @classmethod
    def image(cls, path, size=None, format=None):
        
        # First, open the path
        try:
            im = Image.open(path)
        except IOError:
            # PIL cannot identify the image
            # Or the image is not readable
            raise ValueError("Invalid image file")
        
        # Get some info about it
        basename = os.path.basename(path)
        filename, ext = os.path.splitext(basename)
        original_size = im.size
        
        if size is None and format is None:
            # No need to process anything
            return cls(path)
        
        if format is None:
            # If no specific format is specified just use whatever is there
            # And keep the same extension
            PIL_format = im.format
            format = ext[1:] if ext.startswith(".") else ext
        else:
            # Let PIL guess it from the format (extension)
            PIL_format = None
        
        if size is None:
            # Do not resize
            # Note: do not return because format may be different (transparency, background, etc.)
            size = original_size
        else:
            size = tuple(size)
        
        logger.debug("Resizing from %s to %s", original_size, size)
        logger.debug("Converting to %s/%s from %s/%s", format, PIL_format, ext, im.format)
        
        # If some processing is necessary, do it now.
        final_im = Image.new("RGB", size, "white")
        # Resize the image
        im.thumbnail(size, Image.ANTIALIAS)
        
        # Center it in the image with the desired size
        actual_size = im.size
        paste_pos = tuple((size[i]-actual_size[i])/2 for i in (0, 1))
        final_im.paste(im, paste_pos)
        
        try:
            # Create a temporary file
            fd, temp = tempfile.mkstemp(suffix="."+format)
        except IOError as e:
            logger.exception("Could not create temporary file. Manipulating in memory")
            
            f = StringIO()
            # We cannot use the below because of cStringIO, it works for StringIO
            #f.name = path
            # So we try to guess it, just like PIL does it
            if PIL_format is None:
                try:
                    PIL_format = Image.EXTENSION["."+format]
                except KeyError:
                    Image.init()
                    try:
                        PIL_format = Image.EXTENSION["."+format]
                    except KeyError:
                        # let it fail from within PIL's save
                        pass
                logger.debug("Final PIL_format: %s", PIL_format)
            
            try:
                final_im.save(f, PIL_format)
            except KeyError:
                # PIL cannot identify the image
                raise ValueError("Invalid output image type")
            image = cls(filename+"."+format, f)
            
            f.close()
        else:
            logger.debug("Image will be saved temporarily to: " + temp)
            
            try:
                final_im.save(temp, PIL_format)
            except KeyError:
                # PIL cannot identify the image
                raise ValueError("Invalid output image type")
            
            with open(temp, 'rb') as f:
                # Create the StoredFile instance
                image = cls(filename+"."+format, f)
            
            # tempfile.mkstemp does not delete the file once created
            try:
                os.remove(temp)
            except (OSError, IOError) as e:
                # Could not delete the temp file
                # Maybe because it's on Windows, or it's already gone
                pass
    
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
        return cbpos.res.base('cache/{}{}'.format(self.id, self.filetype))

    def __repr__(self):
        return "<StoredFile %s>" % (self.filename,)
