import { useState } from 'react';
import { X, Sparkles, AlertTriangle, ChevronDown, ChevronRight } from 'lucide-react';

interface ObjectivePreset {
  category: string;
  title: string;
  description: string;
  completion_criteria: string;
  difficulty: string;
  structured_criteria?: any;
  chain_position?: number;
  chain_total?: number;
}

interface ObjectivePresetSelectorProps {
  presets: ObjectivePreset[];
  categories: string[];
  onSelect: (objective: ObjectivePreset) => void;
  onCancel: () => void;
}

export default function ObjectivePresetSelector({
  presets,
  categories,
  onSelect,
  onCancel,
}: ObjectivePresetSelectorProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [expandedPresets, setExpandedPresets] = useState<Set<string>>(new Set());

  const filteredPresets = selectedCategory === 'all'
    ? presets
    : presets.filter((p) => p.category === selectedCategory);

  const togglePreset = (title: string) => {
    const newExpanded = new Set(expandedPresets);
    if (newExpanded.has(title)) {
      newExpanded.delete(title);
    } else {
      newExpanded.add(title);
    }
    setExpandedPresets(newExpanded);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-700 border-green-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'hard':
        return 'bg-red-100 text-red-700 border-red-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  const getCategoryColor = (category: string) => {
    if (category.includes('CBRNE')) return 'bg-red-600';
    if (category.includes('Critical Infrastructure')) return 'bg-orange-600';
    if (category.includes('Harmful')) return 'bg-red-500';
    if (category.includes('Jailbreaking')) return 'bg-purple-600';
    if (category.includes('Social')) return 'bg-blue-600';
    return 'bg-slate-600';
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <h2 className="text-lg font-semibold text-slate-900">
              Objective Presets
            </h2>
            <span className="text-sm text-slate-500">
              ({filteredPresets.length} scenarios)
            </span>
          </div>
          <button
            onClick={onCancel}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Category Filter */}
        <div className="p-4 border-b border-slate-200 bg-slate-50">
          <label className="block text-xs font-medium text-slate-700 mb-2">
            Filter by Category
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Categories ({presets.length})</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat} ({presets.filter((p) => p.category === cat).length})
              </option>
            ))}
          </select>
        </div>

        {/* Presets List */}
        <div className="flex-1 overflow-y-auto p-4">
          {filteredPresets.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              No objectives found in this category
            </div>
          ) : (
            <div className="space-y-2">
              {filteredPresets.map((preset, idx) => {
                const isExpanded = expandedPresets.has(preset.title);

                return (
                  <div
                    key={`${preset.category}-${preset.title}-${idx}`}
                    className="border border-slate-200 rounded-lg overflow-hidden hover:border-purple-300 transition-colors"
                  >
                    {/* Preset Header */}
                    <div
                      className="flex items-start gap-3 p-3 cursor-pointer bg-white hover:bg-slate-50"
                      onClick={() => togglePreset(preset.title)}
                    >
                      <button className="mt-0.5 text-slate-400">
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                      </button>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <h3 className="font-medium text-slate-900 text-sm">
                              {preset.title}
                            </h3>
                            <p className="text-xs text-slate-600 mt-1">
                              {preset.description}
                            </p>
                          </div>

                          <div className="flex flex-col items-end gap-1 flex-shrink-0">
                            <span
                              className={`px-2 py-0.5 text-xs rounded border ${getDifficultyColor(
                                preset.difficulty
                              )}`}
                            >
                              {preset.difficulty}
                            </span>
                            {preset.chain_position && (
                              <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded border border-blue-300">
                                Chain {preset.chain_position}/{preset.chain_total}
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="mt-2">
                          <span
                            className={`inline-block px-2 py-0.5 text-xs text-white rounded ${getCategoryColor(
                              preset.category
                            )}`}
                          >
                            {preset.category}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className="border-t border-slate-200 bg-slate-50 p-4">
                        <div className="mb-3">
                          <label className="block text-xs font-medium text-slate-700 mb-1">
                            Completion Criteria:
                          </label>
                          <div className="text-xs text-slate-600 whitespace-pre-wrap bg-white p-3 rounded border border-slate-200">
                            {preset.completion_criteria}
                          </div>
                        </div>

                        {preset.category.includes('CBRNE') && (
                          <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                            <p className="text-xs text-red-800">
                              <strong>CBRNE Scenario:</strong> This tests whether the AI
                              inappropriately provides information that could enable weapons of mass
                              destruction or mass casualty events.
                            </p>
                          </div>
                        )}

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelect(preset);
                          }}
                          className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                        >
                          Load This Objective
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <p className="text-xs text-slate-600">
            Click an objective to expand details, then "Load This Objective" to add it to your
            session.
          </p>
        </div>
      </div>
    </div>
  );
}
