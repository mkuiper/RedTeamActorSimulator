"""Simulation orchestration service."""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.agents.actor import ActorAgent
from app.agents.assessor import AssessorAgent
from app.database import async_session_maker
from app.models import Objective, Persona, Session, Turn
from app.models.objective import ObjectiveStatus
from app.models.session import SessionStatus
from app.providers import get_provider
from app.schemas.simulation import SimulationStepResponse

logger = logging.getLogger(__name__)


class SimulationService:
    """Orchestrates the simulation between actor, subject, and assessor."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._actor: Optional[ActorAgent] = None
        self._assessor: Optional[AssessorAgent] = None
        self._session: Optional[Session] = None
        self._persona: Optional[Persona] = None

    async def _load_session(self):
        """Load session data from database."""
        async with async_session_maker() as db:
            result = await db.execute(
                select(Session)
                .options(
                    selectinload(Session.objectives),
                    selectinload(Session.turns),
                )
                .where(Session.id == self.session_id)
            )
            self._session = result.scalar_one_or_none()

            if not self._session:
                raise ValueError(f"Session not found: {self.session_id}")

            # Load persona
            persona_result = await db.execute(
                select(Persona).where(Persona.id == self._session.persona_id)
            )
            self._persona = persona_result.scalar_one_or_none()

            if not self._persona:
                raise ValueError(f"Persona not found: {self._session.persona_id}")

    def _initialize_agents(self):
        """Initialize actor and assessor agents."""
        # Parse model strings (format: "provider:model")
        actor_parts = self._session.actor_model.split(":", 1)
        assessor_parts = self._session.assessor_model.split(":", 1)

        actor_provider = actor_parts[0] if len(actor_parts) > 1 else "anthropic"
        actor_model = actor_parts[1] if len(actor_parts) > 1 else actor_parts[0]

        assessor_provider = assessor_parts[0] if len(assessor_parts) > 1 else "anthropic"
        assessor_model = assessor_parts[1] if len(assessor_parts) > 1 else assessor_parts[0]

        self._actor = ActorAgent(
            provider_name=actor_provider,
            model=actor_model,
            persona_name=self._persona.name,
            persona_description=self._persona.description,
            skill_level=self._persona.skill_level,
            resources=self._persona.resources,
            background=self._persona.background,
            # Enhanced attributes
            motivation=self._persona.motivation,
            communication_style=self._persona.communication_style,
            persistence_level=self._persona.persistence_level,
            # Personality sliders
            patience=self._persona.patience,
            aggression=self._persona.aggression,
            creativity=self._persona.creativity,
            deception=self._persona.deception,
            # Detailed guidance
            behavioral_notes=self._persona.behavioral_notes,
            example_phrases=self._persona.example_phrases,
            domain_knowledge=self._persona.domain_knowledge,
            # Custom prompts
            custom_prompt_prefix=self._persona.custom_prompt_prefix,
            custom_prompt_suffix=self._persona.custom_prompt_suffix,
        )

        self._assessor = AssessorAgent(
            provider_name=assessor_provider,
            model=assessor_model,
        )

    async def run(self):
        """Run the full simulation."""
        await self._load_session()
        self._initialize_agents()

        logger.info(f"Starting simulation for session {self.session_id}")

        async with async_session_maker() as db:
            # Get fresh session reference
            result = await db.execute(
                select(Session)
                .options(selectinload(Session.objectives))
                .where(Session.id == self.session_id)
            )
            session = result.scalar_one()

            # Process each objective in chain order
            objectives = sorted(session.objectives, key=lambda o: o.chain_order)

            for objective in objectives:
                logger.info(f"Processing objective: {objective.title}")

                # Update objective status
                objective.status = ObjectiveStatus.IN_PROGRESS
                objective.started_at = datetime.utcnow()
                await db.commit()

                # Run turns for this objective
                completed = await self._run_objective(db, session, objective)

                if completed:
                    objective.status = ObjectiveStatus.COMPLETED
                    objective.completed_at = datetime.utcnow()
                else:
                    objective.status = ObjectiveStatus.FAILED
                    # Generate bottleneck analysis
                    objective.bottleneck_notes = await self._generate_bottleneck_analysis(
                        db, objective
                    )

                await db.commit()

            # Mark session as completed
            session.status = SessionStatus.COMPLETED
            await db.commit()

            logger.info(f"Simulation completed for session {self.session_id}")

    async def _run_objective(
        self,
        db,
        session: Session,
        objective: Objective,
    ) -> bool:
        """
        Run turns for a single objective.

        Returns True if objective was completed, False otherwise.
        """
        # Parse subject model
        subject_parts = session.subject_model.split(":", 1)
        subject_provider_name = subject_parts[0] if len(subject_parts) > 1 else "anthropic"
        subject_model = subject_parts[1] if len(subject_parts) > 1 else subject_parts[0]
        subject_provider = get_provider(subject_provider_name)

        conversation_history = []
        last_assessor_hint = None
        last_subject_thinking = None

        for turn_num in range(1, session.max_turns + 1):
            logger.info(f"Turn {turn_num}/{session.max_turns} for objective: {objective.title}")

            # Generate actor message
            actor_response = await self._actor.generate_message(
                conversation_history=conversation_history,
                objective_description=objective.description,
                sneaky_mode=session.sneaky_mode,
                completion_criteria=objective.completion_criteria if session.sneaky_mode else None,
                assessor_hint=last_assessor_hint,
                subject_thinking=last_subject_thinking,
            )

            actor_message = actor_response["content"]
            actor_thinking = actor_response.get("thinking")

            # Get subject response
            # Convert conversation to subject's perspective
            subject_messages = []
            for msg in conversation_history:
                if msg["role"] == "actor":
                    subject_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "subject":
                    subject_messages.append({"role": "assistant", "content": msg["content"]})

            subject_messages.append({"role": "user", "content": actor_message})

            subject_response = await subject_provider.generate(
                messages=subject_messages,
                model=subject_model,
                request_thinking=session.sneaky_mode,  # Request thinking in sneaky mode
            )

            subject_thinking = subject_response.thinking
            last_subject_thinking = subject_thinking

            # Assess the response
            context = "\n".join([
                f"{msg['role']}: {msg['content'][:200]}..."
                for msg in conversation_history[-4:]  # Last 4 messages for context
            ]) if conversation_history else None

            evaluation = await self._assessor.evaluate(
                actor_message=actor_message,
                subject_response=subject_response.content,
                objective_description=objective.description,
                completion_criteria=objective.completion_criteria,
                sneaky_mode=session.sneaky_mode,
                conversation_context=context,
            )

            last_assessor_hint = evaluation.actor_hint

            # Update conversation history
            conversation_history.append({"role": "actor", "content": actor_message})
            conversation_history.append({"role": "subject", "content": subject_response.content})

            # Save turn to database
            turn = Turn(
                session_id=session.id,
                objective_id=objective.id,
                turn_number=turn_num,
                actor_message=actor_message,
                actor_thinking=actor_thinking,
                subject_response=subject_response.content,
                subject_thinking=subject_thinking,
                assessor_evaluation=evaluation.to_dict(),
                criteria_met=evaluation.criteria_met,
                refusal_detected=evaluation.refusal_detected,
                actor_strategy=evaluation.strategy_observed,
            )
            db.add(turn)

            # Update objective metrics
            objective.turns_taken = turn_num
            if evaluation.refusal_detected:
                objective.refusal_count += 1

            await db.commit()

            # Check if criteria met
            if evaluation.criteria_met:
                logger.info(f"Objective completed: {objective.title}")
                return True

        # Max turns reached without completion
        logger.info(f"Max turns reached for objective: {objective.title}")
        return False

    async def _generate_bottleneck_analysis(
        self,
        db,
        objective: Objective,
    ) -> str:
        """Generate bottleneck analysis for a failed objective."""
        # Get turns for this objective
        result = await db.execute(
            select(Turn)
            .where(Turn.objective_id == objective.id)
            .order_by(Turn.turn_number)
        )
        turns = result.scalars().all()

        conversation_history = []
        for turn in turns:
            conversation_history.append({"role": "actor", "content": turn.actor_message})
            conversation_history.append({"role": "subject", "content": turn.subject_response})

        return await self._assessor.generate_bottleneck_analysis(
            objective_description=objective.description,
            completion_criteria=objective.completion_criteria,
            conversation_history=conversation_history,
            refusal_count=objective.refusal_count,
            turns_taken=objective.turns_taken,
        )

    async def execute_single_step(self) -> SimulationStepResponse:
        """Execute a single simulation step (for debugging/manual control)."""
        await self._load_session()
        self._initialize_agents()

        async with async_session_maker() as db:
            # Get current session and objective
            result = await db.execute(
                select(Session)
                .options(
                    selectinload(Session.objectives),
                    selectinload(Session.turns),
                )
                .where(Session.id == self.session_id)
            )
            session = result.scalar_one()

            # Find current objective
            current_objective = None
            for obj in sorted(session.objectives, key=lambda o: o.chain_order):
                if obj.status in [ObjectiveStatus.PENDING, ObjectiveStatus.IN_PROGRESS]:
                    current_objective = obj
                    break

            if not current_objective:
                raise ValueError("No pending objectives")

            # Get current turn number
            current_turn = len([t for t in session.turns if t.objective_id == current_objective.id]) + 1

            # Build conversation history
            conversation_history = []
            for turn in sorted(session.turns, key=lambda t: t.turn_number):
                if turn.objective_id == current_objective.id:
                    conversation_history.append({"role": "actor", "content": turn.actor_message})
                    conversation_history.append({"role": "subject", "content": turn.subject_response})

            # This is a simplified version - full implementation would mirror _run_objective
            # For now, return a placeholder
            return SimulationStepResponse(
                turn_number=current_turn,
                actor_message="[Step execution not fully implemented]",
                subject_response="[Step execution not fully implemented]",
                assessment={},
                criteria_met=False,
                objective_completed=False,
                simulation_completed=False,
            )
