'use client';

import { Job } from '@/lib/api';

interface JobCardProps {
  job: Job;
}

export default function JobCard({ job }: JobCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600 bg-green-50';
    if (score >= 65) return 'text-blue-600 bg-blue-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getTypeColor = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'remote':
        return 'bg-purple-100 text-purple-800';
      case 'hybrid':
        return 'bg-blue-100 text-blue-800';
      case 'onsite':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const truncateDescription = (text: string, maxLength: number = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border border-gray-200">
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {job.title}
          </h3>
          <p className="text-md font-medium text-gray-700">{job.company}</p>
        </div>
        <div className={`ml-4 px-3 py-1 rounded-full text-sm font-bold ${getScoreColor(job.score)}`}>
          {Math.round(job.score)}%
        </div>
      </div>

      {/* Location and Type */}
      <div className="flex flex-wrap gap-2 mb-3">
        {job.location && (
          <span className="inline-flex items-center text-sm text-gray-600">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {job.location}
          </span>
        )}
        {job.type && (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(job.type)}`}>
            {job.type.toUpperCase()}
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-4 line-clamp-3">
        {truncateDescription(job.description)}
      </p>

      {/* LLM Reasoning
      {job.llm_reasoning && (
        <div className="mb-3 p-3 bg-blue-50 border-l-4 border-blue-400 rounded">
          <p className="text-xs font-semibold text-blue-900 mb-1 flex items-center">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            AI Analysis:
          </p>
          <p className="text-xs text-blue-800 italic">{job.llm_reasoning}</p>
        </div>
      )} */}

      {/* Keywords */}
      {job.keywords_matched && job.keywords_matched.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-700 mb-2">
            Matched Skills ({job.keywords_matched.length}):
          </p>
          <div className="flex flex-wrap gap-1">
            {job.keywords_matched.slice(0, 8).map((keyword, idx) => (
              <span
                key={idx}
                className="inline-block px-2 py-1 text-xs bg-indigo-50 text-indigo-700 rounded"
              >
                {keyword}
              </span>
            ))}
            {job.keywords_matched.length > 8 && (
              <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                +{job.keywords_matched.length - 8} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Apply Button */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <span className="text-xs text-gray-500">
          {new Date(job.created_at).toLocaleDateString()}
        </span>
        {job.apply_url && (
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
          >
            Apply Now
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}

