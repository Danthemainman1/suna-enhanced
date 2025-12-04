"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Mail, Shield, UserX } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: "owner" | "admin" | "member" | "viewer";
  status: "active" | "pending";
  joinedAt: string;
  lastActive?: string;
}

interface InviteData {
  email: string;
  role: "admin" | "member" | "viewer";
}

async function fetchTeamMembers(): Promise<TeamMember[]> {
  const response = await fetch("/api/team/members");
  if (!response.ok) {
    throw new Error("Failed to fetch team members");
  }
  return response.json();
}

async function inviteTeamMember(data: InviteData): Promise<void> {
  const response = await fetch("/api/team/invite", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to send invitation");
  }
}

async function updateMemberRole(
  memberId: string,
  role: string
): Promise<void> {
  const response = await fetch(`/api/team/members/${memberId}/role`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });

  if (!response.ok) {
    throw new Error("Failed to update member role");
  }
}

async function removeMember(memberId: string): Promise<void> {
  const response = await fetch(`/api/team/members/${memberId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to remove member");
  }
}

async function revokeInvitation(invitationId: string): Promise<void> {
  const response = await fetch(`/api/team/invitations/${invitationId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to revoke invitation");
  }
}

export default function TeamPage() {
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [inviteData, setInviteData] = useState<InviteData>({
    email: "",
    role: "member",
  });
  const queryClient = useQueryClient();

  const { data: members, isLoading } = useQuery({
    queryKey: ["team-members"],
    queryFn: fetchTeamMembers,
  });

  const inviteMutation = useMutation({
    mutationFn: inviteTeamMember,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
      toast.success("Invitation sent successfully");
      setIsInviteDialogOpen(false);
      setInviteData({ email: "", role: "member" });
    },
    onError: () => {
      toast.error("Failed to send invitation");
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ memberId, role }: { memberId: string; role: string }) =>
      updateMemberRole(memberId, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
      toast.success("Member role updated");
    },
    onError: () => {
      toast.error("Failed to update member role");
    },
  });

  const removeMutation = useMutation({
    mutationFn: removeMember,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
      toast.success("Member removed successfully");
    },
    onError: () => {
      toast.error("Failed to remove member");
    },
  });

  const handleInvite = () => {
    if (!inviteData.email.trim()) {
      toast.error("Please enter an email address");
      return;
    }

    inviteMutation.mutate(inviteData);
  };

  const getRoleBadge = (role: string) => {
    const colors: Record<string, string> = {
      owner: "bg-purple-100 text-purple-800 border-purple-200",
      admin: "bg-blue-100 text-blue-800 border-blue-200",
      member: "bg-green-100 text-green-800 border-green-200",
      viewer: "bg-gray-100 text-gray-800 border-gray-200",
    };

    return (
      <Badge variant="outline" className={colors[role] || ""}>
        {role}
      </Badge>
    );
  };

  const getStatusBadge = (status: string) => {
    return status === "active" ? (
      <Badge className="bg-green-100 text-green-800 border-green-200">
        Active
      </Badge>
    ) : (
      <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
        Pending
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="container mx-auto max-w-6xl px-6 py-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium flex items-center gap-2">
              <Shield className="w-6 h-6" />
              Team Management
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage team members and their roles
            </p>
          </div>

          <Dialog
            open={isInviteDialogOpen}
            onOpenChange={setIsInviteDialogOpen}
          >
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Invite Member
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Invite Team Member</DialogTitle>
                <DialogDescription>
                  Send an invitation to a new team member
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="email">Email Address *</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="user@example.com"
                    value={inviteData.email}
                    onChange={(e) =>
                      setInviteData((prev) => ({
                        ...prev,
                        email: e.target.value,
                      }))
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="role">Role *</Label>
                  <Select
                    value={inviteData.role}
                    onValueChange={(value: any) =>
                      setInviteData((prev) => ({ ...prev, role: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="viewer">Viewer</SelectItem>
                      <SelectItem value="member">Member</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground mt-1">
                    Viewer: Read-only access • Member: Can create and edit •
                    Admin: Full access
                  </p>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsInviteDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleInvite}
                  disabled={!inviteData.email.trim() || inviteMutation.isPending}
                >
                  {inviteMutation.isPending ? "Sending..." : "Send Invitation"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {isLoading ? (
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse flex items-center gap-4">
                    <div className="w-10 h-10 bg-muted rounded-full"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-muted rounded w-1/3"></div>
                      <div className="h-3 bg-muted rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : !members || members.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <Mail className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No team members yet</h3>
              <p className="text-muted-foreground mb-4">
                Invite team members to collaborate on your workspace
              </p>
              <Button onClick={() => setIsInviteDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Invite Member
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Team Members ({members.length})</CardTitle>
              <CardDescription>
                Manage roles and permissions for your team
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Member</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Joined</TableHead>
                    <TableHead>Last Active</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {members.map((member) => (
                    <TableRow key={member.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{member.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {member.email}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {member.role === "owner" ? (
                          getRoleBadge(member.role)
                        ) : (
                          <Select
                            value={member.role}
                            onValueChange={(value) =>
                              updateRoleMutation.mutate({
                                memberId: member.id,
                                role: value,
                              })
                            }
                          >
                            <SelectTrigger className="w-[120px]">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="viewer">Viewer</SelectItem>
                              <SelectItem value="member">Member</SelectItem>
                              <SelectItem value="admin">Admin</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                      </TableCell>
                      <TableCell>{getStatusBadge(member.status)}</TableCell>
                      <TableCell>{formatDate(member.joinedAt)}</TableCell>
                      <TableCell>
                        {member.lastActive
                          ? formatDate(member.lastActive)
                          : "Never"}
                      </TableCell>
                      <TableCell className="text-right">
                        {member.role !== "owner" && (
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <UserX className="w-4 h-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Remove Member</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to remove {member.name} from
                                  the team? This action cannot be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => removeMutation.mutate(member.id)}
                                  className="bg-destructive hover:bg-destructive/90 text-white"
                                >
                                  Remove
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
