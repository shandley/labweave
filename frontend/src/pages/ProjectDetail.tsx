import React from 'react'
import { useParams } from 'react-router-dom'

const ProjectDetail: React.FC = () => {
  const { id } = useParams()
  
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Project Detail {id}</h1>
      <p>Project detail page coming soon...</p>
    </div>
  )
}

export default ProjectDetail