'use client';

import { useState } from 'react';
import { Job } from '@/lib/api';
import JobCard from './JobCard';

interface JobColumnProps {
  title: string;
  jobs: Job[];
  color: string;
  icon: React.ReactNode;
}

export default function JobColumn({ title, jobs, color, icon }: JobColumnProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const colorClasses = {
    green: 'bg-green-50 border-green-200',
    blue: 'bg-blue-50 border-blue-200',
    gray: 'bg-gray-50 border-gray-200',
  };

  const headerColors = {
    green: 'bg-green-600',
    blue: 'bg-blue-600',
    gray: 'bg-gray-600',
  };

  return (
    <div className="flex flex-col h-full">
      {/* Column Header - Clickable to toggle collapse */}
      <div 
        className={`${headerColors[color as keyof typeof headerColors]} text-white rounded-t-lg px-4 py-3 sticky top-0 z-10 shadow-md cursor-pointer hover:opacity-90 transition-opacity`}
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {icon}
            <h2 className="text-xl font-bold ml-2">{title}</h2>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-white bg-opacity-25 px-3 py-1 rounded-full text-sm font-semibold">
              {jobs.length}
            </span>
            {/* Collapse/Expand Icon */}
            <svg 
              className={`w-5 h-5 transition-transform duration-200 ${isCollapsed ? 'rotate-180' : ''}`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Jobs List - Collapsible with vertical scrollbar */}
      <div 
        className={`transition-all duration-300 ease-in-out overflow-hidden ${
          isCollapsed ? 'max-h-0' : 'flex-1'
        }`}
      >
        <div 
          className={`h-full overflow-y-auto p-4 space-y-4 ${colorClasses[color as keyof typeof colorClasses]} border-l border-r border-b rounded-b-lg`}
          style={{ 
            maxHeight: isCollapsed ? '0' : 'calc(100vh - 350px)',
            scrollbarWidth: 'thin',
            scrollbarColor: '#888 #f1f1f1'
          }}
        >
          {jobs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <svg className="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p className="text-sm">No jobs in this category yet</p>
            </div>
          ) : (
            jobs.map((job) => <JobCard key={job.id} job={job} />)
          )}
        </div>
      </div>
    </div>
  );
}
