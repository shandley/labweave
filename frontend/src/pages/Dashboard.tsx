import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiService } from '@/services/api'
import { useAuth } from '@/context/AuthContext'

const Dashboard: React.FC = () => {
  const { user } = useAuth()

  // Fetch dashboard statistics
  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: apiService.getProjects,
  })

  const { data: experiments } = useQuery({
    queryKey: ['experiments'],
    queryFn: apiService.getExperiments,
  })

  const { data: documents } = useQuery({
    queryKey: ['documents'],
    queryFn: apiService.getDocuments,
  })

  const stats = [
    { name: 'Total Projects', value: projects?.length || 0, color: 'bg-blue-500' },
    { name: 'Active Experiments', value: experiments?.filter((e: any) => e.status === 'active').length || 0, color: 'bg-green-500' },
    { name: 'Documents', value: documents?.length || 0, color: 'bg-purple-500' },
  ]

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Welcome back, {user?.full_name}
      </h1>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 h-12 w-12 ${stat.color} rounded-md flex items-center justify-center`}>
                  <span className="text-white text-xl font-bold">{stat.value}</span>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Projects */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Recent Projects
            </h3>
          </div>
          <div className="px-4 py-5 sm:p-6">
            {projects?.slice(0, 5).map((project: any) => (
              <div key={project.id} className="py-3 border-b border-gray-200 last:border-0">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-900">{project.title}</h4>
                  <span className="text-sm text-gray-500">{project.status}</span>
                </div>
                <p className="text-sm text-gray-500 mt-1">{project.description}</p>
              </div>
            ))}
            {(!projects || projects.length === 0) && (
              <p className="text-sm text-gray-500">No projects yet</p>
            )}
          </div>
        </div>

        {/* Recent Experiments */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Recent Experiments
            </h3>
          </div>
          <div className="px-4 py-5 sm:p-6">
            {experiments?.slice(0, 5).map((experiment: any) => (
              <div key={experiment.id} className="py-3 border-b border-gray-200 last:border-0">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-900">{experiment.title}</h4>
                  <span className="text-sm text-gray-500">{experiment.status}</span>
                </div>
                <p className="text-sm text-gray-500 mt-1">{experiment.description}</p>
              </div>
            ))}
            {(!experiments || experiments.length === 0) && (
              <p className="text-sm text-gray-500">No experiments yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard