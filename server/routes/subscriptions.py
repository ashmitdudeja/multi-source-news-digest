from fastapi import APIRouter, HTTPException, Request
from server.database import insert_subscription, get_subscriptions_by_email, delete_subscription
from server.middleware.rate_limiter import limiter
from server.models import SubscriptionRequest, SubscriptionResponse, MessageResponse

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])


@router.post("", summary="Subscribe to a topic")
@limiter.limit("10/15minutes")
async def subscribe(request: Request, body: SubscriptionRequest):
    """Subscribe an email to receive updates about a specific topic."""
    try:
        sub_id = await insert_subscription(body.email, body.topic)
        return {
            "success": True,
            "data": {
                "id": sub_id,
                "email": body.email,
                "topic": body.topic,
            },
            "message": f"Subscribed to '{body.topic}' successfully",
        }
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=409, detail="Already subscribed to this topic")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{email}", summary="Get subscriptions for an email")
@limiter.limit("100/15minutes")
async def get_subscriptions(request: Request, email: str):
    """Get all topic subscriptions for a given email."""
    subs = await get_subscriptions_by_email(email)
    return {"success": True, "data": subs}


@router.delete("/{sub_id}", summary="Unsubscribe")
@limiter.limit("10/15minutes")
async def unsubscribe(request: Request, sub_id: int):
    """Remove a topic subscription by its ID."""
    await delete_subscription(sub_id)
    return {"success": True, "message": "Unsubscribed successfully"}
