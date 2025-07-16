"use client";

import { PanelSection } from "./panel-section";
import { Card, CardContent } from "@/components/ui/card";
import { BookText } from "lucide-react";

interface ConversationContextProps {
  context: {
    name?: string;
    uid?: number;
    goal?: any;
    diet_preferences?: string;
    workout_plan?: any;
    meal_plan?: string[];
    injury_notes?: string;
    handoff_logs?: string[];
    progress_logs?: any[];
  };
}

// Helper function to safely render context values
function renderContextValue(value: any): string {
  if (value === null || value === undefined) {
    return "null";
  }
  
  if (typeof value === "object") {
    if (Array.isArray(value)) {
      return value.length > 0 ? `${value.length} items` : "empty array";
    }
    return Object.keys(value).length > 0 ? `${Object.keys(value).length} properties` : "empty object";
  }
  
  return String(value);
}

export function ConversationContext({ context }: ConversationContextProps) {
  return (
    <PanelSection
      title="User Session Context"
      icon={<BookText className="h-4 w-4 text-green-600" />}
    >
      <Card className="bg-gradient-to-r from-white to-gray-50 border-gray-200 shadow-sm">
        <CardContent className="p-3">
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(context).map(([key, value]) => (
              <div
                key={key}
                className="flex items-center gap-2 bg-white p-2 rounded-md border border-gray-200 shadow-sm transition-all"
              >
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <div className="text-xs">
                  <span className="text-zinc-500 font-light">{key}:</span>{" "}
                  <span
                    className={
                      value
                        ? "text-zinc-900 font-light"
                        : "text-gray-400 italic"
                    }
                  >
                    {renderContextValue(value)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </PanelSection>
  );
}