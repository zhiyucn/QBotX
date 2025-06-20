from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import tomli

# 加载配置文件
with open("config.toml", "rb") as f:
    config = tomli.load(f)

if config["database"]["type"] == "sqlite":
    engine = create_engine(f'sqlite:///{config["database"]["path"]}')

Base = declarative_base()

class Memory(Base):
    __tablename__ = 'memory'
    id = Column(Integer, primary_key=True)
    message = Column(String)
    #group_id = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Memory(id={self.id}, created_at={self.created_at})>"

class Emoji(Base):
    __tablename__ ='emoji'
    id = Column(Integer, primary_key=True)
    message = Column(String)
    file_name = Column(String)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Emoji(id={self.id}, created_at={self.created_at})>"
Base.metadata.create_all(engine)