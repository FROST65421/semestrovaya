from sqlalchemy import create_engine, ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship, selectinload

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer(), unique=True)
    first_name: Mapped[str] = mapped_column(String())
    last_name: Mapped[str] = mapped_column(String(), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Likes", back_populates="user")

class News(Base):
    __tablename__ = "news"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    title: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    release_date: Mapped[str] = mapped_column(String())
    comments = relationship("Comment", back_populates="news")
    likes = relationship("Likes", back_populates="news")

class Likes(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    user = relationship("User", back_populates="likes")
    news = relationship("News", back_populates="likes")

class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    text: Mapped[str] = mapped_column(String())
    user = relationship("User", back_populates="comments")
    news = relationship("News", back_populates="comments")

engine = create_engine("sqlite:///bot.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

# ==================== USER CRUD ====================
def create_user(tg_id: int, first_name: str, last_name: str = "") -> User:
    with SessionLocal() as session:
        user = User(tg_id=tg_id, first_name=first_name, last_name=last_name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def find_user_by_tg_id(tg_id: int) -> User | None:
    with SessionLocal() as session:
        return session.query(User).filter_by(tg_id=tg_id).first()

def find_user_by_id(user_id: int) -> User | None:
    with SessionLocal() as session:
        return session.query(User).filter_by(id=user_id).first()

def delete_user(tg_id: int) -> bool:
    with SessionLocal() as session:
        user = session.query(User).filter_by(tg_id=tg_id).first()
        if user:
            session.delete(user)
            session.commit()
            return True
        return False

# ==================== NEWS CRUD ====================
def create_news(title: str, description: str, release_date: str) -> News:
    with SessionLocal() as session:
        news = News(title=title, description=description, release_date=release_date)
        session.add(news)
        session.commit()
        session.refresh(news)
        return news

def get_all_news() -> list[News]:
    with SessionLocal() as session:
        return session.query(News).all()

def find_news_by_id(news_id: int) -> News | None:
    with SessionLocal() as session:
        return session.query(News).filter_by(id=news_id).first()

def delete_news(news_id: int) -> bool:
    with SessionLocal() as session:
        news = session.query(News).filter_by(id=news_id).first()
        if news:
            session.delete(news)
            session.commit()
            return True
        return False

# ==================== COMMENT CRUD ====================
def create_comment(user_id: int, news_id: int, text: str) -> Comment:
    with SessionLocal() as session:
        comment = Comment(user_id=user_id, news_id=news_id, text=text)
        session.add(comment)
        session.commit()
        session.refresh(comment)
        return comment

def get_comments_by_news_id(news_id: int) -> list[Comment]:
    with SessionLocal() as session:
        comments = session.query(Comment).options(selectinload(Comment.user)).filter_by(news_id=news_id).all()
        for c in comments:
            session.expunge(c)
        return comments

def delete_comment(comment_id: int) -> bool:
    with SessionLocal() as session:
        comment = session.query(Comment).filter_by(id=comment_id).first()
        if comment:
            session.delete(comment)
            session.commit()
            return True
        return False

# ==================== LIKES CRUD ====================
def toggle_like(user_id: int, news_id: int) -> bool:
    with SessionLocal() as session:
        like = session.query(Likes).filter_by(user_id=user_id, news_id=news_id).first()
        if like:
            session.delete(like)
            session.commit()
            return False
        session.add(Likes(user_id=user_id, news_id=news_id))
        session.commit()
        return True

def get_like_count(news_id: int) -> int:
    with SessionLocal() as session:
        return session.query(Likes).filter_by(news_id=news_id).count()

def has_user_liked(user_id: int, news_id: int) -> bool:
    with SessionLocal() as session:
        return session.query(Likes).filter_by(user_id=user_id, news_id=news_id).first() is not None