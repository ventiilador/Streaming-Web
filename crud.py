from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc, distinct, or_, asc, insert, delete, update
from sqlalchemy.orm import selectinload, joinedload
from models import FollowUp, Hashtag, User, UserPreference, Video, Comment, user_comment_favorites, user_comment_hated, user_video_favorites, user_video_hated, user_subscriptions, PrivateMessage
from auth import verify_password, hash_password
from datetime import datetime
from functions import pretty_date

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
    

    subscription_result = await db.execute(select(user_subscriptions).where(
    and_(
        user_subscriptions.c.user_id == user_id,
        user_subscriptions.c.channel_id == user.id
    )
    ))

    subscription = subscription_result.fetchone()

    subscribed = bool(subscription)

    followup_result = await db.execute(select(FollowUp).where(
        and_(
            FollowUp.followed_id == user.id,
            FollowUp.follower_id == user_id
        )
    ))
    followup = followup_result.scalars().first()
    followed_up = bool(followup)

    print(followed_up)
    if user.private_account and not subscribed and user_id != user.id:
        return {
        "user": {
                "id": user.id,
                "username": user.username,
                "subscribers": user.subscribers_count,
                "subscribed": subscribed,
                "followup": followed_up
            }
        }

    videos_result = await db.execute(select(Video).where(Video.owner_id == user.id))
    videos = videos_result.scalars().all()

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "subscribers": user.subscribers_count,
            "subscribed": subscribed,
            "followup": followed_up
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

    owner_result = await db.execute(select(User).where(User.id == video.owner_id))
    owner = owner_result.scalars().first()

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

    if owner.private_account and not subscribed and owner.id != user_id:
        return {"error": "you dont have access to this content"}
    
    await db.execute(update(Video).where(Video.id == video_id).values(views=video.views + 1))
    await db.commit()

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
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalars().first()

    owner_result = await db.execute(select(User).where(User.id == video.owner_id))
    owner = owner_result.scalars().first()

    result = await db.execute(select(user_subscriptions)
        .where(and_(
            user_subscriptions.c.user_id == user_id,
            user_subscriptions.c.channel_id == owner.id
        ))
    )

    subscription = result.fetchone()

    if owner.private_account and not subscription and user_id != owner.id:
        return {"error": "not allowed to comment"}

    new_comment = Comment(owner_id=user_id, video_id=video_id, content=content, date=datetime.now())
    
    db.add(new_comment)
    await db.commit()

    return {"Success": "OK"}

async def get_comments(db: AsyncSession, user_id: int, video_id: int, offset_value: int, order_by="likes"):

    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalars().first()

    owner_result = await db.execute(select(User).where(User.id == video.owner_id))
    owner = owner_result.scalars().first()

    result = await db.execute(select(user_subscriptions)
        .where(and_(
            user_subscriptions.c.user_id == user_id,
            user_subscriptions.c.channel_id == owner.id
        ))
    )

    subscription = result.fetchone()

    if owner.private_account and not subscription and user_id != owner.id:
        return {"error": "not allowed to see the comments"}

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
    
    channel_result = await db.execute(select(User).where(User.id == video_owner_id))
    channel = channel_result.scalars().first()

    follow_up_result = await db.execute(select(FollowUp).where(and_(FollowUp.follower_id==user_id, FollowUp.followed_id==video_owner_id)))
    follow_up = follow_up_result.scalars().first()

    if channel.private_account:
        if not follow_up:
            new_follow_up = FollowUp(follower_id=user_id, followed_id=video_owner_id, date=datetime.now())
            db.add(new_follow_up)
            await db.commit()
            await db.refresh(new_follow_up)
            return {"info": "Your follow up has been send"}
        else:
            return {"info": "Your follow up was already sent"}

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
    
    channel_result = await db.execute(select(User).where(User.id == channel_id))
    channel = channel_result.scalars().first()

    follow_up_result = await db.execute(select(FollowUp).where(and_(FollowUp.follower_id==user_id, FollowUp.followed_id==channel_id)))
    follow_up = follow_up_result.scalars().first()

    if channel.private_account:
        if not follow_up:
            new_follow_up = FollowUp(follower_id=user_id, followed_id=channel_id, date=datetime.now())
            db.add(new_follow_up)
            await db.commit()
            await db.refresh(new_follow_up)
            return {"info": "Your follow up has been send"}
        else:
            return {"info": "Your follow up was already sent"}

    await db.execute(insert(user_subscriptions)
        .values(user_id=user_id, channel_id=channel_id)
    )

    await db.execute(update(User)
        .where(User.id == channel_id)
        .values(subscribers_count=User.subscribers_count + 1)
    )

    await db.commit()
    return {"Success": "Subscribed successfully"}

async def upload_video(
    db: AsyncSession,
    user_id: int,
    title: str,
    description: str,
    video_extension: str,
    miniature_extension: str,
    hashtags: list[str] = None
) -> Video:
    hashtag_objs = []

    if hashtags:
        for tag_name in hashtags:
            stmt = select(Hashtag).where(Hashtag.name == tag_name)
            result = await db.execute(stmt)
            hashtag = result.scalar_one_or_none()

            if not hashtag:
                hashtag = Hashtag(name=tag_name)
                db.add(hashtag)
                await db.flush()

            hashtag_objs.append(hashtag)

    new_video = Video(
        title=title,
        description=description,
        video_extension=video_extension,
        miniature_extension=miniature_extension,
        owner_id=user_id,
        upload_date=datetime.now(),
        hashtags=hashtag_objs
    )

    db.add(new_video)
    await db.flush()

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

async def get_videos_by_user_id(db: AsyncSession, user_id: int):
    videos_result = await db.execute(select(Video).where(Video.owner_id == user_id))
    videos = videos_result.scalars().all()

    if videos:
        return {"videos": videos}
    return {"error": "No videos found"}

async def check_if_user_is_video_owner_by_id(db: AsyncSession, user_id: int, video_id: int):
    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalars().first()

    if video.owner_id == user_id:
        return True
    return False

async def edit_video(
    db: AsyncSession,
    user_id: int,
    video_id: int,
    title: str,
    description: str,
    miniature_extension: str,
    hashtags: list[str] = None,
):
    video_result = await db.execute(
        select(Video).where(Video.id == video_id).options(selectinload(Video.hashtags))
    )
    video = video_result.scalars().first()

    if not video or video.owner_id != user_id:
        return False

    update_data = {
        "title": title,
        "description": description,
    }
    if miniature_extension:
        update_data["miniature_extension"] = miniature_extension

    await db.execute(update(Video).where(Video.id == video_id).values(**update_data))

    if hashtags is not None:
        current_hashtags = {h.name: h for h in video.hashtags}

        new_tags = set(hashtags) - set(current_hashtags.keys())
        to_remove = set(current_hashtags.keys()) - set(hashtags)

        for tag_name in to_remove:
            hashtag_obj = current_hashtags[tag_name]
            video.hashtags.remove(hashtag_obj)

        for tag_name in new_tags:
            stmt = select(Hashtag).where(Hashtag.name == tag_name)
            result = await db.execute(stmt)
            hashtag_obj = result.scalar_one_or_none()

            if not hashtag_obj:
                hashtag_obj = Hashtag(name=tag_name)
                db.add(hashtag_obj)
                await db.flush()

            video.hashtags.append(hashtag_obj)

    await db.commit()
    return True


async def get_profile_data_by_id(db: AsyncSession, user_id: int):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()

    if user:
        return {"username": user.username, "biography": user.biography, "user_id": user.id}
    
    return {"error": "user not found"}

async def update_profile_by_id(db: AsyncSession, user_id: int, username: str, biography: str, profile_extension: str):
    result = await db.execute(select(User).where(User.username == username))
    user_with_same_username = result.scalars().first()

    if not user_with_same_username:
        await db.execute(update(User).where(User.id == user_id).values(username=username))

    await db.execute(update(User).where(User.id == user_id).values(biography=biography))

    if profile_extension:
        await db.execute(update(User).where(User.id == user_id).values(profile_extension=profile_extension))

    await db.commit()
    return {"success": "profile updated successfully"}

async def get_user_profile_extension(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    return user.profile_extension

async def search_videos(db: AsyncSession, search: str, filter: str, offset: int, limit: int = 20):
    search_pattern = f"%{search}%"

    query = (
        select(Video)
        .join(Video.hashtags, isouter=True)
        .where(
            or_(
                Video.title.ilike(search_pattern),
                Video.description.ilike(search_pattern),
                Hashtag.name.ilike(search_pattern)
            )
        )
        .distinct()
        .options(selectinload(Video.owner))
    )

    if filter == "recent":
        query = query.order_by(desc(Video.upload_date))
    elif filter == "oldest":
        query = query.order_by(asc(Video.upload_date))
    elif filter == "popular":
        query = query.order_by(desc(Video.views))
    elif filter == "relevance":
        query = query.order_by(desc(Video.likes))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    videos = result.scalars().all()

    return [
        {
            "id": video.id,
            "title": video.title,
            "views": video.views,
            "upload_date": pretty_date(video.upload_date.isoformat()),
            "owner": video.owner.username,
        }
        for video in videos
        if not video.owner.private_account
    ]


async def search_channels(db: AsyncSession, search: str, filter: str, offset: int, limit: int = 20):
    query = select(User).where(User.username.ilike(f"%{search}%"))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    channels = result.scalars().all()

    return channels

async def change_password(db: AsyncSession, user_id: int, current_password: str, new_password: str):

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()

    if not user:
        return {"error": "user not found"}
    
    if not verify_password(current_password, user.password_hash):
        return {"error": "current password is not correct"}
    
    new_password_hashed = hash_password(new_password)
    await db.execute(update(User).where(User.id == user_id).values(password_hash=new_password_hashed))
    await db.commit()
    return {"success": "Password changed successfully"}

async def check_account_privacity_by_id(db: AsyncSession, user_id: int):

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()

    if user:
        return {"privacity": user.private_account}
    
    return {"error": "User not found"}

async def change_privacity_settings_by_id(db: AsyncSession, user_id: int, private_account: bool):
    await db.execute(update(User).where(User.id == user_id).values(private_account=private_account))
    await db.commit()
    return {"success":"Privacity changed successfully"}

async def stream_video_permission(db: AsyncSession, user_id: int, video_id: int):

    video_result = await db.execute(select(Video).where(Video.id == video_id))
    video = video_result.scalars().first()

    owner_result = await db.execute(select(User).where(User.id == video.owner_id))
    owner = owner_result.scalars().first()

    if not owner.private_account:
        return True

    result = await db.execute(select(user_subscriptions)
        .where(and_(
            user_subscriptions.c.user_id == user_id,
            user_subscriptions.c.channel_id == owner.id
        ))
    )

    subscription = result.fetchone()

    if subscription or user_id == owner.id:
        return True

async def adjust_user_preferences_for_video(
    db: AsyncSession,
    user_id: int,
    video_id: int,
    liked: bool = False,
    view_weight: float = 0.1,
    like_weight: float = 0.5
):

    result = await db.execute(
        select(Hashtag).join(Hashtag.videos).where(Video.id == video_id)
    )
    hashtags = result.scalars().all()

    for hashtag in hashtags:
        stmt = select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.hashtag_id == hashtag.id
        )
        pref_result = await db.execute(stmt)
        preference = pref_result.scalar_one_or_none()

        increment = view_weight + (like_weight if liked else 0)

        if preference:
            preference.weight += increment
        else:
            preference = UserPreference(
                user_id=user_id,
                hashtag_id=hashtag.id,
                weight=increment
            )
            db.add(preference)

    await db.commit()

async def get_user_preferences(db: AsyncSession, user_id: int) -> List[UserPreference]:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id).order_by(UserPreference.weight.desc())
    )
    return result.scalars().all()

async def get_videos_by_hashtag(db, hashtag_id: int, limit: int, offset: int):
    result = await db.execute(
        select(Video)
        .join(Video.hashtags)
        .options(selectinload(Video.owner))
        .where(Hashtag.id == hashtag_id)
        .offset(offset)
        .limit(limit)
        .order_by(Video.upload_date.desc())
    )
    videos = result.scalars().all()

    return [
        {
            "id": v.id,
            "title": v.title,
            "upload_date": pretty_date(v.upload_date),
            "views": v.views,
            "owner": v.owner.username if v.owner else "Unknown"
        }
        for v in videos
        if v.owner and not v.owner.private_account
    ]


async def get_default_videos(db: AsyncSession, offset: int, limit: int) -> List[Dict[str, Any]]:
    stmt = (
        select(Video)
        .options(selectinload(Video.owner))
        .offset(offset)
        .limit(limit)
        .order_by(Video.upload_date.desc())
    )
    result = await db.execute(stmt)
    videos = result.scalars().all()

    return [
        {
            "id": v.id,
            "title": v.title,
            "description": v.description,
            "owner": v.owner.username if v.owner else "Unknown",
            "views": v.views,
            "upload_date": pretty_date(v.upload_date)
        }
        for v in videos
        if v.owner and not v.owner.private_account
    ]



async def delete_account(db: AsyncSession, user_id: int):
    try:
        await db.execute(delete(user_video_favorites).where(user_video_favorites.c.user_id == user_id))
        await db.execute(delete(user_video_hated).where(user_video_hated.c.user_id == user_id))
        await db.execute(delete(user_comment_favorites).where(user_comment_favorites.c.user_id == user_id))
        await db.execute(delete(user_comment_hated).where(user_comment_hated.c.user_id == user_id))

        await db.execute(delete(user_subscriptions).where(user_subscriptions.c.user_id == user_id))
        await db.execute(delete(user_subscriptions).where(user_subscriptions.c.channel_id == user_id))

        await db.execute(delete(UserPreference).where(UserPreference.user_id == user_id))

        user = await db.get(User, user_id)
        if user:
            await db.delete(user)

        await db.commit()
        return {"success": "Account and related data deleted successfully"}

    except Exception as e:
        await db.rollback()
        print("Error deleting account:", e)
        return {"error": "Failed to delete account"}


async def mail_data(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(FollowUp)
        .options(joinedload(FollowUp.follower))
        .where(FollowUp.followed_id == user_id)
        .order_by(desc(FollowUp.date))
    )
    follow_ups = result.scalars().all()

    return {
        "follow_ups": [
            {
                "id": f.id,
                "follower_id": f.follower_id,
                "follower_username": f.follower.username,
                "date": pretty_date(f.date)
            }
            for f in follow_ups
        ]
    }


async def accept_followup(db: AsyncSession, user_id: int, followup_id: int, follower_id: int):

    await db.execute(delete(FollowUp).where(FollowUp.id == followup_id))

    await db.execute(insert(user_subscriptions)
        .values(user_id=follower_id, channel_id=user_id)
    )

    await db.execute(update(User)
        .where(User.id == user_id)
        .values(subscribers_count=User.subscribers_count + 1)
    )
    await db.commit()
    return {"success": "The followup has been accepted successfully"}

async def deny_followup(db: AsyncSession, user_id: int, followup_id: int):

    await db.execute(delete(FollowUp).where(FollowUp.id == followup_id))
    await db.commit()
    return {"success": "The followup has been denied successfully"}


async def get_contacts(db: AsyncSession, user_id: int):

    subscription_results = await db.execute(select(user_subscriptions).where(user_subscriptions.c.user_id == user_id))
    subscriptions = subscription_results.all()

    contacts = []

    for sub in subscriptions:
        subscription_result = await db.execute(select(user_subscriptions).where(user_subscriptions.c.user_id == sub[1]))
        subscription = subscription_result.scalars().first()

        if subscription:
            contact_result = await db.execute(select(User).where(User.id == subscription))
            contact = contact_result.scalars().first()
            contacts.append(contact)

    return {
        "contacts" : [
            {
                "id": contact.id,
                "username": contact.username,
            }
            for contact in contacts
        ]
    }


async def check_chat_permission(db: AsyncSession, user_id: int, destination_id: int):

    first_subscription_result = await db.execute(select(user_subscriptions).where(and_(user_subscriptions.c.user_id == user_id, user_subscriptions.c.channel_id == destination_id)))
    first_subscription = first_subscription_result.first()

    second_subscription_result = await db.execute(select(user_subscriptions).where(and_(user_subscriptions.c.user_id == destination_id, user_subscriptions.c.channel_id == user_id)))
    second_subscription = second_subscription_result.first()

    if first_subscription and second_subscription:
        return True
    
    return False


async def get_chat_data(db: AsyncSession, user_id: int, destination_id: int, offset: int):
    
    messages_result = await db.execute(
        select(PrivateMessage)
        .where(
            and_(
                or_(
                    PrivateMessage.recipient_id == user_id,
                    PrivateMessage.recipient_id == destination_id
                ),
                or_(
                    PrivateMessage.sender_id == user_id,
                    PrivateMessage.sender_id == destination_id
                )
            )
        )
        .order_by(desc(PrivateMessage.date))
        .offset(offset)
        .limit(30)
    )
    messages = messages_result.scalars().all()

    return {
        "messages" : [
            {
                "content": message.content,
                "date": pretty_date(message.date),
                "self": user_id == message.sender_id
            }
        for message in messages
        ]
    }

async def send_message(db: AsyncSession, user_id: int, destination_id: int, content: str):

    new_message = PrivateMessage(content=content, date=datetime.now(), sender_id=user_id, recipient_id=destination_id)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

async def get_contact_data(db: AsyncSession, contact_id: int):

    contact_result = await db.execute(select(User).where(User.id == contact_id))
    contact = contact_result.scalars().first()

    if contact:
        return {
            "username": contact.username,
            "active": pretty_date(contact.last_time_active)
        }
    
    return {"error": "We couldnt find your contact"}


async def set_presence(db: AsyncSession, user_id: int, status):

    await db.execute(update(User).where(User.id == user_id).values(online=status, last_time_active=datetime.now()))
    await db.commit()

async def get_contact_ids_list(db: AsyncSession, user_id: int):

    subscription_results = await db.execute(select(user_subscriptions).where(user_subscriptions.c.user_id == user_id))
    subscriptions = subscription_results.all()

    contacts = []

    for sub in subscriptions:
        subscription_result = await db.execute(select(user_subscriptions).where(user_subscriptions.c.user_id == sub[1]))
        subscription = subscription_result.scalars().first()

        if subscription:
            contact_result = await db.execute(select(User).where(User.id == subscription))
            contact = contact_result.scalars().first()
            contacts.append(contact)
    
    return [
        contact.id
        for contact in contacts
    ]