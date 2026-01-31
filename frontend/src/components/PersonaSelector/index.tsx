import { useState } from 'react';
import { User, Sliders, BookText, Lightbulb } from 'lucide-react';
import type { Persona } from '../../types';

interface PersonaSelectorProps {
  personas: Persona[];
  selectedId: string;
  onSelect: (personaId: string) => void;
}

export default function PersonaSelector({
  personas,
  selectedId,
  onSelect,
}: PersonaSelectorProps) {
  const [viewMode, setViewMode] = useState<'presets' | 'dimensions'>('presets');
  const selectedPersona = personas.find((p) => p.id === selectedId);

  // Group personas by preset status
  const presetPersonas = personas.filter((p) => p.is_preset);
  const customPersonas = personas.filter((p) => !p.is_preset);

  const renderDimensionSelector = () => {
    if (!selectedPersona) return null;

    return (
      <div className="space-y-3">
        {/* Core Dimensions - Horizontal Layout */}
        <div className="grid grid-cols-3 gap-2">
          {/* Skill Level */}
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Skill Level
            </label>
            <div className="flex gap-1">
              {(['novice', 'semi_skilled', 'expert'] as const).map((level) => (
                <button
                  key={level}
                  className={`flex-1 px-2 py-1 text-xs rounded border transition-colors ${
                    selectedPersona.skill_level === level
                      ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                      : 'border-slate-200 bg-white text-slate-600'
                  }`}
                  disabled
                >
                  {level === 'novice' ? 'Nov' : level === 'semi_skilled' ? 'Semi' : 'Exp'}
                </button>
              ))}
            </div>
          </div>

          {/* Resources */}
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Resources
            </label>
            <div className="flex gap-1">
              {(['low', 'medium', 'high'] as const).map((level) => (
                <button
                  key={level}
                  className={`flex-1 px-2 py-1 text-xs rounded border transition-colors ${
                    selectedPersona.resources === level
                      ? 'border-green-500 bg-green-50 text-green-700 font-medium'
                      : 'border-slate-200 bg-white text-slate-600'
                  }`}
                  disabled
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Background */}
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Background
            </label>
            <div className="flex gap-1">
              {(['technical', 'non_technical'] as const).map((bg) => (
                <button
                  key={bg}
                  className={`flex-1 px-2 py-1 text-xs rounded border transition-colors ${
                    selectedPersona.background === bg
                      ? 'border-purple-500 bg-purple-50 text-purple-700 font-medium'
                      : 'border-slate-200 bg-white text-slate-600'
                  }`}
                  disabled
                >
                  {bg === 'technical' ? 'Tech' : 'Non-Tech'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Behavioral Attributes - Horizontal */}
        <div className="grid grid-cols-2 gap-2">
          {/* Motivation */}
          {selectedPersona.motivation && (
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Motivation
              </label>
              <div className="px-2 py-1.5 bg-orange-50 border border-orange-200 rounded text-xs text-orange-700 font-medium">
                {selectedPersona.motivation.replace('_', ' ')}
              </div>
            </div>
          )}

          {/* Communication Style */}
          {selectedPersona.communication_style && (
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Communication
              </label>
              <div className="px-2 py-1.5 bg-indigo-50 border border-indigo-200 rounded text-xs text-indigo-700 font-medium">
                {selectedPersona.communication_style.replace('_', ' ')}
              </div>
            </div>
          )}
        </div>

        {/* Personality Traits - Compact Grid */}
        <div className="border-t pt-3">
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Personality Traits
          </label>
          <div className="grid grid-cols-2 gap-2">
            {[
              { key: 'patience', label: 'Patience' },
              { key: 'aggression', label: 'Aggression' },
              { key: 'creativity', label: 'Creativity' },
              { key: 'deception', label: 'Deception' },
            ].map((trait) => (
              <div key={trait.key} className="bg-slate-50 p-2 rounded border border-slate-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-slate-700">{trait.label}</span>
                  <span className="text-xs text-slate-600 font-semibold">
                    {selectedPersona[trait.key as keyof Persona]?.toFixed(1)}
                  </span>
                </div>
                <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-red-400 to-red-600 rounded-full"
                    style={{
                      width: `${(Number(selectedPersona[trait.key as keyof Persona]) || 0) * 100}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Behavioral Notes */}
        {selectedPersona.behavioral_notes && (
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-2 flex items-center gap-1">
              <BookText className="w-3 h-3" />
              Behavioral Notes
            </label>
            <div className="p-2 bg-slate-50 rounded border border-slate-200 text-xs text-slate-600">
              {selectedPersona.behavioral_notes}
            </div>
          </div>
        )}

        {/* Example Phrases */}
        {selectedPersona.example_phrases && (
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-2">
              Example Phrases
            </label>
            <div className="p-2 bg-slate-50 rounded border border-slate-200 text-xs text-slate-600 italic">
              {selectedPersona.example_phrases}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-3">
      {/* View Mode Tabs */}
      <div className="flex gap-2 border-b border-slate-200">
        <button
          onClick={() => setViewMode('presets')}
          className={`px-3 py-2 text-sm font-medium transition-colors border-b-2 ${
            viewMode === 'presets'
              ? 'border-red-600 text-red-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <User className="w-4 h-4 inline mr-1" />
          Presets
        </button>
        <button
          onClick={() => setViewMode('dimensions')}
          className={`px-3 py-2 text-sm font-medium transition-colors border-b-2 ${
            viewMode === 'dimensions'
              ? 'border-red-600 text-red-600'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
          disabled={!selectedPersona}
        >
          <Sliders className="w-4 h-4 inline mr-1" />
          Dimensions
        </button>
      </div>

      {/* Content */}
      {viewMode === 'presets' ? (
        <div className="space-y-3">
          {/* Preset Personas Dropdown */}
          {presetPersonas.length > 0 && (
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Preset Personas
              </label>
              <select
                value={selectedId && presetPersonas.find(p => p.id === selectedId) ? selectedId : ''}
                onChange={(e) => onSelect(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">Select a preset persona...</option>
                {presetPersonas.map((persona) => (
                  <option key={persona.id} value={persona.id}>
                    {persona.name} - {persona.skill_level.replace('_', ' ')} / {persona.resources} resources
                  </option>
                ))}
              </select>

              {/* Show selected persona details */}
              {selectedPersona && selectedPersona.is_preset && (
                <div className="p-3 border border-slate-200 rounded-lg bg-slate-50">
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-slate-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm text-slate-900">{selectedPersona.name}</div>
                      <div className="text-xs text-slate-600 mt-1">
                        {selectedPersona.description}
                      </div>
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                          {selectedPersona.skill_level.replace('_', ' ')}
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">
                          {selectedPersona.resources} resources
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700">
                          {selectedPersona.background.replace('_', '-')}
                        </span>
                        {selectedPersona.motivation && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-700">
                            {selectedPersona.motivation}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Custom Personas Dropdown */}
          {customPersonas.length > 0 && (
            <div className="space-y-2">
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Custom Personas
              </label>
              <select
                value={selectedId && customPersonas.find(p => p.id === selectedId) ? selectedId : ''}
                onChange={(e) => onSelect(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">Select a custom persona...</option>
                {customPersonas.map((persona) => (
                  <option key={persona.id} value={persona.id}>
                    {persona.name} - {persona.skill_level.replace('_', ' ')} / {persona.resources}
                  </option>
                ))}
              </select>

              {/* Show selected custom persona details */}
              {selectedPersona && !selectedPersona.is_preset && (
                <div className="p-3 border border-slate-200 rounded-lg bg-slate-50">
                  <div className="font-medium text-sm text-slate-900">{selectedPersona.name}</div>
                  <div className="text-xs text-slate-600 mt-1">
                    {selectedPersona.description}
                  </div>
                  <div className="text-xs text-slate-500 mt-2">
                    {selectedPersona.skill_level.replace('_', ' ')} / {selectedPersona.resources} /{' '}
                    {selectedPersona.background.replace('_', '-')}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        renderDimensionSelector()
      )}
    </div>
  );
}
