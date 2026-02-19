import { Avatar } from "./MessageBubble";

export function ThinkingIndicator() {
  return (
    <div className="flex gap-4 max-w-3xl mx-auto w-full animate-pulse">
      <Avatar msgRole="assistant" />
      <div className="flex-1 space-y-2 pt-1">
        <div className="h-4 w-24 bg-muted/50 rounded" />
        <div className="h-3 w-64 bg-muted/30 rounded" />
      </div>
    </div>
  );
}
