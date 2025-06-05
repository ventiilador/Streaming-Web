from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc, or_, asc, insert, delete, update
from sqlalchemy.orm import selectinload
from models import User, Video, Comment, user_comment_favorites
from auth import verify_password, hash_password
from datetime import datetime

async def login(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user:
        if verify_password(plain_password=password, hashed_password=user.password_hash):
            return user
    return None

async def register(db: AsyncSession, username: str, email: str, password: str):
    result = await db.execute(select(User).where(
        or_(
            User.username == username,
            User.email == email
            )
    ))
    user = result.scalars().first()
    if user:
        return None
    new_user = User(username=username, email=email, password_hash=hash_password(password=password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_data_by_id(db: AsyncSession, id: int):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    if user:
        return {"user_id": user.id, "username": user.username, "email": user.email}
    return None

async def get_profile_data_by_username(db: AsyncSession, username: str):
    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalars().first()
    videos_result = await db.execute(select(Video).where(Video.owner_id == user.id))
    videos = videos_result.scalars().all()
    data = {}

    if user:
        data["user"] = {"id": user.id, "username": user.username}
    if videos:
        data["videos"] = videos

    if user or videos:
        return data
    return {"error": "no data"}

async def get_video_data_by_id(db: AsyncSession, video_id: int):
    result = await db.execute(
        select(Video)
        .where(Video.id == video_id)
        .options(
            selectinload(Video.owner),
        )
    )
    video = result.scalars().first()

    if video:
        return {
            "title": video.title,
            "description": video.description,
            "owner_id": video.owner.id,
            "owner_username": video.owner.username,
        }

    return {"Error": "No data"}

async def comment(db: AsyncSession, user_id: int, video_id: int, content: str):

    new_comment = Comment(owner_id=user_id, video_id=video_id, content=content, date=datetime.now())
    
    db.add(new_comment)
    await db.commit()

    return {"Success": "OK"}

async def get_comments_by_likes(db: AsyncSession, user_id: int, video_id: int, offeset_value: int):
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.owner))
        .where(Comment.video_id == video_id)
        .order_by(desc(Comment.likes))
        .offset(offeset_value)
        .limit(30)
        )
    comments = result.scalars().all()
    comments_data = []
    for comment in comments:
        result = await db.execute(select(user_comment_favorites)
            .where(
                and_(
                    user_comment_favorites.c.user_id == user_id,
                    user_comment_favorites.c.comment_id == comment.id
                )
            )
        )
        result_obj = result.fetchone()
        liked = True if result_obj else False
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "likes": comment.likes,
            "dislikes": comment.dislikes,
            "owner_id": comment.owner.id,
            "owner_username": comment.owner.username,
            "date": comment.date,
            "liked": liked
        })
    
    return {"comments": comments_data}

async def get_comments_by_recent(db: AsyncSession, user_id: int, video_id: int, offeset_value: int):
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.owner))
        .where(Comment.video_id == video_id)
        .order_by(desc(Comment.id))
        .offset(offeset_value)
        .limit(30)
        )
    comments = result.scalars().all()
    comments_data = []
    for comment in comments:
        result = await db.execute(select(user_comment_favorites)
            .where(
                and_(
                    user_comment_favorites.c.user_id == user_id,
                    user_comment_favorites.c.comment_id == comment.id
                )
            )
        )
        result_obj = result.fetchone()
        liked = True if result_obj else False
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "likes": comment.likes,
            "dislikes": comment.dislikes,
            "owner_id": comment.owner.id,
            "owner_username": comment.owner.username,
            "date": comment.date,
            "liked": liked
        })
    
    return {"comments": comments_data}

async def get_comments_by_old(db: AsyncSession, user_id: int, video_id: int, offeset_value: int):
    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.owner))
        .where(Comment.video_id == video_id)
        .order_by(asc(Comment.id))
        .offset(offeset_value)
        .limit(30)
        )
    comments = result.scalars().all()
    comments_data = []
    for comment in comments:
        result = await db.execute(select(user_comment_favorites)
            .where(
                and_(
                    user_comment_favorites.c.user_id == user_id,
                    user_comment_favorites.c.comment_id == comment.id
                )
            )
        )
        result_obj = result.fetchone()
        liked = True if result_obj else False
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "likes": comment.likes,
            "dislikes": comment.dislikes,
            "owner_id": comment.owner.id,
            "owner_username": comment.owner.username,
            "date": comment.date,
            "liked": liked
        })
    
    return {"comments": comments_data}


async def like_unlike(db: AsyncSession, user_id: int, comment_id: int):
    result = await db.execute(
        select(user_comment_favorites).where(
            and_(
                user_comment_favorites.c.user_id == user_id,
                user_comment_favorites.c.comment_id == comment_id
            )
        )
    )
    comment = result.fetchone()

    if comment:
        await db.execute(delete(user_comment_favorites).where(
            user_comment_favorites.c.user_id == user_id,
            user_comment_favorites.c.comment_id == comment_id
        ))
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(likes=Comment.likes - 1)
        )
        await db.commit()
        return False
    else:
        await db.execute(insert(user_comment_favorites).values(
            user_id=user_id,
            comment_id=comment_id
        ))
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(likes=Comment.likes + 1)
        )
        await db.commit()
        return True
    
