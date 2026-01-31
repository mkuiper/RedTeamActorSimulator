# Features In Progress

## ✅ Completed

### CBRNE Objective Presets
- Added 13 new CBRNE and critical infrastructure test objectives
- Categories: Chemical, Biological, Radiological, Nuclear, Explosive, Critical Infrastructure
- API endpoint: `/api/objective-presets`
- Backend fully functional

### Persona Customization
- Editable persona dimensions (horizontal radio buttons)
- Editable personality traits (sliders)
- Modifications tracked per persona
- All attributes can be tweaked after selecting a preset

### Ollama Support
- Backend configured for local models
- Documentation: `docs/OLLAMA_SETUP.md`
- Requires Ollama installation on system

## 🚧 In Progress (UI Needed)

### Custom Persona Creator
**Status:** API ready, UI needed

Create completely custom personas from scratch:
- Name and description
- All dimensional attributes (skill, resources, background)
- Behavioral traits (motivation, communication, persistence)
- Personality sliders (patience, aggression, creativity, deception)
- Behavioral notes and example phrases

**Implementation:**
- Add "Create Custom" button in Persona section
- Modal or expandable form for persona creation
- Calls `personasApi.create(data)`

### Objective Preset Selector
**Status:** API ready, UI needed

Quick-load preset objectives by category:
- Browse by category (CBRNE-Chemical, CBRNE-Biological, etc.)
- Preview objective details
- One-click load into session form
- Multiple objective selection for chains

**Implementation:**
- Add "Load Preset" button in Objectives section
- Dropdown or modal showing categories
- List objectives with descriptions
- Click to populate objective form fields

## 🎯 Suggested UI Locations

### ConfigPanel - Persona Section
```tsx
{expandedSections.persona && (
  <div className="pl-6">
    <div className="flex gap-2 mb-3">
      <button
        onClick={() => setShowCustomPersonaCreator(true)}
        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-600 text-white rounded"
      >
        <Plus className="w-3 h-3" />
        Create Custom Persona
      </button>
    </div>

    <PersonaSelector ... />

    {showCustomPersonaCreator && (
      <CustomPersonaCreator
        onSave={(persona) => {
          // Add to personas list
          setShowCustomPersonaCreator(false);
        }}
        onCancel={() => setShowCustomPersonaCreator(false)}
      />
    )}
  </div>
)}
```

### ConfigPanel - Objectives Section
```tsx
{expandedSections.objectives && (
  <div className="space-y-4 pl-6">
    <div className="flex gap-2">
      <button
        onClick={() => setShowObjectivePresets(true)}
        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-purple-600 text-white rounded"
      >
        <Sparkles className="w-3 h-3" />
        Load Preset
      </button>
    </div>

    {showObjectivePresets && (
      <ObjectivePresetSelector
        presets={objectivePresets}
        categories={objectiveCategories}
        onSelect={(objective) => {
          // Populate formData.objectives
          setShowObjectivePresets(false);
        }}
        onCancel={() => setShowObjectivePresets(false)}
      />
    )}

    {/* Existing objective form fields */}
  </div>
)}
```

## 📊 API Endpoints Available

- `GET /api/objective-presets` - List all presets
- `GET /api/objective-presets/categories` - List categories
- `GET /api/objective-presets/by-category/{category}` - Filter by category
- `POST /api/personas` - Create custom persona
- `GET /api/personas` - List all personas (presets + custom)

## 🎨 Component Structure Needed

```
frontend/src/components/
├── CustomPersonaCreator/
│   └── index.tsx          # Form for creating personas from scratch
├── ObjectivePresetSelector/
│   └── index.tsx          # Browse and select preset objectives
├── PersonaSelector/
│   └── index.tsx          # ✅ Already updated with editing
└── ConfigPanel/
    └── index.tsx          # ✅ Partially updated (imports ready)
```

## 💡 Implementation Priority

1. **Objective Preset Selector** (Highest impact)
   - Users can quickly test CBRNE scenarios
   - No manual typing of complex objectives

2. **Custom Persona Creator** (Medium priority)
   - Current editing of presets covers most use cases
   - Custom from scratch is nice-to-have

## 🔧 Next Steps

1. Create `ObjectivePresetSelector` component
2. Create `CustomPersonaCreator` component
3. Integrate both into `ConfigPanel`
4. Test end-to-end workflow
5. Update documentation

## 📝 Notes

- All backend work is complete
- Frontend just needs UI components to expose functionality
- Data structures and APIs are ready
- No database changes required
