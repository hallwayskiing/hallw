import { useAppStore } from "@store/store";
import { AlertCircle, Loader2, Square, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

function buildPreview(session: {
  streamingContent: string;
  messages: Array<{ type: string; msgRole: string; content?: string }>;
}) {
  const latest = [...session.messages]
    .reverse()
    .find((m) => m.type === "text" && m.msgRole === "assistant" && m.content?.trim());
  const src = session.streamingContent || latest?.content || "";
  return (
    src
      .split("\n")
      .filter((l) => l.trim())
      .pop() || ""
  );
}

function getCardToneClass(session: { isRunning: boolean; hasFatalError: boolean; needsAttention: boolean }) {
  if (session.hasFatalError) return "border-rose-500/35 shadow-rose-500/15";
  if (session.needsAttention) return "border-amber-500/35 shadow-amber-500/15";
  if (session.isRunning) return "border-emerald-500/20 shadow-emerald-500/10";
  return "border-sky-500/25 shadow-sky-500/10";
}

function getHoverToneClass(session: { isRunning: boolean; hasFatalError: boolean; needsAttention: boolean }) {
  if (session.hasFatalError) return "hover:bg-rose-500/10";
  if (session.needsAttention) return "hover:bg-amber-500/10";
  if (session.isRunning) return "hover:bg-emerald-500/10";
  return "hover:bg-sky-500/10";
}

function getRemainingSeconds(expiresAt: number | undefined, nowMs: number): number | null {
  if (typeof expiresAt !== "number" || !Number.isFinite(expiresAt) || expiresAt <= 0) return null;
  return Math.max(0, Math.ceil((expiresAt - nowMs) / 1000));
}

function buildRequiredLabel(label: string | null, remainingSeconds: number | null): string | null {
  if (!label) return null;
  const suffix = remainingSeconds === null ? "" : ` in ${remainingSeconds}s`;
  return `${label}${suffix}`;
}

export function RunningSessionsDock() {
  const chatSessions = useAppStore((s) => s.chatSessions);
  const sessionOrder = useAppStore((s) => s.sessionOrder);
  const resumeSession = useAppStore((s) => s.resumeSession);
  const endSession = useAppStore((s) => s.endSession);
  const [nowMs, setNowMs] = useState(() => Date.now());

  useEffect(() => {
    const timer = window.setInterval(() => setNowMs(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const sessions = useMemo(() => {
    return sessionOrder
      .map((sessionId) => chatSessions[sessionId])
      .filter((session) => !!session && (session.isRunning || session.hasFatalError || session.messages.length > 0))
      .map((session) => {
        const pendingRequest = session.pendingDecision || session.pendingConfirmation;
        const requiredLabel = pendingRequest ? "Action Required" : null;
        const requiredRemainingSeconds = getRemainingSeconds(pendingRequest?.expiresAt, nowMs);
        return {
          sessionId: session.id,
          title: session.title,
          isRunning: session.isRunning,
          hasFatalError: session.hasFatalError,
          needsAttention: !!pendingRequest,
          requiredStatusText: buildRequiredLabel(requiredLabel, requiredRemainingSeconds),
          preview: buildPreview(session),
        };
      });
  }, [chatSessions, nowMs, sessionOrder]);

  if (sessions.length === 0) return null;

  const topSessions = sessions.slice(0, 6);

  return (
    <div className="absolute right-5 bottom-5 z-20 flex flex-col gap-2 w-[320px]">
      {topSessions.map((session) => (
        <div
          key={session.sessionId}
          className={`flex items-stretch gap-2 rounded-xl border bg-card/80 backdrop-blur-sm shadow-lg p-2 ${getCardToneClass(session)}`}
        >
          <button
            type="button"
            className={`flex-1 min-w-0 text-left rounded-lg px-2 py-1.5 transition-colors ${getHoverToneClass(session)}`}
            onClick={() => resumeSession(session.sessionId)}
            title="Return to this session"
          >
            {session.hasFatalError ? (
              <div className="flex items-center gap-2 text-xs font-medium text-rose-400">
                <AlertCircle className="w-3.5 h-3.5" />
                Error
                <span className="text-foreground/40">#{session.sessionId.slice(0, 6)}</span>
              </div>
            ) : session.requiredStatusText ? (
              <div className="flex items-center gap-2 text-xs font-medium text-amber-400">
                <AlertCircle className="w-3.5 h-3.5" />
                {session.requiredStatusText}
                <span className="text-foreground/40">#{session.sessionId.slice(0, 6)}</span>
              </div>
            ) : session.isRunning ? (
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-medium">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Running
                <span className="text-foreground/40">#{session.sessionId.slice(0, 6)}</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-xs font-medium text-foreground/60">
                <span>Idle</span>
                <span className="text-foreground/40">#{session.sessionId.slice(0, 6)}</span>
              </div>
            )}
            <p className="mt-1 text-sm text-foreground truncate">{session.title}</p>
            <p className="text-xs text-muted-foreground truncate">{session.preview}</p>
          </button>
          <button
            type="button"
            className={`shrink-0 rounded-lg px-3 transition-colors ${
              session.isRunning
                ? "text-rose-400 hover:bg-rose-500/15"
                : "text-foreground/55 hover:bg-foreground/10 hover:text-foreground/85"
            }`}
            onClick={() => endSession(session.sessionId)}
            title={session.isRunning ? "Stop and delete this session" : "Delete this session"}
          >
            {session.isRunning ? <Square className="w-4 h-4 fill-current" /> : <X className="w-4 h-4" />}
          </button>
        </div>
      ))}
    </div>
  );
}
