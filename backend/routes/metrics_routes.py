from fastapi import APIRouter, Depends, Query
from typing import List
from datetime import datetime, timedelta
from models.metrics import DashboardMetrics, PayerMetrics, CategoryMetrics, TrendMetrics
from routes.auth_routes import get_current_user
from utils.db_utils import denials_collection

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(user=Depends(get_current_user)):
    """Get dashboard summary metrics."""
    all_denials = await denials_collection.find({}).to_list(10000)

    # Calculate metrics
    open_denials = [d for d in all_denials if d.get("status") in ["pending", "in_review", "appeal_ready"]]
    total_at_risk = sum(d.get("denied_amount", 0) for d in open_denials)
    total_denied_amount = sum(d.get("denied_amount", 0) for d in all_denials)

    # Urgent appeals (deadline within 7 days)
    now = datetime.utcnow()
    urgent_count = 0
    for d in open_denials:
        deadline = d.get("appeal_deadline")
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline.replace("Z", ""))
                days_until = (deadline_dt - now).days
                if days_until <= 7:
                    urgent_count += 1
            except:
                pass

    # High probability (win_probability >= 70)
    high_prob_count = sum(1 for d in open_denials if (d.get("win_probability") or 0) >= 70)

    # This month recoveries
    this_month_start = datetime(now.year, now.month, 1)
    approved_this_month = [
        d for d in all_denials
        if d.get("status") == "approved" and d.get("updated_at") >= this_month_start
    ]
    recovered_this_month = sum(d.get("denied_amount", 0) for d in approved_this_month)

    submitted_this_month = [
        d for d in all_denials
        if d.get("status") in ["approved", "denied"] and d.get("updated_at") >= this_month_start
    ]
    recovery_rate_this_month = 0
    if submitted_this_month:
        recovery_rate_this_month = int((len(approved_this_month) / len(submitted_this_month)) * 100)

    # YTD recoveries
    ytd_start = datetime(now.year, 1, 1)
    approved_ytd = [
        d for d in all_denials
        if d.get("status") == "approved" and d.get("updated_at") >= ytd_start
    ]
    total_recovered_ytd = sum(d.get("denied_amount", 0) for d in approved_ytd)

    return DashboardMetrics(
        total_open_denials=len(open_denials),
        total_at_risk=total_at_risk,
        total_denied_amount=total_denied_amount,
        urgent_appeals=urgent_count,
        high_probability_count=high_prob_count,
        recovered_this_month=recovered_this_month,
        recovery_rate_this_month=recovery_rate_this_month,
        total_recovered_ytd=total_recovered_ytd,
        total_claims_recovered=len(approved_ytd)
    )

@router.get("/by-payer", response_model=List[PayerMetrics])
async def get_metrics_by_payer(user=Depends(get_current_user)):
    """Get success rate by payer."""
    all_denials = await denials_collection.find({}).to_list(10000)

    # Group by payer
    payer_stats = {}
    for denial in all_denials:
        payer = denial.get("payer_name", "Unknown")
        if payer not in payer_stats:
            payer_stats[payer] = {
                "total_denials": 0,
                "appeals_submitted": 0,
                "appeals_won": 0,
                "recovered_amount": 0.0
            }

        payer_stats[payer]["total_denials"] += 1

        status = denial.get("status")
        if status in ["submitted", "approved", "denied"]:
            payer_stats[payer]["appeals_submitted"] += 1

        if status == "approved":
            payer_stats[payer]["appeals_won"] += 1
            payer_stats[payer]["recovered_amount"] += denial.get("denied_amount", 0)

    # Convert to response format
    result = []
    for payer_name, stats in payer_stats.items():
        success_rate = 0
        if stats["appeals_submitted"] > 0:
            success_rate = int((stats["appeals_won"] / stats["appeals_submitted"]) * 100)

        result.append(PayerMetrics(
            payer_name=payer_name,
            total_denials=stats["total_denials"],
            appeals_submitted=stats["appeals_submitted"],
            appeals_won=stats["appeals_won"],
            success_rate=success_rate,
            recovered_amount=stats["recovered_amount"]
        ))

    return sorted(result, key=lambda x: x.recovered_amount, reverse=True)

@router.get("/by-category", response_model=List[CategoryMetrics])
async def get_metrics_by_category(user=Depends(get_current_user)):
    """Get performance by denial category."""
    all_denials = await denials_collection.find({}).to_list(10000)

    # Group by category
    category_stats = {}
    for denial in all_denials:
        category = denial.get("denial_category", "Other")
        if category not in category_stats:
            category_stats[category] = {
                "total_denials": 0,
                "appeals_submitted": 0,
                "appeals_won": 0,
                "recovered_amount": 0.0
            }

        category_stats[category]["total_denials"] += 1

        status = denial.get("status")
        if status in ["submitted", "approved", "denied"]:
            category_stats[category]["appeals_submitted"] += 1

        if status == "approved":
            category_stats[category]["appeals_won"] += 1
            category_stats[category]["recovered_amount"] += denial.get("denied_amount", 0)

    # Convert to response format
    result = []
    for category, stats in category_stats.items():
        success_rate = 0
        if stats["appeals_submitted"] > 0:
            success_rate = int((stats["appeals_won"] / stats["appeals_submitted"]) * 100)

        result.append(CategoryMetrics(
            category=category,
            total_denials=stats["total_denials"],
            appeals_submitted=stats["appeals_submitted"],
            appeals_won=stats["appeals_won"],
            success_rate=success_rate,
            recovered_amount=stats["recovered_amount"]
        ))

    return sorted(result, key=lambda x: x.recovered_amount, reverse=True)

@router.get("/trends", response_model=List[TrendMetrics])
async def get_trends(months: int = Query(default=12), user=Depends(get_current_user)):
    """Get recovery trends over time."""
    all_denials = await denials_collection.find({}).to_list(10000)

    # Calculate trends
    now = datetime.utcnow()
    trends = {}

    for i in range(months):
        month_start = datetime(now.year, now.month, 1) - timedelta(days=30 * i)
        month_key = month_start.strftime("%Y-%m")

        trends[month_key] = {
            "recovered_amount": 0.0,
            "submitted_appeals": 0,
            "won_appeals": 0
        }

    for denial in all_denials:
        updated_at = denial.get("updated_at")
        if not updated_at:
            continue

        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace("Z", ""))
            except:
                continue

        month_key = updated_at.strftime("%Y-%m")
        if month_key not in trends:
            continue

        status = denial.get("status")
        if status in ["submitted", "approved", "denied"]:
            trends[month_key]["submitted_appeals"] += 1

        if status == "approved":
            trends[month_key]["won_appeals"] += 1
            trends[month_key]["recovered_amount"] += denial.get("denied_amount", 0)

    # Convert to response format
    result = []
    for month, stats in sorted(trends.items()):
        success_rate = 0
        if stats["submitted_appeals"] > 0:
            success_rate = int((stats["won_appeals"] / stats["submitted_appeals"]) * 100)

        result.append(TrendMetrics(
            month=month,
            recovered_amount=stats["recovered_amount"],
            submitted_appeals=stats["submitted_appeals"],
            won_appeals=stats["won_appeals"],
            success_rate=success_rate
        ))

    return result
