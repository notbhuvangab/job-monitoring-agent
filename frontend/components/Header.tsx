'use client';

import { useState } from 'react';
import { Stats } from '@/lib/api';

interface HeaderProps {
  stats: Stats | null;
  searchQuery: string;
  remoteOnly: boolean;
  onSearch: (query: string) => void;
  onRemoteToggle: (enabled: boolean) => void;
  onUploadResume: (file: File) => void;
  onDeleteResume: () => void;
  onTriggerFetch: () => void;
  hasResume: boolean;
  isFetching?: boolean;
}

export default function Header({ stats, searchQuery, remoteOnly, onSearch, onRemoteToggle, onUploadResume, onDeleteResume, onTriggerFetch, hasResume, isFetching = false }: HeaderProps) {
  const [uploading, setUploading] = useState(false);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    onSearch(query);
  };

  const handleRemoteToggle = () => {
    onRemoteToggle(!remoteOnly);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploading(true);
      try {
        await onUploadResume(file);
        alert('Resume uploaded successfully! Jobs will be re-scored.');
      } catch (error) {
        alert('Error uploading resume. Please try again.');
      } finally {
        setUploading(false);
      }
    }
  };

  return (
    <header className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Title and Stats */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Job Monitoring & Resume Fit Agent
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              AI-powered job matching with real-time updates
            </p>
          </div>
          
          {/* Stats */}
          {stats && (
            <div className="flex gap-4">
              <div className="bg-green-50 px-4 py-2 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{stats.by_label.best_fit}</div>
                <div className="text-xs text-gray-600">Best Fit</div>
              </div>
              <div className="bg-blue-50 px-4 py-2 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{stats.by_label.mid_fit}</div>
                <div className="text-xs text-gray-600">Mid Fit</div>
              </div>
              <div className="bg-gray-50 px-4 py-2 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">{stats.by_label.least_fit}</div>
                <div className="text-xs text-gray-600">Least Fit</div>
              </div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex flex-wrap gap-4 items-center">
          {/* Search */}
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <input
                type="text"
                placeholder="Search jobs by title, company, or keywords..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg
                className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* Remote Toggle */}
          <label className="flex items-center cursor-pointer">
            <div className="relative">
              <input
                type="checkbox"
                checked={remoteOnly}
                onChange={handleRemoteToggle}
                className="sr-only"
              />
              <div className={`block w-14 h-8 rounded-full ${remoteOnly ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
              <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition ${remoteOnly ? 'transform translate-x-6' : ''}`}></div>
            </div>
            <div className="ml-3 text-sm font-medium text-gray-700">
              Remote Only
            </div>
          </label>

          {/* Resume Actions */}
          {!hasResume ? (
            <label className="cursor-pointer inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-lg transition-colors duration-200">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              {uploading ? 'Uploading...' : 'Upload Resume'}
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
          ) : (
            <div className="flex gap-2">
              <span className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 text-sm font-medium rounded-lg">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Resume Uploaded
              </span>
              <button
                onClick={onDeleteResume}
                className="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Resume
              </button>
            </div>
          )}

          {/* Trigger Fetch - Disabled if no resume */}
          <button
            onClick={onTriggerFetch}
            disabled={!hasResume || isFetching}
            className={`inline-flex items-center px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors duration-200 ${
              hasResume && !isFetching
                ? 'bg-green-600 hover:bg-green-700 cursor-pointer' 
                : 'bg-gray-400 cursor-not-allowed opacity-60'
            }`}
            title={
              !hasResume ? 'Upload a resume first' : 
              isFetching ? 'Fetching jobs...' : 
              'Fetch jobs now'
            }
          >
            {isFetching ? (
              <>
                <svg className="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Fetching...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Fetch Jobs Now
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}

