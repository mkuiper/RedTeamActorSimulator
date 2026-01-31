import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Download,
  RefreshCw,
} from 'lucide-react';
import { simulationApi, exportApi } from '../../services/api';
import type { Session, Turn, SimulationStatus } from '../../types';

interface DialogViewProps {
  session: Session | null;
  activeTab: 'conversation' | 'assessment' | 'report' | 'actor-thinking' | 'question-log';
  onRefresh: () => void;
}

export default function DialogView({ session, activeTab, onRefresh }: DialogViewProps) {
  const [isPolling, setIsPolling] = useState(false);

  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ['simulation-status', session?.id],
    queryFn: () => (session ? simulationApi.getStatus(session.id) : null),
    enabled: !!session && session.status === 'running',
    refetchInterval: isPolling ? 2000 : false,
  });

  useEffect(() => {
    if (session?.status === 'running') {
      setIsPolling(true);
    } else {
      setIsPolling(false);
    }
  }, [session?.status]);

  if (!session) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400">
        <div className="text-center">
          <p className="text-lg">Select or create a session to begin</p>
          <p className="text-sm mt-2">
            Configure your simulation in the left panel
          </p>
        </div>
      </div>
    );
  }

  const handleDownloadMarkdown = async () => {
    try {
      const markdown = await exportApi.getMarkdownReport(session.id);
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${session.id}.md`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      const blob = await exportApi.getPdfReport(session.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${session.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download PDF:', error);
    }
  };

  const renderConversation = () => {
    if (!session.turns || session.turns.length === 0) {
      return (
        <div className="text-center text-slate-400 py-12">
          {session.status === 'pending' ? (
            <p>Start the simulation to see the conversation</p>
          ) : session.status === 'running' ? (
            <div className="flex items-center justify-center gap-2">
              <RefreshCw className="w-5 h-5 animate-spin" />
              <p>Waiting for first turn...</p>
            </div>
          ) : (
            <p>No conversation data available</p>
          )}
        </div>
      );
    }

    // Group turns by objective
    const turnsByObjective: Record<string, Turn[]> = {};
    session.turns.forEach((turn) => {
      if (!turnsByObjective[turn.objective_id]) {
        turnsByObjective[turn.objective_id] = [];
      }
      turnsByObjective[turn.objective_id].push(turn);
    });

    return (
      <div className="space-y-6">
        {session.objectives.map((objective) => (
          <div key={objective.id} className="space-y-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-lg">
              <span className="font-medium text-slate-700">
                Objective {objective.chain_order + 1}: {objective.title}
              </span>
              <span
                className={`ml-auto px-2 py-0.5 text-xs rounded-full ${
                  objective.status === 'completed'
                    ? 'bg-green-100 text-green-700'
                    : objective.status === 'failed'
                    ? 'bg-red-100 text-red-700'
                    : objective.status === 'in_progress'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-slate-200 text-slate-600'
                }`}
              >
                {objective.status}
              </span>
            </div>

            <div className="space-y-3 pl-4">
              {(turnsByObjective[objective.id] || [])
                .sort((a, b) => a.turn_number - b.turn_number)
                .map((turn) => (
                  <div key={turn.id} className="space-y-2">
                    {/* Actor message */}
                    <div className="dialog-message actor">
                      <div className="text-xs text-blue-600 mb-1 font-medium">
                        Actor (Turn {turn.turn_number})
                      </div>
                      <p className="text-sm whitespace-pre-wrap">{turn.actor_message}</p>
                    </div>

                    {/* Subject response */}
                    <div className="dialog-message subject">
                      <div className="flex items-center gap-2 text-xs text-slate-500 mb-1">
                        <span className="font-medium">Subject</span>
                        {turn.refusal_detected && (
                          <span className="flex items-center gap-1 text-orange-600">
                            <AlertTriangle className="w-3 h-3" />
                            Refusal
                          </span>
                        )}
                        {turn.criteria_met && (
                          <span className="flex items-center gap-1 text-green-600">
                            <CheckCircle className="w-3 h-3" />
                            Criteria Met
                          </span>
                        )}
                      </div>
                      <p className="text-sm whitespace-pre-wrap">{turn.subject_response}</p>
                    </div>

                    {/* Subject thinking (if available) */}
                    {turn.subject_thinking && (
                      <div className="ml-4 p-2 bg-purple-50 border-l-2 border-purple-300 text-xs text-purple-700">
                        <div className="font-medium mb-1">Subject's Thinking:</div>
                        <p className="whitespace-pre-wrap">{turn.subject_thinking}</p>
                      </div>
                    )}
                  </div>
                ))}
            </div>
          </div>
        ))}

        {session.status === 'running' && (
          <div className="flex items-center justify-center gap-2 text-slate-500 py-4">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Simulation in progress...</span>
          </div>
        )}
      </div>
    );
  };

  const renderAssessment = () => {
    if (!session.turns || session.turns.length === 0) {
      return (
        <div className="text-center text-slate-400 py-12">
          <p>No assessment data available</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* Summary stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border border-slate-200">
            <div className="text-2xl font-bold text-slate-900">
              {session.turns.length}
            </div>
            <div className="text-sm text-slate-500">Total Turns</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-slate-200">
            <div className="text-2xl font-bold text-orange-600">
              {session.turns.filter((t) => t.refusal_detected).length}
            </div>
            <div className="text-sm text-slate-500">Refusals</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-slate-200">
            <div className="text-2xl font-bold text-green-600">
              {session.objectives.filter((o) => o.status === 'completed').length}
            </div>
            <div className="text-sm text-slate-500">Objectives Met</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-slate-200">
            <div className="text-2xl font-bold text-red-600">
              {session.objectives.filter((o) => o.status === 'failed').length}
            </div>
            <div className="text-sm text-slate-500">Objectives Failed</div>
          </div>
        </div>

        {/* Objective assessments */}
        <div className="space-y-4">
          {session.objectives.map((objective) => (
            <div
              key={objective.id}
              className="bg-white p-4 rounded-lg border border-slate-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-medium text-slate-900">{objective.title}</h4>
                  <p className="text-sm text-slate-500">{objective.description}</p>
                </div>
                <span
                  className={`px-2 py-1 text-xs rounded-full ${
                    objective.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : objective.status === 'failed'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {objective.status}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-slate-500">Turns:</span>{' '}
                  <span className="font-medium">{objective.turns_taken}</span>
                </div>
                <div>
                  <span className="text-slate-500">Refusals:</span>{' '}
                  <span className="font-medium">{objective.refusal_count}</span>
                </div>
                <div>
                  <span className="text-slate-500">Criteria:</span>{' '}
                  <span className="font-medium text-xs">{objective.completion_criteria.slice(0, 50)}...</span>
                </div>
              </div>

              {objective.bottleneck_notes && (
                <div className="mt-3 p-3 bg-red-50 rounded-lg">
                  <h5 className="text-sm font-medium text-red-800 mb-1">
                    Bottleneck Analysis
                  </h5>
                  <p className="text-sm text-red-700 whitespace-pre-wrap">
                    {objective.bottleneck_notes}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Turn-by-turn assessments */}
        <div className="space-y-2">
          <h4 className="font-medium text-slate-900">Turn Assessments</h4>
          {session.turns
            .sort((a, b) => a.turn_number - b.turn_number)
            .map((turn) => (
              <div
                key={turn.id}
                className={`p-3 rounded-lg border ${
                  turn.criteria_met
                    ? 'border-green-200 bg-green-50'
                    : turn.refusal_detected
                    ? 'border-orange-200 bg-orange-50'
                    : 'border-slate-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Turn {turn.turn_number}</span>
                  <div className="flex items-center gap-2 text-xs">
                    <span
                      className={`px-2 py-0.5 rounded ${
                        turn.assessor_evaluation.criteria_status === 'met'
                          ? 'bg-green-200 text-green-800'
                          : turn.assessor_evaluation.criteria_status === 'partially_met'
                          ? 'bg-yellow-200 text-yellow-800'
                          : 'bg-slate-200 text-slate-700'
                      }`}
                    >
                      {turn.assessor_evaluation.criteria_status}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded ${
                        turn.assessor_evaluation.effectiveness === 'high'
                          ? 'bg-green-200 text-green-800'
                          : turn.assessor_evaluation.effectiveness === 'medium'
                          ? 'bg-yellow-200 text-yellow-800'
                          : 'bg-red-200 text-red-800'
                      }`}
                    >
                      {turn.assessor_evaluation.effectiveness} effectiveness
                    </span>
                  </div>
                </div>
                <p className="text-sm text-slate-600">
                  {turn.assessor_evaluation.progress_notes}
                </p>
                {turn.assessor_evaluation.safety_measures.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {turn.assessor_evaluation.safety_measures.map((measure, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded"
                      >
                        {measure}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
        </div>
      </div>
    );
  };

  const renderReport = () => {
    if (session.status !== 'completed') {
      return (
        <div className="text-center text-slate-400 py-12">
          <p>Report will be available when the simulation completes</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-slate-900">Simulation Report</h3>
          <div className="flex gap-2">
            <button
              onClick={handleDownloadMarkdown}
              className="flex items-center gap-1 px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 rounded transition-colors"
            >
              <Download className="w-4 h-4" />
              Download Markdown
            </button>
            <button
              onClick={handleDownloadPdf}
              className="flex items-center gap-1 px-3 py-1.5 text-sm bg-red-600 text-white hover:bg-red-700 rounded transition-colors"
            >
              <Download className="w-4 h-4" />
              Download PDF
            </button>
          </div>
        </div>

        {session.final_report_md ? (
          <div className="prose prose-sm max-w-none bg-white p-6 rounded-lg border border-slate-200">
            <pre className="whitespace-pre-wrap text-sm">{session.final_report_md}</pre>
          </div>
        ) : (
          <div className="text-center text-slate-400 py-8">
            <p>Report not yet generated. Click download to generate.</p>
          </div>
        )}
      </div>
    );
  };

  const renderActorThinking = () => {
    if (!session.turns || session.turns.length === 0) {
      return (
        <div className="text-center text-slate-400 py-12">
          <p>No actor thinking data available</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">About Actor Thinking</h3>
          <p className="text-sm text-blue-700">
            This tab shows the internal reasoning process of the actor (adversarial persona) as they formulate each question.
            This helps understand the strategy and thought process behind each attempt to probe the subject model.
          </p>
        </div>

        {session.turns
          .sort((a, b) => a.turn_number - b.turn_number)
          .map((turn) => (
            <div key={turn.id} className="border border-slate-200 rounded-lg overflow-hidden">
              <div className="bg-slate-100 px-4 py-2 flex items-center justify-between">
                <span className="font-medium text-slate-700">Turn {turn.turn_number}</span>
                <span className="text-xs text-slate-500">
                  {turn.actor_strategy || 'Strategy not identified'}
                </span>
              </div>

              <div className="p-4 space-y-3">
                {/* Actor's thinking */}
                {turn.actor_thinking ? (
                  <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded">
                    <div className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      Actor's Thought Process
                    </div>
                    <p className="text-sm text-blue-800 whitespace-pre-wrap">{turn.actor_thinking}</p>
                  </div>
                ) : (
                  <div className="bg-slate-50 border-l-4 border-slate-300 p-3 rounded">
                    <p className="text-sm text-slate-500 italic">No thinking captured for this turn</p>
                  </div>
                )}

                {/* Resulting message */}
                <div>
                  <div className="text-xs font-medium text-slate-600 mb-1">Resulting Question:</div>
                  <div className="bg-white border border-slate-200 p-3 rounded">
                    <p className="text-sm text-slate-900 whitespace-pre-wrap">{turn.actor_message}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
      </div>
    );
  };

  const renderQuestionLog = () => {
    if (!session.turns || session.turns.length === 0) {
      return (
        <div className="text-center text-slate-400 py-12">
          <p>No questions logged yet</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="font-medium text-purple-900 mb-2">Question Log</h3>
          <p className="text-sm text-purple-700">
            Chronological list of all questions asked by the actor, showing the progression and evolution of the attack strategy.
          </p>
        </div>

        <div className="space-y-2">
          {session.turns
            .sort((a, b) => a.turn_number - b.turn_number)
            .map((turn) => {
              const objective = session.objectives.find(o => o.id === turn.objective_id);

              return (
                <div
                  key={turn.id}
                  className={`border rounded-lg p-4 transition-all ${
                    turn.criteria_met
                      ? 'border-green-300 bg-green-50'
                      : turn.refusal_detected
                      ? 'border-orange-300 bg-orange-50'
                      : 'border-slate-200 bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-medium text-slate-700">
                        Turn {turn.turn_number}
                      </span>
                      {objective && (
                        <span className="text-xs px-2 py-0.5 bg-slate-200 text-slate-700 rounded">
                          {objective.title}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      {turn.criteria_met && (
                        <span className="flex items-center gap-1 text-green-700">
                          <CheckCircle className="w-3 h-3" />
                          Success
                        </span>
                      )}
                      {turn.refusal_detected && (
                        <span className="flex items-center gap-1 text-orange-700">
                          <XCircle className="w-3 h-3" />
                          Refused
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="text-sm text-slate-900 whitespace-pre-wrap">{turn.actor_message}</p>

                  {turn.actor_strategy && (
                    <div className="mt-2 text-xs text-slate-500">
                      Strategy: {turn.actor_strategy}
                    </div>
                  )}

                  <div className="mt-2 text-xs text-slate-400">
                    {new Date(turn.created_at).toLocaleString()}
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    );
  };

  return (
    <div className="h-full">
      {/* Refresh button */}
      <div className="flex justify-end mb-4">
        <button
          onClick={onRefresh}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-slate-600 hover:text-slate-800"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {activeTab === 'conversation' && renderConversation()}
      {activeTab === 'actor-thinking' && renderActorThinking()}
      {activeTab === 'question-log' && renderQuestionLog()}
      {activeTab === 'assessment' && renderAssessment()}
      {activeTab === 'report' && renderReport()}
    </div>
  );
}
