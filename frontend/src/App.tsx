import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Shield, Settings, MessageSquare, FileText, Plus, Brain, List } from 'lucide-react';
import ConfigPanel from './components/ConfigPanel';
import DialogView from './components/DialogView';
import { sessionsApi } from './services/api';
import type { Session } from './types';

type Tab = 'conversation' | 'assessment' | 'report' | 'actor-thinking' | 'question-log';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('conversation');
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [showNewSession, setShowNewSession] = useState(false);

  const { data: sessionsData, refetch: refetchSessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: sessionsApi.list,
  });

  const handleSessionSelect = async (sessionId: string) => {
    const session = await sessionsApi.get(sessionId);
    setSelectedSession(session);
    setShowNewSession(false);
  };

  const handleNewSession = () => {
    setSelectedSession(null);
    setShowNewSession(true);
  };

  const handleSessionCreated = async (session: Session) => {
    setSelectedSession(session);
    setShowNewSession(false);
    refetchSessions();
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-red-600" />
            <div>
              <h1 className="text-xl font-bold text-slate-900">
                Red Team Actor Simulator
              </h1>
              <p className="text-sm text-slate-500">
                AI Safety Testing Framework
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={handleNewSession}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Session
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Left Panel - Configuration (1/3) */}
        <div className="w-1/3 border-r border-slate-200 bg-white overflow-y-auto">
          <ConfigPanel
            sessions={sessionsData?.sessions || []}
            selectedSession={selectedSession}
            showNewSession={showNewSession}
            onSessionSelect={handleSessionSelect}
            onSessionCreated={handleSessionCreated}
          />
        </div>

        {/* Right Panel - Dialog View (2/3) */}
        <div className="w-2/3 flex flex-col">
          {/* Tabs */}
          <div className="bg-white border-b border-slate-200 px-6">
            <div className="flex gap-1 overflow-x-auto">
              <button
                onClick={() => setActiveTab('conversation')}
                className={`tab-button ${activeTab === 'conversation' ? 'active' : ''}`}
              >
                <span className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Conversation
                </span>
              </button>
              <button
                onClick={() => setActiveTab('actor-thinking')}
                className={`tab-button ${activeTab === 'actor-thinking' ? 'active' : ''}`}
              >
                <span className="flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  Actor Thinking
                </span>
              </button>
              <button
                onClick={() => setActiveTab('question-log')}
                className={`tab-button ${activeTab === 'question-log' ? 'active' : ''}`}
              >
                <span className="flex items-center gap-2">
                  <List className="w-4 h-4" />
                  Question Log
                </span>
              </button>
              <button
                onClick={() => setActiveTab('assessment')}
                className={`tab-button ${activeTab === 'assessment' ? 'active' : ''}`}
              >
                <span className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Assessment
                </span>
              </button>
              <button
                onClick={() => setActiveTab('report')}
                className={`tab-button ${activeTab === 'report' ? 'active' : ''}`}
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Report
                </span>
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto p-6">
            <DialogView
              session={selectedSession}
              activeTab={activeTab}
              onRefresh={() => selectedSession && handleSessionSelect(selectedSession.id)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
