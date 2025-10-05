'use client';

import { useEffect, useState } from 'react';
import { api, Job, Stats, SchedulerInfo } from '@/lib/api';
import { WebSocketClient } from '@/lib/websocket';
import Header from '@/components/Header';
import JobColumn from '@/components/JobColumn';

export default function Home() {
  // Initialize with empty arrays - will be populated after hydration
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true); // Only for initial page load
  const [searchQuery, setSearchQuery] = useState('');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [hasResume, setHasResume] = useState(false);
  const [wsClient] = useState(() => new WebSocketClient());
  const [isFetching, setIsFetching] = useState(false);
  const [schedulerInfo, setSchedulerInfo] = useState<SchedulerInfo | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  // Fetch jobs with smart merging
  const fetchJobs = async () => {
    try {
      const fetchedJobs = await api.getJobs({
        search: searchQuery || undefined,
        remote_only: remoteOnly,
        limit: 1000,
      });
      
      // Always use fresh data from database (no merging with old cached data)
      setJobs(fetchedJobs);
      
      // Persist fresh jobs to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('job-monitoring-jobs', JSON.stringify(fetchedJobs));
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  // Fetch stats
  const fetchStats = async () => {
    try {
      const fetchedStats = await api.getStats();
      setStats(fetchedStats);
      
      // Persist to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('job-monitoring-stats', JSON.stringify(fetchedStats));
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Check if resume exists
  const checkResume = async () => {
    const resume = await api.getCurrentResume();
    setHasResume(resume !== null);
  };

  // Fetch scheduler info
  const fetchSchedulerInfo = async () => {
    try {
      const info = await api.getSchedulerInfo();
      setSchedulerInfo(info);
    } catch (error) {
      console.error('Error fetching scheduler info:', error);
    }
  };

  // Hydration effect - load from localStorage after client-side hydration
  useEffect(() => {
    // Load cached data from localStorage after hydration
    const loadCachedData = () => {
      try {
        const savedJobs = localStorage.getItem('job-monitoring-jobs');
        const savedStats = localStorage.getItem('job-monitoring-stats');
        
        if (savedJobs) {
          setJobs(JSON.parse(savedJobs));
        }
        
        if (savedStats) {
          setStats(JSON.parse(savedStats));
        }
      } catch (error) {
        console.error('Error loading cached data:', error);
      }
    };
    
    setIsHydrated(true);
    loadCachedData();
  }, []);

  // Initial load - ALWAYS fetch fresh data from database
  useEffect(() => {
    if (!isHydrated) return; // Wait for hydration
    
    const loadData = async () => {
      // Always fetch fresh data from database (will merge with cached data)
      const promises = [
        fetchJobs(), // Always fetch jobs to get latest from DB
        fetchStats(), // Always fetch stats to get latest from DB
        checkResume(),
        fetchSchedulerInfo()
      ];
      
      await Promise.all(promises);
      setLoading(false); // Initial load complete
    };
    
    loadData();

    // Setup WebSocket - stream new jobs without loading state
    wsClient.connect((message) => {
      if (message.type === 'new_job') {
        console.log('New job received:', message.data);
        const newJob = message.data;
        
        // Add new job to state without re-fetching (streaming!)
        setJobs(prevJobs => {
          // Check if job already exists
          if (prevJobs.some(j => j.id === newJob.id)) {
            return prevJobs;
          }
          const updatedJobs = [newJob, ...prevJobs];
          
          // Persist to localStorage
          if (typeof window !== 'undefined') {
            localStorage.setItem('job-monitoring-jobs', JSON.stringify(updatedJobs));
          }
          
          return updatedJobs;
        });
        
        // Update stats without re-fetching
        setStats(prevStats => {
          if (!prevStats) return prevStats;
          
          const label = newJob.label;
          const type = newJob.type;
          
          const updatedStats = {
            ...prevStats,
            total_jobs: prevStats.total_jobs + 1,
            classified_jobs: prevStats.classified_jobs + 1,
            by_label: {
              best_fit: prevStats.by_label.best_fit + (label === 'best' ? 1 : 0),
              mid_fit: prevStats.by_label.mid_fit + (label === 'mid' ? 1 : 0),
              least_fit: prevStats.by_label.least_fit + (label === 'least' ? 1 : 0),
            },
            by_type: {
              remote: prevStats.by_type.remote + (type === 'remote' ? 1 : 0),
              hybrid: prevStats.by_type.hybrid + (type === 'hybrid' ? 1 : 0),
              onsite: prevStats.by_type.onsite + (type === 'onsite' ? 1 : 0),
            }
          };
          
          // Persist to localStorage
          if (typeof window !== 'undefined') {
            localStorage.setItem('job-monitoring-stats', JSON.stringify(updatedStats));
          }
          
          return updatedStats;
        });
      }
    });

    return () => {
      wsClient.disconnect();
    };
  }, [isHydrated]);

  // Refetch when filters change (background, no loading state)
  useEffect(() => {
    if (!loading && isHydrated) {
      fetchJobs(); // This happens in background
    }
  }, [searchQuery, remoteOnly, isHydrated, loading]);

  // Refresh scheduler info periodically
  useEffect(() => {
    if (!loading && isHydrated) {
      const interval = setInterval(fetchSchedulerInfo, 30000); // Every 30 seconds
      return () => clearInterval(interval);
    }
  }, [loading, isHydrated]);

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  // Handle remote toggle
  const handleRemoteToggle = (enabled: boolean) => {
    setRemoteOnly(enabled);
  };

  // Handle resume upload
  const handleUploadResume = async (file: File) => {
    await api.uploadResume(file);
    setHasResume(true);
    // Refresh jobs after resume upload
    setTimeout(() => {
      fetchJobs();
      fetchStats();
    }, 2000);
  };

  // Handle resume delete
  const handleDeleteResume = async () => {
    if (confirm('Are you sure you want to delete your resume? This will stop job scoring.')) {
      await api.deleteResume();
      setHasResume(false);
      alert('Resume deleted successfully.');
    }
  };

  // Handle trigger fetch
  const handleTriggerFetch = async () => {
    if (!hasResume) {
      alert('Please upload a resume first before fetching jobs.');
      return;
    }
    
    setIsFetching(true);
    try {
      await api.triggerFetch();
      // Show success message but don't block the UI
      console.log('Job fetch triggered! New jobs will stream in real-time via WebSocket.');
      // No need to refresh - WebSocket will stream jobs as they're processed!
    } catch (error: any) {
      const errorMsg = error?.response?.data?.detail || 'Error triggering job fetch.';
      alert(errorMsg);
    } finally {
      // Reset fetching state after a short delay to show the loading state
      setTimeout(() => setIsFetching(false), 2000);
    }
  };

  // Categorize jobs
  const bestFitJobs = jobs.filter(job => job.label === 'best');
  const midFitJobs = jobs.filter(job => job.label === 'mid');
  const leastFitJobs = jobs.filter(job => job.label === 'least');

  return (
    <div className="min-h-screen bg-gray-100">
        <Header
          stats={stats}
          searchQuery={searchQuery}
          remoteOnly={remoteOnly}
          onSearch={handleSearch}
          onRemoteToggle={handleRemoteToggle}
          onUploadResume={handleUploadResume}
          onDeleteResume={handleDeleteResume}
          onTriggerFetch={handleTriggerFetch}
          hasResume={hasResume}
          isFetching={isFetching}
        />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status notifications */}
        {isFetching && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center">
              <svg className="animate-spin w-5 h-5 text-blue-600 mr-3" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-blue-800 font-medium">
                Fetching and processing new jobs... They will appear below as they're scored.
              </p>
            </div>
          </div>
        )}

        {jobs.length > 0 && !loading && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <p className="text-green-800 text-sm">
                  Showing {jobs.length} jobs • Data persists across page refreshes
                </p>
              </div>
              
              {/* Scheduler Info */}
              {schedulerInfo && (
                <div className="text-xs text-green-700">
                  <div className="flex items-center space-x-4">
                    <span>
                      Last fetch: {schedulerInfo.last_fetch 
                        ? new Date(schedulerInfo.last_fetch).toLocaleTimeString()
                        : 'Never'
                      }
                    </span>
                    <span>
                      Next fetch: {schedulerInfo.next_fetch 
                        ? new Date(schedulerInfo.next_fetch).toLocaleTimeString()
                        : 'Not scheduled'
                      }
                    </span>
                    {schedulerInfo.is_running && (
                      <span className="text-orange-600 font-medium">
                        🔄 Fetching...
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Loading indicator for initial load only */}
        {loading && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <svg className="animate-spin w-5 h-5 text-blue-600 mr-3" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-blue-800 font-medium">
              Fetching and processing new jobs... They will appear below as they're scored.
            </p>
          </div>
        </div>
        )}

        {/* Dashboard - always visible after initial load */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[calc(100vh-300px)]">
          {/* Best Fit Column */}
          <JobColumn
            title="Best Fit"
            jobs={bestFitJobs}
            color="green"
            icon={
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            }
          />

          {/* Mid Fit Column */}
          <JobColumn
            title="Mid Fit"
            jobs={midFitJobs}
            color="blue"
            icon={
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            }
          />

          {/* Least Fit Column */}
          <JobColumn
            title="Least Fit"
            jobs={leastFitJobs}
            color="gray"
            icon={
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            }
          />
        </div>
      </main>
    </div>
  );
}