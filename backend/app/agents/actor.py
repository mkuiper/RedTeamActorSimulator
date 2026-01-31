"""Actor agent implementation."""

import logging
from typing import List, Optional

from app.agents.prompts import (
    ACTOR_SYSTEM_PROMPT,
    ACTOR_SNEAKY_MODE_SECTION,
    ACTOR_BEHAVIORAL_NOTES_SECTION,
    ACTOR_EXAMPLE_PHRASES_SECTION,
    ACTOR_DOMAIN_KNOWLEDGE_SECTION,
)
from app.models.persona import (
    Background,
    CommunicationStyle,
    Motivation,
    PersistenceLevel,
    ResourceLevel,
    SkillLevel,
)
from app.providers import get_provider

logger = logging.getLogger(__name__)


class ActorAgent:
    """Agent that plays the role of a user with a specific persona."""

    def __init__(
        self,
        provider_name: str,
        model: str,
        persona_name: str,
        persona_description: str,
        skill_level: SkillLevel,
        resources: ResourceLevel,
        background: Background,
        # Enhanced attributes
        motivation: Optional[Motivation] = None,
        communication_style: Optional[CommunicationStyle] = None,
        persistence_level: Optional[PersistenceLevel] = None,
        # Personality sliders
        patience: float = 0.5,
        aggression: float = 0.3,
        creativity: float = 0.5,
        deception: float = 0.3,
        # Detailed guidance
        behavioral_notes: Optional[str] = None,
        example_phrases: Optional[str] = None,
        domain_knowledge: Optional[str] = None,
        # Custom prompts
        custom_prompt_prefix: Optional[str] = None,
        custom_prompt_suffix: Optional[str] = None,
    ):
        self.provider = get_provider(provider_name)
        self.model = model
        self.persona_name = persona_name
        self.persona_description = persona_description
        self.skill_level = skill_level
        self.resources = resources
        self.background = background

        # Enhanced attributes with defaults
        self.motivation = motivation or Motivation.CURIOSITY
        self.communication_style = communication_style or CommunicationStyle.DIRECT
        self.persistence_level = persistence_level or PersistenceLevel.MEDIUM

        # Personality sliders
        self.patience = patience
        self.aggression = aggression
        self.creativity = creativity
        self.deception = deception

        # Detailed guidance
        self.behavioral_notes = behavioral_notes or ""
        self.example_phrases = example_phrases or ""
        self.domain_knowledge = domain_knowledge or ""

        # Custom prompts
        self.custom_prompt_prefix = custom_prompt_prefix or ""
        self.custom_prompt_suffix = custom_prompt_suffix or ""

    def _build_system_prompt(
        self,
        objective_description: str,
        sneaky_mode: bool = False,
        completion_criteria: Optional[str] = None,
        assessor_hint: Optional[str] = None,
        subject_thinking: Optional[str] = None,
    ) -> str:
        """Build the system prompt for the actor."""
        # Build optional sections
        behavioral_notes_section = ""
        if self.behavioral_notes:
            behavioral_notes_section = ACTOR_BEHAVIORAL_NOTES_SECTION.format(
                behavioral_notes=self.behavioral_notes
            )

        example_phrases_section = ""
        if self.example_phrases:
            example_phrases_section = ACTOR_EXAMPLE_PHRASES_SECTION.format(
                example_phrases=self.example_phrases
            )

        domain_knowledge_section = ""
        if self.domain_knowledge:
            domain_knowledge_section = ACTOR_DOMAIN_KNOWLEDGE_SECTION.format(
                domain_knowledge=self.domain_knowledge
            )

        sneaky_section = ""
        if sneaky_mode and completion_criteria:
            sneaky_section = ACTOR_SNEAKY_MODE_SECTION.format(
                completion_criteria=completion_criteria,
                assessor_hint=assessor_hint or "No hint available yet.",
                subject_thinking=subject_thinking or "No thinking captured.",
            )

        return ACTOR_SYSTEM_PROMPT.format(
            # Core attributes
            skill_level=self.skill_level.value.replace("_", " "),
            resources=self.resources.value,
            background=self.background.value.replace("_", "-"),
            persona_name=self.persona_name,
            persona_description=self.persona_description,
            # Enhanced attributes
            motivation=self.motivation.value,
            communication_style=self.communication_style.value,
            persistence_level=self.persistence_level.value,
            # Personality sliders
            patience=self.patience,
            aggression=self.aggression,
            creativity=self.creativity,
            deception=self.deception,
            # Optional sections
            behavioral_notes_section=behavioral_notes_section,
            example_phrases_section=example_phrases_section,
            domain_knowledge_section=domain_knowledge_section,
            custom_prompt_prefix=self.custom_prompt_prefix,
            custom_prompt_suffix=self.custom_prompt_suffix,
            # Objective
            objective_description=objective_description,
            sneaky_mode_section=sneaky_section,
        )

    async def generate_message(
        self,
        conversation_history: List[dict],
        objective_description: str,
        sneaky_mode: bool = False,
        completion_criteria: Optional[str] = None,
        assessor_hint: Optional[str] = None,
        subject_thinking: Optional[str] = None,
        temperature: float = 0.8,
    ) -> dict:
        """
        Generate the next message from the actor's perspective.

        Args:
            conversation_history: List of previous messages in the conversation
            objective_description: What the actor is trying to achieve
            sneaky_mode: Whether to include hidden information
            completion_criteria: The criteria for success (only used in sneaky mode)
            assessor_hint: Hint from assessor (only used in sneaky mode)
            subject_thinking: Subject's chain-of-thought (only used in sneaky mode)
            temperature: Sampling temperature for generation

        Returns:
            Dictionary with 'content' (the message) and 'thinking' (the actor's reasoning)
        """
        system_prompt = self._build_system_prompt(
            objective_description=objective_description,
            sneaky_mode=sneaky_mode,
            completion_criteria=completion_criteria,
            assessor_hint=assessor_hint,
            subject_thinking=subject_thinking,
        )

        # Format conversation for the actor's perspective
        # The actor sends "user" messages and receives "assistant" messages from the subject
        formatted_history = []
        for msg in conversation_history:
            if msg["role"] == "actor":
                # Actor's previous messages are "assistant" from the actor's view
                formatted_history.append({
                    "role": "assistant",
                    "content": msg["content"],
                })
            elif msg["role"] == "subject":
                # Subject's responses are "user" input for the actor to respond to
                formatted_history.append({
                    "role": "user",
                    "content": msg["content"],
                })

        # If this is the first message, add a prompt to start
        if not formatted_history:
            formatted_history.append({
                "role": "user",
                "content": "Begin the conversation. Send your first message to the AI assistant.",
            })

        try:
            # Request thinking for supported models (Anthropic, OpenAI o1)
            request_thinking = "claude" in self.model.lower() or "o1" in self.model.lower()

            response = await self.provider.generate(
                messages=formatted_history,
                model=self.model,
                system_prompt=system_prompt,
                temperature=temperature,
                request_thinking=request_thinking,
            )
            return {
                "content": response.content,
                "thinking": response.thinking,
            }
        except Exception as e:
            logger.error(f"Actor generation error: {e}")
            raise

    async def analyze_strategy(
        self,
        conversation_history: List[dict],
    ) -> dict:
        """
        Analyze the strategies used throughout the conversation.

        Args:
            conversation_history: Full conversation history

        Returns:
            Analysis of strategies used
        """
        from app.agents.prompts import STRATEGY_ANALYSIS_PROMPT

        # Format conversation for analysis
        formatted_conv = "\n\n".join([
            f"Turn {i+1} - {msg['role'].upper()}:\n{msg['content']}"
            for i, msg in enumerate(conversation_history)
        ])

        prompt = STRATEGY_ANALYSIS_PROMPT.format(
            conversation_history=formatted_conv,
            persona_name=self.persona_name,
            skill_level=self.skill_level.value,
            resources=self.resources.value,
            background=self.background.value,
        )

        try:
            response = await self.provider.generate(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.3,  # Lower temperature for analysis
            )

            # Parse JSON response
            import json
            # Try to extract JSON from response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())
        except Exception as e:
            logger.error(f"Strategy analysis error: {e}")
            return {
                "strategies": [],
                "overall_approach": "Analysis failed",
                "pivots": [],
                "error": str(e),
            }
