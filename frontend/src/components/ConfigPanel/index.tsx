import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ChevronDown,
  ChevronRight,
  User,
  Cpu,
  Target,
  Link2,
  Play,
  Square,
  Trash2,
  Download,
  Upload,
} from 'lucide-react';
import { personasApi, providersApi, simulationApi, exportApi, sessionsApi } from '../../services/api';
import type { Session, SessionFormData, Persona, Provider } from '../../types';
import PersonaSelector from '../PersonaSelector';

interface ConfigPanelProps {
  sessions: Session[];
  selectedSession: Session | null;
  showNewSession: boolean;
  onSessionSelect: (id: string) => void;
  onSessionCreated: (session: Session) => void;
}

export default function ConfigPanel({
  sessions,
  selectedSession,
  showNewSession,
  onSessionSelect,
  onSessionCreated,
}: ConfigPanelProps) {
  const [expandedSections, setExpandedSections] = useState({
    sessions: true,
    persona: true,
    models: true,
    objectives: true,
  });

  const { data: personasData } = useQuery({
    queryKey: ['personas'],
    queryFn: personasApi.list,
  });

  const { data: providersData } = useQuery({
    queryKey: ['providers'],
    queryFn: providersApi.list,
  });

  const [formData, setFormData] = useState<SessionFormData>({
    name: '',
    max_turns: 20,
    sneaky_mode: false,
    actor_model: 'anthropic:claude-sonnet-4-5-20250929',
    assessor_model: 'anthropic:claude-sonnet-4-5-20250929',
    subject_model: 'openai:gpt-4o',
    persona_id: '',
    objectives: [{ title: '', description: '', completion_criteria: '' }],
  });

  // Track persona modifications
  const [personaModifications, setPersonaModifications] = useState<Record<string, Partial<Persona>>>({});

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleCreateSession = async () => {
    if (!formData.name || !formData.persona_id || !formData.objectives[0].title) {
      alert('Please fill in required fields');
      return;
    }

    try {
      const session = await sessionsApi.create(formData);
      onSessionCreated(session);
    } catch (error) {
      console.error('Failed to create session:', error);
      alert('Failed to create session');
    }
  };

  const handleStartSimulation = async () => {
    if (!selectedSession) return;
    try {
      await simulationApi.start(selectedSession.id);
      // Refresh session to get updated status
      onSessionSelect(selectedSession.id);
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
  };

  const handleStopSimulation = async () => {
    if (!selectedSession) return;
    try {
      await simulationApi.stop(selectedSession.id);
      onSessionSelect(selectedSession.id);
    } catch (error) {
      console.error('Failed to stop simulation:', error);
    }
  };

  const handleExport = async () => {
    if (!selectedSession) return;
    try {
      const blob = await exportApi.exportSession(selectedSession.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session_${selectedSession.id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export session:', error);
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const result = await exportApi.importSession(file);
      onSessionSelect(result.session_id);
    } catch (error) {
      console.error('Failed to import session:', error);
    }
  };

  const personas = personasData?.personas || [];
  const providers = providersData?.providers || [];

  // Apply persona modifications
  const modifiedPersonas = personas.map((p) => ({
    ...p,
    ...(personaModifications[p.id] || {}),
  }));

  const handlePersonaUpdate = (personaId: string, updates: Partial<Persona>) => {
    setPersonaModifications((prev) => ({
      ...prev,
      [personaId]: {
        ...(prev[personaId] || {}),
        ...updates,
      },
    }));
  };

  const getModelOptions = () => {
    const options: { value: string; label: string; provider: string }[] = [];
    providers.forEach((provider: Provider) => {
      if (provider.available) {
        provider.models.forEach((model) => {
          options.push({
            value: `${provider.name}:${model.id}`,
            label: `${provider.display_name} - ${model.name}`,
            provider: provider.name,
          });
        });
      }
    });
    return options;
  };

  const modelOptions = getModelOptions();

  return (
    <div className="h-full flex flex-col">
      {/* Sessions List */}
      <div className="border-b border-slate-200">
        <button
          onClick={() => toggleSection('sessions')}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-50"
        >
          <span className="font-medium text-slate-900">Sessions</span>
          {expandedSections.sessions ? (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-slate-400" />
          )}
        </button>

        {expandedSections.sessions && (
          <div className="px-4 pb-3 space-y-2">
            {sessions.length === 0 ? (
              <p className="text-sm text-slate-500 italic">No sessions yet</p>
            ) : (
              sessions.slice(0, 5).map((session) => (
                <button
                  key={session.id}
                  onClick={() => onSessionSelect(session.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedSession?.id === session.id
                      ? 'bg-red-50 text-red-700 border border-red-200'
                      : 'hover:bg-slate-100 text-slate-700'
                  }`}
                >
                  <div className="font-medium truncate">{session.name}</div>
                  <div className="text-xs text-slate-500 flex items-center gap-2">
                    <span
                      className={`inline-block w-2 h-2 rounded-full ${
                        session.status === 'completed'
                          ? 'bg-green-500'
                          : session.status === 'running'
                          ? 'bg-yellow-500'
                          : session.status === 'failed'
                          ? 'bg-red-500'
                          : 'bg-slate-300'
                      }`}
                    />
                    {session.status}
                  </div>
                </button>
              ))
            )}

            <div className="flex gap-2 pt-2">
              <label className="flex-1">
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImport}
                  className="hidden"
                />
                <span className="flex items-center justify-center gap-1 px-3 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 rounded cursor-pointer transition-colors">
                  <Upload className="w-3 h-3" />
                  Import
                </span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Session Actions (when session selected) */}
      {selectedSession && (
        <div className="border-b border-slate-200 p-4 space-y-3">
          <h3 className="font-medium text-slate-900">{selectedSession.name}</h3>

          <div className="flex gap-2">
            {selectedSession.status === 'pending' && (
              <button
                onClick={handleStartSimulation}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
              >
                <Play className="w-3 h-3" />
                Start
              </button>
            )}

            {selectedSession.status === 'running' && (
              <button
                onClick={handleStopSimulation}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                <Square className="w-3 h-3" />
                Stop
              </button>
            )}

            <button
              onClick={handleExport}
              className="flex items-center gap-1 px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 rounded transition-colors"
            >
              <Download className="w-3 h-3" />
              Export
            </button>
          </div>

          <div className="text-xs text-slate-500 space-y-1">
            <div>Actor: {selectedSession.actor_model}</div>
            <div>Subject: {selectedSession.subject_model}</div>
            <div>Max Turns: {selectedSession.max_turns}</div>
            <div>Sneaky Mode: {selectedSession.sneaky_mode ? 'Yes' : 'No'}</div>
          </div>
        </div>
      )}

      {/* New Session Form */}
      {showNewSession && (
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <h3 className="font-medium text-slate-900">Create New Session</h3>

          {/* Session Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Session Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="My Test Session"
            />
          </div>

          {/* Persona Section */}
          <div>
            <button
              onClick={() => toggleSection('persona')}
              className="w-full flex items-center justify-between py-2"
            >
              <span className="flex items-center gap-2 font-medium text-slate-700">
                <User className="w-4 h-4" />
                Persona *
              </span>
              {expandedSections.persona ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
            </button>

            {expandedSections.persona && (
              <div className="pl-6">
                <PersonaSelector
                  personas={modifiedPersonas}
                  selectedId={formData.persona_id}
                  onSelect={(personaId) => setFormData({ ...formData, persona_id: personaId })}
                  onPersonaUpdate={handlePersonaUpdate}
                />
              </div>
            )}
          </div>

          {/* Models Section */}
          <div>
            <button
              onClick={() => toggleSection('models')}
              className="w-full flex items-center justify-between py-2"
            >
              <span className="flex items-center gap-2 font-medium text-slate-700">
                <Cpu className="w-4 h-4" />
                Models
              </span>
              {expandedSections.models ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
            </button>

            {expandedSections.models && (
              <div className="space-y-3 pl-6">
                <div>
                  <label className="block text-xs text-slate-600 mb-1">Actor Model</label>
                  <select
                    value={formData.actor_model}
                    onChange={(e) => setFormData({ ...formData, actor_model: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  >
                    {modelOptions.map((opt) => (
                      <option key={`actor-${opt.value}`} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-slate-600 mb-1">Subject Model (being tested)</label>
                  <select
                    value={formData.subject_model}
                    onChange={(e) => setFormData({ ...formData, subject_model: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  >
                    {modelOptions.map((opt) => (
                      <option key={`subject-${opt.value}`} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-slate-600 mb-1">Assessor Model</label>
                  <select
                    value={formData.assessor_model}
                    onChange={(e) => setFormData({ ...formData, assessor_model: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  >
                    {modelOptions.map((opt) => (
                      <option key={`assessor-${opt.value}`} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Objectives Section */}
          <div>
            <button
              onClick={() => toggleSection('objectives')}
              className="w-full flex items-center justify-between py-2"
            >
              <span className="flex items-center gap-2 font-medium text-slate-700">
                <Target className="w-4 h-4" />
                Objectives *
              </span>
              {expandedSections.objectives ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
            </button>

            {expandedSections.objectives && (
              <div className="space-y-4 pl-6">
                {formData.objectives.map((obj, index) => (
                  <div key={index} className="space-y-2 p-3 border border-slate-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-slate-500">
                        Objective {index + 1}
                      </span>
                      {formData.objectives.length > 1 && (
                        <button
                          onClick={() => {
                            const newObjectives = formData.objectives.filter((_, i) => i !== index);
                            setFormData({ ...formData, objectives: newObjectives });
                          }}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      )}
                    </div>

                    <input
                      type="text"
                      placeholder="Title"
                      value={obj.title}
                      onChange={(e) => {
                        const newObjectives = [...formData.objectives];
                        newObjectives[index].title = e.target.value;
                        setFormData({ ...formData, objectives: newObjectives });
                      }}
                      className="w-full px-2 py-1.5 border border-slate-300 rounded text-sm"
                    />

                    <textarea
                      placeholder="Description (what the actor sees)"
                      value={obj.description}
                      onChange={(e) => {
                        const newObjectives = [...formData.objectives];
                        newObjectives[index].description = e.target.value;
                        setFormData({ ...formData, objectives: newObjectives });
                      }}
                      className="w-full px-2 py-1.5 border border-slate-300 rounded text-sm"
                      rows={2}
                    />

                    <textarea
                      placeholder="Completion Criteria (hidden from actor)"
                      value={obj.completion_criteria}
                      onChange={(e) => {
                        const newObjectives = [...formData.objectives];
                        newObjectives[index].completion_criteria = e.target.value;
                        setFormData({ ...formData, objectives: newObjectives });
                      }}
                      className="w-full px-2 py-1.5 border border-slate-300 rounded text-sm"
                      rows={2}
                    />
                  </div>
                ))}

                <button
                  onClick={() => {
                    setFormData({
                      ...formData,
                      objectives: [
                        ...formData.objectives,
                        { title: '', description: '', completion_criteria: '' },
                      ],
                    });
                  }}
                  className="flex items-center gap-1 text-sm text-red-600 hover:text-red-700"
                >
                  <Link2 className="w-3 h-3" />
                  Add to Chain
                </button>
              </div>
            )}
          </div>

          {/* Settings */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Max Turns per Objective</label>
              <input
                type="number"
                value={formData.max_turns}
                onChange={(e) => setFormData({ ...formData, max_turns: parseInt(e.target.value) })}
                className="w-20 px-2 py-1 border border-slate-300 rounded text-sm text-right"
                min={1}
                max={100}
              />
            </div>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.sneaky_mode}
                onChange={(e) => setFormData({ ...formData, sneaky_mode: e.target.checked })}
                className="rounded border-slate-300 text-red-600 focus:ring-red-500"
              />
              <span className="text-sm text-slate-700">Enable Sneaky Mode</span>
            </label>
          </div>

          {/* Create Button */}
          <button
            onClick={handleCreateSession}
            className="w-full py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            Create Session
          </button>
        </div>
      )}
    </div>
  );
}
