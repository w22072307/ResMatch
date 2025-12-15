'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Users,
  Calendar,
  MessageSquare,
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  BarChart3,
  Clock,
  DollarSign,
  CheckCircle,
  AlertCircle,
  Send
} from 'lucide-react';
import { studiesAPI, authAPI, messagesAPI, researchersAPI } from '@/lib/api';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'react-hot-toast';

interface Study {
  id: string;
  title: string;
  description: string;
  institution: string;
  category: string;
  duration: string;
  compensation: number;
  location: string;
  participants_needed: number;
  participants_current: number;
  status: string;
  created_at: string;
}

interface DashboardStats {
  activeStudies: number;
  totalParticipants: number;
  pendingApplications: number;
  completionRate: number;
}

export default function ResearcherDashboard() {
  const [studies, setStudies] = useState<Study[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    activeStudies: 0,
    totalParticipants: 0,
    pendingApplications: 0,
    completionRate: 0,
  });
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [createStudyOpen, setCreateStudyOpen] = useState(false);
  const [messagesOpen, setMessagesOpen] = useState(false);
  const [applicationsOpen, setApplicationsOpen] = useState(false);
  const [selectedApplications, setSelectedApplications] = useState<any[]>([]);
  const [participantsOpen, setParticipantsOpen] = useState(false);
  const [selectedParticipants, setSelectedParticipants] = useState<any[]>([]);
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [messageText, setMessageText] = useState('');
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileForm, setProfileForm] = useState({
    institution: '',
    department: '',
    title: '',
    bio: '',
  });
  const [studyForm, setStudyForm] = useState({
    title: '',
    description: '',
    institution: '',
    category: '',
    duration: '',
    compensation: '',
    location: '',
    participants_needed: '',
    requirements: '',
  });

  useEffect(() => {
    const loadUser = async () => {
      const userData = localStorage.getItem('user');
      if (userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        // Also fetch full profile to get researcher_profile data
        try {
          const profile = await authAPI.getProfile();
          setUser(profile);
          if (profile.researcher_profile) {
            setProfileForm({
              institution: profile.researcher_profile.institution || '',
              department: profile.researcher_profile.department || '',
              title: profile.researcher_profile.title || '',
              bio: profile.researcher_profile.bio || '',
            });
          }
        } catch (error) {
          console.error('Failed to load profile:', error);
        }
      } else {
        window.location.href = '/';
      }
    };
    loadUser();
  }, []);

  useEffect(() => {
    if (user?.id) {
      fetchStudies();
      fetchConversations();
    }
  }, [user]);

  const fetchConversations = async () => {
    try {
      const convs = await messagesAPI.getConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  const fetchMessages = async (otherUserId: string, studyId?: string) => {
    try {
      const params: any = { other_user_id: otherUserId };
      if (studyId) params.study_id = studyId;
      const msgs = await messagesAPI.getMessages(params);
      setMessages(msgs);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!messageText.trim() || !selectedConversation) return;
    try {
      await messagesAPI.sendMessage({
        receiver_id: selectedConversation.other_user.id,
        content: messageText,
        study_id: selectedConversation.study?.id,
      });
      setMessageText('');
      fetchMessages(selectedConversation.other_user.id, selectedConversation.study?.id);
      fetchConversations();
    } catch (error: any) {
      console.error('Failed to send message:', error);
      toast.error(error.message || 'Failed to send message');
    }
  };

  const fetchStudies = async () => {
    try {
      if (!user?.id) {
        setLoading(false);
        return;
      }
      const studiesData = await studiesAPI.getStudies({ researcher_id: user.id });
      setStudies(studiesData);
      const activeStudies = studiesData.filter((s: Study) => s.status === 'ACTIVE').length;
      const totalParticipants = studiesData.reduce((sum: number, s: Study) => sum + s.participants_current, 0);
      setStats({
        activeStudies,
        totalParticipants,
        pendingApplications: 5,
        completionRate: 87,
      });
    } catch (error) {
      console.error('Failed to fetch studies:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'bg-green-100 text-green-800';
      case 'DRAFT': return 'bg-gray-100 text-gray-800';
      case 'COMPLETED': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  const handleUpdateProfile = async () => {
    try {
      const profileData: any = {};
      if (profileForm.institution) profileData.institution = profileForm.institution;
      if (profileForm.department) profileData.department = profileForm.department;
      if (profileForm.title) profileData.title = profileForm.title;
      if (profileForm.bio) profileData.bio = profileForm.bio;
      
      await researchersAPI.updateProfile(profileData);
      toast.success('Profile updated successfully!');
      setProfileOpen(false);
      // Refresh user data
      try {
        const profile = await authAPI.getProfile();
        setUser(profile);
      } catch (error) {
        console.error('Failed to refresh profile:', error);
      }
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      toast.error(error.message || 'Failed to update profile. Please try again.');
    }
  };

  const handleCreateStudy = async () => {
    try {
      const studyData = {
        title: studyForm.title,
        description: studyForm.description,
        institution: studyForm.institution,
        category: studyForm.category,
        duration: studyForm.duration,
        compensation: studyForm.compensation ? parseFloat(studyForm.compensation) : null,
        location: studyForm.location || 'Remote',
        participants_needed: parseInt(studyForm.participants_needed),
        requirements: studyForm.requirements ? studyForm.requirements.split(',').map(r => r.trim()) : [],
      };
      
      await studiesAPI.createStudy(studyData);
      toast.success('Study created successfully!');
      setCreateStudyOpen(false);
      setStudyForm({
        title: '',
        description: '',
        institution: '',
        category: '',
        duration: '',
        compensation: '',
        location: '',
        participants_needed: '',
        requirements: '',
      });
      fetchStudies();
    } catch (error: any) {
      console.error('Failed to create study:', error);
      toast.error(error.message || 'Failed to create study. Please try again.');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">Researcher Dashboard</h1>
            </div>
            <div className="flex items-center gap-4">
              <Dialog open={messagesOpen} onOpenChange={setMessagesOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Messages
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl max-h-[80vh]">
                  <DialogHeader>
                    <DialogTitle>Messages</DialogTitle>
                    <DialogDescription>View and send messages</DialogDescription>
                  </DialogHeader>
                  <div className="grid grid-cols-2 gap-4 h-[60vh]">
                    <div className="border rounded-lg overflow-hidden flex flex-col">
                      <div className="p-3 border-b bg-gray-50">
                        <h3 className="font-medium text-sm">Conversations</h3>
                      </div>
                      <div className="flex-1 overflow-y-auto">
                        <div className="p-2 space-y-1">
                          {conversations.length === 0 ? (
                            <p className="text-sm text-gray-500 p-4">No conversations yet</p>
                          ) : (
                            conversations.map((conv) => (
                              <div
                                key={conv.id}
                                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                                  selectedConversation?.id === conv.id
                                    ? 'bg-blue-100 border border-blue-200'
                                    : 'hover:bg-gray-50 border border-transparent'
                                }`}
                                onClick={() => {
                                  setSelectedConversation(conv);
                                  fetchMessages(conv.other_user.id, conv.study?.id);
                                }}
                              >
                                <div className="font-medium text-sm">{conv.other_user.name}</div>
                                <div className="text-xs text-gray-600 truncate">{conv.study?.title || 'General'}</div>
                                {conv.unread_count > 0 && (
                                  <div className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 mt-1">
                                    {conv.unread_count} unread
                                  </div>
                                )}
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="border rounded-lg overflow-hidden flex flex-col">
                      {selectedConversation ? (
                        <>
                          <div className="p-4 border-b bg-gray-50">
                            <div className="font-medium">{selectedConversation.other_user.name}</div>
                            <div className="text-sm text-gray-600">{selectedConversation.study?.title || 'General'}</div>
                          </div>
                          <div className="flex-1 overflow-y-auto p-4 min-h-0">
                            <div className="space-y-4">
                              {messages.map((msg) => (
                                <div
                                  key={msg.id}
                                  className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                                >
                                  <div
                                    className={`max-w-[70%] px-4 py-2 rounded-2xl shadow-sm ${
                                      msg.sender_id === user?.id
                                        ? 'bg-blue-500 text-white rounded-br-md'
                                        : 'bg-gray-200 text-gray-900 rounded-bl-md'
                                    }`}
                                  >
                                    <div className="text-sm break-words">{msg.content}</div>
                                    <div className={`text-xs mt-1 ${
                                      msg.sender_id === user?.id ? 'text-blue-100' : 'text-gray-500'
                                    }`}>
                                      {new Date(msg.created_at).toLocaleString()}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                          <div className="p-4 border-t bg-white flex gap-2 flex-shrink-0">
                            <Input
                              value={messageText}
                              onChange={(e) => setMessageText(e.target.value)}
                              placeholder="Type a message..."
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  handleSendMessage();
                                }
                              }}
                              className="flex-1"
                            />
                            <Button onClick={handleSendMessage} disabled={!messageText.trim()}>
                              <Send className="w-4 h-4" />
                            </Button>
                          </div>
                        </>
                      ) : (
                        <div className="flex items-center justify-center h-full text-gray-500">
                          <div className="text-center">
                            <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                            <p>Select a conversation to view messages</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
              <Dialog open={createStudyOpen} onOpenChange={setCreateStudyOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    Create New Study
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Create New Study</DialogTitle>
                    <DialogDescription>
                      Fill in the details to create a new research study
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="title">Title *</Label>
                      <Input
                        id="title"
                        value={studyForm.title}
                        onChange={(e) => setStudyForm({ ...studyForm, title: e.target.value })}
                        placeholder="Study title"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="description">Description *</Label>
                      <Textarea
                        id="description"
                        value={studyForm.description}
                        onChange={(e) => setStudyForm({ ...studyForm, description: e.target.value })}
                        placeholder="Study description"
                        rows={4}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="institution">Institution *</Label>
                        <Input
                          id="institution"
                          value={studyForm.institution}
                          onChange={(e) => setStudyForm({ ...studyForm, institution: e.target.value })}
                          placeholder="University/Organization"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="category">Category *</Label>
                        <Select value={studyForm.category} onValueChange={(value) => setStudyForm({ ...studyForm, category: value })}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select category" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Psychology">Psychology</SelectItem>
                            <SelectItem value="Medicine">Medicine</SelectItem>
                            <SelectItem value="Technology">Technology</SelectItem>
                            <SelectItem value="Education">Education</SelectItem>
                            <SelectItem value="Social Science">Social Science</SelectItem>
                            <SelectItem value="Other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="duration">Duration *</Label>
                        <Input
                          id="duration"
                          value={studyForm.duration}
                          onChange={(e) => setStudyForm({ ...studyForm, duration: e.target.value })}
                          placeholder="e.g., 4 weeks"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="participants_needed">Participants Needed *</Label>
                        <Input
                          id="participants_needed"
                          type="number"
                          value={studyForm.participants_needed}
                          onChange={(e) => setStudyForm({ ...studyForm, participants_needed: e.target.value })}
                          placeholder="Number of participants"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="compensation">Compensation ($)</Label>
                        <Input
                          id="compensation"
                          type="number"
                          value={studyForm.compensation}
                          onChange={(e) => setStudyForm({ ...studyForm, compensation: e.target.value })}
                          placeholder="0.00"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="location">Location</Label>
                        <Input
                          id="location"
                          value={studyForm.location}
                          onChange={(e) => setStudyForm({ ...studyForm, location: e.target.value })}
                          placeholder="Remote or City, State"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="requirements">Requirements (comma-separated)</Label>
                      <Input
                        id="requirements"
                        value={studyForm.requirements}
                        onChange={(e) => setStudyForm({ ...studyForm, requirements: e.target.value })}
                        placeholder="e.g., Age 18-30, English speaker"
                      />
                    </div>
                    <div className="flex justify-end gap-2 pt-4">
                      <Button variant="outline" onClick={() => setCreateStudyOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleCreateStudy} disabled={!studyForm.title || !studyForm.description || !studyForm.institution || !studyForm.category || !studyForm.duration || !studyForm.participants_needed}>
                        Create Study
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {user?.name?.charAt(0) || 'R'}
                </div>
                <span className="text-sm font-medium">{user?.name || 'Researcher'}</span>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Studies</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeStudies}</div>
              <p className="text-xs text-muted-foreground">Currently running</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Participants</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalParticipants}</div>
              <p className="text-xs text-muted-foreground">Across all studies</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Applications</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pendingApplications}</div>
              <p className="text-xs text-muted-foreground">Need review</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.completionRate}%</div>
              <p className="text-xs text-muted-foreground">Average completion</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="studies" className="space-y-6">
          <TabsList>
            <TabsTrigger value="studies">My Studies</TabsTrigger>
            <TabsTrigger value="applications">Applications</TabsTrigger>
            <TabsTrigger value="participants">Participants</TabsTrigger>
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="studies" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">My Studies</h2>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search studies..."
                    className="pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <Button variant="outline" size="icon">
                  <Filter className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="grid gap-6">
              {studies.map((study) => (
                <Card key={study.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-xl">{study.title}</CardTitle>
                          <Badge className={getStatusColor(study.status)}>
                            {study.status}
                          </Badge>
                        </div>
                        <CardDescription className="text-base">
                          {study.description}
                        </CardDescription>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>{study.institution}</span>
                          <span>•</span>
                          <span>{study.category}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="icon">
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button variant="outline" size="icon">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="outline" size="icon">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">
                            {study.participants_current}/{study.participants_needed}
                          </div>
                          <div className="text-xs text-gray-500">Participants</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">{study.duration}</div>
                          <div className="text-xs text-gray-500">Duration</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <DollarSign className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">${study.compensation}</div>
                          <div className="text-xs text-gray-500">Compensation</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">{study.location}</div>
                          <div className="text-xs text-gray-500">Location</div>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Recruitment Progress</span>
                        <span>{Math.round((study.participants_current / study.participants_needed) * 100)}%</span>
                      </div>
                      <Progress 
                        value={(study.participants_current / study.participants_needed) * 100} 
                        className="h-2"
                      />
                    </div>
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-600">2 pending applications</span>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={async () => {
                            try {
                              const applications = await studiesAPI.getStudyApplications(study.id);
                              setSelectedApplications(applications);
                              setApplicationsOpen(true);
                            } catch (error) {
                              console.error('Failed to fetch applications:', error);
                              toast.error('Failed to load applications');
                            }
                          }}
                        >
                          View Applications
                        </Button>
                        <Button
                          size="sm"
                          onClick={async () => {
                            try {
                              const participants = await studiesAPI.getStudyParticipants(study.id);
                              setSelectedParticipants(participants);
                              setParticipantsOpen(true);
                            } catch (error) {
                              console.error('Failed to fetch participants:', error);
                              toast.error('Failed to load participants');
                            }
                          }}
                        >
                          View Participants
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="applications" className="space-y-6">
            <h2 className="text-xl font-semibold">Recent Applications</h2>
            <div className="grid gap-4">
              {studies.map((study) => (
                <Card key={study.id}>
                  <CardHeader>
                    <CardTitle>{study.title}</CardTitle>
                    <CardDescription>View applications for this study</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button
                      variant="outline"
                      onClick={async () => {
                        try {
                          const applications = await studiesAPI.getStudyApplications(study.id);
                          setSelectedApplications(applications);
                          setApplicationsOpen(true);
                        } catch (error) {
                          console.error('Failed to fetch applications:', error);
                          toast.error('Failed to load applications');
                        }
                      }}
                    >
                      View Applications
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="participants" className="space-y-6">
            <h2 className="text-xl font-semibold">Matched Participants</h2>
            <Card>
              <CardContent className="p-8 text-center">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No participants matched yet</h3>
                <p className="text-gray-600 mb-4">Once you publish studies and participants apply, you'll see them here.</p>
                <Button>Create New Study</Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profile" className="space-y-6">
            <h2 className="text-xl font-semibold">My Profile</h2>
            <Card>
              <CardHeader>
                <CardTitle>Researcher Profile</CardTitle>
                <CardDescription>Your researcher profile information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Name</label>
                  <div className="mt-1 p-2 border rounded bg-gray-50">{user?.name || 'N/A'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <div className="mt-1 p-2 border rounded bg-gray-50">{user?.email || 'N/A'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium">Institution</label>
                  <div className="mt-1 p-2 border rounded bg-gray-50">{user?.researcher_profile?.institution || 'Not set'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium">Department</label>
                  <div className="mt-1 p-2 border rounded bg-gray-50">{user?.researcher_profile?.department || 'Not set'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium">Title</label>
                  <div className="mt-1 p-2 border rounded bg-gray-50">{user?.researcher_profile?.title || 'Not set'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium">Bio</label>
                  <div className="mt-1 p-2 border rounded bg-gray-50">{user?.researcher_profile?.bio || 'Not set'}</div>
                </div>
                <Dialog open={profileOpen} onOpenChange={setProfileOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full">Edit Profile</Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>Edit Profile</DialogTitle>
                      <DialogDescription>Update your researcher profile information</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="institution">Institution</Label>
                        <Input
                          id="institution"
                          value={profileForm.institution}
                          onChange={(e) => setProfileForm({ ...profileForm, institution: e.target.value })}
                          placeholder="University/Organization"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="department">Department</Label>
                        <Input
                          id="department"
                          value={profileForm.department}
                          onChange={(e) => setProfileForm({ ...profileForm, department: e.target.value })}
                          placeholder="Department name"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="title">Title</Label>
                        <Input
                          id="title"
                          value={profileForm.title}
                          onChange={(e) => setProfileForm({ ...profileForm, title: e.target.value })}
                          placeholder="e.g., Professor, Research Scientist"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="bio">Bio</Label>
                        <Textarea
                          id="bio"
                          value={profileForm.bio}
                          onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                          placeholder="Tell us about your research background"
                          rows={4}
                        />
                      </div>
                      <div className="flex justify-end gap-2 pt-4">
                        <Button variant="outline" onClick={() => setProfileOpen(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleUpdateProfile}>Save Changes</Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>

              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <h2 className="text-xl font-semibold">Analytics Dashboard</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Study Performance</CardTitle>
                  <CardDescription>Overview of your research studies</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span>Total Studies Created</span>
                      <span className="font-medium">{studies.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Active Studies</span>
                      <span className="font-medium">{stats.activeStudies}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Completed Studies</span>
                      <span className="font-medium">0</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Average Completion Rate</span>
                      <span className="font-medium">{stats.completionRate}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Participant Engagement</CardTitle>
                  <CardDescription>How participants interact with your studies</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span>Total Participants</span>
                      <span className="font-medium">{stats.totalParticipants}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Pending Applications</span>
                      <span className="font-medium">{stats.pendingApplications}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Average Response Time</span>
                      <span className="font-medium">2.3 days</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Retention Rate</span>
                      <span className="font-medium">94%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Applications Dialog */}
        <Dialog open={applicationsOpen} onOpenChange={setApplicationsOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Study Applications</DialogTitle>
              <DialogDescription>
                Review and manage applications for this study
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {selectedApplications.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No applications yet</h3>
                  <p className="text-gray-500">Applications will appear here when participants apply to your study.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {selectedApplications.map((application: any) => (
                    <Card key={application.id}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <CardTitle className="text-lg">{application.user.name}</CardTitle>
                            <CardDescription>{application.user.email}</CardDescription>
                            <div className="flex items-center gap-2">
                              <Badge
                                variant={application.status === 'APPROVED' ? 'default' : application.status === 'REJECTED' ? 'destructive' : 'secondary'}
                              >
                                {application.status}
                              </Badge>
                              <span className="text-sm text-gray-500">
                                Applied {new Date(application.created_at).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                // TODO: Implement messaging functionality
                                toast('Messaging feature coming soon!');
                              }}
                            >
                              <MessageSquare className="w-4 h-4 mr-2" />
                              Message
                            </Button>
                            {application.status === 'PENDING' && (
                              <>
                                <Button
                                  size="sm"
                                  onClick={() => {
                                    // TODO: Implement approval functionality
                                    toast.success('Application approved!');
                                  }}
                                >
                                  Approve
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => {
                                    // TODO: Implement rejection functionality
                                    toast.error('Application rejected!');
                                  }}
                                >
                                  Reject
                                </Button>
                              </>
                            )}
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {application.message && (
                          <div className="mb-4">
                            <h4 className="text-sm font-medium mb-2">Application Message:</h4>
                            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
                              {application.message}
                            </p>
                          </div>
                        )}

                        {application.user.participant_profile && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h4 className="text-sm font-medium mb-2">Profile Information:</h4>
                              <div className="space-y-1 text-sm">
                                <div><span className="font-medium">Gender:</span> {application.user.participant_profile.gender || 'Not specified'}</div>
                                <div><span className="font-medium">Location:</span> {application.user.participant_profile.location || 'Not specified'}</div>
                                <div><span className="font-medium">Phone:</span> {application.user.participant_profile.phone_number || 'Not specified'}</div>
                                {application.user.participant_profile.date_of_birth && (
                                  <div><span className="font-medium">Age:</span> {new Date().getFullYear() - new Date(application.user.participant_profile.date_of_birth).getFullYear()}</div>
                                )}
                              </div>
                            </div>
                            <div>
                              <h4 className="text-sm font-medium mb-2">Research Interests:</h4>
                              <div className="flex flex-wrap gap-1">
                                {application.user.participant_profile.interests ? (
                                  JSON.parse(application.user.participant_profile.interests).map((interest: string, index: number) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {interest}
                                    </Badge>
                                  ))
                                ) : (
                                  <span className="text-sm text-gray-500">No interests specified</span>
                                )}
                              </div>
                              {application.user.participant_profile.bio && (
                                <div className="mt-3">
                                  <h5 className="text-sm font-medium mb-1">Bio:</h5>
                                  <p className="text-sm text-gray-600">{application.user.participant_profile.bio}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>

        {/* Participants Dialog */}
        <Dialog open={participantsOpen} onOpenChange={setParticipantsOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Study Participants</DialogTitle>
              <DialogDescription>
                View participants currently enrolled in this study
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {selectedParticipants.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No participants enrolled yet</h3>
                  <p className="text-gray-500">Participants will appear here once they are approved and start participating in your study.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {selectedParticipants.map((participantData: any) => (
                    <Card key={participantData.id}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <CardTitle className="text-lg">{participantData.user.name}</CardTitle>
                            <CardDescription>{participantData.user.email}</CardDescription>
                            <div className="flex items-center gap-2">
                              <Badge
                                variant={participantData.status === 'ACTIVE' ? 'default' : participantData.status === 'COMPLETED' ? 'secondary' : 'outline'}
                              >
                                {participantData.status}
                              </Badge>
                              <span className="text-sm text-gray-500">
                                Started {new Date(participantData.start_date || participantData.created_at).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                // TODO: Implement messaging functionality
                                toast('Messaging feature coming soon!');
                              }}
                            >
                              <MessageSquare className="w-4 h-4 mr-2" />
                              Message
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-sm font-medium mb-2">Participation Details:</h4>
                            <div className="space-y-1 text-sm">
                              <div><span className="font-medium">Status:</span> {participantData.status}</div>
                              <div><span className="font-medium">Consent Given:</span> {participantData.consent_given ? 'Yes' : 'No'}</div>
                              {participantData.start_date && (
                                <div><span className="font-medium">Start Date:</span> {new Date(participantData.start_date).toLocaleDateString()}</div>
                              )}
                              {participantData.end_date && (
                                <div><span className="font-medium">End Date:</span> {new Date(participantData.end_date).toLocaleDateString()}</div>
                              )}
                            </div>
                            {participantData.notes && (
                              <div className="mt-3">
                                <h5 className="text-sm font-medium mb-1">Notes:</h5>
                                <p className="text-sm text-gray-600">{participantData.notes}</p>
                              </div>
                            )}
                          </div>
                          <div>
                            {participantData.user.participant_profile && (
                              <>
                                <h4 className="text-sm font-medium mb-2">Profile Information:</h4>
                                <div className="space-y-1 text-sm">
                                  <div><span className="font-medium">Gender:</span> {participantData.user.participant_profile.gender || 'Not specified'}</div>
                                  <div><span className="font-medium">Location:</span> {participantData.user.participant_profile.location || 'Not specified'}</div>
                                  <div><span className="font-medium">Phone:</span> {participantData.user.participant_profile.phone_number || 'Not specified'}</div>
                                  {participantData.user.participant_profile.date_of_birth && (
                                    <div><span className="font-medium">Age:</span> {new Date().getFullYear() - new Date(participantData.user.participant_profile.date_of_birth).getFullYear()}</div>
                                  )}
                                </div>
                                <h4 className="text-sm font-medium mb-2 mt-3">Research Interests:</h4>
                                <div className="flex flex-wrap gap-1">
                                  {participantData.user.participant_profile.interests ? (
                                    JSON.parse(participantData.user.participant_profile.interests).map((interest: string, index: number) => (
                                      <Badge key={index} variant="outline" className="text-xs">
                                        {interest}
                                      </Badge>
                                    ))
                                  ) : (
                                    <span className="text-sm text-gray-500">No interests specified</span>
                                  )}
                                </div>
                                {participantData.user.participant_profile.bio && (
                                  <div className="mt-3">
                                    <h5 className="text-sm font-medium mb-1">Bio:</h5>
                                    <p className="text-sm text-gray-600">{participantData.user.participant_profile.bio}</p>
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
