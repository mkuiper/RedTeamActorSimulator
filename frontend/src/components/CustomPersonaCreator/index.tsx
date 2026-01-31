import { useState } from 'react';
import { X, User, Save } from 'lucide-react';
import type { PersonaFormData } from '../../types';

interface CustomPersonaCreatorProps {
  onSave: (persona: PersonaFormData) => void;
  onCancel: () => void;
}

export default function CustomPersonaCreator({ onSave, onCancel }: CustomPersonaCreatorProps) {
  const [formData, setFormData] = useState<PersonaFormData>({
    name: '',
    description: '',
    skill_level: 'novice',
    resources: 'low',
    background: 'technical',
    behavioral_notes: '',
  });

  const handleSubmit = () => {
    if (!formData.name || !formData.description) {
      alert('Please provide a name and description');
      return;
    }
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <User className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-slate-900">Create Custom Persona</h2>
          </div>
          <button onClick={onCancel} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Persona Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Advanced Researcher"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe this persona's characteristics, goals, and typical behavior..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>

          {/* Skill Level */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Skill Level *</label>
            <div className="flex gap-3">
              {(['novice', 'semi_skilled', 'expert'] as const).map((level) => (
                <label key={level} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="skill_level"
                    value={level}
                    checked={formData.skill_level === level}
                    onChange={(e) =>
                      setFormData({ ...formData, skill_level: e.target.value as any })
                    }
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-slate-700">
                    {level === 'novice' ? 'Novice' : level === 'semi_skilled' ? 'Semi-Skilled' : 'Expert'}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Resources */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Resources *</label>
            <div className="flex gap-3">
              {(['low', 'medium', 'high'] as const).map((level) => (
                <label key={level} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="resources"
                    value={level}
                    checked={formData.resources === level}
                    onChange={(e) => setFormData({ ...formData, resources: e.target.value as any })}
                    className="text-green-600 focus:ring-green-500"
                  />
                  <span className="text-sm text-slate-700">
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Background */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Background *</label>
            <div className="flex gap-3">
              {(['technical', 'non_technical'] as const).map((bg) => (
                <label key={bg} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="background"
                    value={bg}
                    checked={formData.background === bg}
                    onChange={(e) => setFormData({ ...formData, background: e.target.value as any })}
                    className="text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm text-slate-700">
                    {bg === 'technical' ? 'Technical' : 'Non-Technical'}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Behavioral Notes */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Behavioral Notes (Optional)
            </label>
            <textarea
              value={formData.behavioral_notes}
              onChange={(e) => setFormData({ ...formData, behavioral_notes: e.target.value })}
              placeholder="Additional behavioral guidance, tactics, or characteristics..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end gap-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            <Save className="w-4 h-4" />
            Create Persona
          </button>
        </div>
      </div>
    </div>
  );
}
