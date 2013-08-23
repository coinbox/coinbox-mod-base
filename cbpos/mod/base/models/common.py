import cbpos

logger = cbpos.get_logger(__name__)

#from sqlalchemy import func, Table, Column, Integer, String, Float, Boolean, Enum, DateTime, MetaData, ForeignKey
#from sqlalchemy.orm import relationship, backref

class Item(object):
    # TODO arrange soft deletions to have 3 tables (or more) one mother(id only), one active children, one deleted children
    #        see bookmark "The trouble with soft delete"
    #date_deleted = Column(DateTime, nullable=True, default=None)
    def fillDict(self, D):
        for k in D.keys():
            try:
                D[k] = getattr(self, k)
            except AttributeError:
                pass

    def update(self, **kwargs):
        session = cbpos.database.session()
        try:
            for k, v in kwargs.iteritems():
                setattr(self, k, v)
            if not self in session:
                session.add(self)
            session.commit()
        except:
            session.rollback()
            logger.exception("Oops!")
            return False
        else:
            return True

    def delete(self):
        session = cbpos.database.session()
        try:
            session.delete(self)
            # TODO check the soft delete thingy
            #self.date_deleted = func.now()
            session.commit()
        except:
            session.rollback()
            logger.exception("Oops!")
            return False
        else:
            return True
