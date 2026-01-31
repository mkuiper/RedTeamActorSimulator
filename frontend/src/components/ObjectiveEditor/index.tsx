import { useState } from 'react';
import {
  Plus,
  Trash2,
  GripVertical,
  Check,
  ChevronDown,
  ChevronRight,
  BookOpen,
  Edit3,
} from 'lucide-react';

interface CriteriaItem {
  id: string;
  text: string;
  required: boolean;
  met: boolean;
}

interface StructuredCriteria {
  match_mode: 'all' | 'any' | 'majority' | 'threshold';
  threshold?: number;
  items: CriteriaItem[];
}

export interface ObjectiveData {
  title: string;
  description: string;
  completion_criteria: string;
  structured_criteria?: StructuredCriteria;
  difficulty?: string;
}

interface ObjectiveEditorProps {
  objectives: ObjectiveData[];
  onChange: (objectives: ObjectiveData[]) => void;
  presetObjectives?: any[];
}

export default function ObjectiveEditor({
  objectives,
  onChange,
  presetObjectives = [],
}: ObjectiveEditorProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [showPresets, setShowPresets] = useState(false);
  const [presetCategory, setPresetCategory] = useState<string>('all');

  const updateObjective = (index: number, updates: Partial<ObjectiveData>) => {
    const newObjectives = [...objectives];
    newObjectives[index] = { ...newObjectives[index], ...updates };
    onChange(newObjectives);
  };

  const addObjective = () => {
    onChange([
      ...objectives,
      {
        title: '',
        description: '',
        completion_criteria: '',
        structured_criteria: {
          match_mode: 'all',
          items: [],
        },
        difficulty: 'medium',
      },
    ]);
    setEditingIndex(objectives.length);
  };

  const removeObjective = (index: number) => {
    onChange(objectives.filter((_, i) => i !== index));
    if (editingIndex === index) setEditingIndex(null);
  };

  const addCriterion = (objectiveIndex: number) => {
    const objective = objectives[objectiveIndex];
    const criteria = objective.structured_criteria || {
      match_mode: 'all',
      items: [],
    };

    const newItem: CriteriaItem = {
      id: `c${criteria.items.length + 1}`,
      text: '',
      required: true,
      met: false,
    };

    updateObjective(objectiveIndex, {
      structured_criteria: {
        ...criteria,
        items: [...criteria.items, newItem],
      },
    });
  };

  const updateCriterion = (
    objectiveIndex: number,
    criterionIndex: number,
    updates: Partial<CriteriaItem>
  ) => {
    const objective = objectives[objectiveIndex];
    const criteria = objective.structured_criteria!;
    const newItems = [...criteria.items];
    newItems[criterionIndex] = { ...newItems[criterionIndex], ...updates };

    updateObjective(objectiveIndex, {
      structured_criteria: {
        ...criteria,
        items: newItems,
      },
    });
  };

  const removeCriterion = (objectiveIndex: number, criterionIndex: number) => {
    const objective = objectives[objectiveIndex];
    const criteria = objective.structured_criteria!;

    updateObjective(objectiveIndex, {
      structured_criteria: {
        ...criteria,
        items: criteria.items.filter((_, i) => i !== criterionIndex),
      },
    });
  };

  const loadPreset = (preset: any) => {
    const newObjective: ObjectiveData = {
      title: preset.title,
      description: preset.description,
      completion_criteria: preset.completion_criteria,
      structured_criteria: preset.structured_criteria || {
        match_mode: preset.structured_criteria?.match_mode || 'all',
        items: preset.structured_criteria?.items || [],
      },
      difficulty: preset.difficulty || 'medium',
    };

    onChange([...objectives, newObjective]);
    setShowPresets(false);
  };

  const categories = presetObjectives.reduce((acc, preset) => {
    const cat = preset.category || 'Other';
    if (!acc.includes(cat)) acc.push(cat);
    return acc;
  }, ['all'] as string[]);

  const filteredPresets = presetCategory === 'all'
    ? presetObjectives
    : presetObjectives.filter((p) => p.category === presetCategory);

  return (
    <div className="space-y-4">
      {/* Preset Objectives Browser */}
      <div className="border border-slate-200 rounded-lg">
        <button
          onClick={() => setShowPresets(!showPresets)}
          className="w-full flex items-center justify-between p-3 hover:bg-slate-50 transition-colors"
        >
          <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
            <BookOpen className="w-4 h-4" />
            Browse Preset Objectives
          </span>
          {showPresets ? (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-slate-400" />
          )}
        </button>

        {showPresets && (
          <div className="border-t border-slate-200 p-3 space-y-3">
            {/* Category Filter */}
            <div className="flex gap-2 flex-wrap">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setPresetCategory(cat)}
                  className={`px-3 py-1 text-xs rounded-full transition-colors ${
                    presetCategory === cat
                      ? 'bg-red-100 text-red-700 font-medium'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Preset List */}
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredPresets.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No presets available</p>
              ) : (
                filteredPresets.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadPreset(preset)}
                    className="w-full text-left p-2 border border-slate-200 rounded hover:border-red-300 hover:bg-red-50 transition-colors group"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-sm text-slate-800">{preset.title}</div>
                        <div className="text-xs text-slate-500 mt-0.5 line-clamp-2">
                          {preset.description}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-slate-400">{preset.category}</span>
                          <span
                            className={`text-xs px-1.5 py-0.5 rounded ${
                              preset.difficulty === 'easy'
                                ? 'bg-green-100 text-green-700'
                                : preset.difficulty === 'hard'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }`}
                          >
                            {preset.difficulty}
                          </span>
                        </div>
                      </div>
                      <Plus className="w-4 h-4 text-slate-400 group-hover:text-red-600 flex-shrink-0 mt-1" />
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Objective List */}
      <div className="space-y-3">
        {objectives.map((obj, objIndex) => (
          <div
            key={objIndex}
            className={`border rounded-lg transition-all ${
              editingIndex === objIndex
                ? 'border-red-300 shadow-md'
                : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            {/* Objective Header */}
            <div className="flex items-center justify-between p-3 bg-slate-50">
              <div className="flex items-center gap-2 flex-1">
                <GripVertical className="w-4 h-4 text-slate-400" />
                <span className="text-sm font-medium text-slate-700">
                  {obj.title || `Objective ${objIndex + 1}`}
                </span>
                {obj.difficulty && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${
                      obj.difficulty === 'easy'
                        ? 'bg-green-100 text-green-700'
                        : obj.difficulty === 'hard'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {obj.difficulty}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setEditingIndex(editingIndex === objIndex ? null : objIndex)}
                  className="p-1 hover:bg-slate-200 rounded transition-colors"
                >
                  <Edit3 className="w-4 h-4 text-slate-600" />
                </button>
                {objectives.length > 1 && (
                  <button
                    onClick={() => removeObjective(objIndex)}
                    className="p-1 hover:bg-red-100 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </button>
                )}
              </div>
            </div>

            {/* Objective Editor (expanded) */}
            {editingIndex === objIndex && (
              <div className="p-4 space-y-4">
                {/* Title */}
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Title *</label>
                  <input
                    type="text"
                    value={obj.title}
                    onChange={(e) => updateObjective(objIndex, { title: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    placeholder="e.g., System Prompt Extraction"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">
                    Description (What actor sees) *
                  </label>
                  <textarea
                    value={obj.description}
                    onChange={(e) => updateObjective(objIndex, { description: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    rows={3}
                    placeholder="Describe what the actor is trying to achieve..."
                  />
                </div>

                {/* Difficulty */}
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Difficulty</label>
                  <select
                    value={obj.difficulty || 'medium'}
                    onChange={(e) => updateObjective(objIndex, { difficulty: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>

                {/* Structured Criteria */}
                <div className="border-t pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-medium text-slate-700">
                      Completion Criteria (Hidden from actor)
                    </label>
                    <button
                      onClick={() => addCriterion(objIndex)}
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-red-50 text-red-600 rounded hover:bg-red-100 transition-colors"
                    >
                      <Plus className="w-3 h-3" />
                      Add Criterion
                    </button>
                  </div>

                  {/* Match Mode */}
                  <div className="mb-3">
                    <label className="text-xs text-slate-600 mb-1 block">Match Mode</label>
                    <div className="flex gap-2">
                      {(['all', 'any', 'majority', 'threshold'] as const).map((mode) => (
                        <button
                          key={mode}
                          onClick={() =>
                            updateObjective(objIndex, {
                              structured_criteria: {
                                ...obj.structured_criteria!,
                                match_mode: mode,
                              },
                            })
                          }
                          className={`px-3 py-1 text-xs rounded transition-colors ${
                            obj.structured_criteria?.match_mode === mode
                              ? 'bg-red-600 text-white'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          {mode.toUpperCase()}
                        </button>
                      ))}
                    </div>
                    {obj.structured_criteria?.match_mode === 'threshold' && (
                      <input
                        type="number"
                        min={1}
                        value={obj.structured_criteria.threshold || 1}
                        onChange={(e) =>
                          updateObjective(objIndex, {
                            structured_criteria: {
                              ...obj.structured_criteria!,
                              threshold: parseInt(e.target.value),
                            },
                          })
                        }
                        className="mt-2 w-20 px-2 py-1 border border-slate-300 rounded text-xs"
                        placeholder="Min #"
                      />
                    )}
                  </div>

                  {/* Criteria Items */}
                  <div className="space-y-2">
                    {obj.structured_criteria?.items.map((criterion, critIndex) => (
                      <div
                        key={criterion.id}
                        className="flex items-start gap-2 p-2 bg-slate-50 rounded"
                      >
                        <input
                          type="checkbox"
                          checked={criterion.required}
                          onChange={(e) =>
                            updateCriterion(objIndex, critIndex, { required: e.target.checked })
                          }
                          className="mt-1.5 rounded border-slate-300 text-red-600 focus:ring-red-500"
                          title="Required criterion"
                        />
                        <input
                          type="text"
                          value={criterion.text}
                          onChange={(e) =>
                            updateCriterion(objIndex, critIndex, { text: e.target.value })
                          }
                          className="flex-1 px-2 py-1 border border-slate-300 rounded text-xs"
                          placeholder="Criterion description..."
                        />
                        <button
                          onClick={() => removeCriterion(objIndex, critIndex)}
                          className="p-1 hover:bg-red-100 rounded transition-colors"
                        >
                          <Trash2 className="w-3 h-3 text-red-600" />
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Legacy Text Criteria */}
                  <div className="mt-3">
                    <label className="text-xs text-slate-600 mb-1 block">
                      Text Criteria (Legacy/Fallback)
                    </label>
                    <textarea
                      value={obj.completion_criteria}
                      onChange={(e) =>
                        updateObjective(objIndex, { completion_criteria: e.target.value })
                      }
                      className="w-full px-2 py-1.5 border border-slate-300 rounded text-xs font-mono"
                      rows={3}
                      placeholder="- Point 1&#10;- Point 2&#10;- Point 3"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add Objective Button */}
      <button
        onClick={addObjective}
        className="w-full flex items-center justify-center gap-2 py-3 border-2 border-dashed border-slate-300 rounded-lg text-sm text-slate-600 hover:border-red-300 hover:text-red-600 hover:bg-red-50 transition-colors"
      >
        <Plus className="w-4 h-4" />
        Add Objective to Chain
      </button>
    </div>
  );
}
