"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";

export interface Command {
  id: string;
  label: string;
  description?: string;
  category: "navigate" | "action" | "search" | "settings";
  icon?: string;
  shortcut?: string;
  onSelect: () => void;
}

export function useCommands() {
  const router = useRouter();

  const navigateCommands: Command[] = [
    {
      id: "nav-dashboard",
      label: "Dashboard",
      description: "Go to dashboard",
      category: "navigate",
      icon: "LayoutDashboard",
      onSelect: () => router.push("/dashboard"),
    },
    {
      id: "nav-agents",
      label: "Agents",
      description: "View all agents",
      category: "navigate",
      icon: "Bot",
      onSelect: () => router.push("/agents"),
    },
    {
      id: "nav-workflows",
      label: "Workflows",
      description: "Manage workflows",
      category: "navigate",
      icon: "GitBranch",
      onSelect: () => router.push("/workflows"),
    },
    {
      id: "nav-analytics",
      label: "Analytics",
      description: "View analytics",
      category: "navigate",
      icon: "BarChart3",
      onSelect: () => router.push("/analytics"),
    },
    {
      id: "nav-debugger",
      label: "Debugger",
      description: "Debug tasks",
      category: "navigate",
      icon: "Bug",
      onSelect: () => router.push("/debugger"),
    },
    {
      id: "nav-settings",
      label: "Settings",
      description: "Open settings",
      category: "navigate",
      icon: "Settings",
      onSelect: () => router.push("/settings"),
    },
  ];

  const actionCommands: Command[] = [
    {
      id: "action-create-agent",
      label: "Create Agent",
      description: "Create a new agent",
      category: "action",
      icon: "Plus",
      onSelect: () => router.push("/agents/new"),
    },
    {
      id: "action-submit-task",
      label: "Submit Task",
      description: "Submit a new task",
      category: "action",
      icon: "FileUp",
      onSelect: () => router.push("/dashboard?action=new-task"),
    },
  ];

  const settingsCommands: Command[] = [
    {
      id: "settings-api-keys",
      label: "API Keys",
      description: "Manage API keys",
      category: "settings",
      icon: "Key",
      onSelect: () => router.push("/settings/api-keys"),
    },
    {
      id: "settings-team",
      label: "Team",
      description: "Manage team members",
      category: "settings",
      icon: "Users",
      onSelect: () => router.push("/settings/team"),
    },
  ];

  const allCommands = [
    ...navigateCommands,
    ...actionCommands,
    ...settingsCommands,
  ];

  return {
    commands: allCommands,
    navigateCommands,
    actionCommands,
    settingsCommands,
  };
}
