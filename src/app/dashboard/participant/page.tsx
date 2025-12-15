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
  DollarSign,
  Search,
  Filter,
  Eye,
  Clock,
  MapPin,
  CheckCircle,
  Star,
  TrendingUp,
  Award,
  MessageSquare,
  Send
} from 'lucide-react';
import { matchingAPI, authAPI, studiesAPI, participantsAPI, messagesAPI } from '@/lib/api';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
  requirements: string[];
  researcher?: {
    id: string;
    name: string;
    email: string;
  };
  matchScore?: number;
}

interface ParticipantStats {
  activeStudies: number;
  completedStudies: number;
  totalEarnings: number;
  matchRate: number;
}

export default function ParticipantDashboard() {
  const [recommendedStudies, setRecommendedStudies] = useState<Study[]>([]);
  const [myStudies, setMyStudies] = useState<Study[]>([]);
  const [studyHistory, setStudyHistory] = useState<Study[]>([]);
  const [applyDialogOpen, setApplyDialogOpen] = useState(false);
  const [studyDetailsDialogOpen, setStudyDetailsDialogOpen] = useState(false);
  const [selectedStudy, setSelectedStudy] = useState<Study | null>(null);
  const [applicationMessage, setApplicationMessage] = useState('');
  const [stats, setStats] = useState<ParticipantStats>({
    activeStudies: 1,
    completedStudies: 5,
    totalEarnings: 385,
    matchRate: 92,
  });
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [messagesOpen, setMessagesOpen] = useState(false);
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [messageText, setMessageText] = useState('');
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileForm, setProfileForm] = useState({
    date_of_birth: '',
    gender: '',
    location: '',
    bio: '',
    interests: '',
    availability: '',
    phone_number: '',
  });

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
    } else {
      window.location.href = '/';
    }
  }, []);

  useEffect(() => {
    if (user?.id) {
      fetchRecommendedStudies();
      fetchUserStudies();
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

  const fetchUserStudies = async () => {
    try {
      const participations = await participantsAPI.getParticipations();
      const applications = await participantsAPI.getApplications();

      // Filter active and completed participations
      const activeParticipations = participations.filter((p: any) => p.status === 'ACTIVE');
      const completedParticipations = participations.filter((p: any) => p.status === 'COMPLETED');

      // Get pending applications that don't have corresponding participations
      const participationStudyIds = participations.map((p: any) => p.study?.id).filter(id => id);
      const pendingApplications = applications.filter((app: any) =>
        app.status === 'PENDING' && !participationStudyIds.includes(app.study?.id)
      );

      const activeStudyIds = activeParticipations.map((p: any) => p.study?.id).filter(id => id);
      const completedStudyIds = completedParticipations.map((p: any) => p.study?.id).filter(id => id);

      // Set active studies directly from participation data
      const activeStudiesFromParticipations = activeParticipations.map((p: any) => ({
        id: p.study.id,
        title: p.study.title,
        description: p.study.description,
        institution: p.study.institution,
        category: p.study.category,
        duration: p.study.duration,
        compensation: p.study.compensation,
        location: p.study.location,
        participants_needed: 0, // Not available in this context
        participants_current: 0, // Not available in this context
        status: 'ACTIVE', // Since these are active participations
        requirements: [], // Not available in this context
        researcher: p.study.researcher,
        matchScore: undefined
      }));

      // Add pending applications to the studies list
      const pendingStudiesFromApplications = await Promise.all(
        pendingApplications.map(async (app: any) => {
          try {
            // We need to fetch the full study details since applications API might not include all study info
            const studyDetails = await studiesAPI.getStudy(app.study.id);
            return {
              id: studyDetails.id,
              title: studyDetails.title,
              description: studyDetails.description,
              institution: studyDetails.institution,
              category: studyDetails.category,
              duration: studyDetails.duration,
              compensation: studyDetails.compensation,
              location: studyDetails.location,
              participants_needed: studyDetails.participants_needed,
              participants_current: studyDetails.participants_current,
              status: 'PENDING', // Application is pending approval
              requirements: studyDetails.requirements || [],
              researcher: studyDetails.researcher,
              matchScore: undefined
            };
          } catch (error) {
            console.error(`Failed to fetch study details for application ${app.id}:`, error);
            return null;
          }
        })
      );

      const validPendingStudies = pendingStudiesFromApplications.filter(study => study !== null);
      const allMyStudies = [...activeStudiesFromParticipations, ...validPendingStudies];

      setMyStudies(allMyStudies);

      // Set completed studies directly from participation data
      const completedStudies = completedParticipations.map((p: any) => ({
        id: p.study.id,
        title: p.study.title,
        description: p.study.description,
        institution: p.study.institution,
        category: p.study.category,
        duration: p.study.duration,
        compensation: p.study.compensation,
        location: p.study.location,
        participants_needed: 0, // Not available in this context
        participants_current: 0, // Not available in this context
        status: 'COMPLETED', // Since these are completed participations
        requirements: [], // Not available in this context
        researcher: p.study.researcher,
        matchScore: undefined
      }));
      setStudyHistory(completedStudies);
    } catch (error) {
      console.error('Failed to fetch user studies:', error);
      setMyStudies([]);
      setStudyHistory([]);
    }
  };

  const fetchRecommendedStudies = async () => {
    try {
      if (!user?.id) {
        setLoading(false);
        return;
      }
      const response = await matchingAPI.getMatchedStudies();
      setRecommendedStudies(response.matches || []);
    } catch (error) {
      console.error('Failed to fetch recommended studies:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 80) return 'bg-blue-100 text-blue-800';
    if (score >= 70) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const formatRequirements = (requirements: any[]) => {
    if (!requirements || !Array.isArray(requirements)) return [];

    return requirements.map(req => {
      if (typeof req === 'string') return req;

      // Handle object format
      if (req && typeof req === 'object' && req.type) {
        if (req.type === 'age' && req.min && req.max) {
          return `Age: ${req.min}-${req.max}`;
        } else if (req.type === 'gender' && req.value) {
          return `Gender: ${req.value}`;
        } else if (req.type === 'interest' && req.value) {
          return `Interest: ${req.value}`;
        } else if (req.type === 'language' && req.value) {
          return `Language: ${req.value}`;
        } else if (req.type === 'status' && req.value) {
          return `Status: ${req.value}`;
        } else if (req.type === 'device' && req.value) {
          return `Device: ${req.value}`;
        } else if (req.type === 'fitness' && req.value) {
          return `Fitness: ${req.value}`;
        } else if (req.type === 'bmi' && req.min && req.max) {
          return `BMI: ${req.min}-${req.max}`;
        } else {
          return `${req.type}: ${req.value || 'N/A'}`;
        }
      }

      return req;
    });
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  const handleApplyToStudy = (study: Study) => {
    setSelectedStudy(study);
    setApplicationMessage('');
    setApplyDialogOpen(true);
  };

  const handleSubmitApplication = async () => {
    if (!selectedStudy) return;

    try {
      await studiesAPI.applyToStudy(selectedStudy.id, { message: applicationMessage });
      toast.success('Application submitted successfully! You will see this study in "My Studies" once approved by the researcher.');
      setApplyDialogOpen(false);
      setSelectedStudy(null);
      setApplicationMessage('');
      fetchRecommendedStudies();
      fetchUserStudies();
    } catch (error: any) {
      console.error('Failed to apply to study:', error);
      toast.error(error.message || 'Failed to apply to study. Please try again.');
    }
  };

  const handleLearnMore = (study: Study) => {
    setSelectedStudy(study);
    setStudyDetailsDialogOpen(true);
  };

  const handleContactResearcher = async (study: Study) => {
    if (!study.researcher) {
      toast.error('Researcher information not available');
      return;
    }

    try {
      // Start a conversation with the researcher
      await messagesAPI.sendMessage({
        receiver_id: study.researcher.id,
        content: `Hi ${study.researcher.name}, I'm a participant in your study "${study.title}".`,
        study_id: study.id,
      });

      // Switch to messages tab to show the conversation
      // This would require adding a way to switch tabs or navigate to messages
      toast.success(`Message sent to ${study.researcher.name}`);
    } catch (error: any) {
      console.error('Failed to contact researcher:', error);
      toast.error('Failed to send message to researcher');
    }
  };

  const handleUpdateProfile = async () => {
    try {
      const profileData: any = {};
      if (profileForm.date_of_birth) profileData.date_of_birth = profileForm.date_of_birth;
      if (profileForm.gender) profileData.gender = profileForm.gender;
      if (profileForm.location) profileData.location = profileForm.location;
      if (profileForm.bio) profileData.bio = profileForm.bio;
      if (profileForm.interests) profileData.interests = profileForm.interests.split(',').map(i => i.trim());
      if (profileForm.availability) profileData.availability = profileForm.availability.split(',').map(a => a.trim());
      if (profileForm.phone_number) profileData.phone_number = profileForm.phone_number;
      
      await participantsAPI.updateProfile(profileData);
      toast.success('Profile updated successfully!');
      setProfileOpen(false);
      // Refresh user data
      const userData = localStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      toast.error(error.message || 'Failed to update profile. Please try again.');
    }
  };

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const profile = await participantsAPI.getProfile();
        if (profile.participant_profile) {
          const p = profile.participant_profile;
          setProfileForm({
            date_of_birth: p.date_of_birth || '',
            gender: p.gender || '',
            location: p.location || '',
            bio: p.bio || '',
            interests: Array.isArray(p.interests) ? p.interests.join(', ') : (p.interests || ''),
            availability: Array.isArray(p.availability) ? p.availability.join(', ') : (p.availability || ''),
            phone_number: p.phone_number || '',
          });
        }
      } catch (error) {
        console.error('Failed to load profile:', error);
      }
    };
    if (user?.id) {
      loadProfile();
    }
  }, [user]);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">Participant Dashboard</h1>
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
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {user?.name?.charAt(0) || 'P'}
                </div>
                <span className="text-sm font-medium">{user?.name || 'Participant'}</span>
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
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeStudies}</div>
              <p className="text-xs text-muted-foreground">Currently participating</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Studies</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.completedStudies}</div>
              <p className="text-xs text-muted-foreground">Successfully finished</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Earnings</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.totalEarnings}</div>
              <p className="text-xs text-muted-foreground">From all studies</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Match Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.matchRate}%</div>
              <p className="text-xs text-muted-foreground">Profile compatibility</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="recommended" className="space-y-6">
          <TabsList>
            <TabsTrigger value="recommended">Recommended Studies</TabsTrigger>
            <TabsTrigger value="my-studies">My Studies</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="profile">Profile</TabsTrigger>
          </TabsList>

          <TabsContent value="recommended" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Personalized Recommendations</h2>
                <p className="text-gray-600">Based on your profile and preferences</p>
              </div>
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
              {recommendedStudies.map((study) => (
                <Card key={study.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-xl">{study.title}</CardTitle>
                          {study.matchScore && (
                            <Badge className={getMatchScoreColor(study.matchScore)}>
                              {study.matchScore}% Match
                            </Badge>
                          )}
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
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => handleLearnMore(study)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
                        <MapPin className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">{study.location}</div>
                          <div className="text-xs text-gray-500">Location</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">
                            {study.participants_current}/{study.participants_needed}
                          </div>
                          <div className="text-xs text-gray-500">Participants</div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="text-sm font-medium">Requirements:</div>
                      <div className="flex flex-wrap gap-2">
                        {formatRequirements(study.requirements).map((req, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {req}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="flex items-center">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              className={`w-4 h-4 ${
                                star <= 4 ? 'text-yellow-400 fill-current' : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm text-gray-600">4.2 (128 reviews)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleLearnMore(study)}
                        >
                          Learn More
                        </Button>
                        <Button size="sm" onClick={() => handleApplyToStudy(study)}>
                          Apply Now
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="my-studies" className="space-y-6">
            <h2 className="text-xl font-semibold">My Studies & Applications</h2>
            <div className="grid gap-6">
              {myStudies.map((study) => (
                <Card key={study.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-xl">{study.title}</CardTitle>
                          <Badge className={
                            study.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                            study.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                            study.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }>
                            {study.status === 'ACTIVE' ? 'ACTIVE' :
                             study.status === 'PENDING' ? 'PENDING APPROVAL' :
                             study.status === 'COMPLETED' ? 'COMPLETED' :
                             study.status}
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
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
                        <MapPin className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">{study.location}</div>
                          <div className="text-xs text-gray-500">Location</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-500" />
                        <div>
                          <div className="text-sm font-medium">
                            {study.participants_current}/{study.participants_needed}
                          </div>
                          <div className="text-xs text-gray-500">Participants</div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {study.status === 'PENDING' ? (
                          <>
                            <Clock className="w-4 h-4 text-yellow-600" />
                            <span className="text-sm text-yellow-600 font-medium">Waiting for approval</span>
                          </>
                        ) : study.status === 'ACTIVE' ? (
                          <>
                            <Award className="w-4 h-4 text-blue-600" />
                            <span className="text-sm text-blue-600 font-medium">Study in progress</span>
                          </>
                        ) : study.status === 'COMPLETED' ? (
                          <>
                            <CheckCircle className="w-4 h-4 text-green-600" />
                            <span className="text-sm text-green-600 font-medium">Study completed</span>
                          </>
                        ) : (
                          <>
                            <Award className="w-4 h-4 text-blue-600" />
                            <span className="text-sm text-blue-600 font-medium">Study active</span>
                          </>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleLearnMore(study)}
                        >
                          View Details
                        </Button>
                        {study.status !== 'PENDING' && study.researcher && (
                          <Button
                            size="sm"
                            onClick={() => handleContactResearcher(study)}
                          >
                            Contact Researcher
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <h2 className="text-xl font-semibold">Participation History</h2>
            {studyHistory.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Award className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No completed studies yet</h3>
                  <p className="text-gray-600 mb-4">Your completed studies and achievements will appear here.</p>
                  <Button>Browse Recommended Studies</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {studyHistory.map((study) => (
                  <Card key={study.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-xl">{study.title}</CardTitle>
                            <Badge className="bg-blue-100 text-blue-800">
                              COMPLETED
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
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
                            <div className="text-xs text-gray-500">Earned</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-gray-500" />
                          <div>
                            <div className="text-sm font-medium">{study.location}</div>
                            <div className="text-xs text-gray-500">Location</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Award className="w-4 h-4 text-green-600" />
                          <div>
                            <div className="text-sm font-medium text-green-600">Completed</div>
                            <div className="text-xs text-gray-500">Status</div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <span className="text-sm text-green-600 font-medium">Study completed successfully</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleLearnMore(study)}
                          >
                            View Details
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="profile" className="space-y-6">
            <h2 className="text-xl font-semibold">My Profile</h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Profile Information</CardTitle>
                  <CardDescription>Update your personal details</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Full Name</label>
                    <div className="mt-1 p-2 border rounded bg-gray-50">{user?.name || 'John Doe'}</div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Email</label>
                    <div className="mt-1 p-2 border rounded bg-gray-50">{user?.email || 'john@example.com'}</div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Age</label>
                    <div className="mt-1 p-2 border rounded bg-gray-50">24</div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Location</label>
                    <div className="mt-1 p-2 border rounded bg-gray-50">San Francisco, CA</div>
                  </div>
                  <Dialog open={profileOpen} onOpenChange={setProfileOpen}>
                    <DialogTrigger asChild>
                      <Button className="w-full">Edit Profile</Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Edit Profile</DialogTitle>
                        <DialogDescription>Update your profile information</DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="date_of_birth">Date of Birth</Label>
                          <Input
                            id="date_of_birth"
                            type="date"
                            value={profileForm.date_of_birth}
                            onChange={(e) => setProfileForm({ ...profileForm, date_of_birth: e.target.value })}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="gender">Gender</Label>
                          <Input
                            id="gender"
                            value={profileForm.gender}
                            onChange={(e) => setProfileForm({ ...profileForm, gender: e.target.value })}
                            placeholder="e.g., Male, Female, Other"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="location">Location</Label>
                          <Input
                            id="location"
                            value={profileForm.location}
                            onChange={(e) => setProfileForm({ ...profileForm, location: e.target.value })}
                            placeholder="City, State"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="bio">Bio</Label>
                          <Textarea
                            id="bio"
                            value={profileForm.bio}
                            onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                            placeholder="Tell us about yourself"
                            rows={3}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="interests">Interests (comma-separated)</Label>
                          <Input
                            id="interests"
                            value={profileForm.interests}
                            onChange={(e) => setProfileForm({ ...profileForm, interests: e.target.value })}
                            placeholder="e.g., Psychology, Health, Technology"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="availability">Availability</Label>
                          <Input
                            id="availability"
                            value={profileForm.availability}
                            onChange={(e) => setProfileForm({ ...profileForm, availability: e.target.value })}
                            placeholder="e.g., Weekdays, Evenings"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="phone_number">Phone Number</Label>
                          <Input
                            id="phone_number"
                            value={profileForm.phone_number}
                            onChange={(e) => setProfileForm({ ...profileForm, phone_number: e.target.value })}
                            placeholder="+1 (555) 123-4567"
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

              <Card>
                <CardHeader>
                  <CardTitle>Research Preferences</CardTitle>
                  <CardDescription>Tell us what interests you</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Interests</label>
                    <div className="mt-1 flex flex-wrap gap-2">
                      <Badge variant="outline">Psychology</Badge>
                      <Badge variant="outline">Health</Badge>
                      <Badge variant="outline">Technology</Badge>
                      <Badge variant="outline">Education</Badge>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Availability</label>
                    <div className="mt-1 p-2 border rounded bg-gray-50">Weekdays, Evenings</div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Study Types</label>
                    <div className="mt-1 flex flex-wrap gap-2">
                      <Badge variant="outline">Online Surveys</Badge>
                      <Badge variant="outline">In-person</Badge>
                      <Badge variant="outline">Longitudinal</Badge>
                    </div>
                  </div>
                  <Button className="w-full" variant="outline">Update Preferences</Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Achievements</CardTitle>
                  <CardDescription>Your research milestones</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                      <Star className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div>
                      <div className="font-medium">First Study</div>
                      <div className="text-sm text-gray-600">Completed your first research study</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <Award className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="font-medium">Reliable Participant</div>
                      <div className="text-sm text-gray-600">100% completion rate</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <div className="font-medium">5 Studies</div>
                      <div className="text-sm text-gray-600">Participated in 5 studies</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Apply to Study Dialog */}
        <Dialog open={applyDialogOpen} onOpenChange={setApplyDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Apply to Study</DialogTitle>
              <DialogDescription>
                Send a message to the researcher explaining why you're interested in this study.
              </DialogDescription>
            </DialogHeader>

            {selectedStudy && (
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-lg">{selectedStudy.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{selectedStudy.description}</p>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span>{selectedStudy.institution}</span>
                    <span>•</span>
                    <span>{selectedStudy.category}</span>
                    <span>•</span>
                    <span>${selectedStudy.compensation}</span>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">Researcher: </span>
                      <span className="text-gray-600">{selectedStudy.researcher?.name || 'Research Team'}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="application-message">Your Message (Optional)</Label>
                  <Textarea
                    id="application-message"
                    placeholder="Tell the researcher why you're interested in participating in this study..."
                    value={applicationMessage}
                    onChange={(e) => setApplicationMessage(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setApplyDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleSubmitApplication}>
                    <Send className="w-4 h-4 mr-2" />
                    Submit Application
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Study Details Dialog */}
        <Dialog open={studyDetailsDialogOpen} onOpenChange={setStudyDetailsDialogOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Study Details</DialogTitle>
              <DialogDescription>
                Complete information about this research study
              </DialogDescription>
            </DialogHeader>

            {selectedStudy && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold mb-2">{selectedStudy.title}</h2>
                  <p className="text-gray-600 mb-4">{selectedStudy.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                    <span className="font-medium">{selectedStudy.institution}</span>
                    <span>•</span>
                    <span>{selectedStudy.category}</span>
                    <span>•</span>
                    <span>{selectedStudy.duration}</span>
                  </div>
                  <div className="text-sm text-gray-600 mb-4">
                    <span className="font-medium">Researcher: </span>
                    <span>{selectedStudy.researcher?.name || 'Research Team'}</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Study Information</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="font-medium">Compensation:</span>
                        <span>${selectedStudy.compensation}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Location:</span>
                        <span>{selectedStudy.location}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Participants:</span>
                        <span>{selectedStudy.participants_current}/{selectedStudy.participants_needed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Status:</span>
                        <Badge variant={selectedStudy.status === 'ACTIVE' ? 'default' : 'secondary'}>
                          {selectedStudy.status}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Requirements</h3>
                    <div className="space-y-2">
                      {formatRequirements(selectedStudy.requirements).map((req, index) => (
                        <Badge key={index} variant="outline" className="mr-2 mb-2">
                          {req}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setStudyDetailsDialogOpen(false)}>
                    Close
                  </Button>
                  {selectedStudy.status === 'ACTIVE' && (
                    <Button onClick={() => {
                      setStudyDetailsDialogOpen(false);
                      handleApplyToStudy(selectedStudy);
                    }}>
                      <Send className="w-4 h-4 mr-2" />
                      Apply Now
                    </Button>
                  )}
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
