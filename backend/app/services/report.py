"""Report generation service."""

import io
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session_maker
from app.models import Objective, Persona, Session, Turn

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating simulation reports."""

    def __init__(self, session_id: str):
        self.session_id = session_id

    async def _load_session_data(self):
        """Load all session data for report generation."""
        async with async_session_maker() as db:
            result = await db.execute(
                select(Session)
                .options(
                    selectinload(Session.objectives),
                    selectinload(Session.turns),
                )
                .where(Session.id == self.session_id)
            )
            session = result.scalar_one_or_none()

            if not session:
                raise ValueError(f"Session not found: {self.session_id}")

            # Load persona
            persona_result = await db.execute(
                select(Persona).where(Persona.id == session.persona_id)
            )
            persona = persona_result.scalar_one_or_none()

            return session, persona

    async def generate_markdown(self) -> str:
        """Generate a Markdown report for the session."""
        session, persona = await self._load_session_data()

        # Calculate metrics
        total_turns = len(session.turns)
        total_refusals = sum(1 for t in session.turns if t.refusal_detected)
        completed_objectives = sum(1 for o in session.objectives if o.status.value == "completed")
        total_objectives = len(session.objectives)

        refusal_rate = (total_refusals / total_turns * 100) if total_turns > 0 else 0
        success_rate = (completed_objectives / total_objectives * 100) if total_objectives > 0 else 0

        # Build report
        report = f"""# Red Team Simulation Report

## Session Overview

| Property | Value |
|----------|-------|
| **Session ID** | `{session.id}` |
| **Session Name** | {session.name} |
| **Status** | {session.status.value.upper()} |
| **Created** | {session.created_at.strftime('%Y-%m-%d %H:%M:%S')} |
| **Completed** | {session.updated_at.strftime('%Y-%m-%d %H:%M:%S')} |

## Configuration

### Models
| Role | Model |
|------|-------|
| Actor | `{session.actor_model}` |
| Assessor | `{session.assessor_model}` |
| Subject | `{session.subject_model}` |

### Settings
- **Max Turns per Objective**: {session.max_turns}
- **Sneaky Mode**: {'Enabled' if session.sneaky_mode else 'Disabled'}

### Persona: {persona.name if persona else 'Unknown'}
"""

        if persona:
            report += f"""
| Attribute | Value |
|-----------|-------|
| Skill Level | {persona.skill_level.value.replace('_', ' ').title()} |
| Resources | {persona.resources.value.title()} |
| Background | {persona.background.value.replace('_', ' ').title()} |

**Description**: {persona.description}

**Behavioral Notes**: {persona.behavioral_notes or 'None'}
"""

        report += f"""
## Summary Metrics

| Metric | Value |
|--------|-------|
| Total Objectives | {total_objectives} |
| Completed Objectives | {completed_objectives} |
| **Success Rate** | **{success_rate:.1f}%** |
| Total Turns | {total_turns} |
| Refusals Detected | {total_refusals} |
| **Refusal Rate** | **{refusal_rate:.1f}%** |

## Objectives Analysis

"""

        # Objective details
        for obj in sorted(session.objectives, key=lambda o: o.chain_order):
            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "pending": "⏳",
                "in_progress": "🔄",
                "skipped": "⏭️",
            }.get(obj.status.value, "❓")

            report += f"""### {obj.chain_order + 1}. {obj.title} {status_emoji}

**Status**: {obj.status.value.upper()}
**Turns Taken**: {obj.turns_taken}
**Refusals**: {obj.refusal_count}

**Objective**: {obj.description}

**Completion Criteria**: {obj.completion_criteria}

"""

            if obj.bottleneck_notes:
                report += f"""**Bottleneck Analysis**:
{obj.bottleneck_notes}

"""

        # Conversation logs
        report += """## Conversation Logs

"""

        for obj in sorted(session.objectives, key=lambda o: o.chain_order):
            obj_turns = [t for t in session.turns if t.objective_id == obj.id]
            obj_turns.sort(key=lambda t: t.turn_number)

            report += f"""### Objective: {obj.title}

"""

            for turn in obj_turns:
                refusal_tag = " 🚫" if turn.refusal_detected else ""
                criteria_tag = " ✅" if turn.criteria_met else ""

                report += f"""#### Turn {turn.turn_number}{refusal_tag}{criteria_tag}

**Actor ({persona.name if persona else 'Unknown'}):**
> {turn.actor_message}

**Subject Response:**
> {turn.subject_response}

"""

                if turn.assessor_evaluation:
                    eval_data = turn.assessor_evaluation
                    report += f"""**Assessment:**
- Criteria Status: {eval_data.get('criteria_status', 'N/A')}
- Progress: {eval_data.get('progress_notes', 'N/A')}
- Strategy: {eval_data.get('strategy_observed', 'N/A')}

"""

        # Strategy summary
        report += """## Strategy Analysis

"""

        # Collect unique strategies
        strategies_seen = {}
        for turn in session.turns:
            strategy = turn.actor_strategy or turn.assessor_evaluation.get('strategy_observed', '')
            if strategy and strategy not in strategies_seen:
                strategies_seen[strategy] = {
                    'first_seen': turn.turn_number,
                    'count': 0,
                }
            if strategy:
                strategies_seen[strategy]['count'] += 1

        if strategies_seen:
            report += """| Strategy | First Used | Times Used |
|----------|------------|------------|
"""
            for strategy, data in strategies_seen.items():
                report += f"| {strategy} | Turn {data['first_seen']} | {data['count']} |\n"
        else:
            report += "*No strategy data captured*\n"

        report += f"""

---

*Report generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*
*Red Team Actor Simulator v0.1.0*
"""

        return report

    async def generate_pdf(self) -> bytes:
        """Generate a PDF report for the session."""
        # First generate markdown
        markdown_content = await self.generate_markdown()

        try:
            import markdown
            from weasyprint import HTML, CSS

            # Convert markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['tables', 'fenced_code'],
            )

            # Wrap in HTML document with styling
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        h3 {{
            color: #34495e;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 10px 0;
            padding: 10px 20px;
            background-color: #f9f9f9;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

            # Generate PDF
            html = HTML(string=full_html)
            pdf_bytes = html.write_pdf()

            return pdf_bytes

        except ImportError as e:
            logger.error(f"PDF generation dependencies not available: {e}")
            raise RuntimeError(
                "PDF generation requires 'markdown' and 'weasyprint' packages. "
                "Install with: pip install markdown weasyprint"
            )
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
