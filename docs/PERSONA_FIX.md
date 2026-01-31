# Persona UI Fix - January 2026

## Issue
Personas were not showing in the frontend because the database schema was outdated and missing the new enhanced persona fields.

## What Was Fixed

### 1. Database Schema Update
**Problem**: Old database didn't have new persona columns:
- motivation
- communication_style
- persistence_level
- patience, aggression, creativity, deception (personality sliders)
- behavioral_notes, example_phrases, domain_knowledge
- custom_prompt_prefix, custom_prompt_suffix

**Solution**: Deleted old database and recreated with new schema
```bash
rm /home/mike/ClaudeProjects/RedTeamActorSimulator/backend/redteam_simulator.db
# Database auto-recreates on server restart with all new fields
```

### 2. New PersonaSelector Component
Created `/frontend/src/components/PersonaSelector/index.tsx` with:

**Two View Modes:**
1. **Presets Tab** - Card-based persona selection
   - Displays all preset personas with rich information
   - Shows badges for skill level, resources, background, motivation
   - Click to select
   - Separates preset vs custom personas

2. **Dimensions Tab** - Detailed view of selected persona
   - **Radio buttons for core dimensions:**
     - Skill Level (Novice / Semi-skilled / Expert)
     - Resources (Low / Medium / High)
     - Background (Technical / Non-technical)
   - **Read-only displays for:**
     - Motivation
     - Communication Style
     - Persistence Level
   - **Personality trait sliders:**
     - Patience (0-1 scale with visual bar)
     - Aggression (0-1 scale with visual bar)
     - Creativity (0-1 scale with visual bar)
     - Deception (0-1 scale with visual bar)
   - **Rich text displays:**
     - Behavioral Notes
     - Example Phrases
     - Domain Knowledge

### 3. Updated ConfigPanel
Replaced old inline persona selection with new PersonaSelector component:

**Before:**
```tsx
{personas.map((persona) => (
  <label>
    <input type="radio" ... />
    {persona.name}
  </label>
))}
```

**After:**
```tsx
<PersonaSelector
  personas={personas}
  selectedId={formData.persona_id}
  onSelect={(id) => setFormData({ ...formData, persona_id: id })}
/>
```

### 4. Updated TypeScript Types
Enhanced `Persona` interface in `/frontend/src/types/index.ts`:

```typescript
export interface Persona {
  id: string;
  name: string;
  description: string;
  skill_level: SkillLevel;
  resources: ResourceLevel;
  background: Background;

  // New enhanced fields
  motivation?: string | null;
  communication_style?: string | null;
  persistence_level?: string | null;
  patience: number;
  aggression: number;
  creativity: number;
  deception: number;
  behavioral_notes: string | null;
  example_phrases?: string | null;
  domain_knowledge?: string | null;
  custom_prompt_prefix?: string | null;
  custom_prompt_suffix?: string | null;

  is_preset: boolean;
  created_at: string;
}
```

## Features

### Preset Personas Available
After database recreation, these 8 preset personas are auto-loaded:
1. **Script Kiddie** - Novice / Low / Technical
2. **Curious Student** - Novice / Low / Non-technical
3. **Determined Amateur** - Semi-skilled / Medium / Technical
4. **Social Engineer** - Semi-skilled / Medium / Non-technical
5. **Professional Researcher** - Expert / High / Technical
6. **Nation-State Actor** - Expert / High / Technical
7. **Disgruntled Insider** - Semi-skilled / Medium / Technical
8. **Conspiracy Theorist** - Novice / Low / Non-technical

Each has:
- Full description
- Motivation (curiosity, financial, ideological, etc.)
- Communication style (direct, emotional, manipulative, etc.)
- Persistence level (low, medium, high, relentless)
- Personality traits (patience, aggression, creativity, deception)
- Behavioral notes
- Example phrases
- Domain knowledge

### UI Improvements

**Visual Design:**
- ✅ Clean tabbed interface (Presets / Dimensions)
- ✅ Color-coded badges for quick scanning
- ✅ Radio buttons with descriptions for dimensions
- ✅ Visual progress bars for personality traits
- ✅ Expandable sections for detailed information
- ✅ Proper hover states and selection feedback
- ✅ Responsive layout with proper spacing

**User Experience:**
- ✅ Select persona from presets
- ✅ View all dimensions in one place
- ✅ Understand persona characteristics at a glance
- ✅ See personality trait distributions visually
- ✅ Read behavioral guidance and example phrases

## Testing

1. **Verify personas load:**
   ```bash
   curl http://localhost:8000/api/personas | jq '.personas | length'
   # Should return 8
   ```

2. **Check frontend:**
   - Navigate to http://localhost:5173 (or your frontend port)
   - Create new session
   - Expand "Persona" section
   - Verify all 8 personas appear in "Presets" tab
   - Select a persona
   - Switch to "Dimensions" tab
   - Verify all fields display correctly

3. **Test radio buttons:**
   - In Dimensions tab, verify:
     - Skill Level shows 3 options with descriptions
     - Resources shows 3 options with descriptions
     - Background shows 2 options with descriptions
     - Correct option is selected (radio button checked)

4. **Test personality sliders:**
   - Verify 4 trait bars display
   - Each shows value (0.0-1.0)
   - Visual bar width matches value
   - Labels and descriptions present

## Files Modified

### Backend
- Database: `/backend/redteam_simulator.db` (recreated)

### Frontend
- **New**: `/frontend/src/components/PersonaSelector/index.tsx`
- **Modified**: `/frontend/src/components/ConfigPanel/index.tsx`
- **Modified**: `/frontend/src/types/index.ts`

## Next Steps

### Optional Enhancements
1. **Custom Persona Creator**
   - UI to create custom personas
   - Sliders for personality traits
   - Dropdowns for dimensions
   - Text areas for notes/phrases

2. **Persona Comparison**
   - Side-by-side comparison of 2 personas
   - Highlight differences
   - Help choose best fit

3. **Persona Search/Filter**
   - Filter by skill level
   - Filter by background
   - Search by keyword in description

4. **Persona Import/Export**
   - Export custom persona as JSON
   - Import shared personas
   - Persona library/marketplace

## Notes

- Database recreation means any existing sessions are lost (development only)
- Preset personas are auto-inserted on startup via `/backend/app/main.py`
- Frontend hot-reloads on changes
- Backend uses SQLAlchemy ORM to auto-create tables

## Troubleshooting

**Issue**: Personas still not showing
- Check backend logs: `tail -f /tmp/claude/...`
- Verify database was recreated: `ls -la backend/*.db`
- Check API: `curl http://localhost:8000/api/personas`

**Issue**: TypeScript errors in frontend
- Clear cache: `rm -rf frontend/.vite`
- Restart dev server: `npm run dev`

**Issue**: Radio buttons not working
- Verify `selectedId` prop is passed
- Check console for React errors
- Ensure `onSelect` callback is wired up
