"use client";

import { useState, useEffect } from "react";
import { Command as CommandPrimitive } from "cmdk";
import { Search } from "lucide-react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { useCommands } from "./use-commands";
import { CommandItem } from "./command-item";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const { commands, navigateCommands, actionCommands, settingsCommands } =
    useCommands();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const handleSelect = (callback: () => void) => {
    setOpen(false);
    callback();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="overflow-hidden p-0 shadow-lg max-w-2xl">
        <CommandPrimitive className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground [&_[cmdk-group]:not([hidden])_~[cmdk-group]]:pt-0 [&_[cmdk-group]]:px-2 [&_[cmdk-input-wrapper]_svg]:h-5 [&_[cmdk-input-wrapper]_svg]:w-5 [&_[cmdk-input]]:h-12 [&_[cmdk-item]]:px-2 [&_[cmdk-item]]:py-3 [&_[cmdk-item]_svg]:h-5 [&_[cmdk-item]_svg]:w-5">
          <div className="flex items-center border-b px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            <CommandPrimitive.Input
              placeholder="Type a command or search..."
              className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <CommandPrimitive.List className="max-h-[400px] overflow-y-auto overflow-x-hidden p-2">
            <CommandPrimitive.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </CommandPrimitive.Empty>

            {navigateCommands.length > 0 && (
              <CommandPrimitive.Group heading="Navigate">
                {navigateCommands.map((command) => (
                  <CommandItem
                    key={command.id}
                    command={command}
                    onSelect={() => handleSelect(command.onSelect)}
                  />
                ))}
              </CommandPrimitive.Group>
            )}

            {actionCommands.length > 0 && (
              <CommandPrimitive.Group heading="Actions">
                {actionCommands.map((command) => (
                  <CommandItem
                    key={command.id}
                    command={command}
                    onSelect={() => handleSelect(command.onSelect)}
                  />
                ))}
              </CommandPrimitive.Group>
            )}

            {settingsCommands.length > 0 && (
              <CommandPrimitive.Group heading="Settings">
                {settingsCommands.map((command) => (
                  <CommandItem
                    key={command.id}
                    command={command}
                    onSelect={() => handleSelect(command.onSelect)}
                  />
                ))}
              </CommandPrimitive.Group>
            )}
          </CommandPrimitive.List>
        </CommandPrimitive>
      </DialogContent>
    </Dialog>
  );
}
