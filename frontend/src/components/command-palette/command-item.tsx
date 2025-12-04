use client;

import { Command as CommandPrimitive } from "cmdk";
import * as LucideIcons from "lucide-react";
import { Command } from "./use-commands";

interface CommandItemProps {
  command: Command;
  onSelect: () => void;
}

type LucideIconName = keyof typeof LucideIcons;

export function CommandItem({ command, onSelect }: CommandItemProps) {
  const IconComponent = command.icon && command.icon in LucideIcons
    ? LucideIcons[command.icon as LucideIconName] as React.ComponentType<{ className?: string; "aria-hidden"?: boolean }>
    : null;

  return (
    <CommandPrimitive.Item
      value={command.id}
      onSelect={onSelect}
      className="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none aria-selected:bg-accent aria-selected:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
    >
      {IconComponent && (
        <IconComponent className="mr-2 h-4 w-4" aria-hidden={true} />
      )}
      <div className="flex-1">
        <div className="font-medium">{command.label}</div>
        {command.description && (
          <div className="text-xs text-muted-foreground">
            {command.description}
          </div>
        )}
      </div>
      {command.shortcut && (
        <kbd className="pointer-events-none ml-auto hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex">
          {command.shortcut}
        </kbd>
      )}
    </CommandPrimitive.Item>
  );
}