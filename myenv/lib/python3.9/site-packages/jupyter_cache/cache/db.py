from contextlib import contextmanager
import datetime
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.exc import IntegrityError, OperationalError

try:
    from sqlalchemy.orm import declarative_base  # sqlalchemy >= 1.4.0
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base  # sqlalchemy < 1.4.0

from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy.sql.expression import desc

from jupyter_cache import __version__
from jupyter_cache.utils import shorten_path

OrmBase = declarative_base()
DB_NAME = "global.db"

# version changes:
# 0.5.0:
#   - __version__.txt file written to cache on creation
#   - table: nbstage -> nbproject
#   - added read_data and exec_data fields to nbproject


def create_db(path: Union[str, Path]) -> Engine:
    """Get or create a database at the given path.

    :param path: The path to the cache folder.
    """
    exists = (Path(path) / DB_NAME).exists()
    engine = create_engine(f"sqlite:///{os.path.join(path, DB_NAME)}")
    if not exists:
        # add all the tables, and a version identifier
        OrmBase.metadata.create_all(engine)
        Path(path).joinpath("__version__.txt").write_text(__version__)

    return engine


def get_version(path: Union[str, Path]) -> Optional[str]:
    """Attempt to get the version of the cache."""
    version_file = Path(path).joinpath("__version__.txt")
    if version_file.exists():
        return version_file.read_text().strip()


def datetime_utcnow():
    return lambda: datetime.datetime.now(datetime.timezone.utc)


@contextmanager
def session_context(engine: Engine):
    """Open a connection to the database."""
    session = sessionmaker(bind=engine)()
    try:
        yield session
    except OperationalError as exc:
        session.rollback()
        raise RuntimeError(
            "Unexpected error accessing jupyter cache, it may need to be cleared."
        ) from exc
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Setting(OrmBase):
    """A settings key/value pair representation."""

    __tablename__ = "settings"

    pk = Column(Integer(), primary_key=True)
    key = Column(String(36), nullable=False, unique=True)
    value = Column(JSON())

    def __repr__(self):
        return "{}(pk={},{}={})".format(
            self.__class__.__name__, self.pk, self.key, self.value
        )

    @staticmethod
    def set_value(key: str, value, db: Engine):
        with session_context(db) as session:  # type: Session
            setting = session.query(Setting).filter_by(key=key).one_or_none()
            if setting is None:
                session.add(Setting(key=key, value=value))
            else:
                setting.value = value
            try:
                session.commit()
            except IntegrityError:
                raise TypeError(value)

    @staticmethod
    def get_value(key: str, db: Engine, default=None):
        with session_context(db) as session:  # type: Session
            result = session.query(Setting.value).filter_by(key=key).one_or_none()
            if result is None:
                if default is not None:
                    result = [default]
                else:
                    raise KeyError(f"Setting not found in DB: {key}")
            value = result[0]
        return value

    @staticmethod
    def get_dict(db: Engine) -> dict:
        with session_context(db) as session:  # type: Session
            results = session.query(Setting.key, Setting.value).all()
        return {k: v for k, v in results}


class NbProjectRecord(OrmBase):
    """A record of a notebook within the project."""

    __tablename__ = "nbproject"

    pk = Column(Integer(), primary_key=True)
    uri = Column(String(255), nullable=False, unique=True)
    read_data = Column(JSON(), nullable=False)
    """Data on how to read the uri to a notebook."""
    assets = Column(JSON(), nullable=False, default=list)
    """A list of file assets required for the notebook to run."""
    exec_data = Column(JSON(), nullable=True)
    """Data on how to execute the notebook."""
    created = Column(DateTime, nullable=False, default=datetime_utcnow())
    traceback = Column(Text(), nullable=True, default="")
    """A traceback is added if a notebook fails to execute fully."""

    def __repr__(self):
        return f"{self.__class__.__name__}(pk={self.pk})"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def format_dict(
        self,
        cache_record: Optional["NbCacheRecord"] = None,
        path_length: Optional[int] = None,
        assets: bool = True,
        read_error: Optional[str] = None,
        read_name: bool = True,
    ) -> dict:
        """Return data for display."""
        status = "-"
        if cache_record:
            status = f"✅ [{cache_record.pk}]"
        elif self.traceback:
            status = "❌"
        elif read_error:
            status = "❗️ (unreadable)"
        data = {
            "ID": self.pk,
            "URI": str(shorten_path(self.uri, path_length)),
            "Reader": self.read_data.get("name", "-") if read_name else self.read_data,
            "Added": self.created.isoformat(" ", "minutes"),
            "Status": status,
        }
        if assets:
            data["Assets"] = len(self.assets)
        return data

    @validates("read_data")
    def validate_read_data(self, key, value):
        if not isinstance(value, dict):
            raise ValueError("read_data must be a dict")
        if "name" not in value:
            raise ValueError("read_data must have a name")
        return value

    @validates("assets")
    def validator_assets(self, key, value):
        return self.validate_assets(value)

    @staticmethod
    def validate_assets(paths, uri=None):
        """Validate asset paths are within same folder as the notebook URI"""
        if not (
            isinstance(paths, (list, tuple)) and all(isinstance(v, str) for v in paths)
        ):
            raise TypeError(f"assets must be interable of strings: {paths}")
        if uri is None:
            return list(paths)

        uri_folder = Path(uri).parent
        for path in paths:
            try:
                Path(path).relative_to(uri_folder)
            except ValueError:
                raise ValueError(f"Asset '{path}' is not in folder '{uri_folder}''")
        return list(paths)

    @staticmethod
    def create_record(
        uri: str,
        db: Engine,
        read_data: Dict[str, Any],
        raise_on_exists=True,
        *,
        assets=(),
    ) -> "NbProjectRecord":
        assets = NbProjectRecord.validate_assets(assets, uri)
        with session_context(db) as session:  # type: Session
            record = NbProjectRecord(uri=uri, read_data=read_data, assets=assets)
            session.add(record)
            try:
                session.commit()
            except IntegrityError:
                if raise_on_exists:
                    raise ValueError(f"URI already in project: {uri}")
                return NbProjectRecord.record_from_uri(uri, db)
            session.refresh(record)
            session.expunge(record)
        return record

    def remove_pks(pks: List[int], db: Engine):
        with session_context(db) as session:  # type: Session
            session.query(NbProjectRecord).filter(NbProjectRecord.pk.in_(pks)).delete(
                synchronize_session=False
            )
            session.commit()

    def remove_uris(uris: List[str], db: Engine):
        with session_context(db) as session:  # type: Session
            session.query(NbProjectRecord).filter(NbProjectRecord.uri.in_(uris)).delete(
                synchronize_session=False
            )
            session.commit()

    @staticmethod
    def record_from_pk(pk: int, db: Engine) -> "NbProjectRecord":
        with session_context(db) as session:  # type: Session
            result = session.query(NbProjectRecord).filter_by(pk=pk).one_or_none()
            if result is None:
                raise KeyError(f"Project record not found for NB with PK: {pk}")
            session.expunge(result)
        return result

    @staticmethod
    def record_from_uri(uri: str, db: Engine) -> "NbProjectRecord":
        with session_context(db) as session:  # type: Session
            result = session.query(NbProjectRecord).filter_by(uri=uri).one_or_none()
            if result is None:
                raise KeyError(f"Project record not found for NB with URI: {uri}")
            session.expunge(result)
        return result

    @staticmethod
    def records_all(db: Engine) -> "NbProjectRecord":
        with session_context(db) as session:  # type: Session
            results = session.query(NbProjectRecord).order_by(NbProjectRecord.pk).all()
            session.expunge_all()
        return results

    def remove_tracebacks(pks, db: Engine):
        """Remove all tracebacks."""
        with session_context(db) as session:  # type: Session
            session.query(NbProjectRecord).filter(NbProjectRecord.pk.in_(pks)).update(
                {NbProjectRecord.traceback: None}, synchronize_session=False
            )
            session.commit()

    def set_traceback(uri: str, traceback: Optional[str], db: Engine):
        with session_context(db) as session:  # type: Session
            result = session.query(NbProjectRecord).filter_by(uri=uri).one_or_none()
            if result is None:
                raise KeyError(f"Project record not found for NB with URI: {uri}")
            result.traceback = traceback
            try:
                session.commit()
            except IntegrityError:
                raise TypeError(traceback)


class NbCacheRecord(OrmBase):
    """A record of an executed notebook cache."""

    __tablename__ = "nbcache"

    pk = Column(Integer(), primary_key=True)
    hashkey = Column(String(255), nullable=False, unique=True)
    uri = Column(String(255), nullable=False, unique=False)
    description = Column(String(255), nullable=False, default="")
    data = Column(JSON())
    """Extra data, such as the execution time."""
    created = Column(DateTime, nullable=False, default=datetime_utcnow())
    accessed = Column(
        DateTime, nullable=False, default=datetime_utcnow(), onupdate=datetime_utcnow()
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(pk={self.pk})"

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def format_dict(
        self, hashkey=False, path_length=None, show_descript=False, show_data=True
    ):
        data = {
            "ID": self.pk,
            "Origin URI": str(shorten_path(self.uri, path_length)),
            "Created": self.created.isoformat(" ", "minutes"),
            "Accessed": self.accessed.isoformat(" ", "minutes"),
        }
        if show_descript:
            data["Description"] = self.description
        if hashkey:
            data["Hashkey"] = self.hashkey
        if show_data and self.data:
            data["Data"] = self.data
        return data

    @staticmethod
    def create_record(uri: str, hashkey: str, db: Engine, **kwargs) -> "NbCacheRecord":
        with session_context(db) as session:  # type: Session
            record = NbCacheRecord(hashkey=hashkey, uri=uri, **kwargs)
            session.add(record)
            try:
                session.commit()
            except IntegrityError:
                raise ValueError(f"hashkey already exists:{hashkey}")
            session.refresh(record)
            session.expunge(record)
        return record

    def remove_record(pk: int, db: Engine):
        with session_context(db) as session:  # type: Session
            record = session.get(NbCacheRecord, pk)
            session.delete(record)
            session.commit()

    def remove_records(pks: List[int], db: Engine):
        with session_context(db) as session:  # type: Session
            session.query(NbCacheRecord).filter(NbCacheRecord.pk.in_(pks)).delete(
                synchronize_session=False
            )
            session.commit()

    @staticmethod
    def record_from_hashkey(hashkey: str, db: Engine) -> "NbCacheRecord":
        with session_context(db) as session:  # type: Session
            result = (
                session.query(NbCacheRecord).filter_by(hashkey=hashkey).one_or_none()
            )
            if result is None:
                raise KeyError(f"Cache record not found for NB with hashkey: {hashkey}")
            session.expunge(result)
        return result

    @staticmethod
    def record_from_pk(pk: int, db: Engine) -> "NbCacheRecord":
        with session_context(db) as session:  # type: Session
            result = session.query(NbCacheRecord).filter_by(pk=pk).one_or_none()
            if result is None:
                raise KeyError(f"Cache record not found for NB with PK: {pk}")
            session.expunge(result)
        return result

    def touch(pk, db: Engine):
        """Touch a record, to change its last accessed time."""
        with session_context(db) as session:  # type: Session
            record = session.query(NbCacheRecord).filter_by(pk=pk).one_or_none()
            if record is None:
                raise KeyError(f"Cache record not found for NB with PK: {pk}")
            record.accessed = datetime_utcnow()()
            session.commit()

    def touch_hashkey(hashkey, db: Engine):
        """Touch a record, to change its last accessed time."""
        with session_context(db) as session:  # type: Session
            record = (
                session.query(NbCacheRecord).filter_by(hashkey=hashkey).one_or_none()
            )
            if record is None:
                raise KeyError(f"Cache record not found for NB with hashkey: {hashkey}")
            record.accessed = datetime_utcnow()()
            session.commit()

    @staticmethod
    def records_from_uri(uri: str, db: Engine) -> "NbCacheRecord":
        with session_context(db) as session:  # type: Session
            results = session.query(NbCacheRecord).filter_by(uri=uri).all()
            session.expunge_all()
        return results

    @staticmethod
    def records_all(db: Engine) -> "NbCacheRecord":
        with session_context(db) as session:  # type: Session
            results = session.query(NbCacheRecord).all()
            session.expunge_all()
        return results

    def records_to_delete(keep: int, db: Engine) -> List[int]:
        """Return pks of the oldest records, where keep is number to keep."""
        with session_context(db) as session:  # type: Session
            pks_to_keep = [
                pk
                for pk, in session.query(NbCacheRecord.pk)
                .order_by(desc("accessed"))
                .limit(keep)
                .all()
            ]
            pks_to_delete = [
                pk
                for pk, in session.query(NbCacheRecord.pk)
                .filter(NbCacheRecord.pk.notin_(pks_to_keep))
                .all()
            ]
        return pks_to_delete
