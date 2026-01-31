import { useState } from 'react';
import { User, Sliders, BookText, Lightbulb } from 'lucide-react';
import type { Persona } from '../../types';

interface PersonaSelectorProps {
  personas: Persona[];
  selectedId: string;
  onSelect: (personaId: string) => void;
  onPersonaUpdate?: (personaId: string, updates: Partial<Persona>) => void;
}

export default function PersonaSelector({
  personas,
  selectedId,
  onSelect,
  onPersonaUpdate,
}: PersonaSelectorProps) {
  const [viewMode, setViewMode] = useState<'presets' | 'dimensions'>('presets');
  const selectedPersona = personas.find((p) => p.id === selectedId);

  // Group personas by preset status
  const presetPersonas = personas.filter((p) => p.is_preset);
  const customPersonas = personas.filter((p) => !p.is_preset);

  const renderDimensionSelector = () => {
    if (!selectedPersona) return null;

    const handleUpdate = (field: keyof Persona, value: any) => {
      if (onPersonaUpdate) {
        onPersonaUpdate(selectedPersona.id, { [field]: value });
      }
    };

    return (
      <div className="space-y-3">
        {/* Skill Level - Horizontal Radio Buttons */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Skill Level
          </label>
          <div className="flex gap-3">
            {(['novice', 'semi_skilled', 'expert'] as const).map((level) => (
              <label
                key={level}
                className="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="radio"
                  name="skill_level"
                  value={level}
                  checked={selectedPersona.skill_level === level}
                  onChange={() => handleUpdate('skill_level', level)}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-slate-700">
                  {level === 'novice' ? 'Novice' : level === 'semi_skilled' ? 'Semi-Skilled' : 'Expert'}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Resources - Horizontal Radio Buttons */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Resources
          </label>
          <div className="flex gap-3">
            {(['low', 'medium', 'high'] as const).map((level) => (
              <label
                key={level}
                className="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="radio"
                  name="resources"
                  value={level}
                  checked={selectedPersona.resources === level}
                  onChange={() => handleUpdate('resources', level)}
                  className="text-green-600 focus:ring-green-500"
                />
                <span className="text-sm text-slate-700">
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Background - Horizontal Radio Buttons */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Background
          </label>
          <div className="flex gap-3">
            {(['technical', 'non_technical', 'mixed'] as const).map((bg) => (
              <label
                key={bg}
                className="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="radio"
                  name="background"
                  value={bg}
                  checked={selectedPersona.background === bg}
                  onChange={() => handleUpdate('background', bg)}
                  className="text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-slate-700">
                  {bg === 'technical' ? 'Technical' : bg === 'non_technical' ? 'Non-Technical' : 'Mixed'}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Motivation - Horizontal */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Motivation
          </label>
          <select
            value={selectedPersona.motivation || ''}
            onChange={(e) => handleUpdate('motivation', e.target.value)}
            className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded focus:ring-2 focus:ring-orange-500"
          >
            <option value="curiosity">Curiosity</option>
            <option value="financial">Financial</option>
            <option value="ideological">Ideological</option>
            <option value="revenge">Revenge</option>
            <option value="thrill">Thrill</option>
            <option value="professional">Professional</option>
            <option value="academic">Academic</option>
          </select>
        </div>

        {/* Communication Style - Horizontal */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Communication Style
          </label>
          <select
            value={selectedPersona.communication_style || ''}
            onChange={(e) => handleUpdate('communication_style', e.target.value)}
            className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded focus:ring-2 focus:ring-indigo-500"
          >
            <option value="direct">Direct</option>
            <option value="indirect">Indirect</option>
            <option value="emotional">Emotional</option>
            <option value="logical">Logical</option>
            <option value="manipulative">Manipulative</option>
            <option value="authoritative">Authoritative</option>
            <option value="submissive">Submissive</option>
          </select>
        </div>

        {/* Persistence Level - Horizontal */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Persistence Level
          </label>
          <div className="flex gap-3">
            {(['low', 'medium', 'high', 'relentless'] as const).map((level) => (
              <label
                key={level}
                className="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="radio"
                  name="persistence_level"
                  value={level}
                  checked={selectedPersona.persistence_level === level}
                  onChange={() => handleUpdate('persistence_level', level)}
                  className="text-red-600 focus:ring-red-500"
                />
                <span className="text-sm text-slate-700">
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Personality Traits - Editable Sliders */}
        <div className="border-t pt-3">
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Personality Traits (0-1 scale)
          </label>
          <div className="grid grid-cols-2 gap-3">
            {[
              { key: 'patience', label: 'Patience' },
              { key: 'aggression', label: 'Aggression' },
              { key: 'creativity', label: 'Creativity' },
              { key: 'deception', label: 'Deception' },
            ].map((trait) => (
              <div key={trait.key}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-slate-700">{trait.label}</span>
                  <span className="text-xs text-slate-600 font-semibold">
                    {(selectedPersona[trait.key as keyof Persona] as number)?.toFixed(1)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={selectedPersona[trait.key as keyof Persona] as number}
                  onChange={(e) => handleUpdate(trait.key as keyof Persona, parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-red-600"
                />
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
