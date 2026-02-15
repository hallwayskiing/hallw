import { ReactNode } from "react";

export type SaveStatus = "idle" | "saving" | "success" | "error";

export interface Config {
  [key: string]: any;
}

export interface ServerResponse {
  success: boolean;
  error?: string;
}

export interface TabConfig {
  id: string;
  label: string;
  icon: ReactNode;
  color: string;
  gradient: string;
}
