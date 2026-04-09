from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    def get_all(self, skip=0, limit=None):
        q = self.db.query(self.model).offset(skip)
        if limit is not None:
            q = q.limit(limit)
        return q.all()

    def get_by_id(self, id: int):
        return self.db.query(self.model).filter(self.model.id == id).first()

    def create(self, obj):
        self.db.add(obj)
        self.db.flush()
        return obj

    def update(self, obj):
        self.db.flush()
        return obj

    def delete(self, id: int):
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
        return obj
