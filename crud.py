from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc, or_, asc, insert, delete, update
from sqlalchemy.orm import selectinload
from models import User, Video, Comment, user_comment_favorites, user_comment_hated, user_video_favorites, user_video_hated, user_subscriptions
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

async def get_profile_data_by_username(db: AsyncSession, user_id: int, username: str):
    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalars().first()

    if not user:
        return {"error": "User not found"}

    videos_result = await db.execute(select(Video).where(Video.owner_id == user.id))
    videos = videos_result.scalars().all()

    subscription_result = await db.execute(select(user_subscriptions).where(
        and_(
            user_subscriptions.c.user_id == user_id,
            user_subscriptions.c.channel_id == user.id
        )
    ))
    subscription = subscription_result.fetchone()

    subscribed = bool(subscription)

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "subscribers": user.subscribers_count,
            "subscribed": subscribed
        },
        "videos": videos
    }


async def get_video_data_by_id(db: AsyncSession, video_id: int, user_id: int):
    result = await db.execute(
        select(Video)
        .where(Video.id == video_id)
        .options(
            selectinload(Video.owner),
        )
    )
    video = result.scalars().first()

    result = await db.execute(
        select(user_video_favorites).where(
            and_(
                user_video_favorites.c.user_id == user_id,
                user_video_favorites.c.video_id == video_id
            )
        )
    )
    video_liked = result.fetchone()
    liked = bool(video_liked)

    result = await db.execute(
        select(user_video_hated).where(
            and_(
                user_video_hated.c.user_id == user_id,
                user_video_hated.c.video_id == video_id
            )
        )
    )
    video_disliked = result.fetchone()
    disliked = bool(video_disliked)

    result = await db.execute(
        select(user_subscriptions).where(
            and_(
                user_subscriptions.c.user_id == user_id,
                user_subscriptions.c.channel_id == video.owner_id
            )
        )
    )

    subscription = result.fetchone()
    subscribed = bool(subscription)

    if video:
        return {
            "title": video.title,
            "description": video.description,
            "owner_id": video.owner.id,
            "owner_username": video.owner.username,
            "likes": video.likes,
            "dislikes": video.dislikes,
            "liked": liked,
            "disliked": disliked,
            "subscribed": subscribed
        }

    return {"Error": "No data"}

async def comment(db: AsyncSession, user_id: int, video_id: int, content: str):

    new_comment = Comment(owner_id=user_id, video_id=video_id, content=content, date=datetime.now())
    
    db.add(new_comment)
    await db.commit()

    return {"Success": "OK"}

async def get_comments(db: AsyncSession, user_id: int, video_id: int, offset_value: int, order_by="likes"):
    if order_by == "likes":
        ordering = desc(Comment.likes)
    elif order_by == "recent":
        ordering = desc(Comment.id)
    elif order_by == "old":
        ordering = asc(Comment.id)
    else:
        ordering = desc(Comment.likes)

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.owner))
        .where(Comment.video_id == video_id)
        .order_by(ordering)
        .offset(offset_value)
        .limit(30)
    )

    comments = result.scalars().all()
    comments_data = []

    for comment in comments:
        liked = bool(await check_if_liked_comment(db, user_id, comment.id))
        disliked = bool(await check_if_disliked_comment(db, user_id, comment.id))
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "likes": comment.likes,
            "dislikes": comment.dislikes,
            "owner_id": comment.owner.id,
            "owner_username": comment.owner.username,
            "date": comment.date,
            "liked": liked,
            "disliked": disliked
        })

    return {"comments": comments_data}


async def check_if_liked_comment(db: AsyncSession, user_id: int, comment_id: int):
    result = await db.execute(
    select(user_comment_favorites).where(
        and_(
            user_comment_favorites.c.user_id == user_id,
            user_comment_favorites.c.comment_id == comment_id
        )
    )
    )
    return result.fetchone()

async def check_if_disliked_comment(db: AsyncSession, user_id: int, comment_id: int):
    result = await db.execute(
    select(user_comment_hated).where(
        and_(
            user_comment_hated.c.user_id == user_id,
            user_comment_hated.c.comment_id == comment_id
        )
    )
    )
    return result.fetchone()

async def like_unlike_comment(db: AsyncSession, user_id: int, comment_id: int):

    comment_liked = await check_if_liked_comment(db=db, user_id=user_id, comment_id=comment_id)
    comment_disliked = await check_if_disliked_comment(db=db, user_id=user_id, comment_id=comment_id)

    if comment_liked:
        await db.execute(delete(user_comment_favorites).where(
            and_(
                user_comment_favorites.c.user_id == user_id,
                user_comment_favorites.c.comment_id == comment_id
            )
        ))
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(likes=Comment.likes - 1)
        )
        await db.commit()
        return False
    
    elif not comment_liked:
        await db.execute(insert(user_comment_favorites).values(
            user_id=user_id,
            comment_id=comment_id
        ))
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(likes=Comment.likes + 1)
        )

        if comment_disliked:
            await db.execute(delete(user_comment_hated).where(
                and_(
                    user_comment_hated.c.user_id == user_id,
                    user_comment_hated.c.comment_id == comment_id
                )
            ))

            await db.execute(update(Comment)
                .where(Comment.id == comment_id)
                .values(dislikes=Comment.dislikes - 1)
            )

        await db.commit()
        return True
    

async def dislike_undislike_comment(db: AsyncSession, user_id: int, comment_id: int):
    
    comment_disliked = await check_if_disliked_comment(db=db, user_id=user_id, comment_id=comment_id)
    comment_liked = await check_if_liked_comment(db=db, user_id=user_id, comment_id=comment_id)

    if comment_disliked:
        await db.execute(delete(user_comment_hated).where(
            and_(
                user_comment_hated.c.user_id == user_id,
                user_comment_hated.c.comment_id == comment_id
            )
        ))
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(dislikes=Comment.dislikes - 1)
        )
        await db.commit()
        return False
    
    elif not comment_disliked:
        await db.execute(insert(user_comment_hated).values(
            user_id=user_id,
            comment_id=comment_id
        ))
        await db.execute(
            update(Comment)
            .where(Comment.id == comment_id)
            .values(dislikes=Comment.dislikes + 1)
        )

        if comment_liked:
            await db.execute(delete(user_comment_favorites).where(
                and_(
                    user_comment_favorites.c.user_id == user_id,
                    user_comment_favorites.c.comment_id == comment_id
                )
            ))

            await db.execute(update(Comment)
                .where(Comment.id == comment_id)
                .values(likes=Comment.likes - 1)
            )

        await db.commit()
        return True


async def check_if_liked_video(db: AsyncSession, user_id: int, video_id: int):
    result = await db.execute(
    select(user_video_favorites).where(
        and_(
            user_video_favorites.c.user_id == user_id,
            user_video_favorites.c.video_id == video_id
        )
    )
    )
    return result.fetchone()

async def check_if_disliked_video(db: AsyncSession, user_id: int, video_id: int):
    result = await db.execute(
    select(user_video_hated).where(
        and_(
            user_video_hated.c.user_id == user_id,
            user_video_hated.c.video_id == video_id
        )
    )
    )
    return result.fetchone()

async def like_unlike_video(db: AsyncSession, user_id: int, video_id: int):

    video_liked = await check_if_liked_video(db=db, user_id=user_id, video_id=video_id)
    video_disliked = await check_if_disliked_video(db=db, user_id=user_id, video_id = video_id)

    if video_liked:
        await db.execute(
            delete(user_video_favorites).where(
                and_(
                    user_video_favorites.c.user_id == user_id,
                    user_video_favorites.c.video_id == video_id
                )
            )
        )
        await db.execute(update(Video)
            .where(Video.id == video_id)
            .values(likes=Video.likes - 1)
        )
        await db.commit()
        return False
    
    elif not video_liked:
        await db.execute(insert(user_video_favorites)
            .values(
                user_id=user_id,
                video_id=video_id
            )
        )
        await db.execute(update(Video)
            .where(Video.id == video_id)
            .values(likes=Video.likes + 1)
        )

        if video_disliked:
            await db.execute(delete(user_video_hated).where(
                and_(
                    user_video_hated.c.user_id == user_id,
                    user_video_hated.c.video_id == video_id
                )
            ))
            await db.execute(update(Video)
                .where(Video.id == video_id)
                .values(dislikes=Video.dislikes - 1)
            )

        await db.commit()
        return True
    

async def dislike_undislike_video(db: AsyncSession, user_id: int, video_id: int):

    video_disliked = await check_if_disliked_video(db=db, user_id=user_id, video_id = video_id)
    video_liked = await check_if_liked_video(db=db, user_id=user_id, video_id=video_id)
    
    if video_disliked:
        await db.execute(
            delete(user_video_hated).where(
                and_(
                    user_video_hated.c.user_id == user_id,
                    user_video_hated.c.video_id == video_id
                )
            )
        )
        await db.execute(update(Video)
            .where(Video.id == video_id)
            .values(dislikes=Video.dislikes - 1)
        )
        await db.commit()
        return False
    
    elif not video_disliked:
        await db.execute(insert(user_video_hated)
            .values(
                user_id=user_id,
                video_id=video_id
            )
        )
        await db.execute(update(Video)
            .where(Video.id == video_id)
            .values(dislikes=Video.dislikes + 1)
        )

        if video_liked:
            await db.execute(delete(user_video_favorites).where(
                and_(
                    user_video_favorites.c.user_id == user_id,
                    user_video_favorites.c.video_id == video_id
                )
            ))
            await db.execute(update(Video)
                .where(Video.id == video_id)
                .values(likes=Video.likes - 1)
            )

        await db.commit()
        return True
    

async def subscribe_by_video(db: AsyncSession, user_id: int, video_id: int):
    
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()

    if not video:
        return {"Error": "Video/Channel not found"}
    
    video_owner_id = video.owner_id

    if video_owner_id == user_id:
        return {"Error": "You cant subscribe yourself"}

    result = await db.execute(select(user_subscriptions)
        .where(and_(
            user_subscriptions.c.user_id == user_id,
            user_subscriptions.c.channel_id == video_owner_id
        ))
    )
    
    subscription = result.fetchone()

    if subscription:
        await db.execute(delete(user_subscriptions)
            .where(and_(
                user_subscriptions.c.user_id == user_id,
                user_subscriptions.c.channel_id == video_owner_id
            ))
        )

        await db.execute(update(User).where(User.id == video_owner_id)
            .values(subscribers_count=User.subscribers_count - 1)
        )

        await db.commit()
        return {"Success": "Dessubscribed successfully"}

    await db.execute(insert(user_subscriptions)
        .values(user_id=user_id, channel_id=video_owner_id)
    )

    await db.execute(update(User).where(User.id == video_owner_id)
        .values(subscribers_count=User.subscribers_count + 1)
    )

    await db.commit()

    return {"Success": "Subscribed successfully"}


async def subscribe_by_username(db: AsyncSession, user_id: int, username: str):
    print(user_id, username)

    result = await db.execute(select(User).where(User.username == username))
    channel = result.scalars().first()

    if not channel:
        return {"Error": "Channel not found"}

    channel_id = channel.id

    if user_id == channel_id:
        return {"Error": "You can't subscribe to yourself"}

    result = await db.execute(select(user_subscriptions)
        .where(and_(
            user_subscriptions.c.user_id == user_id,
            user_subscriptions.c.channel_id == channel_id
        ))
    )

    subscription = result.fetchone()

    if subscription:
        await db.execute(delete(user_subscriptions)
            .where(and_(
                user_subscriptions.c.user_id == user_id,
                user_subscriptions.c.channel_id == channel_id
            ))
        )

        await db.execute(update(User)
            .where(User.id == channel_id)
            .values(subscribers_count=User.subscribers_count - 1)
        )

        await db.commit()
        return {"Success": "Unsubscribed successfully"}

    await db.execute(insert(user_subscriptions)
        .values(user_id=user_id, channel_id=channel_id)
    )

    await db.execute(update(User)
        .where(User.id == channel_id)
        .values(subscribers_count=User.subscribers_count + 1)
    )

    await db.commit()
    return {"Success": "Subscribed successfully"}

async def upload_video(db: AsyncSession, user_id: int, title: str, description: str, video_extension: str, miniature_extension: str) -> Video:
    new_video = Video(title=title, description=description, video_extension=video_extension, miniature_extension=miniature_extension, owner_id=user_id)
    db.add(new_video)
    try:
        await db.commit()
        await db.refresh(new_video)
        return new_video
    except Exception as e:
        await db.rollback()
        raise e

async def get_miniature_extension_by_video_id(db: AsyncSession, video_id: int):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()

    if video:
        return video.miniature_extension
    return False