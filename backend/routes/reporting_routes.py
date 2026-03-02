from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict

from models.reporting import (
    ExecutiveSummaryResponse,
    DenialAnalysisResponse,
    OverturnRatesResponse,
    PatternIntelligenceResponse,
    OperationalKPIsResponse,
    PracticeScorecardResponse,
    DenialTypeSplit,
    CodeBreakdown,
    MonthlyVolume,
    MonthlyRecovery,
    TopItem,
    ProcedureCodeRow,
    DiagnosisCodeRow,
    OverturnRow,
    MonthlyOverturn,
    PreventabilityMonth,
    RecurringPattern,
    PracticeInsight,
    PayerBehavior,
)
from routes.auth_routes import get_current_user
from utils.db_utils import denials_collection

router = APIRouter(prefix="/api/reporting", tags=["Reporting"])

ADMIN_CATEGORIES = {"Prior Authorization", "Coding Error"}
CLINICAL_CATEGORIES = {"Medical Necessity", "Documentation"}
HIGH_PREVENTABLE = {"Coding Error", "Prior Authorization"}
MEDIUM_PREVENTABLE = {"Documentation"}


def _classify_type(category: str) -> str:
    if category in ADMIN_CATEGORIES:
        return "administrative"
    if category in CLINICAL_CATEGORIES:
        return "clinical"
    return "other"


def _classify_preventability(category: str) -> str:
    if category in HIGH_PREVENTABLE:
        return "high"
    if category in MEDIUM_PREVENTABLE:
        return "medium"
    return "low"


def _parse_dt(val) -> Optional[datetime]:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(str(val).replace("Z", ""))
    except Exception:
        return None


DENIAL_CODE_DESCRIPTIONS = {
    "CO-4": "Procedure code inconsistent with modifier or missing modifier",
    "CO-11": "Diagnosis inconsistent with procedure",
    "CO-16": "Claim lacks information or has submission errors",
    "CO-18": "Duplicate claim/service",
    "CO-22": "Care may be covered by another payer",
    "CO-29": "Time limit for filing has expired",
    "CO-45": "Charges exceed fee schedule or contracted amount",
    "CO-50": "Non-covered service",
    "CO-96": "Non-covered charge(s)",
    "CO-97": "Payment adjusted - already adjudicated",
    "CO-109": "Claim not covered by this payer",
    "CO-150": "Not eligible for this payer",
    "CO-167": "Diagnosis is not covered",
    "CO-197": "Precertification/authorization/notification absent",
    "CO-204": "Service not covered when performed by this provider",
    "CO-222": "Exceeds number of services allowed",
    "CO-236": "Procedure/service not paid separately",
    "PR-1": "Deductible amount",
    "PR-2": "Coinsurance amount",
    "PR-3": "Co-payment amount",
}


async def _get_filtered_denials(
    date_from: Optional[str],
    date_to: Optional[str],
    payers: Optional[str],
    practices: Optional[str],
    categories: Optional[str],
    denial_type: Optional[str],
) -> list:
    query = {}

    if date_from or date_to:
        date_filter = {}
        if date_from:
            date_filter["$gte"] = date_from
        if date_to:
            date_filter["$lte"] = date_to
        query["denial_date"] = date_filter

    if payers:
        payer_list = [p.strip() for p in payers.split(",") if p.strip()]
        if payer_list:
            query["payer_name"] = {"$in": payer_list}

    if practices:
        practice_list = [p.strip() for p in practices.split(",") if p.strip()]
        if practice_list:
            query["provider_practice_name"] = {"$in": practice_list}

    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
        if cat_list:
            query["denial_category"] = {"$in": cat_list}

    denials = await denials_collection.find(query).to_list(50000)

    if denial_type and denial_type != "all":
        denials = [d for d in denials if _classify_type(d.get("denial_category", "")) == denial_type]

    return denials


# ── Executive Summary ──────────────────────────────────────────


@router.get("/executive-summary", response_model=ExecutiveSummaryResponse)
async def get_executive_summary(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    payers: Optional[str] = Query(None),
    practices: Optional[str] = Query(None),
    categories: Optional[str] = Query(None),
    denial_type: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    denials = await _get_filtered_denials(date_from, date_to, payers, practices, categories, denial_type)

    total = len(denials)
    submitted = [d for d in denials if d.get("status") in ("submitted", "approved", "denied")]
    approved = [d for d in denials if d.get("status") == "approved"]

    overturn_rate = (len(approved) / len(submitted) * 100) if submitted else 0
    total_recovered = sum(d.get("denied_amount", 0) for d in approved)

    resolution_days_list = []
    for d in denials:
        if d.get("status") in ("approved", "denied"):
            denial_dt = _parse_dt(d.get("denial_date"))
            updated_dt = _parse_dt(d.get("updated_at"))
            if denial_dt and updated_dt:
                delta = (updated_dt - denial_dt).days
                if delta >= 0:
                    resolution_days_list.append(delta)
    avg_resolution = (sum(resolution_days_list) / len(resolution_days_list)) if resolution_days_list else None

    preventable_count = sum(1 for d in denials if _classify_preventability(d.get("denial_category", "")) in ("high", "medium"))
    preventable_rate = (preventable_count / total * 100) if total else 0

    monthly_buckets: dict[str, dict] = defaultdict(lambda: {"administrative": 0, "clinical": 0, "other": 0})
    recovery_buckets: dict[str, float] = defaultdict(float)
    code_counter: Counter = Counter()
    payer_counter: Counter = Counter()

    for d in denials:
        dd = _parse_dt(d.get("denial_date")) or _parse_dt(d.get("created_at"))
        if dd:
            mk = dd.strftime("%Y-%m")
            dtype = _classify_type(d.get("denial_category", ""))
            monthly_buckets[mk][dtype] += 1

        if d.get("status") == "approved":
            upd = _parse_dt(d.get("updated_at"))
            if upd:
                recovery_buckets[upd.strftime("%Y-%m")] += d.get("denied_amount", 0)

        dc = d.get("denial_code")
        if dc:
            code_counter[dc] += 1

        pn = d.get("payer_name")
        if pn:
            payer_counter[pn] += 1

    volume_trend = sorted(
        [MonthlyVolume(month=m, **v) for m, v in monthly_buckets.items()],
        key=lambda x: x.month,
    )
    recovery_trend = sorted(
        [MonthlyRecovery(month=m, recovered_amount=v) for m, v in recovery_buckets.items()],
        key=lambda x: x.month,
    )
    top_codes = [TopItem(name=c, count=n) for c, n in code_counter.most_common(5)]
    top_payers = [TopItem(name=c, count=n) for c, n in payer_counter.most_common(5)]

    return ExecutiveSummaryResponse(
        total_denials=total,
        overall_overturn_rate=round(overturn_rate, 1),
        total_recovered=total_recovered,
        avg_resolution_days=round(avg_resolution, 1) if avg_resolution is not None else None,
        preventable_rate=round(preventable_rate, 1),
        volume_trend=volume_trend,
        recovery_trend=recovery_trend,
        top_denial_codes=top_codes,
        top_payers=top_payers,
    )


# ── Denial Analysis ────────────────────────────────────────────


@router.get("/denial-analysis", response_model=DenialAnalysisResponse)
async def get_denial_analysis(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    payers: Optional[str] = Query(None),
    practices: Optional[str] = Query(None),
    categories: Optional[str] = Query(None),
    denial_type: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    denials = await _get_filtered_denials(date_from, date_to, payers, practices, categories, denial_type)

    buckets: dict[str, list] = {"administrative": [], "clinical": [], "other": []}
    for d in denials:
        buckets[_classify_type(d.get("denial_category", ""))].append(d)

    def _make_split(label: str, items: list) -> DenialTypeSplit:
        total_denied = sum(i.get("denied_amount", 0) for i in items)
        sub = [i for i in items if i.get("status") in ("submitted", "approved", "denied")]
        won = [i for i in items if i.get("status") == "approved"]
        rate = (len(won) / len(sub) * 100) if sub else 0
        return DenialTypeSplit(label=label, count=len(items), total_denied=total_denied, overturn_rate=round(rate, 1))

    admin_split = _make_split("Administrative", buckets["administrative"])
    clinical_split = _make_split("Clinical", buckets["clinical"])
    other_split = _make_split("Other", buckets["other"])

    code_groups: dict[str, list] = defaultdict(list)
    for d in denials:
        dc = d.get("denial_code") or "Unknown"
        code_groups[dc].append(d)

    code_breakdown = []
    for code, items in sorted(code_groups.items(), key=lambda x: len(x[1]), reverse=True):
        sub = [i for i in items if i.get("status") in ("submitted", "approved", "denied")]
        won = [i for i in items if i.get("status") == "approved"]
        rate = (len(won) / len(sub) * 100) if sub else 0
        cats = Counter(i.get("denial_category", "Other") for i in items)
        most_common_cat = cats.most_common(1)[0][0] if cats else "Other"
        code_breakdown.append(CodeBreakdown(
            code=code,
            description=DENIAL_CODE_DESCRIPTIONS.get(code, ""),
            count=len(items),
            total_denied=sum(i.get("denied_amount", 0) for i in items),
            overturn_rate=round(rate, 1),
            classification=_classify_type(most_common_cat),
            preventability=_classify_preventability(most_common_cat),
        ))

    proc_groups: dict[str, dict] = defaultdict(lambda: {
        "total": 0,
        "Medical Necessity": 0,
        "Prior Authorization": 0,
        "Coding Error": 0,
        "Documentation": 0,
        "Other": 0,
    })
    for d in denials:
        pc = d.get("procedure_code") or "Unknown"
        cat = d.get("denial_category", "Other")
        proc_groups[pc]["total"] += 1
        if cat in proc_groups[pc]:
            proc_groups[pc][cat] += 1
        else:
            proc_groups[pc]["Other"] += 1

    procedure_matrix = sorted(
        [
            ProcedureCodeRow(
                procedure_code=pc,
                total=v["total"],
                medical_necessity=v["Medical Necessity"],
                prior_authorization=v["Prior Authorization"],
                coding_error=v["Coding Error"],
                documentation=v["Documentation"],
                other=v["Other"],
            )
            for pc, v in proc_groups.items()
        ],
        key=lambda x: x.total,
        reverse=True,
    )[:20]

    diag_counter: Counter = Counter()
    for d in denials:
        codes = d.get("diagnosis_codes", [])
        if isinstance(codes, str):
            codes = [c.strip() for c in codes.split(",")]
        for c in codes:
            if c:
                diag_counter[c] += 1

    top_diag = [DiagnosisCodeRow(code=c, count=n) for c, n in diag_counter.most_common(15)]

    return DenialAnalysisResponse(
        admin_split=admin_split,
        clinical_split=clinical_split,
        other_split=other_split,
        code_breakdown=code_breakdown,
        procedure_matrix=procedure_matrix,
        top_diagnosis_codes=top_diag,
    )


# ── Overturn Rates ─────────────────────────────────────────────


@router.get("/overturn-rates", response_model=OverturnRatesResponse)
async def get_overturn_rates(
    group_by: str = Query(default="payer"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    payers: Optional[str] = Query(None),
    practices: Optional[str] = Query(None),
    categories: Optional[str] = Query(None),
    denial_type: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    denials = await _get_filtered_denials(date_from, date_to, payers, practices, categories, denial_type)

    resolved = [d for d in denials if d.get("status") in ("submitted", "approved", "denied")]
    won = [d for d in denials if d.get("status") == "approved"]
    overall_rate = (len(won) / len(resolved) * 100) if resolved else 0

    monthly: dict[str, dict] = defaultdict(lambda: {"total": 0, "won": 0})
    for d in resolved:
        upd = _parse_dt(d.get("updated_at"))
        if upd:
            mk = upd.strftime("%Y-%m")
            monthly[mk]["total"] += 1
            if d.get("status") == "approved":
                monthly[mk]["won"] += 1

    trend = sorted(
        [
            MonthlyOverturn(
                month=m,
                overturn_rate=round(v["won"] / v["total"] * 100, 1) if v["total"] else 0,
                overturned=v["won"],
                total_appeals=v["total"],
            )
            for m, v in monthly.items()
        ],
        key=lambda x: x.month,
    )

    field_map = {
        "payer": "payer_name",
        "practice": "provider_practice_name",
        "category": "denial_category",
        "code": "denial_code",
    }
    group_field = field_map.get(group_by, "payer_name")

    groups: dict[str, list] = defaultdict(list)
    for d in resolved:
        key = d.get(group_field) or "Unknown"
        groups[key].append(d)

    rows = []
    for name, items in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        w = [i for i in items if i.get("status") == "approved"]
        days_list = []
        for i in items:
            if i.get("status") in ("approved", "denied"):
                sub_dt = _parse_dt(i.get("submitted_at"))
                upd_dt = _parse_dt(i.get("updated_at"))
                if sub_dt and upd_dt:
                    d_days = (upd_dt - sub_dt).days
                    if d_days >= 0:
                        days_list.append(d_days)
        avg_days = (sum(days_list) / len(days_list)) if days_list else None

        extra = None
        if group_by == "practice":
            code_cnt = Counter(i.get("denial_code", "Unknown") for i in items)
            extra = code_cnt.most_common(1)[0][0] if code_cnt else None
        elif group_by == "category":
            win_probs = [i.get("win_probability", 0) or 0 for i in items]
            avg_wp = sum(win_probs) / len(win_probs) if win_probs else 0
            actual = round(len(w) / len(items) * 100, 1) if items else 0
            extra = f"Predicted: {round(avg_wp)}% / Actual: {actual}%"

        rows.append(OverturnRow(
            name=name,
            total_appeals=len(items),
            overturned=len(w),
            overturn_rate=round(len(w) / len(items) * 100, 1) if items else 0,
            avg_days_to_decision=round(avg_days, 1) if avg_days is not None else None,
            recovered_amount=sum(i.get("denied_amount", 0) for i in w),
            extra=extra,
        ))

    rows.sort(key=lambda x: x.overturn_rate, reverse=True)

    return OverturnRatesResponse(
        overall_overturn_rate=round(overall_rate, 1),
        trend=trend,
        rows=rows,
    )


# ── Pattern Intelligence ───────────────────────────────────────


@router.get("/patterns", response_model=PatternIntelligenceResponse)
async def get_patterns(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    payers: Optional[str] = Query(None),
    practices: Optional[str] = Query(None),
    categories: Optional[str] = Query(None),
    denial_type: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    denials = await _get_filtered_denials(date_from, date_to, payers, practices, categories, denial_type)

    prev_monthly: dict[str, dict] = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0})
    for d in denials:
        dd = _parse_dt(d.get("denial_date")) or _parse_dt(d.get("created_at"))
        if dd:
            mk = dd.strftime("%Y-%m")
            p = _classify_preventability(d.get("denial_category", ""))
            prev_monthly[mk][p] += 1

    preventability_trend = sorted(
        [PreventabilityMonth(month=m, **v) for m, v in prev_monthly.items()],
        key=lambda x: x.month,
    )

    code_groups: dict[str, list] = defaultdict(list)
    for d in denials:
        dc = d.get("denial_code")
        if dc:
            code_groups[dc].append(d)

    now = datetime.utcnow()
    mid = now - timedelta(days=90)

    recurring_patterns = []
    for code, items in sorted(code_groups.items(), key=lambda x: len(x[1]), reverse=True):
        if len(items) < 3:
            continue
        early = sum(1 for i in items if (_parse_dt(i.get("denial_date")) or datetime.min) < mid)
        late = sum(1 for i in items if (_parse_dt(i.get("denial_date")) or datetime.min) >= mid)
        if late > early:
            trend_dir = "up"
        elif late < early:
            trend_dir = "down"
        else:
            trend_dir = "flat"

        payer_cnt = Counter(i.get("payer_name", "Unknown") for i in items)
        practice_cnt = Counter(i.get("provider_practice_name", "Unknown") for i in items)
        common_payer = payer_cnt.most_common(1)[0][0] if payer_cnt else "Unknown"
        common_practice = practice_cnt.most_common(1)[0][0] if practice_cnt else "Unknown"

        cats = Counter(i.get("denial_category", "Other") for i in items)
        top_cat = cats.most_common(1)[0][0] if cats else "Other"
        prev = _classify_preventability(top_cat)

        if prev == "high":
            action = f"Review {top_cat.lower()} processes — this denial is highly preventable."
        elif prev == "medium":
            action = f"Improve documentation practices to address {code} denials."
        else:
            action = f"Prepare stronger clinical evidence for {code} appeals."

        recurring_patterns.append(RecurringPattern(
            code=code,
            frequency=len(items),
            trend=trend_dir,
            common_payer=common_payer,
            common_practice=common_practice,
            suggested_action=action,
        ))

    practice_groups: dict[str, list] = defaultdict(list)
    for d in denials:
        pn = d.get("provider_practice_name") or "Unknown"
        practice_groups[pn].append(d)

    practice_insights = []
    for practice, items in sorted(practice_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        prev_count = sum(1 for i in items if _classify_preventability(i.get("denial_category", "")) in ("high", "medium"))
        code_cnt = Counter(i.get("denial_code", "Unknown") for i in items if _classify_preventability(i.get("denial_category", "")) in ("high", "medium"))
        practice_insights.append(PracticeInsight(
            practice=practice,
            total_denials=len(items),
            preventable_count=prev_count,
            preventable_rate=round(prev_count / len(items) * 100, 1) if items else 0,
            top_codes=[c for c, _ in code_cnt.most_common(3)],
        ))

    payer_groups: dict[str, list] = defaultdict(list)
    for d in denials:
        pn = d.get("payer_name") or "Unknown"
        payer_groups[pn].append(d)

    payer_behavior = []
    for payer, items in sorted(payer_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        code_cnt = Counter(i.get("denial_code", "Unknown") for i in items)
        resolved = [i for i in items if i.get("status") in ("submitted", "approved", "denied")]
        won = [i for i in items if i.get("status") == "approved"]
        rate = (len(won) / len(resolved) * 100) if resolved else 0
        payer_behavior.append(PayerBehavior(
            payer=payer,
            total_denials=len(items),
            top_codes=[c for c, _ in code_cnt.most_common(3)],
            overturn_rate=round(rate, 1),
        ))

    insights = _generate_actionable_insights(denials, practice_groups, payer_groups)

    return PatternIntelligenceResponse(
        preventability_trend=preventability_trend,
        recurring_patterns=recurring_patterns[:15],
        practice_insights=practice_insights,
        payer_behavior=payer_behavior,
        actionable_insights=insights,
    )


def _generate_actionable_insights(
    denials: list,
    practice_groups: dict[str, list],
    payer_groups: dict[str, list],
) -> List[str]:
    insights = []
    total = len(denials)
    if not total:
        return ["No denial data available for the selected period."]

    preventable = sum(1 for d in denials if _classify_preventability(d.get("denial_category", "")) in ("high", "medium"))
    pct = round(preventable / total * 100)
    if pct > 50:
        insights.append(
            f"{pct}% of denials in this period are classified as preventable. "
            "Focus on coding accuracy and prior authorization checks to reduce volume."
        )

    cat_counts = Counter(d.get("denial_category", "Other") for d in denials)
    top_cat, top_count = cat_counts.most_common(1)[0]
    insights.append(
        f"\"{top_cat}\" is the leading denial category with {top_count} occurrences "
        f"({round(top_count / total * 100)}% of all denials)."
    )

    for payer, items in sorted(payer_groups.items(), key=lambda x: len(x[1]), reverse=True)[:3]:
        resolved = [i for i in items if i.get("status") in ("submitted", "approved", "denied")]
        won = [i for i in items if i.get("status") == "approved"]
        if resolved:
            rate = round(len(won) / len(resolved) * 100)
            if rate < 40:
                code_cnt = Counter(i.get("denial_code", "?") for i in items)
                top_code = code_cnt.most_common(1)[0][0]
                insights.append(
                    f"{payer} has a low overturn rate of {rate}%. "
                    f"Most common denial code is {top_code} — review submission requirements for this payer."
                )

    for practice, items in sorted(practice_groups.items(), key=lambda x: len(x[1]), reverse=True)[:3]:
        prev_count = sum(1 for i in items if _classify_preventability(i.get("denial_category", "")) == "high")
        if prev_count > 3:
            insights.append(
                f"{practice} has {prev_count} highly preventable denials. "
                "Consider targeted training on coding and prior authorization workflows."
            )

    return insights[:5]


# ── Operational KPIs ───────────────────────────────────────────


@router.get("/operational-kpis", response_model=OperationalKPIsResponse)
async def get_operational_kpis(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    payers: Optional[str] = Query(None),
    practices: Optional[str] = Query(None),
    categories: Optional[str] = Query(None),
    denial_type: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    denials = await _get_filtered_denials(date_from, date_to, payers, practices, categories, denial_type)

    processing_days = []
    for d in denials:
        if d.get("status") in ("submitted", "approved", "denied"):
            created = _parse_dt(d.get("created_at"))
            submitted = _parse_dt(d.get("submitted_at"))
            if created and submitted:
                delta = (submitted - created).days
                if delta >= 0:
                    processing_days.append(delta)

    avg_processing = (sum(processing_days) / len(processing_days)) if processing_days else None

    letter_gen_times = []
    for d in denials:
        ts = d.get("processing_timestamps") or {}
        secs = ts.get("letter_generation_seconds")
        if secs is not None:
            letter_gen_times.append(secs)
    avg_letter_gen = (sum(letter_gen_times) / len(letter_gen_times)) if letter_gen_times else None

    review_hours_list = []
    for d in denials:
        ts = d.get("processing_timestamps") or {}
        started = _parse_dt(ts.get("review_started_at"))
        completed = _parse_dt(ts.get("review_completed_at"))
        if started and completed:
            hours = (completed - started).total_seconds() / 3600
            if hours >= 0:
                review_hours_list.append(hours)
    avg_review = (sum(review_hours_list) / len(review_hours_list)) if review_hours_list else None

    weekly_buckets: dict[str, int] = defaultdict(int)
    for d in denials:
        if d.get("status") in ("submitted", "approved", "denied"):
            sub = _parse_dt(d.get("submitted_at"))
            if sub:
                wk = sub.strftime("%Y-W%W")
                weekly_buckets[wk] += 1

    throughput_trend = [
        {"week": w, "count": c} for w, c in sorted(weekly_buckets.items())
    ]

    appeals_per_week = None
    if weekly_buckets:
        appeals_per_week = round(sum(weekly_buckets.values()) / len(weekly_buckets), 1)

    monthly_proc: dict[str, list] = defaultdict(list)
    for d in denials:
        if d.get("status") in ("submitted", "approved", "denied"):
            created = _parse_dt(d.get("created_at"))
            submitted = _parse_dt(d.get("submitted_at"))
            if created and submitted:
                delta = (submitted - created).days
                if delta >= 0 and submitted:
                    mk = submitted.strftime("%Y-%m")
                    monthly_proc[mk].append(delta)

    processing_trend = [
        {"month": m, "avg_days": round(sum(v) / len(v), 1)}
        for m, v in sorted(monthly_proc.items())
        if v
    ]

    return OperationalKPIsResponse(
        avg_processing_days=round(avg_processing, 1) if avg_processing is not None else None,
        avg_letter_generation_seconds=round(avg_letter_gen, 1) if avg_letter_gen is not None else None,
        ai_auto_approval_rate=None,
        appeals_per_week=appeals_per_week,
        avg_review_hours=round(avg_review, 2) if avg_review is not None else None,
        fte_capacity_gain=None,
        processing_trend=processing_trend,
        throughput_trend=throughput_trend,
    )


# ── Practice Scorecard ────────────────────────────────────────


def _build_practice_scorecard(practice_name: str, denials: list) -> PracticeScorecardResponse:
    total = len(denials)
    total_denied = sum(d.get("denied_amount", 0) for d in denials)

    submitted = [d for d in denials if d.get("status") in ("submitted", "approved", "denied")]
    approved = [d for d in denials if d.get("status") == "approved"]
    overturn_rate = (len(approved) / len(submitted) * 100) if submitted else 0
    total_recovered = sum(d.get("denied_amount", 0) for d in approved)

    preventable = sum(
        1 for d in denials
        if _classify_preventability(d.get("denial_category", "")) in ("high", "medium")
    )
    preventable_rate = (preventable / total * 100) if total else 0

    resolution_days = []
    for d in denials:
        if d.get("status") in ("approved", "denied"):
            denial_dt = _parse_dt(d.get("denial_date"))
            updated_dt = _parse_dt(d.get("updated_at"))
            if denial_dt and updated_dt:
                delta = (updated_dt - denial_dt).days
                if delta >= 0:
                    resolution_days.append(delta)
    avg_res = (sum(resolution_days) / len(resolution_days)) if resolution_days else None

    buckets: dict[str, list] = {"administrative": [], "clinical": [], "other": []}
    for d in denials:
        buckets[_classify_type(d.get("denial_category", ""))].append(d)

    def _split(label, items):
        td = sum(i.get("denied_amount", 0) for i in items)
        s = [i for i in items if i.get("status") in ("submitted", "approved", "denied")]
        w = [i for i in items if i.get("status") == "approved"]
        r = (len(w) / len(s) * 100) if s else 0
        return DenialTypeSplit(label=label, count=len(items), total_denied=td, overturn_rate=round(r, 1))

    admin_split = _split("Administrative", buckets["administrative"])
    clinical_split = _split("Clinical", buckets["clinical"])

    code_groups: dict[str, list] = defaultdict(list)
    for d in denials:
        dc = d.get("denial_code") or "Unknown"
        code_groups[dc].append(d)

    top_codes = []
    for code, items in sorted(code_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        s = [i for i in items if i.get("status") in ("submitted", "approved", "denied")]
        w = [i for i in items if i.get("status") == "approved"]
        rate = (len(w) / len(s) * 100) if s else 0
        cats = Counter(i.get("denial_category", "Other") for i in items)
        mc = cats.most_common(1)[0][0] if cats else "Other"
        top_codes.append(CodeBreakdown(
            code=code,
            description=DENIAL_CODE_DESCRIPTIONS.get(code, ""),
            count=len(items),
            total_denied=sum(i.get("denied_amount", 0) for i in items),
            overturn_rate=round(rate, 1),
            classification=_classify_type(mc),
            preventability=_classify_preventability(mc),
        ))

    proc_groups: dict[str, dict] = defaultdict(lambda: {
        "total": 0, "Medical Necessity": 0, "Prior Authorization": 0,
        "Coding Error": 0, "Documentation": 0, "Other": 0,
    })
    for d in denials:
        pc = d.get("procedure_code") or "Unknown"
        cat = d.get("denial_category", "Other")
        proc_groups[pc]["total"] += 1
        if cat in proc_groups[pc]:
            proc_groups[pc][cat] += 1
        else:
            proc_groups[pc]["Other"] += 1

    top_procs = sorted(
        [ProcedureCodeRow(
            procedure_code=pc, total=v["total"],
            medical_necessity=v["Medical Necessity"],
            prior_authorization=v["Prior Authorization"],
            coding_error=v["Coding Error"],
            documentation=v["Documentation"],
            other=v["Other"],
        ) for pc, v in proc_groups.items()],
        key=lambda x: x.total, reverse=True,
    )[:5]

    payer_groups: dict[str, list] = defaultdict(list)
    for d in submitted:
        pn = d.get("payer_name") or "Unknown"
        payer_groups[pn].append(d)

    payer_rows = []
    for pname, items in sorted(payer_groups.items(), key=lambda x: len(x[1]), reverse=True):
        w = [i for i in items if i.get("status") == "approved"]
        days_list = []
        for i in items:
            sub_dt = _parse_dt(i.get("submitted_at"))
            upd_dt = _parse_dt(i.get("updated_at"))
            if sub_dt and upd_dt:
                dd = (upd_dt - sub_dt).days
                if dd >= 0:
                    days_list.append(dd)
        avg_d = (sum(days_list) / len(days_list)) if days_list else None
        payer_rows.append(OverturnRow(
            name=pname,
            total_appeals=len(items),
            overturned=len(w),
            overturn_rate=round(len(w) / len(items) * 100, 1) if items else 0,
            avg_days_to_decision=round(avg_d, 1) if avg_d is not None else None,
            recovered_amount=sum(i.get("denied_amount", 0) for i in w),
        ))

    monthly: dict[str, dict] = defaultdict(lambda: {"administrative": 0, "clinical": 0, "other": 0})
    for d in denials:
        dd = _parse_dt(d.get("denial_date")) or _parse_dt(d.get("created_at"))
        if dd:
            mk = dd.strftime("%Y-%m")
            monthly[mk][_classify_type(d.get("denial_category", ""))] += 1

    denial_trend = sorted(
        [MonthlyVolume(month=m, **v) for m, v in monthly.items()],
        key=lambda x: x.month,
    )

    insights = []
    if top_codes:
        tc = top_codes[0]
        insights.append(
            f"{tc.code} is the top denial code ({tc.count} occurrences, "
            f"${tc.total_denied:,.0f} denied). "
            f"Overturn rate: {tc.overturn_rate}%."
        )
    if preventable_rate > 50:
        insights.append(
            f"{round(preventable_rate)}% of denials are preventable. "
            "Focus on billing process improvements."
        )
    if admin_split.overturn_rate > 60:
        insights.append(
            f"Administrative denials have a {admin_split.overturn_rate}% overturn rate — "
            "prioritize these as quick wins."
        )
    if payer_rows:
        best = max(payer_rows, key=lambda r: r.overturn_rate)
        if best.overturn_rate > 60:
            insights.append(
                f"{best.name} has the highest overturn rate ({best.overturn_rate}%). "
                "Prioritize appeals against this payer."
            )
    if not insights:
        insights.append("Not enough data to generate specific insights for this practice.")

    return PracticeScorecardResponse(
        practice_name=practice_name,
        total_denials=total,
        total_denied=total_denied,
        total_recovered=total_recovered,
        overturn_rate=round(overturn_rate, 1),
        preventable_rate=round(preventable_rate, 1),
        avg_resolution_days=round(avg_res, 1) if avg_res is not None else None,
        admin_split=admin_split,
        clinical_split=clinical_split,
        top_denial_codes=top_codes,
        top_procedures=top_procs,
        payer_breakdown=payer_rows,
        denial_trend=denial_trend,
        actionable_insights=insights,
    )


@router.get("/practice-scorecard", response_model=PracticeScorecardResponse)
async def get_practice_scorecard(
    practice: str = Query(..., description="Practice name"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    denials = await _get_filtered_denials(
        date_from=date_from, date_to=date_to,
        payers=None, practices=practice,
        categories=None, denial_type=None,
    )
    return _build_practice_scorecard(practice, denials)


@router.get("/practice-comparison", response_model=List[PracticeScorecardResponse])
async def get_practice_comparison(
    practices: str = Query(..., description="Comma-separated practice names (2-3)"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    user=Depends(get_current_user),
):
    names = [p.strip() for p in practices.split(",") if p.strip()][:3]
    results = []
    for name in names:
        denials = await _get_filtered_denials(
            date_from=date_from, date_to=date_to,
            payers=None, practices=name,
            categories=None, denial_type=None,
        )
        results.append(_build_practice_scorecard(name, denials))
    return results
